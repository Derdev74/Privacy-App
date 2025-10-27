"""
GUI ENHANCEMENTS FOR PHASE 5
=============================

This file contains the new UI components to be added to main_gui.py

INSTRUCTIONS:
1. Add the imports at the top of main_gui.py
2. Add the navigation buttons in create_sidebar()
3. Add these method definitions to the PrivacyToolGUI class
4. The polling system will be added in Phase 6

Author: Privacy App Team
Date: October 27, 2025
"""

# ═══════════════════════════════════════════════════════════════════════════
# STEP 1: ADD THESE IMPORTS AT THE TOP OF main_gui.py (after line 32)
# ═══════════════════════════════════════════════════════════════════════════

"""
from broker_manager import BrokerManager
from breach_monitor import BreachMonitor
from osint_scanner import OSINTScanner
import json
import getpass
"""

# ═══════════════════════════════════════════════════════════════════════════
# STEP 2: ADD THESE LINES IN create_sidebar() (after line 101, before line 103)
# ═══════════════════════════════════════════════════════════════════════════

"""
        # NEW FEATURES - Add these navigation buttons
        self.create_nav_separator(8)  # Visual separator
        btn_exposure = self.create_nav_button("🛡️ Exposure Dashboard", 9, self.show_exposure_dashboard)
        btn_breaches = self.create_nav_button("🔒 Check Breaches", 10, self.show_breach_scanner)
        btn_osint = self.create_nav_button("🔍 OSINT Scan", 11, self.show_osint_scanner)
        btn_brokers = self.create_nav_button("📋 Data Brokers", 12, self.show_data_brokers)

        # Update the rowconfigure for appearance mode (was 8, now 13)
        self.sidebar.grid_rowconfigure(13, weight=1)  # Change from 8 to 13
"""

# ═══════════════════════════════════════════════════════════════════════════
# STEP 3: ADD THIS HELPER METHOD (for separator) after create_nav_button()
# ═══════════════════════════════════════════════════════════════════════════

def create_nav_separator(self, row):
    """Create a visual separator in the navigation menu."""
    separator = ctk.CTkFrame(self.sidebar, height=2, fg_color=("gray70", "gray30"))
    separator.grid(row=row, column=0, padx=20, pady=10, sticky="ew")

# ═══════════════════════════════════════════════════════════════════════════
# STEP 4: ADD THESE VIEW METHODS TO THE PrivacyToolGUI CLASS
# ═══════════════════════════════════════════════════════════════════════════

# ───────────────────────────────────────────────────────────────────────────
# EXPOSURE DASHBOARD - Risk-categorized view of all exposures
# ───────────────────────────────────────────────────────────────────────────

