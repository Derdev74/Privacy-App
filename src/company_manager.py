"""
Company Manager for tracking discovered companies.
Stores company information and privacy contacts in the database.
"""
import psycopg2
from datetime import datetime, date
from database import DatabaseManager
from logger import logger
from utils import format_company_name


class CompanyManager:
    """Manages company records in the database."""

    def __init__(self):
        self.db_manager = DatabaseManager()

    def add_company(self, domain, company_name=None, privacy_contact=None, contact_type='email'):
        """
        Add a company to the database.

        Args:
            domain (str): Company domain (e.g., 'spotify.com')
            company_name (str): Company name (optional, will guess from domain)
            privacy_contact (str): Privacy contact email or URL
            contact_type (str): 'email' or 'webform'

        Returns:
            int: Company ID
        """
        conn = None
        try:
            # Guess company name from domain if not provided
            if not company_name:
                company_name = self._guess_company_name(domain)

            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO companies (domain, company_name, privacy_contact, contact_type)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            ''', (domain, company_name, privacy_contact, contact_type))

            company_id = cursor.fetchone()[0]
            conn.commit()

            logger.info(f"Added company: {company_name} ({domain})")
            return company_id

        except psycopg2.IntegrityError:
            # Company already exists, rollback any pending transaction
            if conn:
                conn.rollback()

            cursor = conn.cursor()
            cursor.execute("SELECT id FROM companies WHERE domain = %s", (domain,))
            result = cursor.fetchone()
            company_id = result[0] if result else None
            
            logger.warning(f"Company already exists: {domain} (ID: {company_id})")
            return company_id

        except Exception as e:
            if conn:
                conn.rollback()
            logger.exception(f"Error adding company: {domain}")
            raise

        finally:
            if conn:
                cursor.close()
                conn.close()

    def bulk_add_companies(self, domains):
        """
        Add multiple companies from a list of domains.

        Args:
            domains (list): List of domain strings

        Returns:
            dict: Statistics of added companies
        """
        logger.info(f"\n📥 Bulk adding {len(domains)} companies...")

        added = 0
        existed = 0
        failed = 0

        conn = None
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            for domain in domains:
                try:
                    company_name = self._guess_company_name(domain)
                    cursor.execute(
                        "INSERT INTO companies (domain, company_name) VALUES (%s, %s) ON CONFLICT (domain) DO NOTHING RETURNING id",
                        (domain, company_name)
                    )
                    if cursor.fetchone() is not None:
                        added += 1
                    else:
                        existed += 1
                except Exception as e:
                    logger.error(f"Failed to add {domain}: {e}")
                    failed += 1

            conn.commit()

        except Exception:
            if conn:
                conn.rollback()
            logger.exception("Error during bulk company addition")
            failed = len(domains)
        finally:
            if conn:
                cursor.close()
                conn.close()

        stats = {
            'total': len(domains),
            'added': added,
            'existed': existed,
            'failed': failed
        }

        logger.info(f"\n✓ Bulk add complete:")
        logger.info(f"   New: {stats['added']}")
        logger.info(f"   Existing: {stats['existed']}")
        logger.info(f"   Failed: {stats['failed']}")

        return stats

    def get_company_by_domain(self, domain):
        """
        Get company information by domain.

        Args:
            domain (str): Company domain

        Returns:
            dict: Company info or None
        """
        conn = None
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT id, domain, company_name, privacy_contact, contact_type, last_verified, notes
                FROM companies
                WHERE domain = %s
            ''', (domain,))

            result = cursor.fetchone()

            if result:
                return {
                    'id': result[0],
                    'domain': result[1],
                    'company_name': result[2],
                    'privacy_contact': result[3],
                    'contact_type': result[4],
                    'last_verified': result[5],
                    'notes': result[6]
                }
            return None

        except Exception as e:
            logger.exception(f"Error retrieving company by domain: {domain}")
            return None

        finally:
            if conn:
                cursor.close()
                conn.close()

    def update_privacy_contact(self, domain, privacy_contact, contact_type='email', notes=None):
        """
        Update privacy contact information for a company.

        Args:
            domain (str): Company domain
            privacy_contact (str): Privacy contact email or URL
            contact_type (str): 'email' or 'webform'
            notes (str): Additional notes

        Returns:
            bool: True if updated successfully
        """
        conn = None
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE companies
                SET privacy_contact = %s,
                    contact_type = %s,
                    last_verified = %s,
                    notes = %s
                WHERE domain = %s
            ''', (privacy_contact, contact_type, date.today(), notes, domain))

            updated = cursor.rowcount > 0
            conn.commit()

            if updated:
                logger.info(f"Updated contact for {domain}: {privacy_contact}")
            else:
                logger.warning(f"Company not found for contact update: {domain}")

            return updated

        except Exception as e:
            if conn:
                conn.rollback()
            logger.exception(f"Error updating contact for {domain}")
            return False

        finally:
            if conn:
                cursor.close()
                conn.close()

    def get_companies_without_contacts(self):
        """
        Get all companies that don't have privacy contacts yet.

        Returns:
            list: List of company dictionaries
        """
        conn = None
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT id, domain, company_name
                FROM companies
                WHERE privacy_contact IS NULL OR privacy_contact = ''
                ORDER BY company_name
            ''')

            companies = []
            for row in cursor.fetchall():
                companies.append({
                    'id': row[0],
                    'domain': row[1],
                    'company_name': row[2]
                })

            return companies

        except Exception as e:
            logger.exception("Error retrieving companies without contacts.")
            return []

        finally:
            if conn:
                cursor.close()
                conn.close()

    def get_all_companies(self, with_contacts_only=False):
        """
        Get all companies.

        Args:
            with_contacts_only (bool): If True, only return companies with privacy contacts

        Returns:
            list: List of company dictionaries
        """
        conn = None
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            if with_contacts_only:
                where_clause = "WHERE privacy_contact IS NOT NULL AND privacy_contact != ''"
            else:
                where_clause = ""

            cursor.execute(f'''
                SELECT id, domain, company_name, privacy_contact, contact_type, last_verified
                FROM companies
                {where_clause}
                ORDER BY company_name
            ''')

            companies = []
            for row in cursor.fetchall():
                companies.append({
                    'id': row[0],
                    'domain': row[1],
                    'company_name': row[2],
                    'privacy_contact': row[3],
                    'contact_type': row[4],
                    'last_verified': row[5]
                })

            return companies

        except Exception as e:
            logger.exception("Error retrieving all companies.")
            return []

        finally:
            if conn:
                cursor.close()
                conn.close()

    def search_companies(self, search_term):
        """
        Search companies by name or domain.

        Args:
            search_term (str): Search term

        Returns:
            list: List of matching company dictionaries
        """
        conn = None
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            search_pattern = f'%{search_term}%'
            cursor.execute('''
                SELECT id, domain, company_name, privacy_contact, contact_type
                FROM companies
                WHERE company_name ILIKE %s OR domain ILIKE %s
                ORDER BY company_name
            ''', (search_pattern, search_pattern))

            companies = []
            for row in cursor.fetchall():
                companies.append({
                    'id': row[0],
                    'domain': row[1],
                    'company_name': row[2],
                    'privacy_contact': row[3],
                    'contact_type': row[4]
                })

            return companies

        except Exception as e:
            logger.exception(f"Error searching companies with term: {search_term}")
            return []

        finally:
            if conn:
                cursor.close()
                conn.close()

    def get_statistics(self):
        """
        Get overall statistics about companies.

        Returns:
            dict: Statistics dictionary
        """
        conn = None
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            # Total companies
            cursor.execute("SELECT COUNT(*) FROM companies")
            total_companies = cursor.fetchone()[0]

            # Companies with contacts
            cursor.execute("""
                SELECT COUNT(*) FROM companies
                WHERE privacy_contact IS NOT NULL AND privacy_contact != ''
            """)
            with_contacts = cursor.fetchone()[0]

            # Total requests
            cursor.execute("SELECT COUNT(*) FROM requests")
            total_requests = cursor.fetchone()[0]

            # Requests by status
            cursor.execute("""
                SELECT status, COUNT(*)
                FROM requests
                GROUP BY status
            """)
            status_counts = dict(cursor.fetchall())

            return {
                'total_companies': total_companies,
                'with_contacts': with_contacts,
                'without_contacts': total_companies - with_contacts,
                'total_requests': total_requests,
                'requests_sent': status_counts.get('SENT', 0),
                'requests_completed': status_counts.get('COMPLETED', 0),
                'success_rate': (status_counts.get('COMPLETED', 0) / total_requests * 100)
                                if total_requests > 0 else 0
            }

        except Exception as e:
            logger.exception("Error getting company statistics.")
            return {}

        finally:
            if conn:
                cursor.close()
                conn.close()

    def get_companies_with_contacts_ready_for_request(self, account_id):
        """
        Get companies that have privacy email contacts and haven't had a deletion request sent yet.

        Args:
            account_id (int): Account ID to check for existing requests

        Returns:
            list: List of company dictionaries ready for deletion requests
        """
        conn = None
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT DISTINCT c.id, c.domain, c.company_name, c.privacy_contact, c.contact_type
                FROM companies c
                WHERE c.privacy_contact IS NOT NULL
                  AND c.privacy_contact != ''
                  AND c.contact_type = 'email'
                  AND NOT EXISTS (
                      SELECT 1 FROM requests r
                      WHERE r.company_id = c.id
                        AND r.account_id = %s
                  )
                ORDER BY c.company_name
            ''', (account_id,))

            companies = []
            for row in cursor.fetchall():
                companies.append({
                    'id': row[0],
                    'domain': row[1],
                    'company_name': row[2],
                    'privacy_contact': row[3],
                    'contact_type': row[4]
                })

            return companies

        except Exception:
            logger.exception("Error retrieving companies ready for deletion requests.")
            return []
        finally:
            if conn:
                cursor.close()
                conn.close()

    def _guess_company_name(self, domain):
        """
        Guess company name from domain using shared utility.

        Args:
            domain (str): Domain name

        Returns:
            str: Guessed company name
        """
        return format_company_name(domain)

# Test/Demo function
def test_company_manager():
    """Test the company manager functionality."""
    print("\n" + "="*60)
    print("COMPANY MANAGER TEST")
    print("="*60)

    manager = CompanyManager()

    # Test adding companies
    print("\n1. Adding test companies...")
    test_companies = [
        'spotify.com',
        'github.com',
        'netflix.com'
    ]

    manager.bulk_add_companies(test_companies)

    # Test updating contact
    print("\n2. Updating privacy contact...")
    manager.update_privacy_contact(
        'spotify.com',
        'privacy@spotify.com',
        'email'
    )

    # Test getting companies without contacts
    print("\n3. Companies without contacts:")
    missing = manager.get_companies_without_contacts()
    for company in missing:
        print(f"   • {company['company_name']} ({company['domain']})")

    # Test statistics
    print("\n4. Statistics:")
    stats = manager.get_statistics()
    print(f"   Total companies: {stats['total_companies']}")
    print(f"   With contacts: {stats['with_contacts']}")
    print(f"   Without contacts: {stats['without_contacts']}")

    print("\n" + "="*60)
    print("Test completed!")
    print("="*60)


if __name__ == "__main__":
    test_company_manager()
