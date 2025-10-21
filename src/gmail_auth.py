"""
Gmail OAuth authentication module.
Handles OAuth 2.0 flow for Gmail API access with secure token storage.
"""

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json
import os
from pathlib import Path

from auth_manager import TokenManager


class GmailAuthenticator:
    """
    Manages Gmail OAuth authentication and API access.

    Scopes:
    - gmail.readonly: Read emails for company discovery
    - gmail.send: Send deletion requests
    """

    # OAuth scopes needed for the application
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.send'
    ]

    def __init__(self, credentials_file='config/google_credentials.json'):
        """
        Initialize the Gmail authenticator.

        Args:
            credentials_file (str): Path to Google OAuth credentials JSON
        """
        self.credentials_file = Path(credentials_file)
        self.token_manager = TokenManager()

        # Verify credentials file exists
        if not self.credentials_file.exists():
            raise FileNotFoundError(
                f"OAuth credentials not found: {credentials_file}\n"
                "Please download credentials from Google Cloud Console."
            )

    def authenticate(self, email_address):
        """
        Authenticate with Gmail API using OAuth 2.0.

        This method:
        1. Checks for existing token in OS keychain
        2. Refreshes token if expired
        3. Starts new OAuth flow if needed (opens browser)
        4. Saves token securely to keychain

        Args:
            email_address (str): Gmail address to authenticate

        Returns:
            Resource: Authenticated Gmail API service object
        """
        print(f"\n🔐 Authenticating Gmail account: {email_address}")

        # Try to get existing token from keychain
        creds = None
        token_data = self.token_manager.get_token(email_address)

        if token_data:
            print("  ✓ Found existing token in keychain")
            try:
                creds = Credentials.from_authorized_user_info(token_data, self.SCOPES)
            except Exception as e:
                print(f"  ⚠ Token data invalid: {e}")
                creds = None

        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                print("  ⟳ Token expired, refreshing...")
                try:
                    creds.refresh(Request())
                    print("  ✓ Token refreshed successfully")
                except Exception as e:
                    print(f"  ✗ Token refresh failed: {e}")
                    print("  ⟳ Starting new OAuth flow...")
                    creds = self._start_oauth_flow()
            else:
                print("  ⟳ No valid token found, starting OAuth flow...")
                creds = self._start_oauth_flow()

            # Save the new/refreshed credentials
            token_data = {
                'token': creds.token,
                'refresh_token': creds.refresh_token,
                'token_uri': creds.token_uri,
                'client_id': creds.client_id,
                'client_secret': creds.client_secret,
                'scopes': creds.scopes
            }
            self.token_manager.save_token(email_address, token_data)
            print("  ✓ Token saved securely to keychain")
        else:
            print("  ✓ Using existing valid token")

        # Build and return Gmail service
        try:
            service = build('gmail', 'v1', credentials=creds)
            print("  ✓ Gmail API service ready")
            return service
        except Exception as e:
            print(f"  ✗ Failed to build Gmail service: {e}")
            raise

    def _start_oauth_flow(self):
        """
        Start the OAuth 2.0 authorization flow.
        Supports both automatic (with browser) and manual (WSL-friendly) flows.

        Returns:
            Credentials: Authorized credentials object
        """
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(self.credentials_file),
                self.SCOPES
            )

            print("\n" + "="*60)
            print("  📱 BROWSER AUTHORIZATION REQUIRED")
            print("="*60)

            # Try automatic flow first (works on systems with browsers)
            try:
                import subprocess
                import platform

                # Check if we're in WSL
                is_wsl = 'microsoft' in platform.uname().release.lower()

                if is_wsl:
                    print("  ⚠ WSL detected - using manual authorization flow")
                    print("="*60)
                    return self._manual_oauth_flow(flow)
                else:
                    print("  A browser window will open for you to:")
                    print("  1. Sign in to your Gmail account")
                    print("  2. Grant permissions to this app")
                    print("  3. You'll be redirected back automatically")
                    print("="*60)
                    print("\n  Opening browser in 3 seconds...")

                    import time
                    time.sleep(3)

                    # Run the OAuth flow (opens browser)
                    creds = flow.run_local_server(
                        port=0,
                        authorization_prompt_message='',
                        success_message='Authorization successful! You can close this window.',
                        open_browser=True
                    )

                    print("\n  ✓ Authorization successful!")
                    return creds

            except Exception as e:
                print(f"\n  ⚠ Automatic flow failed: {e}")
                print("  ⟳ Switching to manual authorization flow...")
                return self._manual_oauth_flow(flow)

        except Exception as e:
            print(f"\n  ✗ OAuth flow failed: {e}")
            raise

    def _manual_oauth_flow(self, flow):
        """
        Manual OAuth flow for WSL/headless environments.
        Uses out-of-band (OOB) flow - user copies authorization code from browser.

        Args:
            flow: OAuth flow object

        Returns:
            Credentials: Authorized credentials object
        """
        print("\n" + "="*60)
        print("  MANUAL AUTHORIZATION (WSL/No Browser)")
        print("="*60)

        # Use out-of-band redirect URI (works without configuration)
        flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'

        # Generate authorization URL
        auth_url, _ = flow.authorization_url(prompt='consent')

        print("\n📋 STEP 1: Copy this URL and open it in your Windows browser:")
        print("\n" + "-"*60)
        print(auth_url)
        print("-"*60)

        print("\n📋 STEP 2: After authorizing, Google will show you an authorization code.")
        print("           The page will say: 'Please copy this code, switch to your application'")
        print("           Copy the AUTHORIZATION CODE (not the full page).")

        print("\n📋 STEP 3: Paste the authorization code below.")
        print("="*60)

        # Get the authorization code from user
        auth_code = input("\nPaste the authorization code here: ").strip()

        if not auth_code:
            raise ValueError("No authorization code provided")

        # Exchange code for credentials
        try:
            print("\n  ⟳ Exchanging authorization code for token...")
            flow.fetch_token(code=auth_code)

            print("  ✓ Authorization successful!")
            return flow.credentials

        except Exception as e:
            print(f"\n  ✗ Failed to exchange code for token: {e}")
            print("\n  Make sure you copied the code exactly as shown (no extra spaces).")
            raise

    def verify_access(self, service, email_address):
        """
        Verify Gmail API access by fetching user profile.

        Args:
            service: Authenticated Gmail service object
            email_address (str): Expected email address

        Returns:
            bool: True if access verified successfully
        """
        try:
            # Get user profile
            profile = service.users().getProfile(userId='me').execute()
            actual_email = profile.get('emailAddress')

            print(f"\n📧 Gmail Account Verified:")
            print(f"  Email: {actual_email}")
            print(f"  Messages Total: {profile.get('messagesTotal', 'N/A')}")
            print(f"  Threads Total: {profile.get('threadsTotal', 'N/A')}")

            # Verify email matches
            if actual_email.lower() != email_address.lower():
                print(f"  ⚠ Warning: Expected {email_address}, got {actual_email}")
                return False

            return True

        except HttpError as e:
            print(f"  ✗ Failed to verify access: {e}")
            return False
        except Exception as e:
            print(f"  ✗ Unexpected error: {e}")
            return False

    def get_gmail_service(self, email_address):
        """
        Get an authenticated Gmail service object for an email address.
        This is a convenience method that wraps authenticate().

        Args:
            email_address (str): Gmail address

        Returns:
            Resource: Authenticated Gmail API service object
        """
        return self.authenticate(email_address)

    def revoke_access(self, email_address):
        """
        Revoke access and delete stored tokens.

        Args:
            email_address (str): Email address to revoke
        """
        try:
            # Delete token from keychain
            self.token_manager.delete_token(email_address)
            print(f"✓ Access revoked for {email_address}")
            print("  Note: You may need to revoke app access in your Google Account settings:")
            print("  https://myaccount.google.com/permissions")
        except Exception as e:
            print(f"✗ Error revoking access: {e}")


# Test/Demo function
def test_authentication():
    """Test the Gmail authentication flow."""
    print("\n" + "="*60)
    print("GMAIL AUTHENTICATION TEST")
    print("="*60)

    authenticator = GmailAuthenticator()

    # Prompt for email
    email = input("\nEnter your Gmail address: ").strip()

    if not email:
        print("✗ No email provided")
        return

    try:
        # Authenticate
        service = authenticator.authenticate(email)

        # Verify access
        if authenticator.verify_access(service, email):
            print("\n" + "="*60)
            print("✓ AUTHENTICATION SUCCESSFUL!")
            print("="*60)
            print("\nYour Gmail account is now connected.")
            print("The app can now:")
            print("  ✓ Read your emails to find companies")
            print("  ✓ Send deletion requests on your behalf")
            print("\nAll data stays local on your machine.")
        else:
            print("\n✗ Authentication verification failed")

    except Exception as e:
        print(f"\n✗ Authentication failed: {e}")
        print("\nTroubleshooting:")
        print("  1. Check that config/google_credentials.json exists")
        print("  2. Ensure Gmail API is enabled in Google Cloud Console")
        print("  3. Verify OAuth consent screen is configured")


if __name__ == "__main__":
    test_authentication()