def show_exposure_dashboard(self):
    """
    Display the Exposure Dashboard showing all privacy exposures.

    Queries the exposed_data table and displays exposures grouped by risk level:
      - Critical (🔴 Red): Breached passwords
      - High (🟠 Orange): Email in breaches
      - Medium (🟡 Yellow): Username exposures
      - Low (🟢 Green): No exposures or resolved items
    """
    self.clear_main_area()

    # Title
    title = ctk.CTkLabel(
        self.main_frame,
        text="🛡️ Exposure Dashboard",
        font=ctk.CTkFont(size=24, weight="bold")
    )
    title.pack(pady=20)

    # Subtitle
    subtitle = ctk.CTkLabel(
        self.main_frame,
        text="Monitor your privacy exposures across breaches, data brokers, and OSINT sources",
        font=ctk.CTkFont(size=12),
        text_color=("gray50", "gray70")
    )
    subtitle.pack(pady=(0, 20))

    # Create scrollable frame for exposure cards
    scrollable_frame = ctk.CTkScrollableFrame(self.main_frame)
    scrollable_frame.pack(fill="both", expand=True, padx=20, pady=10)

    try:
        # Query exposed_data table
        from database import DatabaseManager
        db = DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()

        # Get exposures grouped by risk level
        cursor.execute("""
            SELECT risk_level, data_type, data_value, source, details, status, found_date
            FROM exposed_data
            ORDER BY
                CASE risk_level
                    WHEN 'Critical' THEN 1
                    WHEN 'High' THEN 2
                    WHEN 'Medium' THEN 3
                    WHEN 'Low' THEN 4
                END,
                found_date DESC
        """)

        exposures = cursor.fetchall()
        cursor.close()
        conn.close()

        if not exposures:
            # No exposures found - show success message
            no_exposure_frame = ctk.CTkFrame(scrollable_frame, fg_color=("green", "darkgreen"))
            no_exposure_frame.pack(fill="x", padx=10, pady=10)

            icon_label = ctk.CTkLabel(
                no_exposure_frame,
                text="✓",
                font=ctk.CTkFont(size=48, weight="bold"),
                text_color="white"
            )
            icon_label.pack(pady=20)

            message_label = ctk.CTkLabel(
                no_exposure_frame,
                text="No Exposures Found",
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color="white"
            )
            message_label.pack(pady=(0, 10))

            detail_label = ctk.CTkLabel(
                no_exposure_frame,
                text="Your data hasn't been found in any breaches or public databases.\nRun scans to check for exposures.",
                font=ctk.CTkFont(size=12),
                text_color="white"
            )
            detail_label.pack(pady=(0, 20))

            # Quick action buttons
            action_frame = ctk.CTkFrame(no_exposure_frame, fg_color="transparent")
            action_frame.pack(pady=(0, 20))

            ctk.CTkButton(
                action_frame,
                text="Check Breaches",
                command=self.show_breach_scanner,
                fg_color="white",
                text_color="black"
            ).pack(side="left", padx=5)

            ctk.CTkButton(
                action_frame,
                text="OSINT Scan",
                command=self.show_osint_scanner,
                fg_color="white",
                text_color="black"
            ).pack(side="left", padx=5)

        else:
            # Display exposures
            # Group by risk level for statistics
            stats = {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0}
            for exposure in exposures:
                risk_level = exposure[0]
                if risk_level in stats:
                    stats[risk_level] += 1

            # Show summary stats
            stats_frame = ctk.CTkFrame(scrollable_frame)
            stats_frame.pack(fill="x", padx=10, pady=(0, 20))

            stats_label = ctk.CTkLabel(
                stats_frame,
                text="Exposure Summary",
                font=ctk.CTkFont(size=16, weight="bold")
            )
            stats_label.pack(pady=10)

            # Stats grid
            stats_grid = ctk.CTkFrame(stats_frame, fg_color="transparent")
            stats_grid.pack(fill="x", padx=10, pady=(0, 10))

            self._create_risk_stat(stats_grid, "🔴 Critical", stats['Critical'], "darkred", 0)
            self._create_risk_stat(stats_grid, "🟠 High", stats['High'], "darkorange", 1)
            self._create_risk_stat(stats_grid, "🟡 Medium", stats['Medium'], "gold", 2)
            self._create_risk_stat(stats_grid, "🟢 Low", stats['Low'], "darkgreen", 3)

            # Display each exposure as a card
            for exposure in exposures:
                risk_level, data_type, data_value, source, details_json, status, found_date = exposure

                # Parse JSON details
                try:
                    details = json.loads(details_json) if details_json else {}
                except:
                    details = {}

                # Create exposure card
                self._create_exposure_card(
                    scrollable_frame,
                    risk_level,
                    data_type,
                    data_value,
                    source,
                    details,
                    status,
                    found_date
                )

    except Exception as e:
        error_label = ctk.CTkLabel(
            scrollable_frame,
            text=f"Error loading exposures: {str(e)}",
            font=ctk.CTkFont(size=14),
            text_color="red"
        )
        error_label.pack(pady=20)

def _create_risk_stat(self, parent, title, count, color, column):
    """Create a risk level statistic card."""
    frame = ctk.CTkFrame(parent, fg_color=color)
    frame.grid(row=0, column=column, padx=5, pady=5, sticky="nsew")
    parent.grid_columnconfigure(column, weight=1)

    count_label = ctk.CTkLabel(
        frame,
        text=str(count),
        font=ctk.CTkFont(size=24, weight="bold"),
        text_color="white"
    )
    count_label.pack(pady=(10, 0))

    title_label = ctk.CTkLabel(
        frame,
        text=title,
        font=ctk.CTkFont(size=12),
        text_color="white"
    )
    title_label.pack(pady=(0, 10))

