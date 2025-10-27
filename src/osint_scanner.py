"""
OSINT Exposure Scanner
======================

This module integrates open-source intelligence (OSINT) tools to discover
publicly exposed personal information across the internet.

Supported OSINT Tools:
  1. Sherlock - Username scanning across 300+ social media platforms
  2. theHarvester - Email and subdomain discovery (future)
  3. phoneinfoga - Phone number exposure scanning (future)
  4. SpiderFoot - Comprehensive OSINT automation (future)

Privacy & Ethics:
  - Only scan YOUR OWN usernames/emails/phone numbers
  - Results show public data already accessible online
  - Use findings to request removal from platforms
  - Respect rate limits and robots.txt
  - Never use for stalking or harassment

Architecture:
  All tools run as subprocesses to maintain isolation and security.
  Results are parsed and stored in the exposed_data table for tracking.

References:
  - Sherlock: https://github.com/sherlock-project/sherlock
  - theHarvester: https://github.com/laramies/theHarvester
  - phoneinfoga: https://github.com/sundowndev/phoneinfoga
  - OSINT Framework: https://osintframework.com/
"""

import subprocess
import json
import csv
import os
import tempfile
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging
import shutil

# Setup logging
logger = logging.getLogger(__name__)


class OSINTScanner:
    """
    OSINT (Open Source Intelligence) Scanner for discovering public data exposure.

    This class provides methods to scan for exposed usernames, emails, and
    phone numbers across various online platforms using popular OSINT tools.

    All tools are executed as subprocesses, ensuring isolation and security.
    """

    def __init__(self, db_connection=None):
        """
        Initialize the OSINT Scanner.

        Args:
            db_connection: Optional database connection for storing findings.
                          If provided, findings are automatically saved to exposed_data table.
        """
        self.db_connection = db_connection
        self.temp_dir = tempfile.gettempdir()

    # ═══════════════════════════════════════════════════════════════════════
    # Sherlock Integration - Username Exposure Scanning
    # ═══════════════════════════════════════════════════════════════════════

    def check_sherlock_installed(self) -> Tuple[bool, Optional[str]]:
        """
        Check if Sherlock is installed and available.

        Returns:
            Tuple of (is_installed, path_or_error)
              - (True, "/path/to/sherlock") if installed
              - (False, "error message") if not installed

        Installation:
            # Via pip:
            pip install sherlock-project

            # Or via git:
            git clone https://github.com/sherlock-project/sherlock.git
            cd sherlock
            pip install -r requirements.txt
        """
        try:
            # Try to find sherlock executable
            sherlock_path = shutil.which('sherlock')

            if sherlock_path:
                # Verify it works
                result = subprocess.run(
                    ['sherlock', '--version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    logger.info(f"Sherlock found at: {sherlock_path}")
                    return True, sherlock_path

            # Try python3 -m sherlock
            result = subprocess.run(
                ['python3', '-m', 'sherlock', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info("Sherlock available via 'python3 -m sherlock'")
                return True, "python3 -m sherlock"

            # Not found
            error_msg = """
Sherlock not installed. Install with:
  pip install sherlock-project

Or via git:
  git clone https://github.com/sherlock-project/sherlock.git
  cd sherlock && pip install -r requirements.txt
"""
            logger.warning("Sherlock not found")
            return False, error_msg

        except subprocess.TimeoutExpired:
            return False, "Sherlock check timed out"
        except Exception as e:
            return False, f"Error checking Sherlock: {str(e)}"

    def scan_username_sherlock(self, username: str, timeout: int = 120) -> Dict:
        """
        Scan a username across 300+ social media platforms using Sherlock.

        Sherlock checks for username presence on platforms including:
          - Facebook, Instagram, Twitter, TikTok, LinkedIn
          - GitHub, GitLab, Reddit, Medium, WordPress
          - Dating sites, forums, gaming platforms
          - And 290+ more...

        Args:
            username: Username to search for (e.g., 'johndoe123')
            timeout: Maximum time in seconds to wait (default: 120s)

        Returns:
            Dictionary containing:
              - found: Boolean indicating if username was found
              - platform_count: Number of platforms where username exists
              - platforms: List of platform details (name, url, category)
              - risk_level: 'Medium' if found, 'Low' if not
              - error: Error message if scan failed

        Example:
            >>> scanner = OSINTScanner()
            >>> result = scanner.scan_username_sherlock('johndoe123')
            >>> print(f"Found on {result['platform_count']} platforms")
            >>> for platform in result['platforms']:
            ...     print(f"  - {platform['name']}: {platform['url']}")

        Privacy Note:
            - Only scan YOUR OWN usernames
            - Results show publicly accessible information
            - Use findings to request profile removal
        """
        # Check if Sherlock is installed
        is_installed, sherlock_info = self.check_sherlock_installed()
        if not is_installed:
            logger.error("Sherlock not installed")
            return {
                'found': False,
                'platform_count': 0,
                'platforms': [],
                'error': sherlock_info,
                'risk_level': 'Unknown'
            }

        try:
            # Create temporary file for JSON output
            temp_output = os.path.join(self.temp_dir, f'sherlock_{username}_{datetime.now().timestamp()}.json')

            # Build Sherlock command
            # Options:
            #   --json: Output results as JSON (easiest to parse)
            #   --timeout: Maximum time per site check
            #   --print-found: Only show found accounts (reduces noise)
            #   --folderoutput: Save to temp directory
            cmd = [
                'sherlock',
                username,
                '--json', temp_output,
                '--timeout', '10',
                '--print-found'
            ]

            logger.info(f"Running Sherlock scan for username: {username}")
            logger.debug(f"Command: {' '.join(cmd)}")

            # Execute Sherlock
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            # Parse results
            platforms_found = []
            platform_count = 0

            # Sherlock creates JSON file with results
            if os.path.exists(temp_output):
                with open(temp_output, 'r', encoding='utf-8') as f:
                    sherlock_data = json.load(f)

                # Parse Sherlock JSON format
                # Format: {username: {site: {url_main, url_user, exists, ...}}}
                for site_name, site_data in sherlock_data.items():
                    if isinstance(site_data, dict):
                        # Check if account exists
                        if site_data.get('status') and 'Claimed' in str(site_data.get('status')):
                            platforms_found.append({
                                'name': site_name,
                                'url': site_data.get('url_user', site_data.get('url_main', '')),
                                'category': self._categorize_platform(site_name),
                                'http_status': site_data.get('http_status'),
                                'response_time': site_data.get('response_time_s')
                            })
                            platform_count += 1

                # Clean up temp file
                os.remove(temp_output)

            # Parse stderr for additional info (Sherlock prints progress there)
            stderr_output = result.stderr
            if 'found!' in stderr_output.lower():
                # Extract found count from stderr if JSON parsing failed
                match = re.search(r'(\d+)\s+results?.*found', stderr_output, re.IGNORECASE)
                if match and platform_count == 0:
                    # Fallback parsing from text output
                    platform_count = int(match.group(1))
                    # Parse text output line by line
                    platforms_found = self._parse_sherlock_text_output(stderr_output)

            # Determine risk level
            risk_level = 'Low'
            if platform_count > 0:
                risk_level = 'Medium'  # Username exposure is medium risk

            logger.info(f"Sherlock scan complete: {platform_count} platforms found")

            return {
                'found': platform_count > 0,
                'platform_count': platform_count,
                'platforms': platforms_found,
                'risk_level': risk_level,
                'data_type': 'username',
                'data_value': username,
                'source': 'Sherlock',
                'scanned_at': datetime.now().isoformat()
            }

        except subprocess.TimeoutExpired:
            logger.error(f"Sherlock scan timed out after {timeout}s")
            return {
                'found': False,
                'platform_count': 0,
                'platforms': [],
                'error': f'Scan timed out after {timeout} seconds',
                'risk_level': 'Unknown'
            }
        except FileNotFoundError:
            logger.error("Sherlock executable not found")
            return {
                'found': False,
                'platform_count': 0,
                'platforms': [],
                'error': 'Sherlock not found. Install with: pip install sherlock-project',
                'risk_level': 'Unknown'
            }
        except Exception as e:
            logger.error(f"Sherlock scan error: {str(e)}")
            return {
                'found': False,
                'platform_count': 0,
                'platforms': [],
                'error': str(e),
                'risk_level': 'Unknown'
            }

    def _parse_sherlock_text_output(self, text_output: str) -> List[Dict]:
        """
        Parse Sherlock's text output as fallback when JSON is unavailable.

        Args:
            text_output: Raw text output from Sherlock

        Returns:
            List of platform dictionaries
        """
        platforms = []
        lines = text_output.split('\n')

        for line in lines:
            # Sherlock format: "[+] SiteName: https://site.com/username"
            if '[+]' in line or '[*]' in line:
                # Extract site name and URL
                match = re.match(r'\[\+\]\s+([^:]+):\s+(https?://\S+)', line)
                if match:
                    site_name = match.group(1).strip()
                    url = match.group(2).strip()
                    platforms.append({
                        'name': site_name,
                        'url': url,
                        'category': self._categorize_platform(site_name)
                    })

        return platforms

    def _categorize_platform(self, platform_name: str) -> str:
        """
        Categorize a platform based on its name.

        Args:
            platform_name: Name of the platform

        Returns:
            Category string (social_media, professional, gaming, dating, etc.)
        """
        platform_lower = platform_name.lower()

        # Social media
        if any(x in platform_lower for x in ['facebook', 'instagram', 'twitter', 'tiktok', 'snapchat', 'tumblr']):
            return 'social_media'

        # Professional networks
        if any(x in platform_lower for x in ['linkedin', 'github', 'gitlab', 'stackoverflow']):
            return 'professional'

        # Gaming
        if any(x in platform_lower for x in ['steam', 'xbox', 'playstation', 'twitch', 'discord']):
            return 'gaming'

        # Dating
        if any(x in platform_lower for x in ['tinder', 'bumble', 'match', 'okcupid', 'pof']):
            return 'dating'

        # Forums
        if any(x in platform_lower for x in ['reddit', 'forum', 'board']):
            return 'forum'

        # Creative
        if any(x in platform_lower for x in ['youtube', 'vimeo', 'deviantart', 'behance', 'dribbble']):
            return 'creative'

        return 'other'

    # ═══════════════════════════════════════════════════════════════════════
    # Database Integration
    # ═══════════════════════════════════════════════════════════════════════

    def save_username_exposure_to_db(self, scan_result: Dict, account_id: Optional[int] = None) -> bool:
        """
        Save username exposure findings to the exposed_data table.

        Each platform where the username is found is stored as a separate record.

        Args:
            scan_result: Result from scan_username_sherlock()
            account_id: Optional account ID to associate with

        Returns:
            True if saved successfully, False otherwise
        """
        if not self.db_connection:
            logger.warning("No database connection - cannot save OSINT data")
            return False

        if not scan_result.get('found'):
            logger.info("Username not found on any platforms - nothing to save")
            return False

        try:
            cursor = self.db_connection.cursor()
            username = scan_result.get('data_value', 'unknown')
            platforms = scan_result.get('platforms', [])

            saved_count = 0

            # Save each platform exposure as a separate record
            for platform in platforms:
                details = {
                    'platform': platform.get('name'),
                    'url': platform.get('url'),
                    'category': platform.get('category', 'other'),
                    'http_status': platform.get('http_status'),
                    'scanned_at': scan_result.get('scanned_at', datetime.now().isoformat())
                }

                cursor.execute("""
                    INSERT INTO exposed_data
                    (account_id, data_type, data_value, source, risk_level, details, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    account_id,
                    'username',
                    username,
                    f"Sherlock: {platform.get('name')}",
                    'Medium',
                    json.dumps(details),
                    'EXPOSED'
                ))

                saved_count += 1

            self.db_connection.commit()
            cursor.close()
            logger.info(f"Saved {saved_count} username exposures to database")
            return True

        except Exception as e:
            logger.error(f"Error saving username exposure to database: {e}")
            self.db_connection.rollback()
            return False

    # ═══════════════════════════════════════════════════════════════════════
    # Future OSINT Tool Integrations
    # ═══════════════════════════════════════════════════════════════════════

    def check_theharvester_installed(self) -> Tuple[bool, Optional[str]]:
        """
        Check if theHarvester is installed.

        theHarvester aggregates data from 40+ free sources including:
          - Google, Bing, DuckDuckGo (search engines)
          - Shodan, Censys (IoT/device search)
          - GitHub, LinkedIn (professional platforms)
          - Hunter.io, HaveIBeenPwned (email databases)

        Returns:
            Tuple of (is_installed, path_or_error)

        Installation:
            git clone https://github.com/laramies/theHarvester
            cd theHarvester
            pip3 install -r requirements.txt
        """
        try:
            # Check for theHarvester
            result = subprocess.run(
                ['theHarvester', '--help'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info("theHarvester is installed")
                return True, shutil.which('theHarvester')

            return False, "theHarvester not installed"

        except FileNotFoundError:
            return False, """
theHarvester not installed. Install with:
  git clone https://github.com/laramies/theHarvester
  cd theHarvester
  pip3 install -r requirements.txt
"""
        except Exception as e:
            return False, str(e)

    def scan_email_theharvester(self, domain: str, sources: str = 'google,bing') -> Dict:
        """
        Scan for email exposures using theHarvester.

        FUTURE IMPLEMENTATION - Placeholder for expansion.

        Args:
            domain: Domain to search (e.g., 'example.com')
            sources: Comma-separated list of sources to use

        Returns:
            Dictionary with scan results
        """
        logger.warning("theHarvester integration not yet implemented")
        return {
            'found': False,
            'email_count': 0,
            'emails': [],
            'error': 'Not yet implemented - coming in future version',
            'risk_level': 'Unknown'
        }

    def check_phoneinfoga_installed(self) -> Tuple[bool, Optional[str]]:
        """
        Check if phoneinfoga is installed.

        phoneinfoga is an OSINT tool for phone number reconnaissance that:
          - Validates phone number format
          - Identifies carrier and country
          - Searches for phone number in Google dorks
          - Checks VoIP providers and reputation databases

        Returns:
            Tuple of (is_installed, path_or_error)

        Installation:
            # Via Go:
            go install github.com/sundowndev/phoneinfoga/v2@latest

            # Or download binary from:
            https://github.com/sundowndev/phoneinfoga/releases
        """
        try:
            result = subprocess.run(
                ['phoneinfoga', 'version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info("phoneinfoga is installed")
                return True, shutil.which('phoneinfoga')

            return False, "phoneinfoga not installed"

        except FileNotFoundError:
            return False, """
phoneinfoga not installed. Install with:
  go install github.com/sundowndev/phoneinfoga/v2@latest

Or download from:
  https://github.com/sundowndev/phoneinfoga/releases
"""
        except Exception as e:
            return False, str(e)

    def scan_phone_phoneinfoga(self, phone_number: str) -> Dict:
        """
        Scan for phone number exposures using phoneinfoga.

        FUTURE IMPLEMENTATION - Placeholder for expansion.

        Args:
            phone_number: Phone number to scan (e.g., '+14155552671')

        Returns:
            Dictionary with scan results
        """
        logger.warning("phoneinfoga integration not yet implemented")
        return {
            'found': False,
            'exposure_count': 0,
            'sources': [],
            'error': 'Not yet implemented - coming in future version',
            'risk_level': 'Unknown'
        }


# ═══════════════════════════════════════════════════════════════════════════
# Utility Functions
# ═══════════════════════════════════════════════════════════════════════════

def format_platform_summary(platform: Dict) -> str:
    """
    Format a platform exposure for display.

    Args:
        platform: Platform dictionary from scan results

    Returns:
        Formatted string
    """
    name = platform.get('name', 'Unknown')
    url = platform.get('url', 'N/A')
    category = platform.get('category', 'other').replace('_', ' ').title()

    return f"  • {name} ({category})\n    {url}"


def print_osint_tools_status(scanner: OSINTScanner):
    """
    Print installation status of all OSINT tools.

    Args:
        scanner: Initialized OSINTScanner instance
    """
    print("\n" + "="*70)
    print("OSINT TOOLS INSTALLATION STATUS")
    print("="*70)

    # Check Sherlock
    sherlock_installed, sherlock_info = scanner.check_sherlock_installed()
    print("\n1. Sherlock (Username Scanning)")
    print("-" * 70)
    if sherlock_installed:
        print(f"  ✓ INSTALLED: {sherlock_info}")
    else:
        print(f"  ✗ NOT INSTALLED")
        print(f"    {sherlock_info.strip()}")

    # Check theHarvester
    harvester_installed, harvester_info = scanner.check_theharvester_installed()
    print("\n2. theHarvester (Email Discovery)")
    print("-" * 70)
    if harvester_installed:
        print(f"  ✓ INSTALLED: {harvester_info}")
    else:
        print(f"  ✗ NOT INSTALLED (Future Feature)")
        print(f"    {harvester_info.strip()}")

    # Check phoneinfoga
    phone_installed, phone_info = scanner.check_phoneinfoga_installed()
    print("\n3. phoneinfoga (Phone Number Scanning)")
    print("-" * 70)
    if phone_installed:
        print(f"  ✓ INSTALLED: {phone_info}")
    else:
        print(f"  ✗ NOT INSTALLED (Future Feature)")
        print(f"    {phone_info.strip()}")

    print("\n" + "="*70 + "\n")


# ═══════════════════════════════════════════════════════════════════════════
# Test/Demo Function
# ═══════════════════════════════════════════════════════════════════════════

def test_osint_scanner():
    """Test the OSINT Scanner functionality."""
    print("\n" + "="*70)
    print("TESTING OSINT SCANNER")
    print("="*70)

    scanner = OSINTScanner()

    # Print tool installation status
    print_osint_tools_status(scanner)

    # Test Sherlock if installed
    sherlock_installed, _ = scanner.check_sherlock_installed()

    if sherlock_installed:
        print("\nTest: Sherlock Username Scan")
        print("-" * 70)
        print("NOTE: This test will scan for a common test username.")
        print("      For privacy, only scan YOUR OWN usernames.\n")

        # Use a common test username that should exist on many platforms
        test_username = "test"
        print(f"Scanning username: '{test_username}' (this may take 1-2 minutes)...")

        result = scanner.scan_username_sherlock(test_username)

        if result.get('found'):
            print(f"\n✓ Username found on {result['platform_count']} platforms")
            print(f"  Risk Level: {result['risk_level']}")

            # Show first 5 platforms
            platforms = result.get('platforms', [])
            if platforms:
                print("\n  Sample platforms (showing first 5):")
                for platform in platforms[:5]:
                    print(format_platform_summary(platform))

                if len(platforms) > 5:
                    print(f"\n  ... and {len(platforms) - 5} more platforms")
        else:
            error = result.get('error')
            if error:
                print(f"\n✗ Scan failed: {error}")
            else:
                print(f"\n✓ Username not found on any platforms")

    else:
        print("\nSherlock Test Skipped")
        print("-" * 70)
        print("Sherlock is not installed. Install it to enable username scanning.")
        print("\nInstall with:")
        print("  pip install sherlock-project")

    print("\n" + "="*70)
    print("✓ OSINT Scanner Test Complete")
    print("="*70)
    print("\nREMINDER: Only scan YOUR OWN personal information.")
    print("Use results to request removal from platforms where you're exposed.")
    print("="*70 + "\n")


if __name__ == "__main__":
    # Run test when module is executed directly
    test_osint_scanner()
