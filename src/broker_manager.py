"""
Data Broker Manager
===================

This module manages the curated database of known data brokers and provides
functionality to send opt-out requests to these brokers.

The data broker database is maintained in config/data_brokers.json and includes:
  - People search engines (Spokeo, Whitepages, etc.)
  - Background check services (BeenVerified, TruthFinder, etc.)
  - Marketing data aggregators (Acxiom, etc.)
  - Public records databases

Privacy Approach:
  Email-based automation is the most privacy-preserving and scalable method
  for data broker removal, as it bypasses web-based bot detection systems
  while maintaining a documented paper trail.

References:
  - Big-Ass-Data-Broker-Opt-Out-List (BADBOOL)
  - California DROS platform (launching 2026)
  - CCPA and GDPR deletion rights
"""

import json
import os
from typing import List, Dict, Optional
from datetime import datetime
import logging

# Setup logging
logger = logging.getLogger(__name__)


class BrokerManager:
    """
    Manages the curated database of data brokers and tracks opt-out requests.

    This class provides methods to:
      - Load and query the broker database
      - Filter brokers by various criteria
      - Generate opt-out request data
      - Track which brokers have been contacted

    The broker database is stored in config/data_brokers.json and contains
    metadata about each broker including contact information, opt-out methods,
    and estimated processing times.
    """

    def __init__(self, db_connection=None):
        """
        Initialize the Broker Manager.

        Args:
            db_connection: Optional database connection for tracking sent requests.
                          If provided, enables integration with the requests table.
        """
        self.db_connection = db_connection
        self.brokers = []
        self._load_brokers()

    def _load_brokers(self):
        """
        Load the data broker database from JSON file.

        The JSON file is located at config/data_brokers.json and contains
        a curated list of major data brokers with their contact information
        and opt-out procedures.

        Raises:
            FileNotFoundError: If the broker database file doesn't exist
            json.JSONDecodeError: If the JSON file is malformed
        """
        # Determine the path to the config directory
        # This works whether the script is run from project root or src/
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        broker_db_path = os.path.join(project_root, 'config', 'data_brokers.json')

        try:
            with open(broker_db_path, 'r', encoding='utf-8') as f:
                self.brokers = json.load(f)
            logger.info(f"Loaded {len(self.brokers)} data brokers from database")
        except FileNotFoundError:
            logger.error(f"Broker database not found at: {broker_db_path}")
            logger.error("Please ensure config/data_brokers.json exists")
            self.brokers = []
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in broker database: {e}")
            self.brokers = []

    def get_all_brokers(self) -> List[Dict]:
        """
        Get all brokers from the database.

        Returns:
            List of dictionaries, each containing broker metadata
        """
        return self.brokers

    def get_broker_by_id(self, broker_id: str) -> Optional[Dict]:
        """
        Get a specific broker by ID.

        Args:
            broker_id: Unique identifier for the broker (e.g., 'spokeo', 'whitepages')

        Returns:
            Dictionary containing broker metadata, or None if not found
        """
        for broker in self.brokers:
            if broker.get('broker_id') == broker_id:
                return broker
        return None

    def get_brokers_by_category(self, category: str) -> List[Dict]:
        """
        Filter brokers by category.

        Args:
            category: Broker category. Valid values:
                - 'people_search': People search engines
                - 'background_check': Background check services
                - 'public_records': Public records databases
                - 'marketing_data': Marketing data aggregators
                - 'property_records': Property and address databases
                - 'genealogy': Genealogy and family tree sites
                - 'reputation_management': Reputation management services
                - 'identity_verification': Identity verification services

        Returns:
            List of brokers matching the category
        """
        return [b for b in self.brokers if b.get('category') == category]

    def get_brokers_by_difficulty(self, difficulty: str) -> List[Dict]:
        """
        Filter brokers by opt-out difficulty.

        Args:
            difficulty: 'easy', 'medium', or 'hard'

        Returns:
            List of brokers matching the difficulty level

        Difficulty Levels:
          - easy: Simple webform or email, quick response
          - medium: May require phone/email verification, slower response
          - hard: Requires ID verification, multiple steps, or difficult process
        """
        return [b for b in self.brokers if b.get('difficulty') == difficulty]

    def get_brokers_by_method(self, method: str) -> List[Dict]:
        """
        Filter brokers by opt-out method.

        Args:
            method: 'email' or 'webform'

        Returns:
            List of brokers using the specified opt-out method

        Method Types:
          - email: Send deletion request via email (most privacy-preserving)
          - webform: Complete opt-out form on broker's website
        """
        return [b for b in self.brokers if b.get('opt_out_method') == method]

    def get_email_based_brokers(self) -> List[Dict]:
        """
        Get all brokers that accept email-based opt-out requests.

        Email-based requests are preferred because they:
          - Bypass web-based bot detection
          - Provide documented paper trail
          - Can be automated without CAPTCHA issues
          - Are more privacy-preserving (no browser fingerprinting)

        Returns:
            List of brokers that accept email opt-out requests
        """
        return self.get_brokers_by_method('email')

    def get_webform_based_brokers(self) -> List[Dict]:
        """
        Get all brokers that require webform submission.

        These brokers require manual interaction or browser automation.
        They cannot be easily automated due to:
          - CAPTCHA challenges
          - Email/phone verification steps
          - JavaScript requirements
          - Bot detection systems

        Returns:
            List of brokers requiring webform submission
        """
        return self.get_brokers_by_method('webform')

    def get_statistics(self) -> Dict:
        """
        Get statistics about the broker database.

        Returns:
            Dictionary containing:
              - total_brokers: Total number of brokers in database
              - by_category: Count of brokers per category
              - by_difficulty: Count of brokers per difficulty level
              - by_method: Count of brokers per opt-out method
              - email_automatable: Number of brokers that can be automated via email
        """
        stats = {
            'total_brokers': len(self.brokers),
            'by_category': {},
            'by_difficulty': {},
            'by_method': {},
            'email_automatable': len(self.get_email_based_brokers())
        }

        # Count by category
        for broker in self.brokers:
            category = broker.get('category', 'unknown')
            stats['by_category'][category] = stats['by_category'].get(category, 0) + 1

        # Count by difficulty
        for broker in self.brokers:
            difficulty = broker.get('difficulty', 'unknown')
            stats['by_difficulty'][difficulty] = stats['by_difficulty'].get(difficulty, 0) + 1

        # Count by method
        for broker in self.brokers:
            method = broker.get('opt_out_method', 'unknown')
            stats['by_method'][method] = stats['by_method'].get(method, 0) + 1

        return stats

    def generate_opt_out_request_data(self, broker_id: str, user_data: Dict) -> Optional[Dict]:
        """
        Generate opt-out request data for a specific broker.

        This method prepares all necessary information to send an opt-out request,
        including the broker's contact information and user data.

        Args:
            broker_id: Unique identifier for the broker
            user_data: Dictionary containing user information:
                - name: Full name
                - email: Email address
                - phone: Phone number (optional)
                - address: Physical address (optional)

        Returns:
            Dictionary containing:
              - broker: Full broker information
              - user_data: User information for the request
              - template_type: Suggested email template (e.g., 'ccpa', 'gdpr', 'generic')
              - contact_email: Email address to send the request to
              - opt_out_url: URL for webform (if applicable)

            Returns None if broker not found
        """
        broker = self.get_broker_by_id(broker_id)
        if not broker:
            logger.error(f"Broker not found: {broker_id}")
            return None

        # Determine appropriate template based on broker's supported regulations
        regulations = broker.get('regulation', [])
        template_type = 'generic'
        if 'CCPA' in regulations:
            template_type = 'ccpa'
        elif 'GDPR' in regulations:
            template_type = 'gdpr'

        request_data = {
            'broker': broker,
            'user_data': user_data,
            'template_type': template_type,
            'contact_email': broker.get('contact_email'),
            'opt_out_url': broker.get('opt_out_url'),
            'opt_out_method': broker.get('opt_out_method'),
            'estimated_time': broker.get('estimated_time'),
            'verification_method': broker.get('verification_method'),
            'generated_at': datetime.now().isoformat()
        }

        return request_data

    def search_brokers(self, query: str) -> List[Dict]:
        """
        Search brokers by name.

        Performs case-insensitive search across broker names.

        Args:
            query: Search term (e.g., 'spokeo', 'people search')

        Returns:
            List of matching brokers
        """
        query_lower = query.lower()
        results = []

        for broker in self.brokers:
            name = broker.get('name', '').lower()
            category = broker.get('category', '').lower()
            broker_id = broker.get('broker_id', '').lower()

            if (query_lower in name or
                query_lower in category or
                query_lower in broker_id):
                results.append(broker)

        return results

    def get_recommended_brokers(self, prioritize_easy: bool = True) -> List[Dict]:
        """
        Get a recommended list of brokers to start with.

        This returns a prioritized list of brokers that are:
          - High-impact (major people search engines)
          - Easy to opt-out from
          - Email-based (can be automated)

        Args:
            prioritize_easy: If True, prioritize easy opt-outs first

        Returns:
            Sorted list of recommended brokers to target first
        """
        # Major high-impact brokers
        high_priority_ids = [
            'spokeo', 'whitepages', 'intelius', 'beenverified',
            'truthfinder', 'mylife', 'radaris', 'peoplesmart'
        ]

        high_priority = []
        other_brokers = []

        for broker in self.brokers:
            if broker.get('broker_id') in high_priority_ids:
                high_priority.append(broker)
            else:
                other_brokers.append(broker)

        if prioritize_easy:
            # Sort by difficulty: easy first, then medium, then hard
            difficulty_order = {'easy': 0, 'medium': 1, 'hard': 2}
            high_priority.sort(key=lambda b: difficulty_order.get(b.get('difficulty', 'medium'), 1))
            other_brokers.sort(key=lambda b: difficulty_order.get(b.get('difficulty', 'medium'), 1))

        return high_priority + other_brokers