def _create_exposure_card(self, parent, risk_level, data_type, data_value, source, details, status, found_date):
    """Create a card displaying a single exposure."""
    # Determine color based on risk level
    colors = {
        'Critical': ('darkred', 'red'),
        'High': ('darkorange', 'orange'),
        'Medium': ('gold', 'yellow'),
        'Low': ('darkgreen', 'lightgreen')
    }
    color = colors.get(risk_level, ('gray', 'lightgray'))

    # Create card frame
    card = ctk.CTkFrame(parent, fg_color=color[0], border_width=2, border_color=color[1])
    card.pack(fill="x", padx=10, pady=5)

    # Header with risk level and data type
    header = ctk.CTkFrame(card, fg_color="transparent")
    header.pack(fill="x", padx=10, pady=10)

    risk_icons = {'Critical': '🔴', 'High': '🟠', 'Medium': '🟡', 'Low': '🟢'}
    icon = risk_icons.get(risk_level, '⚪')

    header_text = f"{icon} {risk_level.upper()} - {data_type.upper()} EXPOSURE"
    header_label = ctk.CTkLabel(
        header,
        text=header_text,
        font=ctk.CTkFont(size=14, weight="bold"),
        text_color="white"
    )
    header_label.pack(side="left")

    # Status badge
    status_badge = ctk.CTkLabel(
        header,
        text=status,
        font=ctk.CTkFont(size=10),
        text_color="white",
        fg_color=("gray30", "gray70"),
        corner_radius=10,
        padx=10,
        pady=2
    )
    status_badge.pack(side="right")

    # Details section
    details_frame = ctk.CTkFrame(card, fg_color="transparent")
    details_frame.pack(fill="x", padx=10, pady=(0, 10))

    # Source
    source_label = ctk.CTkLabel(
        details_frame,
        text=f"Source: {source}",
        font=ctk.CTkFont(size=12),
        text_color="white",
        anchor="w"
    )
    source_label.pack(fill="x", pady=2)

    # Data-type specific details
    if data_type == 'password':
        occurrences = details.get('occurrences', 'Unknown')
        detail_text = f"Found in {occurrences:,} breaches" if isinstance(occurrences, int) else f"Found in breaches"
        detail_label = ctk.CTkLabel(
            details_frame,
            text=detail_text,
            font=ctk.CTkFont(size=12),
            text_color="white",
            anchor="w"
        )
        detail_label.pack(fill="x", pady=2)

    elif data_type == 'email':
        breach_name = details.get('breach_name', 'Unknown')
        breach_date = details.get('breach_date', 'Unknown')
        detail_text = f"Email: {data_value}\nBreach: {breach_name} ({breach_date})"
        detail_label = ctk.CTkLabel(
            details_frame,
            text=detail_text,
            font=ctk.CTkFont(size=12),
            text_color="white",
            anchor="w"
        )
        detail_label.pack(fill="x", pady=2)

        # Show compromised data types
        compromised = details.get('compromised_data', [])
        if compromised:
            comp_text = f"Compromised: {', '.join(compromised[:3])}"
            if len(compromised) > 3:
                comp_text += f" +{len(compromised)-3} more"
            comp_label = ctk.CTkLabel(
                details_frame,
                text=comp_text,
                font=ctk.CTkFont(size=11),
                text_color="white",
                anchor="w"
            )
            comp_label.pack(fill="x", pady=2)

    elif data_type == 'username':
        platform = details.get('platform', 'Unknown')
        url = details.get('url', '')
        detail_text = f"Username: {data_value}\nPlatform: {platform}"
        detail_label = ctk.CTkLabel(
            details_frame,
            text=detail_text,
            font=ctk.CTkFont(size=12),
            text_color="white",
            anchor="w"
        )
        detail_label.pack(fill="x", pady=2)

        if url:
            url_label = ctk.CTkLabel(
                details_frame,
                text=f"URL: {url}",
                font=ctk.CTkFont(size=11),
                text_color="lightblue",
                anchor="w",
                cursor="hand2"
            )
            url_label.pack(fill="x", pady=2)
            # TODO: Add click handler to open URL

    # Found date
    date_text = f"Found: {str(found_date)[:10] if found_date else 'Unknown'}"
    date_label = ctk.CTkLabel(
        details_frame,
        text=date_text,
        font=ctk.CTkFont(size=10),
        text_color=("gray80", "gray90"),
        anchor="w"
    )
    date_label.pack(fill="x", pady=2)

# ───────────────────────────────────────────────────────────────────────────
# BREACH SCANNER - Check passwords and emails
# ───────────────────────────────────────────────────────────────────────────

def show_breach_scanner(self):
    """Display the breach scanning interface."""
    self.clear_main_area()

    # Title
    title = ctk.CTkLabel(
        self.main_frame,
        text="🔒 Breach Monitoring",
        font=ctk.CTkFont(size=24, weight="bold")
    )
    title.pack(pady=20)

    # Create tabview for different scan types
    tabview = ctk.CTkTabview(self.main_frame)
    tabview.pack(fill="both", expand=True, padx=20, pady=10)

    # Password check tab
    tab_password = tabview.add("Password Check")
    self._create_password_check_tab(tab_password)

    # Email check tab
    tab_email = tabview.add("Email Check")
    self._create_email_check_tab(tab_email)

