"""
Account Manager for Gmail accounts.
Handles database operations for registered email accounts.
"""
import psycopg2
from datetime import datetime
from database import DatabaseManager
from logger import logger


class AccountManager:
    """Manages Gmail accounts in the database."""

    def __init__(self):
        self.db_manager = DatabaseManager()

    def add_account(self, email_address, service='gmail'):
        """
        Register a Gmail account in the database.

        Args:
            email_address (str): Gmail address
            service (str): Service type (default: 'gmail')

        Returns:
            int: Account ID or None if already exists
        """
        conn = None
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            # Try to insert the account
            cursor.execute('''
                INSERT INTO accounts (email_address, service)
                VALUES (%s, %s)
                RETURNING id
            ''', (email_address, service))

            account_id = cursor.fetchone()[0]
            conn.commit()

            logger.info(f"Account added: {email_address} (ID: {account_id})")
            return account_id

        except psycopg2.IntegrityError:
            # Account already exists, rollback any pending transaction
            if conn:
                conn.rollback()

            # Get existing account ID
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM accounts WHERE email_address = %s",
                (email_address,)
            )
            result = cursor.fetchone()
            account_id = result[0] if result else None
            
            logger.warning(f"Account already exists: {email_address} (ID: {account_id})")
            return account_id

        except Exception as e:
            if conn:
                conn.rollback()
            logger.exception(f"Error adding account: {email_address}")
            raise

        finally:
            if conn:
                cursor.close()
                conn.close()

    def get_account(self, email_address):
        """
        Get account information by email address.

        Args:
            email_address (str): Gmail address

        Returns:
            dict: Account info or None if not found
        """
        conn = None
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT id, email_address, service, added_date
                FROM accounts
                WHERE email_address = %s
            ''', (email_address,))

            result = cursor.fetchone()

            if result:
                return {
                    'id': result[0],
                    'email_address': result[1],
                    'service': result[2],
                    'added_date': result[3]
                }
            return None

        except Exception as e:
            logger.exception(f"Error retrieving account: {email_address}")
            return None

        finally:
            if conn:
                cursor.close()
                conn.close()

    def get_all_accounts(self):
        """
        Get all registered accounts.

        Returns:
            list: List of account dictionaries
        """
        conn = None
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT id, email_address, service, added_date
                FROM accounts
                ORDER BY added_date DESC
            ''')

            accounts = []
            for row in cursor.fetchall():
                accounts.append({
                    'id': row[0],
                    'email_address': row[1],
                    'service': row[2],
                    'added_date': row[3]
                })

            return accounts

        except Exception as e:
            logger.exception("Error retrieving all accounts.")
            return []

        finally:
            if conn:
                cursor.close()
                conn.close()

    def remove_account(self, email_address):
        """
        Remove an account from the database.

        Note: This will also delete all associated requests due to CASCADE.

        Args:
            email_address (str): Gmail address to remove

        Returns:
            bool: True if deleted, False otherwise
        """
        conn = None
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                DELETE FROM accounts
                WHERE email_address = %s
            ''', (email_address,))

            deleted_count = cursor.rowcount
            conn.commit()

            if deleted_count > 0:
                logger.info(f"Account removed: {email_address}")
                logger.warning("All associated deletion requests were also removed due to CASCADE.")
                return True
            else:
                logger.warning(f"Account not found for removal: {email_address}")
                return False

        except Exception as e:
            if conn:
                conn.rollback()
            logger.exception(f"Error removing account: {email_address}")
            return False

        finally:
            if conn:
                cursor.close()
                conn.close()

    def list_accounts(self):
        """
        Print a formatted list of all accounts.
        """
        accounts = self.get_all_accounts()

        if not accounts:
            logger.info("\n📭 No accounts registered yet.")
            logger.info("   Add an account to get started!")
            return

        logger.info("\n" + "="*60)
        print("📧 REGISTERED GMAIL ACCOUNTS")
        print("="*60)

        for i, account in enumerate(accounts, 1):
            print(f"\n{i}. {account['email_address']}")
            print(f"   ID: {account['id']}")
            print(f"   Service: {account['service']}")
            print(f"   Added: {account['added_date'].strftime('%Y-%m-%d %H:%M:%S')}")

        logger.info("\n" + "="*60)
        print(f"Total: {len(accounts)} account(s)")
        print("="*60)

    def get_account_statistics(self, email_address):
        """
        Get statistics for a specific account.

        Args:
            email_address (str): Gmail address

        Returns:
            dict: Statistics including companies found, requests sent, etc.
        """
        conn = None
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            # Default return if account not found
            default_stats = {
                'total_companies': 0, 'companies_with_contacts': 0,
                'requests_sent': 0, 'requests_replied': 0,
                'requests_completed': 0, 'requests_failed': 0,
                'requests_pending': 0, 'completion_rate': 0.0
            }

            # Get account ID
            # Using get_account to leverage its error handling/logging
            account = self.get_account(email_address)
            if not account:
                logger.warning(f"Account {email_address} not found for statistics.")
                return default_stats

            account_id = account['id']

            # Count deletion requests by status
            cursor.execute('''
                SELECT status, COUNT(*)
                FROM requests
                WHERE account_id = %s
                GROUP BY status
            ''', (account_id,))

            status_counts = {}
            for status, count in cursor.fetchall():
                status_counts[status.lower()] = count # Convert to lowercase for consistency

            total_requests = sum(status_counts.values())

            # Get total companies discovered
            cursor.execute('''
                SELECT COUNT(DISTINCT company_id)
                FROM requests
                WHERE account_id = %s
            ''', (account_id,))

            companies_count = cursor.fetchone()[0]

            requests_sent = status_counts.get('sent', 0)
            requests_replied = status_counts.get('replied', 0)
            requests_completed = status_counts.get('completed', 0)
            requests_failed = status_counts.get('failed', 0)
            requests_pending = status_counts.get('pending', 0)

            completion_rate = (requests_completed / requests_sent * 100) if requests_sent > 0 else 0.0

            return {
                'email_address': email_address,
                'total_companies': companies_count,
                'total_requests': total_requests,
                'requests_sent': requests_sent,
                'requests_replied': requests_replied,
                'requests_completed': requests_completed,
                'requests_failed': requests_failed,
                'requests_pending': requests_pending,
                'completion_rate': completion_rate
            }

        except Exception as e:
            logger.exception(f"Error getting statistics for account: {email_address}")
            return default_stats

        finally:
            if conn:
                cursor.close()
                conn.close()


# Test/Demo function
def test_account_manager():
    """Test the account manager functionality."""
    print("\n" + "="*60)
    print("ACCOUNT MANAGER TEST")
    print("="*60)

    manager = AccountManager()

    # Test adding accounts
    print("\n1. Adding test accounts...")
    test_emails = [
        "test1@gmail.com",
        "test2@gmail.com"
    ]

    for email in test_emails:
        manager.add_account(email)

    # Test listing accounts
    print("\n2. Listing all accounts...")
    manager.list_accounts()

    # Test getting specific account
    print("\n3. Getting specific account...")
    account = manager.get_account(test_emails[0])
    if account:
        print(f"   Found: {account['email_address']}")
    else:
        print("   Not found")

    # Test statistics
    print("\n4. Getting account statistics...")
    stats = manager.get_account_statistics(test_emails[0])
    if stats:
        print(f"   Companies: {stats['total_companies']}")
        print(f"   Requests: {stats['total_requests']}")

    # Test removing account
    print("\n5. Removing test accounts...")
    for email in test_emails:
        manager.remove_account(email)

    print("\n" + "="*60)
    print("Test completed!")
    print("="*60)


if __name__ == "__main__":
    test_account_manager()
