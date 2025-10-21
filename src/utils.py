"""
Shared utility functions for the Privacy Data Deletion Tool.
Eliminates code repetition across modules.
"""

import re
from contextlib import contextmanager
from database import DatabaseManager
from logger import logger


class DatabaseConnection:
    """
    Context manager for database connections.
    Automatically handles commit/rollback and cleanup.
    """

    def __init__(self):
        self.db_manager = DatabaseManager()
        self.conn = None
        self.cursor = None

    def __enter__(self):
        """Open database connection."""
        self.conn = self.db_manager.get_connection()
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close connection and handle errors."""
        try:
            if exc_type is None:
                # No exception, commit
                self.conn.commit()
            else:
                # Exception occurred, rollback
                self.conn.rollback()
                logger.error(f"Database transaction failed: {exc_val}")
        finally:
            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.close()

        # Don't suppress exceptions
        return False


@contextmanager
def db_transaction():
    """
    Simple context manager for database transactions.

    Usage:
        with db_transaction() as cursor:
            cursor.execute("SELECT * FROM companies")
            results = cursor.fetchall()
    """
    db_manager = DatabaseManager()
    conn = None
    cursor = None

    try:
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        yield cursor
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        logger.exception("Database transaction error")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


class Validator:
    """
    Validation utilities for common data types.
    """

    @staticmethod
    def validate_email(email):
        """
        Validate email address format.

        Args:
            email (str): Email address to validate

        Returns:
            bool: True if valid email format
        """
        if not email:
            return False

        # RFC 5322 compliant pattern (simplified)
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def validate_url(url):
        """
        Validate URL format.

        Args:
            url (str): URL to validate

        Returns:
            bool: True if valid URL format
        """
        if not url:
            return False

        # Basic HTTP/HTTPS URL validation
        pattern = r'^https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
        return re.match(pattern, url) is not None

    @staticmethod
    def validate_domain(domain):
        """
        Validate domain name format.

        Args:
            domain (str): Domain to validate

        Returns:
            bool: True if valid domain format
        """
        if not domain:
            return False

        # Domain pattern: letters, numbers, dots, hyphens
        pattern = r'^[a-zA-Z0-9][a-zA-Z0-9-_.]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, domain) is not None

    @staticmethod
    def sanitize_domain(domain):
        """
        Clean and normalize a domain name.

        Args:
            domain (str): Domain to sanitize

        Returns:
            str: Cleaned domain name
        """
        if not domain:
            return None

        # Convert to lowercase first
        domain = domain.lower().strip()

        # Remove protocol
        domain = re.sub(r'^https?://', '', domain)

        # Remove www prefix
        domain = re.sub(r'^www\.', '', domain)

        # Remove trailing slash and paths
        domain = domain.split('/')[0]

        return domain if Validator.validate_domain(domain) else None


class EmailExtractor:
    """
    Email extraction utilities.
    """

    # Common privacy-related email patterns
    # Use word boundaries and more specific TLD matching to avoid trailing punctuation
    PRIVACY_PATTERNS = [
        r'\bprivacy@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b',
        r'\bdpo@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b',
        r'\bdata-?protection@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b',
        r'\bgdpr@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b',
        r'\blegal@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b',
        r'\bcompliance@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b',
        r'\bdataprotection@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'
    ]

    @staticmethod
    def extract_emails_from_text(text, privacy_only=False):
        """
        Extract email addresses from text.

        Args:
            text (str): Text to search
            privacy_only (bool): Only return privacy-related emails

        Returns:
            list: List of email addresses found
        """
        if privacy_only:
            # Use specific privacy patterns
            emails = []
            for pattern in EmailExtractor.PRIVACY_PATTERNS:
                matches = re.findall(pattern, text, re.IGNORECASE)
                emails.extend(matches)
            return list(set(emails))  # Remove duplicates
        else:
            # Generic email pattern
            pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(pattern, text)
            return list(set(emails))

    @staticmethod
    def extract_domain_from_email(email):
        """
        Extract domain from email address.

        Args:
            email (str): Email address

        Returns:
            str: Domain name or None
        """
        if not email or '@' not in email:
            return None

        try:
            domain = email.split('@')[1].lower()
            return domain if Validator.validate_domain(domain) else None
        except IndexError:
            return None


class CompanyNameGuesser:
    """
    Utilities for guessing company names from domains.
    """

    COMMON_PREFIXES = ['www', 'mail', 'email', 'newsletter', 'notifications', 'no-reply', 'noreply']

    @staticmethod
    def guess_from_domain(domain):
        """
        Guess company name from domain.

        Examples:
            'spotify.com' -> 'Spotify'
            'github.com' -> 'Github'
            'mail.google.com' -> 'Google'

        Args:
            domain (str): Domain name

        Returns:
            str: Guessed company name
        """
        if not domain:
            return 'Unknown Company'

        # Remove TLD
        parts = domain.split('.')

        # Remove common prefixes
        for i, part in enumerate(parts):
            if part.lower() not in CompanyNameGuesser.COMMON_PREFIXES:
                name = part
                break
        else:
            # All parts are prefixes, use first one
            name = parts[0] if parts else 'Unknown'

        # Capitalize
        return name.capitalize()


class TextCleaner:
    """
    Text cleaning and normalization utilities.
    """

    @staticmethod
    def clean_whitespace(text):
        """Remove extra whitespace from text."""
        if not text:
            return ""
        return ' '.join(text.split())

    @staticmethod
    def extract_text_around(full_text, search_term, context_chars=200):
        """
        Extract text surrounding a search term.

        Args:
            full_text (str): Full text to search
            search_term (str): Term to find
            context_chars (int): Characters before/after to include

        Returns:
            str: Context text
        """
        if not full_text or not search_term:
            return ""

        pos = full_text.lower().find(search_term.lower())
        if pos == -1:
            return ""

        start = max(0, pos - context_chars)
        end = min(len(full_text), pos + len(search_term) + context_chars)

        return full_text[start:end]


class StatusHelper:
    """
    Request status management utilities.
    """

    VALID_STATUSES = ['PENDING', 'SENT', 'REPLIED', 'COMPLETED', 'FAILED']

    @staticmethod
    def is_valid_status(status):
        """Check if a status is valid."""
        return status and status.upper() in StatusHelper.VALID_STATUSES

    @staticmethod
    def normalize_status(status):
        """Normalize status to uppercase."""
        return status.upper() if status else 'PENDING'


# Convenience functions for common operations

def format_company_name(domain):
    """Quick access to company name guesser."""
    return CompanyNameGuesser.guess_from_domain(domain)


def is_valid_email(email):
    """Quick email validation."""
    return Validator.validate_email(email)


def is_valid_url(url):
    """Quick URL validation."""
    return Validator.validate_url(url)


def clean_domain(domain):
    """Quick domain sanitization."""
    return Validator.sanitize_domain(domain)


# Export commonly used items
__all__ = [
    'DatabaseConnection',
    'db_transaction',
    'Validator',
    'EmailExtractor',
    'CompanyNameGuesser',
    'TextCleaner',
    'StatusHelper',
    'format_company_name',
    'is_valid_email',
    'is_valid_url',
    'clean_domain'
]


if __name__ == "__main__":
    # Test utilities
    print("="*60)
    print("UTILITIES TEST")
    print("="*60)

    # Test email validation
    print("\n1. Email Validation:")
    test_emails = [
        "privacy@example.com",
        "invalid.email",
        "test@domain.co.uk",
        "@nodomain.com"
    ]
    for email in test_emails:
        print(f"  {email}: {'✓' if is_valid_email(email) else '✗'}")

    # Test domain sanitization
    print("\n2. Domain Sanitization:")
    test_domains = [
        "https://www.example.com/path",
        "WWW.EXAMPLE.COM",
        "example.com",
        "not a domain"
    ]
    for domain in test_domains:
        cleaned = clean_domain(domain)
        print(f"  {domain} -> {cleaned}")

    # Test company name guessing
    print("\n3. Company Name Guessing:")
    test_company_domains = [
        "spotify.com",
        "mail.google.com",
        "notifications.github.com",
        "netflix.co.uk"
    ]
    for domain in test_company_domains:
        name = format_company_name(domain)
        print(f"  {domain} -> {name}")

    # Test email extraction
    print("\n4. Email Extraction:")
    sample_text = """
    Contact us at privacy@example.com or dpo@example.org.
    For general inquiries: info@example.com
    """
    privacy_emails = EmailExtractor.extract_emails_from_text(sample_text, privacy_only=True)
    all_emails = EmailExtractor.extract_emails_from_text(sample_text, privacy_only=False)
    print(f"  Privacy emails: {privacy_emails}")
    print(f"  All emails: {all_emails}")

    print("\n" + "="*60)
    print("Utilities test complete!")
    print("="*60)
