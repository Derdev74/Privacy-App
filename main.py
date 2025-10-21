#!/usr/bin/env python3
"""
Main Command-Line Interface (CLI) for the Privacy Data Deletion Tool.
This script orchestrates the various modules to provide a user-friendly
interface for managing data deletion requests.
"""

import sys
from pathlib import Path
import time

# Add src directory to Python path for module imports
# This needs to be before importing other modules from src
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Import all necessary modules
from database import initialize_database, DatabaseManager
from gmail_auth import GmailAuthenticator
from account_manager import AccountManager
from email_scanner import EmailScanner
from company_manager import CompanyManager
from contact_finder import ContactFinder
from manual_contact import ManualContactManager
from request_sender import RequestSender
from logger import setup_logging, logger
from reply_tracker import ReplyTracker


class DataDeletionTool:
    """
    Orchestrates the privacy data deletion process through a CLI.
    """

    def __init__(self):
        """
        Initializes the tool by setting up the database and managers.
        """
        # Setup logging
        setup_logging()

        # Ensure database is initialized (one-time setup)
        initialize_database()

        # Initialize core managers
        self.db_manager = DatabaseManager() # For general DB operations if needed
        self.gmail_authenticator = GmailAuthenticator()
        self.account_manager = AccountManager()
        self.company_manager = CompanyManager()
        self.contact_finder = ContactFinder()
        self.manual_contact_manager = ManualContactManager()
        # RequestSender and ReplyTracker are initialized per-account when needed.

    def main_menu(self):
        """
        Displays the main menu and handles user input for navigation.
        """
        while True:
            print("\n" + "="*60)
            print("🔐 PERSONAL DATA DELETION TOOL")
            print("="*60)
            print("1. Add/Manage Email Account")
            print("2. Scan for Companies (Email Discovery)")
            print("3. Find Privacy Contacts (Auto & Manual)")
            print("4. Send Deletion Requests")
            print("5. Check for Replies")
            print("6. View Dashboard & Statistics")
            print("7. Exit")
            print("="*60)

            choice = input("\nSelect an option (1-7): ").strip()

            if choice == '1':
                self.add_account()
            elif choice == '2':
                self.scan_companies()
            elif choice == '3':
                self.find_contacts()
            elif choice == '4':
                self.send_requests()
            elif choice == '5':
                self.check_replies()
            elif choice == '6':
                self.show_dashboard()
            elif choice == '7':
                print("Goodbye! Your data remains safely local.")
                sys.exit(0)
            else: # Use logger for invalid input, but keep it as info for user
                logger.info("Invalid option. Please choose a number between 1 and 7.")

    def add_account(self):
        """
        Guides the user through adding and authenticating a Gmail account.
        """
        email = input("Enter your Gmail address to add/authenticate: ").strip()
        if not email:
            logger.warning("Email address cannot be empty during account addition.")
            return

        try:
            # Authenticate and get service (this will handle OAuth flow)
            service = self.gmail_authenticator.authenticate(email)
            if service:
                # Add account to our database if not already there
                account_id = self.account_manager.add_account(email, 'gmail')
                logger.info(f"Account '{email}' (ID: {account_id}) added and authenticated successfully!")
            else: # This path might be hit if authentication fails but doesn't raise an exception
                logger.error(f"Failed to authenticate '{email}'. Service object was not returned.")
        except Exception:
            logger.exception(f"Error adding account '{email}'.")

    def scan_companies(self):
        """
        Scans registered email accounts for company domains.
        """
        accounts = self.account_manager.get_all_accounts()
        if not accounts:
            logger.warning("No accounts found to scan. Please add an email account first (Option 1).")
            return

        for account in accounts:
            email_address = account['email_address']
            logger.info(f"\n{'='*60}\nScanning emails for companies in: {email_address}...\n{'='*60}")
            try:
                service = self.gmail_authenticator.authenticate(email_address)
                if service:
                    scanner = EmailScanner(service)
                    discovered_domains = scanner.discover_companies()
                    if discovered_domains:
                        stats = self.company_manager.bulk_add_companies(discovered_domains)
                        logger.info(f"Discovered {stats['total']} domains for {email_address}. Added {stats['added']} new companies.")
                    else:
                        logger.info(f"No new companies discovered for {email_address}.")
                else:
                    logger.error(f"Could not get Gmail service for {email_address}. Skipping scan.")
            except Exception:
                logger.exception(f"Error scanning companies for {email_address}.")

    def find_contacts(self):
        """
        Initiates automated and manual privacy contact discovery.
        """
        print("\n" + "="*60)
        print("FINDING PRIVACY CONTACTS")
        logger.info("="*60) # Use logger for this header too

        companies_without_contacts = self.company_manager.get_companies_without_contacts()
        if not companies_without_contacts:
            logger.info("All companies currently have a privacy contact or none are pending discovery.")
            return

        logger.info(f"Found {len(companies_without_contacts)} companies needing contact info.")

        # First, try automated discovery
        logger.info("\nAttempting automated contact discovery...")
        domains_to_auto_find = [c['domain'] for c in companies_without_contacts]
        auto_found_results = self.contact_finder.batch_find_contacts(domains_to_auto_find, verbose=False)

        updated_count = 0
        for domain, contact_info in auto_found_results.items():
            if contact_info:
                self.company_manager.update_privacy_contact(
                    domain,
                    contact_info['contact'],
                    contact_info['type']
                )
                logger.info(f"Auto-found contact for {domain}: {contact_info['contact']}")
                updated_count += 1
        logger.info(f"Completed automated discovery. Updated {updated_count} companies.")

        # Then, offer manual entry for remaining
        remaining_companies = self.company_manager.get_companies_without_contacts()
        if remaining_companies:
            logger.info(f"\n{len(remaining_companies)} companies still need manual contact entry.")
            self.manual_contact_manager.review_and_add_contacts()
        else:
            logger.info("\nAll companies now have a contact after automated discovery!")

    def send_requests(self):
        """
        Sends deletion requests to companies with discovered contacts.
        """
        accounts = self.account_manager.get_all_accounts()
        if not accounts:
            logger.warning("No accounts found to send requests from. Please add an email account first (Option 1).")
            return

        # For simplicity, let's assume we send from the first authenticated account.
        # In a future enhancement, the user could choose which account to send from.
        user_account = accounts[0]
        user_email = user_account['email_address']
        account_id = user_account['id'] # Ensure account_id is passed to get_companies_with_contacts_ready_for_request

        logger.info(f"\n{'='*60}\nSENDING DELETION REQUESTS from: {user_email}\n{'='*60}")

        try:
            request_sender = RequestSender(user_email)
        except ConnectionError as e:
            logger.error(f"Error initializing request sender for {user_email}: {e}")
            return
        except Exception:
            logger.exception(f"An unexpected error occurred while initializing request sender for {user_email}.")

        companies_to_send_to = self.company_manager.get_companies_with_contacts_ready_for_request(account_id)
        if not companies_to_send_to:
            logger.info("No companies found with privacy email contacts that haven't had a request sent yet.")
            logger.info("  - Ensure you've scanned for companies (Option 2).")
            logger.info("  - Ensure you've found contacts (Option 3).")
            return

        logger.info(f"Found {len(companies_to_send_to)} companies to send requests to.")

        for company in companies_to_send_to:
            domain = company['domain']
            company_id = company['id']
            company_name = company['company_name'] if company['company_name'] else domain.split('.')[0].capitalize()

            # For now, default to generic template. Future: allow user to choose or auto-detect.
            # Also, user_name is optional.
            logger.info(f"Sending request to {company_name} ({domain})...")
            # Pass account_id to send_deletion_request
            request_sender.send_deletion_request(company_id, account_id, domain, template_type='generic', user_name="Your Name")
            # Small delay to avoid hitting rate limits too hard and to be polite
            time.sleep(1)

        logger.info("\nDeletion request sending session completed.")

    def check_replies(self):
        """
        Checks for replies to sent deletion requests for all registered accounts.
        """
        accounts = self.account_manager.get_all_accounts()
        if not accounts:
            logger.warning("No accounts found to check replies for. Please add an email account first (Option 1).")
            return

        for account in accounts:
            email_address = account['email_address']
            try:
                reply_tracker = ReplyTracker(email_address)
                # Pass account_id to check_for_replies
                reply_tracker.check_for_replies(account['id'])
            except ConnectionError as e:
                logger.error(f"Error initializing reply tracker for {email_address}: {e}")
            except Exception:
                logger.exception(f"Error checking replies for {email_address}.")

    def show_dashboard(self):
        """
        Displays statistics and a dashboard of the tool's progress.
        """
        print("\n" + "="*60)
        print("DASHBOARD & STATISTICS")
        logger.info("="*60) # Use logger for this header too

        accounts = self.account_manager.get_all_accounts()
        if not accounts:
            logger.warning("No accounts found. Add an account first to see statistics.")
            return
        
        for account in accounts:
            email_address = account['email_address']
            print(f"\n--- Statistics for {email_address} ---")
            stats = self.account_manager.get_account_statistics(email_address)
            print(f"  Total Companies Discovered: {stats['total_companies']}")
            print(f"  Requests Sent:              {stats['requests_sent']}")
            print(f"  Requests Replied:           {stats['requests_replied']}")
            print(f"  Requests Completed:         {stats['requests_completed']}")
            print(f"  Requests Failed:            {stats['requests_failed']}")
            print(f"  Pending Requests:           {stats['requests_pending']}")
            print(f"  Completion Rate:            {stats['completion_rate']:.2f}%")
        logger.info("="*60) # Use logger for this footer too


if __name__ == "__main__":
    app = DataDeletionTool()
    app.main_menu()