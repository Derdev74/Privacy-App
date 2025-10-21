"""
Deletion Request Sender.
This module handles the construction and sending of data deletion emails
using the Gmail API.
"""

import base64
from email.mime.text import MIMEText
from googleapiclient.errors import HttpError

from gmail_auth import GmailAuthenticator
from templates import DeletionTemplates
from company_manager import CompanyManager
from logger import logger
from database import DatabaseManager # For creating the requests table record


class RequestSender:
    """
    Manages sending deletion request emails for a specific user account.
    """

    def __init__(self, user_email):
        """
        Initializes the RequestSender for a given user.

        Args:
            user_email (str): The email address of the user account to send from.
        """
        self.user_email = user_email
        self.authenticator = GmailAuthenticator()
        self.gmail_service = self.authenticator.get_gmail_service(user_email)
        self.template_manager = DeletionTemplates()
        self.company_manager = CompanyManager()
        self.db_manager = DatabaseManager()

        if not self.gmail_service:
            raise ConnectionError(f"Could not get Gmail service for {user_email}. Please ensure the account is authenticated.")

    def _create_message(self, to, subject, message_text):
        """
        Creates a MIMEText message object.

        Args:
            to (str): The recipient's email address.
            subject (str): The subject of the email.
            message_text (str): The body of the email.

        Returns:
            dict: A dictionary containing the raw, base64url-encoded email.
        """
        message = MIMEText(message_text)
        message['to'] = to
        message['from'] = self.user_email
        message['subject'] = subject
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        return {'raw': raw_message}

    def send_deletion_request(self, company_id, account_id, domain, template_type='generic', user_name=None):
        """
        Sends a deletion request to a company and records it in the database.

        Args:
            company_id (int): The ID of the company from the database.
            domain (str): The domain of the company (e.g., 'spotify.com').
            template_type (str): The template to use ('gdpr', 'ccpa', 'generic').
            account_id (int): The ID of the account sending the request.
            user_name (str, optional): The user's name to include in the email.

        Returns:
            bool: True if the email was sent and recorded successfully, False otherwise.
        """
        company = self.company_manager.get_company_by_domain(domain)
        if not company or not company.get('privacy_contact') or company.get('contact_type') != 'email': # type: ignore
            logger.warning(f"Cannot send email to {domain}: No valid privacy email contact found.")
            return False

        to_email = company['privacy_contact']
        company_name = domain.split('.')[0].capitalize()

        # Generate the email content from the template
        template_func = self.template_manager.get_template(template_type)
        email_content = template_func(company_name, self.user_email, user_name=user_name)

        # Create and send the message
        message_to_send = self._create_message(to_email, email_content['subject'], email_content['body'])

        try:
            logger.info(f"Sending deletion request to {domain} at {to_email}...")
            sent_message = self.gmail_service.users().messages().send(
                userId='me',
                body=message_to_send
            ).execute()
            logger.info(f"Email sent successfully! Message ID: {sent_message['id']}")

            # Record the request in the database
            conn = self.db_manager.get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO requests (company_id, account_id, status, sent_date, sent_message_id, notes)
                    VALUES (%s, %s, %s, NOW(), %s, %s)
                    """,
                    (company_id, account_id, 'SENT', sent_message['id'], f'Template: {template_type}')
                )
                conn.commit()
                logger.info("Request logged in the database.")
                return True
            except Exception:
                if conn:
                    conn.rollback()
                logger.exception("Error logging request to database")
                return False
            finally:
                if conn:
                    cursor.close()
                    conn.close()

        except HttpError as error:
            logger.error(f"An error occurred while sending email to {domain}: {error}")
            return False
        except Exception:
            logger.exception(f"An unexpected error occurred while sending email to {domain}.")
            return False