"""
Privacy Contact Finder - Automated web scraping for privacy contacts.
Attempts to find privacy/GDPR contact information from company websites.
"""

import requests
from bs4 import BeautifulSoup
import re
from logger import logger
from urllib.parse import urljoin, urlparse
import time


class ContactFinder:
    """
    Automatically searches for privacy contact information.
    Success rate: ~40-70% depending on company.
    """

    def __init__(self, timeout=10):
        """
        Initialize contact finder.

        Args:
            timeout (int): Request timeout in seconds
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        # Common privacy page paths
        self.common_paths = [
            '/privacy',
            '/privacy-policy',
            '/privacy-center',
            '/legal/privacy',
            '/privacy-notice',
            '/gdpr',
            '/data-protection',
            '/legal',
            '/terms',
            '/contact',
            '/help/privacy'
        ]

        # Email patterns to look for
        self.email_patterns = [
            r'privacy@[a-zA-Z0-9.-]+',
            r'dpo@[a-zA-Z0-9.-]+',
            r'data-?protection@[a-zA-Z0-9.-]+',
            r'gdpr@[a-zA-Z0-9.-]+',
            r'legal@[a-zA-Z0-9.-]+',
            r'compliance@[a-zA-Z0-9.-]+',
            r'dataprotection@[a-zA-Z0-9.-]+'
        ]

    def find_contact(self, domain, verbose=True):
        """
        Attempt to find privacy contact for a domain.

        Args:
            domain (str): Company domain (e.g., 'spotify.com')
            verbose (bool): Print progress messages

        Returns:
            dict: Contact information or None
                {
                    'type': 'email' or 'webform',
                    'contact': email address or URL,
                    'confidence': 'high', 'medium', or 'low',
                    'source': where it was found
                }
        """
        if verbose:
            logger.info(f"\n🔍 Searching for privacy contact: {domain}")

        # Try HTTPS first, then HTTP
        for protocol in ['https', 'http']:
            base_url = f"{protocol}://{domain}"

            # Check if domain is reachable
            if not self._is_reachable(base_url, verbose):
                continue

            # Try common privacy pages
            for path in self.common_paths:
                url = urljoin(base_url, path)

                try:
                    if verbose:
                        print(f"  • Checking: {path}")
                    
                    response = self.session.get(url, timeout=self.timeout, allow_redirects=True)

                    if response.status_code == 200:
                        # Found a valid page, search for contact info
                        contact = self._extract_contact(response.text, domain, url)

                        if contact:
                            contact['source'] = url # Store full URL for better context
                            if verbose:
                                logger.info(f"  ✓ Found: {contact['contact']} (confidence: {contact['confidence']}) from {url}")
                            return contact

                except requests.RequestException:
                    logger.debug(f"  Request failed for {url}")
                except Exception as e:
                    if verbose:
                        logger.warning(f"  Error checking {path}: {e}")
                    continue

                # Small delay to be polite
                time.sleep(0.5)

        # No contact found on privacy pages, try common email patterns
        if verbose:
            logger.info("  • Trying common email patterns...")

        common_contact = self._try_common_emails(domain)
        if common_contact:
            if verbose:
                logger.info(f"  ✓ Guessed: {common_contact['contact']} (confidence: {common_contact['confidence']})")
            return common_contact

        if verbose:
            logger.info(f"  ✗ No contact found for {domain}")

        return None

    def _is_reachable(self, url, verbose=False):
        """
        Check if a URL is reachable.

        Args:
            url (str): URL to check
            verbose (bool): Print status

        Returns:
            bool: True if reachable
        """
        try:
            response = self.session.head(url, timeout=5, allow_redirects=True)
            return True
        except requests.RequestException: # type: ignore
            if verbose:
                logger.debug(f"  Domain not reachable: {url}")
            return False

    def _extract_contact(self, html_content, domain, page_url):
        """
        Extract contact information from HTML content.

        Args:
            html_content (str): HTML content
            domain (str): Company domain
            page_url (str): Page URL where content was found

        Returns:
            dict: Contact info or None
        """
        soup = BeautifulSoup(html_content, 'html.parser')

        # Get all text from the page
        text = soup.get_text()

        # Look for email addresses matching privacy patterns
        for pattern in self.email_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)

            if matches:
                # Prefer emails from the same domain
                for match in matches:
                    if domain in match.lower():
                        return {
                            'type': 'email',
                            'contact': match.lower(),
                            'confidence': 'high'
                        }

                # Otherwise use first match
                return {
                    'type': 'email',
                    'contact': matches[0].lower(),
                    'confidence': 'medium'
                }

        # Look for any email addresses (broader search)
        general_email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        all_emails = re.findall(general_email_pattern, text)

        # Filter for privacy-related keywords nearby
        privacy_keywords = ['privacy', 'data protection', 'gdpr', 'dpo', 'personal data']

        for email in all_emails:
            # Check if email is from the same domain
            if domain in email.lower():
                # Check if privacy keywords appear near this email
                email_context = self._get_text_around_email(text, email)
                if any(keyword in email_context.lower() for keyword in privacy_keywords):
                    return {
                        'type': 'email',
                        'contact': email.lower(),
                        'confidence': 'medium'
                    }

        # Look for contact forms
        forms = soup.find_all('form')
        for form in forms:
            form_text = form.get_text().lower()
            if any(keyword in form_text for keyword in privacy_keywords):
                form_action = form.get('action', '')
                if form_action:
                    form_url = urljoin(page_url, form_action)
                    return {
                        'type': 'webform',
                        'contact': form_url,
                        'confidence': 'medium'
                    }

        return None

    def _get_text_around_email(self, text, email, context_chars=200):
        """
        Get text surrounding an email address.

        Args:
            text (str): Full text
            email (str): Email to find
            context_chars (int): Characters before/after

        Returns:
            str: Context text
        """
        email_pos = text.lower().find(email.lower())
        if email_pos == -1:
            return ""

        start = max(0, email_pos - context_chars)
        end = min(len(text), email_pos + len(email) + context_chars)

        return text[start:end]

    def _try_common_emails(self, domain):
        """
        Try common privacy email patterns.

        Args:
            domain (str): Company domain

        Returns:
            dict: Contact info or None
        """
        common_prefixes = [
            'privacy',
            'dpo',
            'data-protection',
            'dataprotection',
            'gdpr',
            'legal',
            'compliance'
        ]

        # Try each prefix
        for prefix in common_prefixes:
            email = f"{prefix}@{domain}"

            # We can't verify if the email exists without sending mail,
            # so we return it with low confidence
            return {
                'type': 'email',
                'contact': email,
                'confidence': 'low',
                'source': 'guessed'
            }

        return None

    def batch_find_contacts(self, domains, max_workers=3, verbose=False):
        """
        Find contacts for multiple domains (with rate limiting).

        Args:
            domains (list): List of domain strings
            max_workers (int): Max concurrent requests
            verbose (bool): Print progress

        Returns:
            dict: Dictionary mapping domain to contact info
        """
        results = {}

        logger.info(f"\n🔍 Batch searching {len(domains)} domains...")
        logger.info(f"   Rate limit: {max_workers} concurrent requests")

        for i, domain in enumerate(domains, 1):
            logger.info(f"\n[{i}/{len(domains)}] {domain}")

            try:
                contact = self.find_contact(domain, verbose=verbose)
                results[domain] = contact

            except Exception as e:
                logger.exception(f"  Error finding contact for {domain}.")
                results[domain] = None

            # Rate limiting
            if i < len(domains):
                time.sleep(1)  # 1 second between requests

        # Print summary
        found = sum(1 for c in results.values() if c is not None)
        logger.info(f"\n✓ Search complete: {found}/{len(domains)} contacts found")

        return results


# Test/Demo function
def test_contact_finder():
    """Test the contact finder with sample domains."""
    print("\n" + "="*60)
    print("CONTACT FINDER TEST")
    print("="*60)

    finder = ContactFinder()

    # Test domains (mix of well-known companies)
    test_domains = [
        'spotify.com',
        'github.com',
        'netflix.com'
    ]

    print(f"\nTesting with {len(test_domains)} domains...")

    results = finder.batch_find_contacts(test_domains, verbose=True)

    # Display results
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)

    for domain, contact in results.items():
        print(f"\n{domain}:")
        if contact:
            print(f"  Type: {contact['type']}")
            print(f"  Contact: {contact['contact']}")
            print(f"  Confidence: {contact['confidence']}")
            print(f"  Source: {contact.get('source', 'N/A')}")
        else:
            print("  ✗ No contact found")

    print("\n" + "="*60)


if __name__ == "__main__":
    test_contact_finder()
