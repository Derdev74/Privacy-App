"""
Integration tests for database operations.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from database import DatabaseManager
from account_manager import AccountManager
from company_manager import CompanyManager


def test_database_connection():
    """Test database connection."""
    db_manager = DatabaseManager()
    conn = db_manager.get_connection()
    assert conn is not None
    conn.close()
    print("✓ Database connection test passed")


def test_account_operations():
    """Test account CRUD operations."""
    account_manager = AccountManager()

    # Add test account
    test_email = "test@example.com"
    account_id = account_manager.add_account(test_email, "gmail")
    assert account_id is not None

    # Get account
    account = account_manager.get_account(test_email)
    assert account is not None
    assert account['email_address'] == test_email

    # Remove account
    removed = account_manager.remove_account(test_email)
    assert removed == True

    print("✓ Account operations test passed")


def test_company_operations():
    """Test company CRUD operations."""
    company_manager = CompanyManager()

    # Add test company
    test_domain = "test-example.com"
    company_id = company_manager.add_company(test_domain, "Test Company")
    assert company_id is not None

    # Get company
    company = company_manager.get_company_by_domain(test_domain)
    assert company is not None
    assert company['domain'] == test_domain

    # Update privacy contact
    updated = company_manager.update_privacy_contact(
        test_domain,
        "privacy@test-example.com",
        "email"
    )
    assert updated == True

    # Verify update
    company = company_manager.get_company_by_domain(test_domain)
    assert company['privacy_contact'] == "privacy@test-example.com"

    print("✓ Company operations test passed")


def run_all_tests():
    """Run all database tests."""
    print("\n" + "="*60)
    print("RUNNING DATABASE TESTS")
    print("="*60 + "\n")

    print("⚠️  Note: These tests require a running PostgreSQL database")
    print("    and proper configuration in .env file\n")

    try:
        test_database_connection()
        test_account_operations()
        test_company_operations()

        print("\n" + "="*60)
        print("✓ ALL DATABASE TESTS PASSED")
        print("="*60 + "\n")
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        print("="*60 + "\n")


if __name__ == "__main__":
    run_all_tests()