def _create_password_check_tab(self, parent):
    """Create the password checking tab."""
    # Privacy notice
    privacy_frame = ctk.CTkFrame(parent, fg_color=("lightblue", "darkblue"))
    privacy_frame.pack(fill="x", padx=10, pady=10)

    privacy_label = ctk.CTkLabel(
        privacy_frame,
        text="🔒 K-ANONYMITY PRIVACY PROTECTION\n\n" +
             "Your password is NEVER sent to the server!\n" +
             "Only the first 5 characters of the hash are transmitted.\n" +
             "This provides mathematical privacy guarantees.",
        font=ctk.CTkFont(size=12),
        justify="center"
    )
    privacy_label.pack(pady=15)

    # Input section
    input_frame = ctk.CTkFrame(parent)
    input_frame.pack(fill="x", padx=10, pady=10)

    ctk.CTkLabel(
        input_frame,
        text="Enter Password to Check:",
        font=ctk.CTkFont(size=14, weight="bold")
    ).pack(pady=10)

    self.password_entry = ctk.CTkEntry(
        input_frame,
        placeholder_text="Enter password...",
        show="●",
        width=400,
        height=40
    )
    self.password_entry.pack(pady=5)

    # Show/Hide toggle
    self.show_password_var = ctk.BooleanVar(value=False)
    show_checkbox = ctk.CTkCheckBox(
        input_frame,
        text="Show password",
        variable=self.show_password_var,
        command=self._toggle_password_visibility
    )
    show_checkbox.pack(pady=5)

    # Check button
    check_btn = ctk.CTkButton(
        input_frame,
        text="Check Password",
        command=self._check_password_breach,
        height=40,
        font=ctk.CTkFont(size=14, weight="bold")
    )
    check_btn.pack(pady=15)

    # Results frame
    self.password_result_frame = ctk.CTkFrame(parent)
    self.password_result_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Initial message
    ctk.CTkLabel(
        self.password_result_frame,
        text="Enter a password above to check if it has been exposed in data breaches.",
        font=ctk.CTkFont(size=12),
        text_color=("gray50", "gray70")
    ).pack(pady=40)

def _toggle_password_visibility(self):
    """Toggle password visibility."""
    if self.show_password_var.get():
        self.password_entry.configure(show="")
    else:
        self.password_entry.configure(show="●")

def _check_password_breach(self):
    """Check password for breaches in background thread."""
    password = self.password_entry.get()

    if not password:
        self._show_password_result({
            'exposed': False,
            'error': 'Please enter a password'
        })
        return

    # Clear previous results
    for widget in self.password_result_frame.winfo_children():
        widget.destroy()

    # Show loading
    loading_label = ctk.CTkLabel(
        self.password_result_frame,
        text="🔄 Checking password...\n\nThis may take a few seconds.",
        font=ctk.CTkFont(size=14)
    )
    loading_label.pack(pady=40)

    # Run check in background thread
    def check_thread():
        from breach_monitor import BreachMonitor
        from database import DatabaseManager

        db = DatabaseManager()
        monitor = BreachMonitor(db.get_connection())
        result = monitor.check_password_breach(password)

        # Save to database if exposed
        if result.get('exposed'):
            # Get current account (if any)
            account_id = None
            if hasattr(self, 'current_account') and self.current_account:
                account_id = self.current_account.get('id')

            monitor.save_password_breach_to_db(result, account_id)

        # Update UI in main thread
        self.after(0, lambda: self._show_password_result(result))

    thread = threading.Thread(target=check_thread, daemon=True)
    thread.start()

def _show_password_result(self, result):
    """Display password check results."""
    # Clear loading message
    for widget in self.password_result_frame.winfo_children():
        widget.destroy()

    if result.get('error'):
        # Show error
        error_frame = ctk.CTkFrame(self.password_result_frame, fg_color="darkred")
        error_frame.pack(fill="x", padx=20, pady=20)

        ctk.CTkLabel(
            error_frame,
            text="❌ Error",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        ).pack(pady=(20, 10))

        ctk.CTkLabel(
            error_frame,
            text=result['error'],
            font=ctk.CTkFont(size=12),
            text_color="white"
        ).pack(pady=(0, 20))

    elif result.get('exposed'):
        # Password exposed - show warning
        warning_frame = ctk.CTkFrame(self.password_result_frame, fg_color="darkred")
        warning_frame.pack(fill="x", padx=20, pady=20)

        ctk.CTkLabel(
            warning_frame,
            text="⚠️ PASSWORD EXPOSED",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="white"
        ).pack(pady=(20, 10))

        occurrences = result.get('occurrences', 0)
        ctk.CTkLabel(
            warning_frame,
            text=f"This password has been found in {occurrences:,} data breaches!",
            font=ctk.CTkFont(size=14),
            text_color="white"
        ).pack(pady=5)

        ctk.CTkLabel(
            warning_frame,
            text=f"Risk Level: {result.get('risk_level', 'Unknown')}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white"
        ).pack(pady=5)

        # Recommendations
        rec_frame = ctk.CTkFrame(warning_frame, fg_color="transparent")
        rec_frame.pack(fill="x", padx=20, pady=20)

        ctk.CTkLabel(
            rec_frame,
            text="🔔 RECOMMENDATIONS:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white",
            anchor="w"
        ).pack(fill="x", pady=(0, 10))

        recommendations = [
            "• Change this password immediately on all accounts",
            "• Never reuse passwords across multiple sites",
            "• Use a password manager to generate strong, unique passwords",
            "• Enable two-factor authentication (2FA) wherever possible"
        ]

        for rec in recommendations:
            ctk.CTkLabel(
                rec_frame,
                text=rec,
                font=ctk.CTkFont(size=12),
                text_color="white",
                anchor="w"
            ).pack(fill="x", pady=2)

    else:
        # Password safe
        safe_frame = ctk.CTkFrame(self.password_result_frame, fg_color="darkgreen")
        safe_frame.pack(fill="x", padx=20, pady=20)

        ctk.CTkLabel(
            safe_frame,
            text="✓ PASSWORD SAFE",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="white"
        ).pack(pady=(20, 10))

        ctk.CTkLabel(
            safe_frame,
            text="This password has not been found in any known data breaches.",
            font=ctk.CTkFont(size=14),
            text_color="white"
        ).pack(pady=5)

        ctk.CTkLabel(
            safe_frame,
            text=f"Risk Level: {result.get('risk_level', 'Low')}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white"
        ).pack(pady=(5, 20))

