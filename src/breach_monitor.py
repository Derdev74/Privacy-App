"""
Breach Monitoring Module
========================

This module provides privacy-preserving breach monitoring using the
Have I Been Pwned (HIBP) API created by security researcher Troy Hunt.

Features:
  - Password breach checking with k-anonymity (privacy-preserving)
  - Email breach monitoring
  - Automatic storage of findings in exposed_data table
  - Risk level assessment

Privacy Architecture:
====================

1. Password Checking (K-Anonymity):
   - Password is hashed locally with SHA-1
   - Only first 5 characters of hash are sent to HIBP
   - HIBP returns ~800 hash suffixes matching that prefix
   - We search locally for our full hash
   - HIBP never sees your actual password or full hash
   - Mathematical privacy: 16^5 = 1,048,576 possible prefixes

2. Email Checking:
   - Email address is sent to HIBP API
   - NOT k-anonymous - HIBP will see your email
   - User must be warned before running this check
   - Returns list of breaches containing the email

API Documentation:
  - Pwned Passwords: https://haveibeenpwned.com/API/v3#PwnedPasswords
  - Breached Account: https://haveibeenpwned.com/API/v3#BreachesForAccount

References:
  - HIBP: https://haveibeenpwned.com
  - K-Anonymity Paper: https://www.troyhunt.com/ive-just-launched-pwned-passwords-version-2/
"""

import hashlib
import requests
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging

# Setup logging
logger = logging.getLogger(__name__)


