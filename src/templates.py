"""
Deletion Request Template System.
This module provides standardized email templates for data deletion requests
under different privacy regulations (GDPR, CCPA) and a generic version.
"""

from datetime import datetime


class DeletionTemplates:
    """
    Manages and generates formatted email content for deletion requests.
    """

    def __init__(self):
        """
        Initializes the template manager with available templates.
        """
        self.templates = {
            'gdpr': self.gdpr_template,
            'ccpa': self.ccpa_template,
            'generic': self.generic_template
        }

    def get_template(self, template_type='generic'):
        """
        Retrieves a template function by its type.

        Args:
            template_type (str): The type of template ('gdpr', 'ccpa', 'generic').

        Returns:
            function: The corresponding template generation function.
        """
        return self.templates.get(template_type.lower(), self.generic_template)

    def gdpr_template(self, company_name, user_email, **kwargs):
        """
        Generates a data deletion request based on GDPR Article 17.

        Returns:
            dict: A dictionary with 'subject' and 'body' for the email.
        """
        return {
            'subject': f"Data Deletion Request - Article 17 GDPR - {user_email}",
            'body': f"""Dear {company_name} Data Protection Officer,

I am writing to request the complete deletion of all personal data you hold about me, in accordance with my rights under Article 17 of the General Data Protection Regulation (GDPR).

My account is associated with the following email address: {user_email}
Request Date: {datetime.now().strftime('%Y-%m-%d')}

Please erase all personal data associated with my account from all of your systems, including but not limited to:
- Account profiles and user information
- Transaction and activity history
- Marketing, analytics, and tracking data
- Any data held in backup or archival systems

Please also ensure that you forward this request to any third-party processors with whom you have shared my data.

I expect confirmation of the completion of this request within 30 days, as stipulated by the regulation. If you require any further information to verify my identity, please let me know.

Sincerely,
{kwargs.get('user_name', 'A Concerned User')}
"""
        }

    def ccpa_template(self, company_name, user_email, **kwargs):
        """
        Generates a data deletion request based on CCPA.

        Returns:
            dict: A dictionary with 'subject' and 'body' for the email.
        """
        return {
            'subject': f"Personal Information Deletion Request - CCPA Rights",
            'body': f"""Dear {company_name} Privacy Team,

Pursuant to my rights under the California Consumer Privacy Act (CCPA), I am requesting that you delete all personal information you have collected about me.

My account is identified by the email address: {user_email}
Request Date: {datetime.now().strftime('%Y-%m-%d')}

Please delete all categories of personal information you maintain about me and direct any service providers to do the same.

Please confirm receipt of this request and provide confirmation once the deletion is complete, within the 45-day timeframe required by law.

Thank you,
{kwargs.get('user_name', 'A California Consumer')}
"""
        }

    def generic_template(self, company_name, user_email, **kwargs):
        """
        Generates a generic, non-jurisdictional data deletion request.

        Returns:
            dict: A dictionary with 'subject' and 'body' for the email.
        """
        return {
            'subject': f"Request to Delete My Personal Data - {user_email}",
            'body': f"""Dear {company_name} Privacy Team,

I am writing to formally request the complete deletion of my personal data and account from your systems.

The account in question is associated with this email address: {user_email}

Please process this request and provide a confirmation once my data has been permanently erased.

Thank you for your prompt attention to this matter.

Best regards,
{kwargs.get('user_name', 'A User of Your Service')}
"""
        }