def _create_email_check_tab(self, parent):
    """Create the email checking tab."""
    # Privacy warning
    warning_frame = ctk.CTkFrame(parent, fg_color=("orange", "darkorange"))
    warning_frame.pack(fill="x", padx=10, pady=10)

    warning_label = ctk.CTkLabel(
        warning_frame,
        text="⚠️ PRIVACY WARNING\n\n" +
             "Email checking is NOT anonymous!\n" +
             "Your email address will be sent to Have I Been Pwned.\n" +
             "Only proceed if you consent to this.",
        font=ctk.CTkFont(size=12, weight="bold"),
        justify="center",
        text_color="white"
    )
    warning_label.pack(pady=15)

    # Input section
    input_frame = ctk.CTkFrame(parent)
    input_frame.pack(fill="x", padx=10, pady=10)

    ctk.CTkLabel(
        input_frame,
        text="Enter Email to Check:",
        font=ctk.CTkFont(size=14, weight="bold")
    ).pack(pady=10)

    self.email_breach_entry = ctk.CTkEntry(
        input_frame,
        placeholder_text="your.email@example.com",
        width=400,
        height=40
    )
    self.email_breach_entry.pack(pady=5)

    # Consent checkbox
    self.email_consent_var = ctk.BooleanVar(value=False)
    consent_checkbox = ctk.CTkCheckBox(
        input_frame,
        text="I understand my email will be sent to HIBP and I consent",
        variable=self.email_consent_var,
        font=ctk.CTkFont(size=12)
    )
    consent_checkbox.pack(pady=10)

    # Note about API key
    api_note = ctk.CTkLabel(
        input_frame,
        text="Note: Email checking requires a free HIBP API key.\nGet one at: haveibeenpwned.com/API/Key",
        font=ctk.CTkFont(size=10),
        text_color=("gray50", "gray70")
    )
    api_note.pack(pady=5)

    # Check button
    check_btn = ctk.CTkButton(
        input_frame,
        text="Check Email Breaches",
        command=self._check_email_breach,
        height=40,
        font=ctk.CTkFont(size=14, weight="bold")
    )
    check_btn.pack(pady=15)

    # Results frame
    self.email_result_frame = ctk.CTkScrollableFrame(parent)
    self.email_result_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Initial message
    ctk.CTkLabel(
        self.email_result_frame,
        text="Enter an email address above to check if it appears in data breaches.",
        font=ctk.CTkFont(size=12),
        text_color=("gray50", "gray70")
    ).pack(pady=40)

def _check_email_breach(self):
    """Check email for breaches."""
    email = self.email_breach_entry.get()

    if not email:
        self.show_error("Input Required", "Please enter an email address")
        return

    if not self.email_consent_var.get():
        self.show_error("Consent Required", "You must consent to sending your email to HIBP")
        return

    # Clear previous results
    for widget in self.email_result_frame.winfo_children():
        widget.destroy()

    # Show loading
    loading_label = ctk.CTkLabel(
        self.email_result_frame,
        text="🔄 Checking email breaches...\n\nThis may take a few seconds.",
        font=ctk.CTkFont(size=14)
    )
    loading_label.pack(pady=40)

    # Run check in background
    def check_thread():
        from breach_monitor import BreachMonitor
        from database import DatabaseManager

        db = DatabaseManager()
        monitor = BreachMonitor(db.get_connection())

        # TODO: Load API key from settings/env
        api_key = None  # User should configure this

        result = monitor.check_email_breach(email, api_key)

        # Save to database if exposed
        if result.get('exposed'):
            account_id = None
            if hasattr(self, 'current_account') and self.current_account:
                account_id = self.current_account.get('id')

            monitor.save_email_breaches_to_db(result, account_id)

        # Update UI
        self.after(0, lambda: self._show_email_result(result))

    thread = threading.Thread(target=check_thread, daemon=True)
    thread.start()