# ═══════════════════════════════════════════════════════════════════════════
# Utility Functions
# ═══════════════════════════════════════════════════════════════════════════

def format_broker_summary(broker: Dict) -> str:
    """
    Format a broker's information for display.

    Args:
        broker: Broker dictionary

    Returns:
        Formatted string with broker details
    """
    name = broker.get('name', 'Unknown')
    category = broker.get('category', 'unknown').replace('_', ' ').title()
    method = broker.get('opt_out_method', 'unknown').upper()
    difficulty = broker.get('difficulty', 'unknown').upper()
    contact = broker.get('contact_email', broker.get('opt_out_url', 'N/A'))

    summary = f"""
{name}
  Category: {category}
  Method: {method}
  Difficulty: {difficulty}
  Contact: {contact}
  Est. Time: {broker.get('estimated_time', 'Unknown')}
"""
    return summary


def print_broker_statistics(broker_manager: BrokerManager):
    """
    Print statistics about the broker database.

    Args:
        broker_manager: Initialized BrokerManager instance
    """
    stats = broker_manager.get_statistics()

    print("\n" + "="*60)
    print("DATA BROKER DATABASE STATISTICS")
    print("="*60)
    print(f"\nTotal Brokers: {stats['total_brokers']}")
    print(f"Email-Automatable: {stats['email_automatable']}")

    print("\nBy Category:")
    for category, count in sorted(stats['by_category'].items()):
        category_display = category.replace('_', ' ').title()
        print(f"  {category_display}: {count}")

    print("\nBy Difficulty:")
    for difficulty, count in sorted(stats['by_difficulty'].items()):
        print(f"  {difficulty.title()}: {count}")

    print("\nBy Method:")
    for method, count in sorted(stats['by_method'].items()):
        print(f"  {method.title()}: {count}")

    print("="*60 + "\n")


