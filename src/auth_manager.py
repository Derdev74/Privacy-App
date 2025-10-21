"""
Secure token management using OS keychain.
OAuth tokens are stored in your operating system's secure keychain,
not in the database or plain text files.
"""

import keyring
import json


class TokenManager:
    """Manages secure storage of OAuth tokens in OS keychain."""

    def __init__(self):
        self.service_name = "PrivacyDataDeletionTool"

    def save_token(self, account_email, token_data):
        """
        Securely store OAuth tokens in OS keychain.

        Args:
            account_email (str): Email address (used as the key)
            token_data (dict): Token data to store (will be JSON-encoded)
        """
        try:
            keyring.set_password(
                self.service_name,
                account_email,
                json.dumps(token_data)
            )
            print(f"✓ Token saved securely for {account_email}")
        except Exception as e:
            print(f"✗ Error saving token: {e}")
            raise

    def get_token(self, account_email):
        """
        Retrieve OAuth tokens from OS keychain.

        Args:
            account_email (str): Email address (key)

        Returns:
            dict: Token data or None if not found
        """
        try:
            token_json = keyring.get_password(self.service_name, account_email)
            if token_json:
                return json.loads(token_json)
            return None
        except Exception as e:
            print(f"✗ Error retrieving token: {e}")
            return None

    def delete_token(self, account_email):
        """
        Remove tokens from keychain.

        Args:
            account_email (str): Email address (key)
        """
        try:
            keyring.delete_password(self.service_name, account_email)
            print(f"✓ Token deleted for {account_email}")
        except keyring.errors.PasswordDeleteError:
            print(f"⚠ No token found for {account_email}")
        except Exception as e:
            print(f"✗ Error deleting token: {e}")
            raise

    def list_stored_accounts(self):
        """
        List all accounts with stored tokens.
        Note: This is a simplified version. OS keychains don't always
        provide an easy way to list all keys.

        Returns:
            list: List of account emails (may be empty on some systems)
        """
        # This is system-dependent and may not work on all platforms
        # For now, return empty list - accounts will be tracked in database
        return []


if __name__ == "__main__":
    # Test the token manager
    print("\n" + "="*50)
    print("TOKEN MANAGER TEST")
    print("="*50)

    manager = TokenManager()

    # Test saving a token
    test_email = "test@example.com"
    test_token = {
        "access_token": "test_access_token",
        "refresh_token": "test_refresh_token",
        "token_type": "Bearer",
        "expiry": "2024-12-31T23:59:59Z"
    }

    print(f"\n1. Saving test token for {test_email}...")
    manager.save_token(test_email, test_token)

    print(f"\n2. Retrieving token for {test_email}...")
    retrieved = manager.get_token(test_email)
    if retrieved:
        print(f"   ✓ Token retrieved successfully")
        print(f"   Token type: {retrieved.get('token_type')}")
    else:
        print(f"   ✗ Failed to retrieve token")

    print(f"\n3. Deleting token for {test_email}...")
    manager.delete_token(test_email)

    print(f"\n4. Verifying deletion...")
    retrieved_after = manager.get_token(test_email)
    if retrieved_after is None:
        print(f"   ✓ Token successfully deleted")
    else:
        print(f"   ✗ Token still exists")

    print("\n" + "="*50)
    print("Test completed!")
    print("="*50 + "\n")