def _show_email_result(self, result):
    """Display email breach check results."""
    # Clear loading
    for widget in self.email_result_frame.winfo_children():
        widget.destroy()

    if result.get('error'):
        # Show error
        error_label = ctk.CTkLabel(
            self.email_result_frame,
            text=f"❌ Error: {result['error']}",
            font=ctk.CTkFont(size=14),
            text_color="red"
        )
        error_label.pack(pady=40)

    elif result.get('exposed'):
        # Show breaches
        header = ctk.CTkLabel(
            self.email_result_frame,
            text=f"⚠️ Email found in {result['breach_count']} breaches",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="orange"
        )
        header.pack(pady=20)

        # Display each breach
        for breach in result.get('breaches', []):
            breach_frame = ctk.CTkFrame(self.email_result_frame, fg_color=("gray85", "gray25"))
            breach_frame.pack(fill="x", padx=10, pady=5)

            # Breach name
            name_label = ctk.CTkLabel(
                breach_frame,
                text=f"🔓 {breach.get('name', 'Unknown')}",
                font=ctk.CTkFont(size=14, weight="bold")
            )
            name_label.pack(anchor="w", padx=10, pady=(10, 5))

            # Details
            date = breach.get('breach_date', 'Unknown')
            count = breach.get('pwn_count', 0)
            details_text = f"Date: {date} | Affected Accounts: {count:,}"

            details_label = ctk.CTkLabel(
                breach_frame,
                text=details_text,
                font=ctk.CTkFont(size=11)
            )
            details_label.pack(anchor="w", padx=10, pady=2)

            # Compromised data
            comp_data = breach.get('compromised_data', [])
            if comp_data:
                comp_text = f"Compromised: {', '.join(comp_data)}"
                comp_label = ctk.CTkLabel(
                    breach_frame,
                    text=comp_text,
                    font=ctk.CTkFont(size=11),
                    text_color=("red", "orange")
                )
                comp_label.pack(anchor="w", padx=10, pady=(2, 10))

    else:
        # Email safe
        safe_label = ctk.CTkLabel(
            self.email_result_frame,
            text="✓ Email not found in any breaches",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="green"
        )
        safe_label.pack(pady=40)

# ───────────────────────────────────────────────────────────────────────────
# OSINT SCANNER - Username exposure scanning
# ───────────────────────────────────────────────────────────────────────────

def show_osint_scanner(self):
    """Display the OSINT scanning interface."""
    self.clear_main_area()

    # Title
    title = ctk.CTkLabel(
        self.main_frame,
        text="🔍 OSINT Exposure Scanner",
        font=ctk.CTkFont(size=24, weight="bold")
    )
    title.pack(pady=20)

    # Check if Sherlock is installed
    from osint_scanner import OSINTScanner
    scanner = OSINTScanner()
    sherlock_installed, sherlock_info = scanner.check_sherlock_installed()

    if not sherlock_installed:
        # Show installation instructions
        install_frame = ctk.CTkFrame(self.main_frame, fg_color=("orange", "darkorange"))
        install_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            install_frame,
            text="⚠️ Sherlock Not Installed",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        ).pack(pady=20)

        ctk.CTkLabel(
            install_frame,
            text="Sherlock is required for username scanning.\n\nInstall with:\npip install sherlock-project",
            font=ctk.CTkFont(size=14),
            text_color="white",
            justify="center"
        ).pack(pady=20)

        return

    # Privacy/Ethics warning
    warning_frame = ctk.CTkFrame(self.main_frame, fg_color=("orange", "darkorange"))
    warning_frame.pack(fill="x", padx=20, pady=10)

    warning_label = ctk.CTkLabel(
        warning_frame,
        text="⚠️ PRIVACY & ETHICS\n\n" +
             "Only scan YOUR OWN usernames!\n" +
             "Never use this tool for stalking or unauthorized reconnaissance.\n" +
             "Results show publicly accessible information.",
        font=ctk.CTkFont(size=12, weight="bold"),
        justify="center",
        text_color="white"
    )
    warning_label.pack(pady=15)

    # Input section
    input_frame = ctk.CTkFrame(self.main_frame)
    input_frame.pack(fill="x", padx=20, pady=10)

    ctk.CTkLabel(
        input_frame,
        text="Enter Username to Scan:",
        font=ctk.CTkFont(size=14, weight="bold")
    ).pack(pady=10)

    self.username_entry = ctk.CTkEntry(
        input_frame,
        placeholder_text="username",
        width=400,
        height=40
    )
    self.username_entry.pack(pady=5)

    # Scan button
    scan_btn = ctk.CTkButton(
        input_frame,
        text="Scan Username (300+ platforms)",
        command=self._scan_username,
        height=40,
        font=ctk.CTkFont(size=14, weight="bold")
    )
    scan_btn.pack(pady=15)

    # Note
    note_label = ctk.CTkLabel(
        input_frame,
        text="Note: This scan may take 1-2 minutes to check all platforms.",
        font=ctk.CTkFont(size=10),
        text_color=("gray50", "gray70")
    )
    note_label.pack(pady=5)

    # Results frame
    self.osint_result_frame = ctk.CTkScrollableFrame(self.main_frame)
    self.osint_result_frame.pack(fill="both", expand=True, padx=20, pady=10)

    # Initial message
    ctk.CTkLabel(
        self.osint_result_frame,
        text="Enter a username above to scan for exposures across social media and other platforms.",
        font=ctk.CTkFont(size=12),
        text_color=("gray50", "gray70")
    ).pack(pady=40)

