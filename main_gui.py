#!/usr/bin/env python3
"""
Desktop GUI for the Privacy Data Deletion Tool using CustomTkinter.
Modern, user-friendly interface for managing data deletion requests.
"""

import sys
from pathlib import Path
import threading
import time

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

try:
    import customtkinter as ctk
    from PIL import Image
except ImportError:
    print("ERROR: CustomTkinter or Pillow not installed!")
    print("Please run: pip install customtkinter pillow")
    sys.exit(1)

from database import initialize_database
from gmail_auth import GmailAuthenticator
from account_manager import AccountManager
from email_scanner import EmailScanner
from company_manager import CompanyManager
from contact_finder import ContactFinder
from manual_contact import ManualContactManager
from request_sender import RequestSender
from reply_tracker import ReplyTracker
from logger import setup_logging, logger


# Set appearance mode and color theme
ctk.set_appearance_mode("dark")  # Modes: "System" (default), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (default), "green", "dark-blue"


class PrivacyToolGUI(ctk.CTk):
    """
    Main GUI application for the Privacy Data Deletion Tool.
    """

    def __init__(self):
        super().__init__()

        # Initialize logging
        setup_logging()

        # Window configuration
        self.title("Privacy Data Deletion Tool")
        self.geometry("1100x700")
        self.minsize(900, 600)

        # Initialize database
        try:
            initialize_database()
        except Exception as e:
            self.show_error("Database Error", f"Failed to initialize database: {e}")

        # Initialize managers
        self.gmail_auth = GmailAuthenticator()
        self.account_manager = AccountManager()
        self.company_manager = CompanyManager()
        self.contact_finder = ContactFinder()

        # Current account tracking
        self.current_account = None

        # Create UI
        self.create_sidebar()
        self.create_main_area()

        # Load initial state
        self.refresh_accounts()

    def create_sidebar(self):
        """Create the sidebar navigation."""
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar.grid_rowconfigure(8, weight=1)

        # Logo/Title
        self.logo_label = ctk.CTkLabel(
            self.sidebar,
            text="🔐 Privacy Tool",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Navigation buttons
        self.nav_buttons = []

        btn_dashboard = self.create_nav_button("📊 Dashboard", 1, self.show_dashboard)
        btn_accounts = self.create_nav_button("📧 Accounts", 2, self.show_accounts)
        btn_scan = self.create_nav_button("🔍 Scan Companies", 3, self.show_scan)
        btn_contacts = self.create_nav_button("📇 Find Contacts", 4, self.show_contacts)
        btn_requests = self.create_nav_button("📤 Send Requests", 5, self.show_requests)
        btn_replies = self.create_nav_button("📬 Check Replies", 6, self.show_replies)
        btn_settings = self.create_nav_button("⚙️ Settings", 7, self.show_settings)

        # Appearance mode switch
        self.appearance_label = ctk.CTkLabel(self.sidebar, text="Appearance:")
        self.appearance_label.grid(row=9, column=0, padx=20, pady=(10, 0))

        self.appearance_mode = ctk.CTkOptionMenu(
            self.sidebar,
            values=["Dark", "Light", "System"],
            command=self.change_appearance_mode
        )
        self.appearance_mode.grid(row=10, column=0, padx=20, pady=10)

    def create_nav_button(self, text, row, command):
        """Create a navigation button."""
        btn = ctk.CTkButton(
            self.sidebar,
            text=text,
            command=command,
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            anchor="w",
            height=40
        )
        btn.grid(row=row, column=0, padx=20, pady=5, sticky="ew")
        self.nav_buttons.append(btn)
        return btn

    def create_main_area(self):
        """Create the main content area."""
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Main container
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Show dashboard by default
        self.show_dashboard()

    def clear_main_area(self):
        """Clear the main content area."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    # Navigation functions
    def show_dashboard(self):
        """Display the dashboard view."""
        self.clear_main_area()

        # Title
        title = ctk.CTkLabel(
            self.main_frame,
            text="Dashboard",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)

        # Statistics frame
        stats_frame = ctk.CTkFrame(self.main_frame)
        stats_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Get statistics
        accounts = self.account_manager.get_all_accounts()
        company_stats = self.company_manager.get_statistics()

        # Create stat cards
        stats_container = ctk.CTkFrame(stats_frame, fg_color="transparent")
        stats_container.pack(fill="both", expand=True, padx=20, pady=20)

        self.create_stat_card(stats_container, "📧 Accounts", len(accounts), 0, 0)
        self.create_stat_card(stats_container, "🏢 Companies", company_stats.get('total_companies', 0), 0, 1)
        self.create_stat_card(stats_container, "✉️ With Contacts", company_stats.get('with_contacts', 0), 1, 0)
        self.create_stat_card(stats_container, "📤 Requests Sent", company_stats.get('total_requests', 0), 1, 1)

        # Account details
        if accounts:
            details_frame = ctk.CTkFrame(self.main_frame)
            details_frame.pack(fill="x", padx=20, pady=10)

            details_label = ctk.CTkLabel(
                details_frame,
                text="Account Details",
                font=ctk.CTkFont(size=16, weight="bold")
            )
            details_label.pack(pady=10)

            for account in accounts:
                stats = self.account_manager.get_account_statistics(account['email_address'])
                account_card = ctk.CTkFrame(details_frame)
                account_card.pack(fill="x", padx=10, pady=5)

                email_label = ctk.CTkLabel(
                    account_card,
                    text=f"📧 {account['email_address']}",
                    font=ctk.CTkFont(size=14, weight="bold")
                )
                email_label.pack(anchor="w", padx=10, pady=5)

                stats_text = (
                    f"Companies: {stats['total_companies']} | "
                    f"Sent: {stats['requests_sent']} | "
                    f"Completed: {stats['requests_completed']} | "
                    f"Rate: {stats['completion_rate']:.1f}%"
                )
                stats_label = ctk.CTkLabel(account_card, text=stats_text)
                stats_label.pack(anchor="w", padx=10, pady=(0, 5))

    def create_stat_card(self, parent, title, value, row, col):
        """Create a statistics card."""
        card = ctk.CTkFrame(parent)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        parent.grid_rowconfigure(row, weight=1)
        parent.grid_columnconfigure(col, weight=1)

        title_label = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=14))
        title_label.pack(pady=(20, 5))

        value_label = ctk.CTkLabel(
            card,
            text=str(value),
            font=ctk.CTkFont(size=32, weight="bold")
        )
        value_label.pack(pady=(5, 20))

    def show_accounts(self):
        """Display the accounts management view."""
        self.clear_main_area()

        # Title
        title = ctk.CTkLabel(
            self.main_frame,
            text="Email Accounts",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)

        # Add account button
        add_btn = ctk.CTkButton(
            self.main_frame,
            text="➕ Add Gmail Account",
            command=self.add_account_dialog,
            height=40
        )
        add_btn.pack(pady=10)

        # Accounts list
        accounts_frame = ctk.CTkScrollableFrame(self.main_frame, label_text="Registered Accounts")
        accounts_frame.pack(fill="both", expand=True, padx=20, pady=10)

        accounts = self.account_manager.get_all_accounts()
        if not accounts:
            no_accounts = ctk.CTkLabel(
                accounts_frame,
                text="No accounts registered yet. Click 'Add Gmail Account' to get started.",
                text_color="gray"
            )
            no_accounts.pack(pady=20)
        else:
            for account in accounts:
                self.create_account_card(accounts_frame, account)

    def create_account_card(self, parent, account):
        """Create an account information card."""
        card = ctk.CTkFrame(parent)
        card.pack(fill="x", padx=10, pady=5)

        email_label = ctk.CTkLabel(
            card,
            text=f"📧 {account['email_address']}",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        email_label.pack(side="left", padx=10, pady=10)

        added_label = ctk.CTkLabel(
            card,
            text=f"Added: {account['added_date'].strftime('%Y-%m-%d')}",
            text_color="gray"
        )
        added_label.pack(side="left", padx=10)

        remove_btn = ctk.CTkButton(
            card,
            text="Remove",
            command=lambda: self.remove_account(account['email_address']),
            width=80,
            fg_color="red",
            hover_color="darkred"
        )
        remove_btn.pack(side="right", padx=10, pady=10)

    def show_scan(self):
        """Display the company scanning view."""
        self.clear_main_area()

        title = ctk.CTkLabel(
            self.main_frame,
            text="Scan for Companies",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)

        info = ctk.CTkLabel(
            self.main_frame,
            text="Scan your Gmail inbox for companies you've signed up with",
            text_color="gray"
        )
        info.pack(pady=5)

        # Account selection
        accounts = self.account_manager.get_all_accounts()
        if not accounts:
            no_accounts = ctk.CTkLabel(
                self.main_frame,
                text="No accounts available. Please add an account first.",
                text_color="red"
            )
            no_accounts.pack(pady=20)
            return

        select_frame = ctk.CTkFrame(self.main_frame)
        select_frame.pack(pady=20)

        ctk.CTkLabel(select_frame, text="Select Account:").pack(side="left", padx=10)

        account_var = ctk.StringVar(value=accounts[0]['email_address'])
        account_menu = ctk.CTkOptionMenu(
            select_frame,
            variable=account_var,
            values=[acc['email_address'] for acc in accounts]
        )
        account_menu.pack(side="left", padx=10)

        # Options
        options_frame = ctk.CTkFrame(self.main_frame)
        options_frame.pack(pady=10)

        ctk.CTkLabel(options_frame, text="Max Results:").pack(side="left", padx=10)
        max_results = ctk.CTkEntry(options_frame, width=100)
        max_results.insert(0, "500")
        max_results.pack(side="left", padx=10)

        ctk.CTkLabel(options_frame, text="Start Year:").pack(side="left", padx=10)
        start_year = ctk.CTkEntry(options_frame, width=100)
        start_year.insert(0, "2015")
        start_year.pack(side="left", padx=10)

        # Scan button
        scan_btn = ctk.CTkButton(
            self.main_frame,
            text="🔍 Start Scanning",
            command=lambda: self.start_scan(
                account_var.get(),
                int(max_results.get()),
                int(start_year.get())
            ),
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        scan_btn.pack(pady=20)

        # Results area
        self.scan_results = ctk.CTkTextbox(self.main_frame, height=300)
        self.scan_results.pack(fill="both", expand=True, padx=20, pady=10)

    def show_contacts(self):
        """Display the contact finding view."""
        self.clear_main_area()

        title = ctk.CTkLabel(
            self.main_frame,
            text="Find Privacy Contacts",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)

        info = ctk.CTkLabel(
            self.main_frame,
            text="Automatically discover privacy contact information for companies",
            text_color="gray"
        )
        info.pack(pady=5)

        # Find contacts button
        find_btn = ctk.CTkButton(
            self.main_frame,
            text="🔍 Auto-Find Contacts",
            command=self.start_contact_finding,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        find_btn.pack(pady=20)

        # Results area
        self.contact_results = ctk.CTkTextbox(self.main_frame, height=400)
        self.contact_results.pack(fill="both", expand=True, padx=20, pady=10)

    def show_requests(self):
        """Display the send requests view."""
        self.clear_main_area()

        title = ctk.CTkLabel(
            self.main_frame,
            text="Send Deletion Requests",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)

        accounts = self.account_manager.get_all_accounts()
        if not accounts:
            no_accounts = ctk.CTkLabel(
                self.main_frame,
                text="No accounts available. Please add an account first.",
                text_color="red"
            )
            no_accounts.pack(pady=20)
            return

        # Account selection
        select_frame = ctk.CTkFrame(self.main_frame)
        select_frame.pack(pady=20)

        ctk.CTkLabel(select_frame, text="Send From:").pack(side="left", padx=10)

        account_var = ctk.StringVar(value=accounts[0]['email_address'])
        account_menu = ctk.CTkOptionMenu(
            select_frame,
            variable=account_var,
            values=[acc['email_address'] for acc in accounts]
        )
        account_menu.pack(side="left", padx=10)

        # Template selection
        template_frame = ctk.CTkFrame(self.main_frame)
        template_frame.pack(pady=10)

        ctk.CTkLabel(template_frame, text="Template:").pack(side="left", padx=10)

        template_var = ctk.StringVar(value="generic")
        template_menu = ctk.CTkOptionMenu(
            template_frame,
            variable=template_var,
            values=["generic", "gdpr", "ccpa"]
        )
        template_menu.pack(side="left", padx=10)

        # Send button
        send_btn = ctk.CTkButton(
            self.main_frame,
            text="📤 Send Deletion Requests",
            command=lambda: self.start_sending_requests(account_var.get(), template_var.get()),
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        send_btn.pack(pady=20)

        # Results area
        self.request_results = ctk.CTkTextbox(self.main_frame, height=400)
        self.request_results.pack(fill="both", expand=True, padx=20, pady=10)

    def show_replies(self):
        """Display the check replies view."""
        self.clear_main_area()

        title = ctk.CTkLabel(
            self.main_frame,
            text="Check for Replies",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)

        # Check button
        check_btn = ctk.CTkButton(
            self.main_frame,
            text="📬 Check All Accounts",
            command=self.start_checking_replies,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        check_btn.pack(pady=20)

        # Results area
        self.reply_results = ctk.CTkTextbox(self.main_frame, height=400)
        self.reply_results.pack(fill="both", expand=True, padx=20, pady=10)

    def show_settings(self):
        """Display the settings view."""
        self.clear_main_area()

        title = ctk.CTkLabel(
            self.main_frame,
            text="Settings",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)

        settings_frame = ctk.CTkFrame(self.main_frame)
        settings_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Appearance settings
        appearance_section = ctk.CTkFrame(settings_frame)
        appearance_section.pack(fill="x", padx=20, pady=20)

        ctk.CTkLabel(
            appearance_section,
            text="Appearance",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=10, pady=10)

        appearance_row = ctk.CTkFrame(appearance_section, fg_color="transparent")
        appearance_row.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(appearance_row, text="Theme:").pack(side="left", padx=10)
        ctk.CTkOptionMenu(
            appearance_row,
            values=["Dark", "Light", "System"],
            command=self.change_appearance_mode
        ).pack(side="left", padx=10)

        # Database settings
        db_section = ctk.CTkFrame(settings_frame)
        db_section.pack(fill="x", padx=20, pady=20)

        ctk.CTkLabel(
            db_section,
            text="Database",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=10, pady=10)

        db_info = ctk.CTkLabel(
            db_section,
            text="Database: privacy_deletion_db (PostgreSQL)\nAll data is stored locally on your machine.",
            text_color="gray"
        )
        db_info.pack(anchor="w", padx=10, pady=5)

    # Action functions
    def add_account_dialog(self):
        """Show dialog to add a new account."""
        dialog = ctk.CTkInputDialog(
            text="Enter your Gmail address:",
            title="Add Gmail Account"
        )
        email = dialog.get_input()

        if email:
            self.log_message(f"Authenticating {email}...")
            threading.Thread(target=self.add_account_thread, args=(email,), daemon=True).start()

    def add_account_thread(self, email):
        """Add account in background thread."""
        try:
            service = self.gmail_auth.authenticate(email)
            if service:
                self.account_manager.add_account(email, 'gmail')
                self.after(0, lambda: self.log_message(f"✓ Account {email} added successfully!"))
                self.after(0, self.refresh_accounts)
            else:
                self.after(0, lambda: self.show_error("Authentication Failed", f"Could not authenticate {email}"))
        except Exception as e:
            self.after(0, lambda: self.show_error("Error", str(e)))

    def remove_account(self, email):
        """Remove an account."""
        if self.ask_yes_no("Confirm Removal", f"Remove account {email}?\nThis will also delete all associated requests."):
            self.account_manager.remove_account(email)
            self.gmail_auth.revoke_access(email)
            self.refresh_accounts()
            self.show_accounts()

    def start_scan(self, email, max_results, start_year):
        """Start scanning for companies."""
        self.scan_results.delete("1.0", "end")
        self.log_scan(f"Starting scan for {email}...\n")
        threading.Thread(
            target=self.scan_thread,
            args=(email, max_results, start_year),
            daemon=True
        ).start()

    def scan_thread(self, email, max_results, start_year):
        """Scan in background thread."""
        try:
            service = self.gmail_auth.authenticate(email)
            scanner = EmailScanner(service)
            domains = scanner.discover_companies(max_results, start_year)
            stats = self.company_manager.bulk_add_companies(domains)

            self.after(0, lambda: self.log_scan(f"\n✓ Scan complete!\n"))
            self.after(0, lambda: self.log_scan(f"Found: {len(domains)} companies\n"))
            self.after(0, lambda: self.log_scan(f"New: {stats['added']}, Existing: {stats['existed']}\n"))
        except Exception as e:
            self.after(0, lambda: self.show_error("Scan Error", str(e)))

    def start_contact_finding(self):
        """Start finding privacy contacts."""
        self.contact_results.delete("1.0", "end")
        self.log_contact("Finding privacy contacts...\n")
        threading.Thread(target=self.contact_finding_thread, daemon=True).start()

    def contact_finding_thread(self):
        """Find contacts in background thread."""
        try:
            companies = self.company_manager.get_companies_without_contacts()
            self.after(0, lambda: self.log_contact(f"Found {len(companies)} companies without contacts\n"))

            domains = [c['domain'] for c in companies]
            results = self.contact_finder.batch_find_contacts(domains, verbose=False)

            found = 0
            for domain, contact in results.items():
                if contact:
                    self.company_manager.update_privacy_contact(domain, contact['contact'], contact['type'])
                    self.after(0, lambda d=domain, c=contact: self.log_contact(
                        f"✓ {d}: {c['contact']} (confidence: {c['confidence']})\n"
                    ))
                    found += 1

            self.after(0, lambda: self.log_contact(f"\n✓ Complete! Found {found}/{len(domains)} contacts\n"))
        except Exception as e:
            self.after(0, lambda: self.show_error("Contact Finding Error", str(e)))

    def start_sending_requests(self, email, template_type):
        """Start sending deletion requests."""
        self.request_results.delete("1.0", "end")
        self.log_request(f"Sending requests from {email}...\n")
        threading.Thread(target=self.send_requests_thread, args=(email, template_type), daemon=True).start()

    def send_requests_thread(self, email, template_type):
        """Send requests in background thread."""
        try:
            account = self.account_manager.get_account(email)
            if not account:
                self.after(0, lambda: self.show_error("Error", "Account not found"))
                return

            request_sender = RequestSender(email)
            companies = self.company_manager.get_companies_with_contacts_ready_for_request(account['id'])

            self.after(0, lambda: self.log_request(f"Found {len(companies)} companies to send to\n"))

            sent = 0
            for company in companies:
                success = request_sender.send_deletion_request(
                    company['id'],
                    account['id'],
                    company['domain'],
                    template_type
                )
                if success:
                    sent += 1
                    self.after(0, lambda d=company['domain']: self.log_request(f"✓ Sent to {d}\n"))
                time.sleep(1)  # Rate limiting

            self.after(0, lambda: self.log_request(f"\n✓ Sent {sent} requests!\n"))
        except Exception as e:
            self.after(0, lambda: self.show_error("Send Error", str(e)))

    def start_checking_replies(self):
        """Start checking for replies."""
        self.reply_results.delete("1.0", "end")
        self.log_reply("Checking for replies...\n")
        threading.Thread(target=self.check_replies_thread, daemon=True).start()

    def check_replies_thread(self):
        """Check replies in background thread."""
        try:
            accounts = self.account_manager.get_all_accounts()
            total_found = 0
            total_updated = 0

            for account in accounts:
                tracker = ReplyTracker(account['email_address'])
                results = tracker.check_for_replies(account['id'])
                total_found += results['found']
                total_updated += results['updated']

                self.after(0, lambda e=account['email_address'], r=results: self.log_reply(
                    f"{e}: {r['found']} replies, {r['updated']} updated\n"
                ))

            self.after(0, lambda: self.log_reply(
                f"\n✓ Total: {total_found} replies, {total_updated} requests updated\n"
            ))
        except Exception as e:
            self.after(0, lambda: self.show_error("Reply Check Error", str(e)))

    # Helper functions
    def log_message(self, message):
        """Log a message to the console."""
        logger.info(message)

    def log_scan(self, message):
        """Log to scan results."""
        self.scan_results.insert("end", message)
        self.scan_results.see("end")

    def log_contact(self, message):
        """Log to contact results."""
        self.contact_results.insert("end", message)
        self.contact_results.see("end")

    def log_request(self, message):
        """Log to request results."""
        self.request_results.insert("end", message)
        self.request_results.see("end")

    def log_reply(self, message):
        """Log to reply results."""
        self.reply_results.insert("end", message)
        self.reply_results.see("end")

    def refresh_accounts(self):
        """Refresh the accounts list."""
        accounts = self.account_manager.get_all_accounts()
        if accounts:
            self.current_account = accounts[0]['email_address']

    def change_appearance_mode(self, new_mode):
        """Change the appearance mode."""
        ctk.set_appearance_mode(new_mode)

    def show_error(self, title, message):
        """Show an error dialog."""
        error_window = ctk.CTkToplevel(self)
        error_window.title(title)
        error_window.geometry("400x200")

        ctk.CTkLabel(
            error_window,
            text=title,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="red"
        ).pack(pady=20)

        ctk.CTkLabel(error_window, text=message, wraplength=350).pack(pady=10)

        ctk.CTkButton(
            error_window,
            text="OK",
            command=error_window.destroy
        ).pack(pady=20)

    def ask_yes_no(self, title, message):
        """Show a yes/no dialog."""
        dialog = ctk.CTkInputDialog(text=f"{message}\n\nType 'yes' to confirm:", title=title)
        response = dialog.get_input()
        return response and response.lower() == 'yes'


def main():
    """Main entry point for the GUI application."""
    print("="*60)
    print("Privacy Data Deletion Tool - Desktop GUI")
    print("="*60)
    print("\nStarting graphical interface...")

    app = PrivacyToolGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
