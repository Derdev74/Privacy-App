"""
Reply Tracker - Monitors email replies to deletion requests.
Automatically categorizes responses and updates request status in the database.
"""

import re
from datetime import datetime
from googleapiclient.errors import HttpError

from gmail_auth import GmailAuthenticator
from database import DatabaseManager
from logger import logger


class ReplyTracker:
    """
    Tracks and processes replies to deletion requests.
    Updates the database based on reply content analysis.
    """

    def __init__(self, user_email):
        """
        Initialize the reply tracker for a specific user account.

        Args:
            user_email (str): Email address to track replies for
        """
        self.user_email = user_email
        self.authenticator = GmailAuthenticator()
        self.gmail_service = self.authenticator.authenticate(user_email)
        self.db_manager = DatabaseManager()

        if not self.gmail_service:
            raise ConnectionError(
                f"Could not get Gmail service for {user_email}. "
                "Please ensure the account is authenticated."
            )

        # Keywords for automatic categorization
        self.completion_keywords = [
            'deleted', 'removed', 'erased', 'completed', 'processed',
            'account closed', 'data removed', 'successfully deleted',
            'deletion complete', 'request completed', 'has been deleted'
        ]

        self.processing_keywords = [
            'processing', 'received your request', 'working on',
            'will process', 'under review', 'being processed',
            'we have received', 'acknowledge receipt', 'will take'
        ]

        self.verification_keywords = [
            'verify', 'confirm your identity', 'additional information',
            'proof of identity', 'verification required', 'cannot verify',
            'need to confirm', 'please provide'
        ]

    def check_for_replies(self, account_id, days_back=30):
        """
        Check for replies to sent deletion requests and update their status.

        Args:
            account_id (int): Database ID of the account
            days_back (int): How many days back to check for replies

        Returns:
            dict: Summary of replies found and processed
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"Checking for replies: {self.user_email}")
        logger.info(f"{'='*60}")

        # Get all pending/sent requests from database
        pending_requests = self._get_pending_requests(account_id)

        if not pending_requests:
            logger.info("No pending deletion requests to track.")
            return {'found': 0, 'updated': 0}

        logger.info(f"Found {len(pending_requests)} pending requests to check.")

        replies_found = 0
        requests_updated = 0

        for request in pending_requests:
            request_id = request['id']
            company_domain = request['domain']
            sent_message_id = request['sent_message_id']

            if not sent_message_id:
                logger.debug(f"Skipping {company_domain} - no message ID recorded")
                continue

            try:
                # Check for replies to this message
                reply_data = self._check_message_for_replies(sent_message_id)

                if reply_data:
                    replies_found += 1
                    logger.info(f" Reply found from {company_domain}")

                    # Analyze the reply and determine status
                    new_status, notes = self._analyze_reply(reply_data['body'])

                    # Update database
                    self._update_request_status(
                        request_id,
                        new_status,
                        reply_data['date'],
                        notes
                    )
                    requests_updated += 1

                    logger.info(f"  Status: {request['status']} ’ {new_status}")

            except HttpError as e:
                logger.error(f"Gmail API error checking {company_domain}: {e}")
                continue
            except Exception:
                logger.exception(f"Error checking replies for {company_domain}")
                continue

        logger.info(f"\n{'='*60}")
        logger.info(f"Reply check complete:")
        logger.info(f"  Replies found: {replies_found}")
        logger.info(f"  Requests updated: {requests_updated}")
        logger.info(f"{'='*60}")

        return {'found': replies_found, 'updated': requests_updated}

    def _get_pending_requests(self, account_id):
        """
        Get all requests that are waiting for replies.

        Args:
            account_id (int): Account ID

        Returns:
            list: List of pending request dictionaries
        """
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT
                    r.id,
                    r.sent_message_id,
                    r.status,
                    c.domain,
                    c.company_name
                FROM requests r
                JOIN companies c ON r.company_id = c.id
                WHERE r.account_id = %s
                AND r.status IN ('SENT', 'REPLIED')
                AND r.sent_message_id IS NOT NULL
                ORDER BY r.sent_date DESC
            ''', (account_id,))

            requests = []
            for row in cursor.fetchall():
                requests.append({
                    'id': row[0],
                    'sent_message_id': row[1],
                    'status': row[2],
                    'domain': row[3],
                    'company_name': row[4]
                })

            return requests

        except Exception:
            logger.exception("Error retrieving pending requests from database")
            return []
        finally:
            if conn:
                cursor.close()
                conn.close()

    def _check_message_for_replies(self, message_id):
        """
        Check if a sent message has received any replies.

        Args:
            message_id (str): Gmail message ID

        Returns:
            dict: Reply data (body, date) or None if no reply
        """
        try:
            # Get the message to find its thread ID
            message = self.gmail_service.users().messages().get(
                userId='me',
                id=message_id,
                format='minimal'
            ).execute()

            thread_id = message.get('threadId')

            if not thread_id:
                return None

            # Get all messages in the thread
            thread = self.gmail_service.users().threads().get(
                userId='me',
                id=thread_id,
                format='full'
            ).execute()

            messages = thread.get('messages', [])

            # If only 1 message, no reply yet
            if len(messages) <= 1:
                return None

            # Get the most recent message (should be the reply)
            latest_message = messages[-1]

            # Make sure it's not our sent message
            if latest_message['id'] == message_id:
                if len(messages) > 1:
                    latest_message = messages[-2]
                else:
                    return None

            # Extract reply body and date
            reply_body = self._extract_message_body(latest_message)
            reply_date = self._extract_message_date(latest_message)

            return {
                'body': reply_body,
                'date': reply_date,
                'message_id': latest_message['id']
            }

        except HttpError as e:
            if e.resp.status == 404:
                logger.debug(f"Message {message_id} not found (may have been deleted)")
                return None
            raise

    def _extract_message_body(self, message):
        """
        Extract text body from Gmail message.

        Args:
            message (dict): Gmail message object

        Returns:
            str: Message body text
        """
        try:
            payload = message.get('payload', {})

            # Try to get plain text part
            if 'parts' in payload:
                for part in payload['parts']:
                    if part.get('mimeType') == 'text/plain':
                        body_data = part.get('body', {}).get('data', '')
                        if body_data:
                            import base64
                            return base64.urlsafe_b64decode(body_data).decode('utf-8', errors='ignore')

            # Fallback: get body from main payload
            body_data = payload.get('body', {}).get('data', '')
            if body_data:
                import base64
                return base64.urlsafe_b64decode(body_data).decode('utf-8', errors='ignore')

            return ""

        except Exception:
            logger.exception("Error extracting message body")
            return ""

    def _extract_message_date(self, message):
        """
        Extract date from Gmail message.

        Args:
            message (dict): Gmail message object

        Returns:
            datetime: Message date
        """
        try:
            # Gmail provides internalDate as milliseconds since epoch
            internal_date = int(message.get('internalDate', 0))
            return datetime.fromtimestamp(internal_date / 1000)
        except Exception:
            logger.exception("Error extracting message date")
            return datetime.now()

    def _analyze_reply(self, reply_body):
        """
        Analyze reply content and determine appropriate status.

        Args:
            reply_body (str): Email reply body text

        Returns:
            tuple: (new_status, notes)
        """
        reply_lower = reply_body.lower()

        # Check for completion
        if any(keyword in reply_lower for keyword in self.completion_keywords):
            return 'COMPLETED', 'Deletion confirmed by company'

        # Check for verification needed
        if any(keyword in reply_lower for keyword in self.verification_keywords):
            return 'REPLIED', 'Verification or additional information required'

        # Check for processing
        if any(keyword in reply_lower for keyword in self.processing_keywords):
            return 'REPLIED', 'Request acknowledged and being processed'

        # Default: generic reply received
        return 'REPLIED', 'Reply received, manual review recommended'

    def _update_request_status(self, request_id, new_status, reply_date, notes):
        """
        Update request status in database.

        Args:
            request_id (int): Request ID
            new_status (str): New status (REPLIED, COMPLETED, etc.)
            reply_date (datetime): Date reply was received
            notes (str): Additional notes
        """
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            if new_status == 'COMPLETED':
                cursor.execute('''
                    UPDATE requests
                    SET status = %s,
                        reply_received_date = %s,
                        completion_date = %s,
                        notes = %s
                    WHERE id = %s
                ''', (new_status, reply_date, reply_date, notes, request_id))
            else:
                cursor.execute('''
                    UPDATE requests
                    SET status = %s,
                        reply_received_date = %s,
                        notes = %s
                    WHERE id = %s
                ''', (new_status, reply_date, notes, request_id))

            conn.commit()
            logger.debug(f"Updated request {request_id} to status {new_status}")

        except Exception:
            if conn:
                conn.rollback()
            logger.exception(f"Error updating request {request_id} status")
        finally:
            if conn:
                cursor.close()
                conn.close()


# Test/Demo function
def test_reply_tracker():
    """Test the reply tracker with a real account."""
    print("\n" + "="*60)
    print("REPLY TRACKER TEST")
    print("="*60)
    print("\nNote: This requires an authenticated Gmail account")
    print("with sent deletion requests in the database.")

    from account_manager import AccountManager

    account_manager = AccountManager()
    accounts = account_manager.get_all_accounts()

    if not accounts:
        print("\n No accounts found. Please add an account first.")
        return

    # Use first account
    account = accounts[0]
    email = account['email_address']
    account_id = account['id']

    print(f"\nChecking replies for: {email}")

    try:
        tracker = ReplyTracker(email)
        results = tracker.check_for_replies(account_id)

        print(f"\n{'='*60}")
        print("RESULTS")
        print("="*60)
        print(f"Replies found: {results['found']}")
        print(f"Requests updated: {results['updated']}")
        print("="*60)

    except Exception as e:
        print(f"\n Error: {e}")


if __name__ == "__main__":
    test_reply_tracker()