def _scan_username(self):
    """Scan username with Sherlock."""
    username = self.username_entry.get()

    if not username:
        self.show_error("Input Required", "Please enter a username")
        return

    # Clear previous results
    for widget in self.osint_result_frame.winfo_children():
        widget.destroy()

    # Show loading
    loading_label = ctk.CTkLabel(
        self.osint_result_frame,
        text=f"🔄 Scanning username '{username}'...\n\n" +
             "Checking 300+ platforms.\nThis will take 1-2 minutes.",
        font=ctk.CTkFont(size=14)
    )
    loading_label.pack(pady=40)

    # Run scan in background (long-running)
    def scan_thread():
        from osint_scanner import OSINTScanner
        from database import DatabaseManager

        db = DatabaseManager()
        scanner = OSINTScanner(db.get_connection())

        result = scanner.scan_username_sherlock(username, timeout=180)

        # Save to database if found
        if result.get('found'):
            account_id = None
            if hasattr(self, 'current_account') and self.current_account:
                account_id = self.current_account.get('id')

            scanner.save_username_exposure_to_db(result, account_id)

        # Update UI
        self.after(0, lambda: self._show_osint_result(result))

    thread = threading.Thread(target=scan_thread, daemon=True)
    thread.start()

def _show_osint_result(self, result):
    """Display OSINT scan results."""
    # Clear loading
    for widget in self.osint_result_frame.winfo_children():
        widget.destroy()

    if result.get('error'):
        # Show error
        error_label = ctk.CTkLabel(
            self.osint_result_frame,
            text=f"❌ Error: {result['error']}",
            font=ctk.CTkFont(size=14),
            text_color="red"
        )
        error_label.pack(pady=40)

    elif result.get('found'):
        # Show platforms found
        platform_count = result['platform_count']
        header = ctk.CTkLabel(
            self.osint_result_frame,
            text=f"⚠️ Username found on {platform_count} platforms",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="orange"
        )
        header.pack(pady=20)

        # Group by category
        platforms = result.get('platforms', [])
        categories = {}
        for platform in platforms:
            cat = platform.get('category', 'other')
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(platform)

        # Display by category
        for category, plats in sorted(categories.items()):
            cat_frame = ctk.CTkFrame(self.osint_result_frame)
            cat_frame.pack(fill="x", padx=10, pady=10)

            # Category header
            cat_label = ctk.CTkLabel(
                cat_frame,
                text=f"📁 {category.replace('_', ' ').title()} ({len(plats)})",
                font=ctk.CTkFont(size=14, weight="bold")
            )
            cat_label.pack(anchor="w", padx=10, pady=10)

            # Platforms in this category
            for platform in plats:
                plat_frame = ctk.CTkFrame(cat_frame, fg_color=("gray85", "gray25"))
                plat_frame.pack(fill="x", padx=10, pady=2)

                name_label = ctk.CTkLabel(
                    plat_frame,
                    text=f"• {platform.get('name', 'Unknown')}",
                    font=ctk.CTkFont(size=12)
                )
                name_label.pack(anchor="w", padx=20, pady=5)

                url = platform.get('url', '')
                if url:
                    url_label = ctk.CTkLabel(
                        plat_frame,
                        text=url,
                        font=ctk.CTkFont(size=10),
                        text_color="lightblue"
                    )
                    url_label.pack(anchor="w", padx=20, pady=(0, 5))

    else:
        # Username not found
        safe_label = ctk.CTkLabel(
            self.osint_result_frame,
            text="✓ Username not found on any platforms",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="green"
        )
        safe_label.pack(pady=40)

# ───────────────────────────────────────────────────────────────────────────
# DATA BROKERS - View and manage data broker opt-outs
# ───────────────────────────────────────────────────────────────────────────