# ═══════════════════════════════════════════════════════════════════════════
# Test/Demo Function
# ═══════════════════════════════════════════════════════════════════════════

def test_broker_manager():
    """Test the BrokerManager functionality."""
    print("\n" + "="*60)
    print("TESTING BROKER MANAGER")
    print("="*60)

    # Initialize manager
    manager = BrokerManager()

    # Print statistics
    print_broker_statistics(manager)

    # Test filtering
    print("\nEmail-Based Brokers (Can be automated):")
    print("-" * 60)
    email_brokers = manager.get_email_based_brokers()
    for broker in email_brokers[:5]:  # Show first 5
        print(f"  • {broker['name']} ({broker['contact_email']})")
    print(f"  ... and {len(email_brokers) - 5} more")

    print("\nEasy Opt-Out Brokers (Recommended to start):")
    print("-" * 60)
    easy_brokers = manager.get_brokers_by_difficulty('easy')
    for broker in easy_brokers[:5]:  # Show first 5
        print(f"  • {broker['name']} - {broker['opt_out_method']}")
    print(f"  ... and {len(easy_brokers) - 5} more")

    print("\nRecommended Priority List:")
    print("-" * 60)
    recommended = manager.get_recommended_brokers()
    for i, broker in enumerate(recommended[:10], 1):  # Top 10
        print(f"  {i}. {broker['name']} ({broker['difficulty']}, {broker['opt_out_method']})")

    # Test search
    print("\nSearch Results for 'people':")
    print("-" * 60)
    results = manager.search_brokers('people')
    for broker in results[:5]:
        print(f"  • {broker['name']} - {broker['category']}")

    # Test request generation
    print("\nGenerating Sample Opt-Out Request:")
    print("-" * 60)
    user_data = {
        'name': 'John Doe',
        'email': 'john.doe@example.com',
        'phone': '555-1234',
        'address': '123 Main St, Anytown, USA'
    }
    request_data = manager.generate_opt_out_request_data('spokeo', user_data)
    if request_data:
        print(f"  Broker: {request_data['broker']['name']}")
        print(f"  Template Type: {request_data['template_type'].upper()}")
        print(f"  Contact Email: {request_data['contact_email']}")
        print(f"  Verification Method: {request_data['verification_method']}")
        print(f"  Estimated Time: {request_data['estimated_time']}")

    print("\n" + "="*60)
    print("✓ Broker Manager Test Complete")
    print("="*60 + "\n")


if __name__ == "__main__":
    # Run test when module is executed directly
    test_broker_manager()
