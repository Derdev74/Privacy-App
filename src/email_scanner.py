"""
Email Scanner for discovering companies from Gmail.
Scans emails for signup/welcome messages to identify services you've used.
"""

from googleapiclient.errors import HttpError
from logger import logger
import re
from datetime import datetime


class EmailScanner:
    """
    Scans Gmail for company signup/welcome emails.
    Privacy-preserving: Only fetches email headers, not content.
    """

    def __init__(self, gmail_service):
        """
        Initialize email scanner.

        Args:
            gmail_service: Authenticated Gmail API service object
        """
        self.service = gmail_service

    def discover_companies(self, max_results=500, start_year=2015):
        """
        Scan emails for service registrations and extract company domains.

        Args:
            max_results (int): Maximum number of companies to discover
            start_year (int): Start scanning from this year

        Returns:
            list: List of unique company domains
        """
        logger.info(f"\n🔍 Scanning Gmail for company signups...")
        logger.info(f"   Max results: {max_results}")
        logger.info(f"   Start year: {start_year}")

        # Optimized search query for signup/welcome emails
        query = f'''
            from:(-me)
            (
                "welcome to" OR
                "verify your email" OR
                "account created" OR
                "subscription confirmed" OR
                "registration successful" OR
                "thank you for signing up" OR
                "activate your account"
            )
            after:{start_year}/1/1
        '''

        companies = set()
        page_token = None
        messages_scanned = 0
        
        logger.info("\n   Processing emails...")

        try:
            while len(companies) < max_results:
                # Fetch message IDs matching the query (max 100 per request)
                results = self.service.users().messages().list(
                    userId='me',
                    q=query,
                    pageToken=page_token,
                    maxResults=min(100, max_results - len(companies))
                ).execute()

                messages = results.get('messages', [])
                
                if not messages:
                    logger.info(f"\n   ✓ No more messages found")
                    break

                # Fetch headers for each message (batch processing)
                for msg in messages:
                    try:
                        # Fetch only metadata (headers), not full message body
                        msg_data = self.service.users().messages().get(
                            userId='me',
                            id=msg['id'],
                            format='metadata',
                            metadataHeaders=['From', 'Subject']
                        ).execute()

                        messages_scanned += 1

                        # Extract domain from sender
                        headers = msg_data.get('payload', {}).get('headers', [])
                        sender = self._get_header_value(headers, 'From')
                        subject = self._get_header_value(headers, 'Subject')

                        if sender:
                            domain = self.extract_domain(sender)
                            if domain and self._is_valid_domain(domain):
                                if domain not in companies:
                                    companies.add(domain)
                                    print(f"   [{len(companies)}] Found: {domain}")

                                    if len(companies) >= max_results:
                                        break

                    except HttpError as e:
                        print(f"   ⚠ Error fetching message {msg['id']}: {e}")
                        continue

                # Get next page
                page_token = results.get('nextPageToken')
                if not page_token:
                    break

                print(f"   ... scanned {messages_scanned} emails, found {len(companies)} companies")

        except HttpError as e:
            print(f"\n   ✗ Gmail API error: {e}")
            raise
        except Exception as e:
            print(f"\n   ✗ Unexpected error: {e}")
            raise

        print(f"\n✓ Scan complete!")
        print(f"   Total emails scanned: {messages_scanned}")
        print(f"   Unique companies found: {len(companies)}")

        return sorted(list(companies))

    def _get_header_value(self, headers, name):
        """
        Extract header value by name.

        Args:
            headers (list): List of header dictionaries
            name (str): Header name to find

        Returns:
            str: Header value or None
        """
        for header in headers:
            if header.get('name', '').lower() == name.lower():
                return header.get('value', '')
        return None

    def extract_domain(self, sender_string):
        """
        Extract domain from email sender string.

        Examples:
            "Spotify <no-reply@spotify.com>" -> "spotify.com"
            "notifications@github.com" -> "github.com"

        Args:
            sender_string (str): Email sender field

        Returns:
            str: Domain or None if not found
        """
        # Pattern to match email addresses
        match = re.search(r'@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', sender_string)

        if match:
            domain = match.group(1).lower()

            # Clean up common prefixes
            domain = re.sub(r'^(mail|email|noreply|no-reply|notifications?|newsletter)\.', '', domain)

            # Remove common subdomains
            domain = re.sub(r'^(www|web|m|mobile)\.', '', domain)

            return domain

        return None

    def _is_valid_domain(self, domain):
        """
        Check if domain is valid and not a common spam/system domain.

        Args:
            domain (str): Domain to validate

        Returns:
            bool: True if valid, False otherwise
        """
        # Filter out common system/spam domains
        invalid_domains = {
            'gmail.com', 'googlemail.com', 'outlook.com', 'hotmail.com',
            'yahoo.com', 'icloud.com', 'aol.com', 'live.com', 'msn.com',
            'me.com', 'mac.com', 'email.com', 'protonmail.com',
            'localhost', 'example.com', 'test.com'
        }

        if domain in invalid_domains:
            return False

        # Must have at least one dot
        if '.' not in domain:
            return False

        # Basic domain validation
        if not re.match(r'^[a-z0-9.-]+\.[a-z]{2,}$', domain):
            return False

        return True

    def get_sample_emails(self, domain, max_samples=5):
        """
        Get sample email subjects from a specific domain.
        Useful for verifying discovered companies.

        Args:
            domain (str): Domain to search for
            max_samples (int): Number of sample emails to retrieve

        Returns:
            list: List of email subjects
        """
        query = f'from:@{domain}'
        samples = []

        try:
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_samples
            ).execute()

            messages = results.get('messages', [])

            for msg in messages:
                msg_data = self.service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='metadata',
                    metadataHeaders=['Subject', 'Date']
                ).execute()

                headers = msg_data.get('payload', {}).get('headers', [])
                subject = self._get_header_value(headers, 'Subject')
                date = self._get_header_value(headers, 'Date')

                if subject:
                    samples.append({
                        'subject': subject,
                        'date': date
                    })

            return samples

        except HttpError as e:
            logger.error(f"Error getting sample emails for {domain}: {e}")
            return []