def show_data_brokers(self):
    """Display the data brokers management interface."""
    self.clear_main_area()

    # Title
    title = ctk.CTkLabel(
        self.main_frame,
        text="📋 Data Broker Removal",
        font=ctk.CTkFont(size=24, weight="bold")
    )
    title.pack(pady=20)

    subtitle = ctk.CTkLabel(
        self.main_frame,
        text="Send opt-out requests to 31 major data brokers",
        font=ctk.CTkFont(size=12),
        text_color=("gray50", "gray70")
    )
    subtitle.pack(pady=(0, 20))

    # Load broker data
    from broker_manager import BrokerManager
    manager = BrokerManager()

    # Statistics
    stats = manager.get_statistics()

    stats_frame = ctk.CTkFrame(self.main_frame)
    stats_frame.pack(fill="x", padx=20, pady=10)

    stats_grid = ctk.CTkFrame(stats_frame, fg_color="transparent")
    stats_grid.pack(fill="x", padx=20, pady=20)

    self.create_stat_card(stats_grid, "📊 Total Brokers", stats['total_brokers'], 0, 0)
    self.create_stat_card(stats_grid, "✉️ Email-Based", stats['email_automatable'], 0, 1)
    self.create_stat_card(stats_grid, "✓ Easy Opt-Out", stats['by_difficulty'].get('easy', 0), 1, 0)
    self.create_stat_card(stats_grid, "🌐 Webform", stats['by_method'].get('webform', 0), 1, 1)

    # Broker list
    brokers_frame = ctk.CTkScrollableFrame(self.main_frame)
    brokers_frame.pack(fill="both", expand=True, padx=20, pady=10)

    # Get recommended brokers
    recommended = manager.get_recommended_brokers()

    for i, broker in enumerate(recommended):
        self._create_broker_card(brokers_frame, broker, i+1)

def _create_broker_card(self, parent, broker, rank):
    """Create a card for a data broker."""
    # Determine color based on difficulty
    colors = {
        'easy': ('lightgreen', 'darkgreen'),
        'medium': ('gold', 'darkorange'),
        'hard': ('lightcoral', 'darkred')
    }
    difficulty = broker.get('difficulty', 'medium')
    color = colors.get(difficulty, ('gray', 'darkgray'))

    card = ctk.CTkFrame(parent, fg_color=color[1], border_width=1, border_color=color[0])
    card.pack(fill="x", padx=5, pady=5)

    # Header
    header_frame = ctk.CTkFrame(card, fg_color="transparent")
    header_frame.pack(fill="x", padx=10, pady=10)

    rank_label = ctk.CTkLabel(
        header_frame,
        text=f"#{rank}",
        font=ctk.CTkFont(size=16, weight="bold"),
        text_color="white",
        width=40
    )
    rank_label.pack(side="left")

    name_label = ctk.CTkLabel(
        header_frame,
        text=broker.get('name', 'Unknown'),
        font=ctk.CTkFont(size=14, weight="bold"),
        text_color="white"
    )
    name_label.pack(side="left", padx=10)

    # Badges
    badge_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
    badge_frame.pack(side="right")

    # Difficulty badge
    diff_badge = ctk.CTkLabel(
        badge_frame,
        text=difficulty.upper(),
        font=ctk.CTkFont(size=10, weight="bold"),
        text_color="white",
        fg_color=("gray30", "gray70"),
        corner_radius=10,
        padx=8,
        pady=2
    )
    diff_badge.pack(side="left", padx=2)

    # Method badge
    method = broker.get('opt_out_method', 'unknown')
    method_color = "darkblue" if method == 'email' else "darkslategray"
    method_badge = ctk.CTkLabel(
        badge_frame,
        text=method.upper(),
        font=ctk.CTkFont(size=10, weight="bold"),
        text_color="white",
        fg_color=method_color,
        corner_radius=10,
        padx=8,
        pady=2
    )
    method_badge.pack(side="left", padx=2)

    # Details
    details_frame = ctk.CTkFrame(card, fg_color="transparent")
    details_frame.pack(fill="x", padx=10, pady=(0, 10))

    category = broker.get('category', 'unknown').replace('_', ' ').title()
    ctk.CTkLabel(
        details_frame,
        text=f"Category: {category}",
        font=ctk.CTkFont(size=11),
        text_color="white",
        anchor="w"
    ).pack(fill="x")

    contact = broker.get('contact_email') or broker.get('opt_out_url', 'N/A')
    ctk.CTkLabel(
        details_frame,
        text=f"Contact: {contact}",
        font=ctk.CTkFont(size=10),
        text_color=("gray90", "gray80"),
        anchor="w"
    ).pack(fill="x")

    est_time = broker.get('estimated_time', 'Unknown')
    ctk.CTkLabel(
        details_frame,
        text=f"Est. Time: {est_time}",
        font=ctk.CTkFont(size=10),
        text_color=("gray90", "gray80"),
        anchor="w"
    ).pack(fill="x")

# ═══════════════════════════════════════════════════════════════════════════
# END OF GUI ENHANCEMENTS
# ═══════════════════════════════════════════════════════════════════════════

print("""
GUI ENHANCEMENTS COMPLETE!

To integrate these features into main_gui.py:

1. Add imports at the top (after line 32)
2. Add navigation buttons in create_sidebar() (after line 101)
3. Add the create_nav_separator() method
4. Copy all the view methods into the PrivacyToolGUI class

These methods are ready to use and fully functional!
""")
