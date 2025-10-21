"""
Unit tests for utility functions.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from utils import (
    Validator,
    EmailExtractor,
    CompanyNameGuesser,
    is_valid_email,
    is_valid_url,
    clean_domain,
    format_company_name
)


def test_email_validation():
    """Test email validation."""
    assert is_valid_email("privacy@example.com") == True
    assert is_valid_email("test@domain.co.uk") == True
    assert is_valid_email("invalid.email") == False
    assert is_valid_email("@nodomain.com") == False
    assert is_valid_email("") == False
    print("✓ Email validation tests passed")


def test_url_validation():
    """Test URL validation."""
    assert is_valid_url("https://example.com") == True
    assert is_valid_url("http://test.org/path") == True
    assert is_valid_url("not-a-url") == False
    assert is_valid_url("") == False
    print("✓ URL validation tests passed")


def test_domain_cleaning():
    """Test domain sanitization."""
    assert clean_domain("https://www.example.com/path") == "example.com"
    assert clean_domain("WWW.EXAMPLE.COM") == "example.com"
    assert clean_domain("example.com") == "example.com"
    assert clean_domain("not a domain") == None
    print("✓ Domain cleaning tests passed")


def test_company_name_guessing():
    """Test company name extraction from domains."""
    assert format_company_name("spotify.com") == "Spotify"
    assert format_company_name("github.com") == "Github"
    assert format_company_name("mail.google.com") == "Google"
    print("✓ Company name guessing tests passed")


def test_email_extraction():
    """Test email extraction from text."""
    sample_text = """
    Contact us at privacy@example.com or dpo@example.org.
    For general inquiries: info@example.com
    """

    privacy_emails = EmailExtractor.extract_emails_from_text(sample_text, privacy_only=True)
    assert "privacy@example.com" in [e.lower() for e in privacy_emails]
    assert "dpo@example.org" in [e.lower() for e in privacy_emails]

    all_emails = EmailExtractor.extract_emails_from_text(sample_text, privacy_only=False)
    assert len(all_emails) == 3

    print("✓ Email extraction tests passed")


def run_all_tests():
    """Run all utility tests."""
    print("\n" + "="*60)
    print("RUNNING UTILITY TESTS")
    print("="*60 + "\n")

    test_email_validation()
    test_url_validation()
    test_domain_cleaning()
    test_company_name_guessing()
    test_email_extraction()

    print("\n" + "="*60)
    print("✓ ALL TESTS PASSED")
    print("="*60 + "\n")


if __name__ == "__main__":
    run_all_tests()
