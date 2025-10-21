"""
Manual Contact Manager - Interactive CLI for entering privacy contacts.
This module allows users to manually input privacy contact information
for companies where automated discovery failed or was insufficient.
"""

import webbrowser
from urllib.parse import quote_plus
from database import DatabaseManager
from logger import logger
from company_manager import CompanyManager
from utils import is_valid_email, is_valid_url


class ManualContactManager:
    """
    Manages the manual entry and update of company privacy contacts.
    Provides an interactive CLI to review companies without contacts
    and allows the user to input contact details.
    """

    def __init__(self):
        """
        Initializes the ManualContactManager with database and company managers.
        """
        self.db_manager = DatabaseManager()
        self.company_manager = CompanyManager()

    def review_and_add_contacts(self, limit=None):
        """
        Starts an interactive session to review companies without privacy contacts
        and allows the user to manually add them.

        Args:
            limit (int, optional): Maximum number of companies to review. Defaults to None (all).
        """
        print("\n" + "="*60)
        logger.info("MANUAL PRIVACY CONTACT ENTRY")
        print("="*60)
        logger.info("Reviewing companies that currently lack a privacy contact.")
        logger.info("You can search for contacts and enter them manually.")
        logger.info("Type 'skip' to move to the next company, 'exit' to quit.")
        print("="*60)

        companies_to_review = self.company_manager.get_companies_without_contacts()

        if not companies_to_review:
            logger.info("\n🎉 All companies currently have a privacy contact or none are pending review.")
            return

        logger.info(f"\nFound {len(companies_to_review)} companies needing contact info.")

        for i, company in enumerate(companies_to_review):
            if limit and i >= limit:
                print(f"\nLimit of {limit} companies reached. Exiting review.")
                break

            domain = company['domain']
            print(f"\n--- Company {i+1}/{len(companies_to_review)}: {domain} ---")
            print("Options: [e]mail, [w]ebform, [s]kip, [g]oogle, [q]uit")

            while True:
                choice = input("Enter choice: ").lower().strip()

                if choice == 'e':
                    contact_type = 'email'
                    contact_value = input(f"Enter email for {domain}: ").strip()
                    if is_valid_email(contact_value):
                        self.company_manager.update_privacy_contact(domain, contact_value, contact_type) # type: ignore
                        logger.info(f"Email '{contact_value}' saved for {domain}.")
                        break
                    else:
                        logger.warning("Invalid email format. Please try again.")
                elif choice == 'w':
                    contact_type = 'webform'
                    contact_value = input(f"Enter webform URL for {domain}: ").strip()
                    if is_valid_url(contact_value):
                        self.company_manager.update_privacy_contact(domain, contact_value, contact_type) # type: ignore
                        logger.info(f"Webform URL '{contact_value}' saved for {domain}.")
                        break
                    else:
                        logger.warning("Invalid URL format. Please try again.")
                elif choice == 's':
                    logger.info(f"Skipping {domain}.")
                    break
                elif choice == 'g':
                    search_query = quote_plus(f"{domain} privacy contact email GDPR")
                    google_url = f"https://www.google.com/search?q={search_query}"
                    logger.info(f"Opening Google search for '{domain}' in your browser...")
                    webbrowser.open(google_url)
                    # After opening, user can come back and enter details
                    logger.info("Please find the contact and then choose 'e' or 'w' to enter it.")
                elif choice == 'q':
                    logger.info("Exiting manual contact entry.")
                    return
                else:
                    logger.warning("Invalid choice. Please use 'e', 'w', 's', 'g', or 'q'.")

        logger.info("\nManual contact review session completed.")


# Test/Demo function
def test_manual_contact_manager():
    """
    Demonstrates the manual contact manager.
    Note: This requires a running PostgreSQL database and some companies
    without privacy contacts in the 'companies' table.
    """
    print("\n" + "="*60)
    print("MANUAL CONTACT MANAGER TEST")
    print("="*60)

    # Ensure database and company manager are initialized
    db_manager = DatabaseManager()
    db_manager.initialize_schema() # Ensure tables exist
    company_manager = CompanyManager()

    # Add some dummy companies without contacts for testing
    # In a real scenario, these would come from email_scanner/contact_finder
    test_domains = [
        'example.com',
        'testcorp.org',
        'unknownservice.net'
    ]
    print(f"Adding dummy companies for testing: {test_domains}")
    company_manager.bulk_add_companies(test_domains)

    # Verify they are without contacts
    companies_without = company_manager.get_companies_without_contacts()
    print(f"Companies without contacts before test: {[c['domain'] for c in companies_without]}")

    manager = ManualContactManager()
    manager.review_and_add_contacts(limit=2) # Review up to 2 companies for demo

    print("\nVerifying updates...")
    companies_without_after = company_manager.get_companies_without_contacts()
    print(f"Companies without contacts after test: {[c['domain'] for c in companies_without_after]}")

    # Clean up dummy data (optional, for a real test setup)
    # with db_manager.get_connection() as conn:
    #     with conn.cursor() as cur:
    #         cur.execute("DELETE FROM companies WHERE domain IN %s;", (tuple(test_domains),))
    #     conn.commit()
    # print("Cleaned up dummy companies.")

    print("\n" + "="*60)
    print("MANUAL CONTACT MANAGER TEST COMPLETE")
    print("="*60)


if __name__ == "__main__":
    # This block will run when manual_contact.py is executed directly.
    # It's useful for testing the functionality in isolation.
    # Make sure your .env file is configured for PostgreSQL.
    
    # Example usage:
    # 1. Ensure your PostgreSQL is running and .env is configured.
    # 2. Run this script: python src/manual_contact.py
    # 3. It will add some dummy companies and prompt you to enter contacts.
    
    # For a full application, this would be integrated into a main CLI.
    
    # To run this test, you might need to ensure your PYTHONPATH includes the project root
    # or run it from the project root directory.
    # Example:
    # cd "C:\Users\pc\Desktop\Privacy App"
    # python src/manual_contact.py
    
    try:
        test_manual_contact_manager()
    except Exception as e:
        print(f"\nAn error occurred during the manual contact manager test: {e}")
        print("Please ensure your PostgreSQL database is running and configured correctly in your .env file.")
        print("Also, ensure 'src' directory is in your Python path or run from project root.")