class BreachMonitor:
    """
    Monitor for data breaches using Have I Been Pwned (HIBP) API.

    This class provides methods to check if passwords or emails have been
    exposed in known data breaches while maintaining user privacy through
    k-anonymity techniques.
    """

    # HIBP API Base URLs
    PWNED_PASSWORDS_API = "https://api.pwnedpasswords.com/range/{hash_prefix}"
    BREACHED_ACCOUNT_API = "https://haveibeenpwned.com/api/v3/breachedaccount/{email}"

    def __init__(self, db_connection=None):
        """
        Initialize the Breach Monitor.

        Args:
            db_connection: Optional database connection for storing breach findings.
                          If provided, findings are automatically saved to exposed_data table.
        """
        self.db_connection = db_connection
        self.headers = {
            'User-Agent': 'Privacy-Deletion-Tool-Breach-Monitor',
            'Add-Padding': 'true'  # HIBP feature to obscure response size
        }

    # ═══════════════════════════════════════════════════════════════════════
    # Password Breach Checking (K-Anonymity)
    # ═══════════════════════════════════════════════════════════════════════

    def check_password_breach(self, password: str) -> Dict:
        """
        Check if a password has been exposed in known breaches using k-anonymity.

        This method implements the k-anonymity model to preserve privacy:
          1. Hash the password locally with SHA-1
          2. Send only the first 5 characters of the hash to HIBP
          3. Receive ~800 hash suffixes that match the prefix
          4. Search locally for the full hash
          5. Return breach status WITHOUT revealing the password to HIBP

        Privacy Guarantee: HIBP never receives your password or full hash.
        Only 1 out of 1,048,576 possible hash prefixes is revealed.

        Args:
            password: The password to check (NEVER stored or logged)

        Returns:
            Dictionary containing:
              - exposed: Boolean indicating if password was found in breaches
              - occurrences: Number of times seen in breaches (0 if not found)
              - risk_level: 'Critical' (password is breached)
              - hash_prefix: First 5 chars of hash (for debugging)

        Example:
            >>> monitor = BreachMonitor()
            >>> result = monitor.check_password_breach("password123")
            >>> print(result)
            {'exposed': True, 'occurrences': 235000, 'risk_level': 'Critical'}
        """
        try:
            # ═══════════════════════════════════════════════════════════════
            # Step 1: Hash password locally with SHA-1
            # ═══════════════════════════════════════════════════════════════
            # The password is NEVER sent over the network
            sha1_hash = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()

            # ═══════════════════════════════════════════════════════════════
            # Step 2: Send only first 5 characters to HIBP
            # ═══════════════════════════════════════════════════════════════
            # This reveals only 1 out of 1,048,576 possible prefixes
            hash_prefix = sha1_hash[:5]
            hash_suffix = sha1_hash[5:]

            # ═══════════════════════════════════════════════════════════════
            # Step 3: Query HIBP API with prefix only
            # ═══════════════════════════════════════════════════════════════
            api_url = self.PWNED_PASSWORDS_API.format(hash_prefix=hash_prefix)
            response = requests.get(api_url, headers=self.headers, timeout=10)

            if response.status_code != 200:
                logger.error(f"HIBP API error: {response.status_code}")
                return {
                    'exposed': False,
                    'occurrences': 0,
                    'error': f'API returned status code {response.status_code}',
                    'risk_level': 'Unknown'
                }

            # ═══════════════════════════════════════════════════════════════
            # Step 4: Search locally for full hash in response
            # ═══════════════════════════════════════════════════════════════
            # HIBP returns lines like: "SUFFIX:COUNT\r\n"
            # We search for our suffix in the response
            hashes = response.text.splitlines()

            for hash_line in hashes:
                parts = hash_line.split(':')
                if len(parts) == 2:
                    response_suffix, count = parts
                    if response_suffix == hash_suffix:
                        # Password found in breaches!
                        occurrences = int(count)
                        logger.warning(f"Password found in {occurrences} breaches")
                        return {
                            'exposed': True,
                            'occurrences': occurrences,
                            'risk_level': 'Critical',
                            'hash_prefix': hash_prefix,
                            'data_type': 'password',
                            'source': 'HIBP-Password'
                        }

            # Password not found in breaches
            logger.info("Password not found in known breaches")
            return {
                'exposed': False,
                'occurrences': 0,
                'risk_level': 'Low',
                'data_type': 'password',
                'source': 'HIBP-Password'
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error checking password: {e}")
            return {
                'exposed': False,
                'occurrences': 0,
                'error': str(e),
                'risk_level': 'Unknown'
            }
        except Exception as e:
            logger.error(f"Unexpected error checking password: {e}")
            return {
                'exposed': False,
                'occurrences': 0,
                'error': str(e),
                'risk_level': 'Unknown'
            }

    # ═══════════════════════════════════════════════════════════════════════
    # Email Breach Checking (NOT K-Anonymous)
    # ═══════════════════════════════════════════════════════════════════════

    def check_email_breach(self, email: str, api_key: Optional[str] = None) -> Dict:
        """
        Check if an email address appears in known data breaches.

        ⚠️  PRIVACY WARNING: This API is NOT k-anonymous!
        ⚠️  Your email address will be sent to Have I Been Pwned.
        ⚠️  User must consent before calling this method.

        The email address is sent directly to HIBP, which will:
          - See your email address
          - Return list of breaches containing it
          - Not store or share your email (according to HIBP privacy policy)

        Args:
            email: Email address to check
            api_key: Optional HIBP API key for higher rate limits
                    (Get free key at: https://haveibeenpwned.com/API/Key)

        Returns:
            Dictionary containing:
              - exposed: Boolean indicating if email found in breaches
              - breach_count: Number of breaches containing the email
              - breaches: List of breach details (name, date, compromised data)
              - risk_level: 'High' if exposed, 'Low' if not
              - data_type: 'email'
              - source: 'HIBP-Email'

        Example:
            >>> monitor = BreachMonitor()
            >>> result = monitor.check_email_breach("test@example.com")
            >>> print(result)
            {'exposed': True, 'breach_count': 3, 'breaches': [...]}

        Raises:
            ValueError: If email format is invalid
        """
        try:
            # Basic email validation
            if '@' not in email or '.' not in email:
                raise ValueError("Invalid email format")

            # Prepare headers (add API key if provided for higher rate limits)
            headers = self.headers.copy()
            if api_key:
                headers['hibp-api-key'] = api_key

            # ═══════════════════════════════════════════════════════════════
            # Query HIBP Breached Account API
            # ═══════════════════════════════════════════════════════════════
            # This sends the email address directly to HIBP
            api_url = self.BREACHED_ACCOUNT_API.format(email=email)
            response = requests.get(
                api_url,
                headers=headers,
                timeout=10,
                params={'truncateResponse': 'false'}  # Get full breach details
            )

            # ═══════════════════════════════════════════════════════════════
            # Handle API Response
            # ═══════════════════════════════════════════════════════════════

            # 404 = Email not found in any breaches (good news!)
            if response.status_code == 404:
                logger.info(f"Email not found in breaches: {email}")
                return {
                    'exposed': False,
                    'breach_count': 0,
                    'breaches': [],
                    'risk_level': 'Low',
                    'data_type': 'email',
                    'source': 'HIBP-Email',
                    'email': email
                }

            # 401 = Unauthorized (missing or invalid API key)
            elif response.status_code == 401:
                logger.error("HIBP API key required or invalid")
                return {
                    'exposed': False,
                    'breach_count': 0,
                    'error': 'HIBP API key required for email checking. Get one at: https://haveibeenpwned.com/API/Key',
                    'risk_level': 'Unknown'
                }

            # 429 = Rate limit exceeded
            elif response.status_code == 429:
                logger.error("HIBP rate limit exceeded")
                return {
                    'exposed': False,
                    'breach_count': 0,
                    'error': 'Rate limit exceeded. Try again later or use an API key.',
                    'risk_level': 'Unknown'
                }

            # 200 = Email found in breaches
            elif response.status_code == 200:
                breaches = response.json()
                breach_count = len(breaches)

                logger.warning(f"Email found in {breach_count} breaches: {email}")

                # Extract breach details
                breach_details = []
                for breach in breaches:
                    breach_details.append({
                        'name': breach.get('Name'),
                        'title': breach.get('Title'),
                        'domain': breach.get('Domain'),
                        'breach_date': breach.get('BreachDate'),
                        'added_date': breach.get('AddedDate'),
                        'pwn_count': breach.get('PwnCount'),  # Total accounts in breach
                        'description': breach.get('Description'),
                        'compromised_data': breach.get('DataClasses', []),
                        'is_verified': breach.get('IsVerified'),
                        'is_sensitive': breach.get('IsSensitive')
                    })

                return {
                    'exposed': True,
                    'breach_count': breach_count,
                    'breaches': breach_details,
                    'risk_level': 'High',
                    'data_type': 'email',
                    'source': 'HIBP-Email',
                    'email': email
                }

            else:
                logger.error(f"Unexpected HIBP API response: {response.status_code}")
                return {
                    'exposed': False,
                    'breach_count': 0,
                    'error': f'Unexpected API response: {response.status_code}',
                    'risk_level': 'Unknown'
                }

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error checking email breaches: {e}")
            return {
                'exposed': False,
                'breach_count': 0,
                'error': str(e),
                'risk_level': 'Unknown'
            }
        except ValueError as e:
            logger.error(f"Validation error: {e}")
            return {
                'exposed': False,
                'breach_count': 0,
                'error': str(e),
                'risk_level': 'Unknown'
            }
        except Exception as e:
            logger.error(f"Unexpected error checking email breaches: {e}")
            return {
                'exposed': False,
                'breach_count': 0,
                'error': str(e),
                'risk_level': 'Unknown'
            }

    # ═══════════════════════════════════════════════════════════════════════
    # Database Integration
    # ═══════════════════════════════════════════════════════════════════════

    def save_password_breach_to_db(self, password_result: Dict, account_id: Optional[int] = None) -> bool:
        """
        Save password breach finding to the exposed_data table.

        Args:
            password_result: Result from check_password_breach()
            account_id: Optional account ID to associate with

        Returns:
            True if saved successfully, False otherwise
        """
        if not self.db_connection:
            logger.warning("No database connection - cannot save breach data")
            return False

        if not password_result.get('exposed'):
            logger.info("Password not breached - nothing to save")
            return False

        try:
            cursor = self.db_connection.cursor()

            # Don't store the actual password - just breach metadata
            details = {
                'occurrences': password_result.get('occurrences', 0),
                'hash_prefix': password_result.get('hash_prefix', ''),
                'checked_date': datetime.now().isoformat()
            }

            cursor.execute("""
                INSERT INTO exposed_data
                (account_id, data_type, data_value, source, risk_level, details, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                account_id,
                'password',
                '[REDACTED - Password Hash Only]',  # Never store actual password
                'HIBP-Password',
                'Critical',
                json.dumps(details),
                'EXPOSED'
            ))

            self.db_connection.commit()
            cursor.close()
            logger.info("Saved password breach to database")
            return True

        except Exception as e:
            logger.error(f"Error saving password breach to database: {e}")
            self.db_connection.rollback()
            return False

    def save_email_breaches_to_db(self, email_result: Dict, account_id: Optional[int] = None) -> bool:
        """
        Save email breach findings to the exposed_data table.

        Each breach is stored as a separate record for better tracking.

        Args:
            email_result: Result from check_email_breach()
            account_id: Optional account ID to associate with

        Returns:
            True if saved successfully, False otherwise
        """
        if not self.db_connection:
            logger.warning("No database connection - cannot save breach data")
            return False

        if not email_result.get('exposed'):
            logger.info("Email not breached - nothing to save")
            return False

        try:
            cursor = self.db_connection.cursor()
            email = email_result.get('email', 'unknown')
            breaches = email_result.get('breaches', [])

            saved_count = 0

            # Save each breach as a separate record
            for breach in breaches:
                details = {
                    'breach_name': breach.get('name'),
                    'breach_title': breach.get('title'),
                    'breach_date': breach.get('breach_date'),
                    'pwn_count': breach.get('pwn_count'),
                    'compromised_data': breach.get('compromised_data', []),
                    'is_verified': breach.get('is_verified'),
                    'description': breach.get('description', '')[:500],  # Limit size
                    'checked_date': datetime.now().isoformat()
                }

                cursor.execute("""
                    INSERT INTO exposed_data
                    (account_id, data_type, data_value, source, risk_level, details, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    account_id,
                    'email',
                    email,
                    f"HIBP-Email: {breach.get('name')}",
                    'High',
                    json.dumps(details),
                    'EXPOSED'
                ))

                saved_count += 1

            self.db_connection.commit()
            cursor.close()
            logger.info(f"Saved {saved_count} email breaches to database")
            return True

        except Exception as e:
            logger.error(f"Error saving email breaches to database: {e}")
            self.db_connection.rollback()
            return False


# ═══════════════════════════════════════════════════════════════════════════
# Utility Functions
# ═══════════════════════════════════════════════════════════════════════════

def format_breach_summary(breach: Dict) -> str:
    """
    Format a breach report for display.

    Args:
        breach: Breach dictionary from check_email_breach()

    Returns:
        Formatted string
    """
    name = breach.get('name', 'Unknown')
    date = breach.get('breach_date', 'Unknown')
    pwn_count = breach.get('pwn_count', 0)
    data = ', '.join(breach.get('compromised_data', []))

    return f"""
Breach: {name}
  Date: {date}
  Affected Accounts: {pwn_count:,}
  Compromised Data: {data}
"""


# ═══════════════════════════════════════════════════════════════════════════
# Test/Demo Function
# ═══════════════════════════════════════════════════════════════════════════

def test_breach_monitor():
    """Test the BreachMonitor functionality."""
    print("\n" + "="*70)
    print("TESTING BREACH MONITOR (Privacy-Preserving)")
    print("="*70)

    monitor = BreachMonitor()

    # Test 1: Check a known weak password (should be in breaches)
    print("\nTest 1: Checking a known weak password")
    print("-" * 70)
    result = monitor.check_password_breach("password123")
    if result['exposed']:
        print(f"  ⚠️  Password EXPOSED in {result['occurrences']:,} breaches")
        print(f"  Risk Level: {result['risk_level']}")
    else:
        print("  ✓ Password not found in breaches")

    # Test 2: Check a strong random password (should NOT be in breaches)
    print("\nTest 2: Checking a strong random password")
    print("-" * 70)
    result = monitor.check_password_breach("xK9$mP2#qL8@wN4%")
    if result['exposed']:
        print(f"  ⚠️  Password exposed in {result['occurrences']:,} breaches")
    else:
        print("  ✓ Password not found in breaches (as expected)")
        print(f"  Risk Level: {result['risk_level']}")

    # Test 3: Explain k-anonymity
    print("\nTest 3: K-Anonymity Privacy Explanation")
    print("-" * 70)
    print("  How password checking preserves privacy:")
    print("  1. Your password is hashed locally (SHA-1)")
    print("  2. Only first 5 chars of hash sent to HIBP")
    print("  3. HIBP returns ~800 matching hash suffixes")
    print("  4. We search locally for your full hash")
    print("  5. HIBP NEVER sees your password or full hash")
    print("  ")
    print("  Privacy guarantee: 1 out of 1,048,576 possible prefixes")

    # Test 4: Email breach check (with warning)
    print("\nTest 4: Email Breach Check (WARNING: Not k-anonymous)")
    print("-" * 70)
    print("  ⚠️  Email checks send your email address to HIBP")
    print("  ⚠️  This is NOT privacy-preserving like password checks")
    print("  ⚠️  User must consent before running")
    print("  ")
    print("  Skipping email test in demo mode...")
    print("  To test: result = monitor.check_email_breach('test@example.com', api_key)")

    print("\n" + "="*70)
    print("✓ Breach Monitor Test Complete")
    print("="*70)
    print("\nNOTE: Password checking uses k-anonymity for privacy.")
    print("Email checking requires user consent as it's not anonymous.")
    print("="*70 + "\n")


if __name__ == "__main__":
    # Run test when module is executed directly
    test_breach_monitor()