# Test/Demo function
def test_email_scanner():
    """Test the email scanner (requires authentication)."""
    print("\n" + "="*60)
    print("EMAIL SCANNER TEST")
    print("="*60)
    print("\nNote: This test requires Gmail authentication.")
    print("You'll be prompted to authorize the app if needed.")

    from gmail_auth import GmailAuthenticator

    # Prompt for email
    email = input("\nEnter your Gmail address: ").strip()

    if not email:
        print("✗ No email provided")
        return

    try:
        # Authenticate
        print("\nAuthenticating...")
        authenticator = GmailAuthenticator()
        service = authenticator.authenticate(email)

        # Create scanner
        scanner = EmailScanner(service)

        # Scan for companies (limited for testing)
        print("\n" + "="*60)
        print("Starting discovery (limited to 50 companies for testing)...")
        print("="*60)

        companies = scanner.discover_companies(max_results=50, start_year=2020)

        # Display results
        print("\n" + "="*60)
        print("DISCOVERED COMPANIES")
        print("="*60)

        for i, domain in enumerate(companies, 1):
            print(f"{i:3}. {domain}")

        print("\n" + "="*60)
        print(f"Total: {len(companies)} companies discovered")
        print("="*60)

        # Test getting sample emails from first company
        if companies:
            print(f"\nGetting sample emails from: {companies[0]}")
            samples = scanner.get_sample_emails(companies[0], max_samples=3)

            for sample in samples:
                print(f"  • {sample['subject']}")
                print(f"    Date: {sample['date']}")

    except Exception as e:
        print(f"\n✗ Test failed: {e}")


if __name__ == "__main__":
    test_email_scanner()
