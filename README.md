# 🔐 Privacy Data Deletion Tool

**Automate Your Data Deletion Rights Under GDPR & CCPA**

A local-first, privacy-preserving automation tool that helps you exercise your right to data deletion across hundreds of online services. 100% open source, 100% local - your data never leaves your machine.

---

## ✨ Features

### 🔍 **Automatic Company Discovery**
- Scans your Gmail inbox for signup/welcome emails
- Automatically extracts company domains
- Privacy-preserving: only reads email headers, never content
- Discovers hundreds of services you've signed up for over the years

### 📇 **Privacy Contact Finder**
- Automated web scraping to find privacy contact emails
- Checks common privacy policy pages (`/privacy`, `/gdpr`, `/data-protection`)
- Pattern matching for `privacy@`, `dpo@`, `gdpr@` email addresses
- 40-70% success rate for automatic discovery
- Manual entry interface for remaining companies

### 📤 **Automated Deletion Requests**
- Three email templates: GDPR (Article 17), CCPA, and Generic
- Batch sending with Gmail API integration
- Automatic rate limiting to avoid spam filters
- Customizable templates with company name substitution
- Professional, legally-informed language

### 📬 **Reply Tracking**
- Monitors email threads for company responses
- Automatic status categorization:
  - ✅ **COMPLETED**: Deletion confirmed
  - ⏳ **REPLIED**: Request acknowledged/in progress
  - ❓ **PENDING**: Awaiting response
- Keyword-based sentiment analysis
- Dashboard showing completion rates

### 🎨 **Dual Interface**
- **CLI Mode**: Fast, text-based terminal interface for power users
- **Desktop GUI**: Modern graphical interface with dark/light themes
- Interactive launcher - choose your preferred interface at startup

### 🔒 **Privacy & Security**
- **100% Local**: All data stored on your machine in PostgreSQL
- **Secure Token Storage**: OAuth tokens encrypted in OS keychain
- **No Telemetry**: Zero tracking, no external analytics
- **Open Source**: Fully auditable codebase
- **Metadata-Only Scanning**: the inbox scanner fetches headers only (sender, subject, date), never message bodies (see [Limitations](#-limitations-and-lessons))

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **PostgreSQL** (local installation)
- **Gmail Account** with API access enabled
- **Google Cloud Project** with Gmail API enabled

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Derdev74/Privacy-App.git
   cd Privacy-App
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure database**
   ```bash
   cp .env.example .env
   nano .env  # Add your PostgreSQL credentials
   ```

5. **Set up Google OAuth**
   - Create a project in [Google Cloud Console](https://console.cloud.google.com/)
   - Enable Gmail API
   - Create OAuth 2.0 credentials (Desktop app type)
   - Download credentials as JSON
   - Save to `config/google_credentials.json`

6. **Initialize database**
   ```bash
   python src/database.py
   ```

7. **Launch the application**
   ```bash
   python launcher.py
   ```

---

## 📖 Usage

### Option 1: Interactive Launcher (Recommended)

```bash
python launcher.py
```

Choose between CLI or GUI mode, then follow the interactive prompts.

### Option 2: Direct CLI Mode

```bash
python main.py
```

**Workflow:**
1. **Add Email Account** → Authenticate with Gmail OAuth
2. **Scan for Companies** → Discover services from your inbox
3. **Find Privacy Contacts** → Auto-detect + manual entry
4. **Send Deletion Requests** → Batch email sending
5. **Check for Replies** → Track responses and completion
6. **View Dashboard** → Statistics and progress

### Option 3: Desktop GUI Mode

```bash
python main_gui.py
```

Modern graphical interface with:
- Visual dashboard with statistics cards
- Dark/Light theme support
- Progress tracking with textbox outputs
- Click-through navigation

---

## 🎯 How It Works

### 1. **Email Scanning**
```
Your Gmail → Privacy Tool scans headers → Extracts sender domains → Stores in local database
```
- Uses Gmail API with `gmail.readonly` scope
- Optimized query: `from:(-me) AND ("welcome to" OR "verify your email"...)`
- Fetches only metadata (sender, subject, date) with `format='metadata'`
- The scanner never downloads message bodies. Note that the `gmail.readonly` scope would technically allow it (see [Limitations](#-limitations-and-lessons))

### 2. **Contact Discovery**
```
Domain list → Web scraper checks privacy pages → Extracts contact emails → Stores with confidence level
```
- Tries 11 common privacy page paths
- Pattern matches: `privacy@`, `dpo@`, `dataprotection@`, etc.
- Returns confidence level: high/medium/low
- Fallback to common email patterns if not found

### 3. **Deletion Requests**
```
Template selection → Generate personalized emails → Send via Gmail API → Log message IDs for tracking
```
- Professional templates cite GDPR Article 17 / CCPA
- Variable substitution: `{company_name}`, `{user_email}`, `{date}`
- Stores Gmail `threadId` for reply tracking
- 1-second delay between sends (rate limiting)

### 4. **Reply Monitoring**
```
Check Gmail threads → Analyze reply content → Categorize by keywords → Update status in database
```
- Reads the **full text of replies** in the threads of your deletion requests (and only those threads), to classify them
- Keyword matching:
  - "deleted", "removed" → **COMPLETED**
  - "received your request", "processing" → **REPLIED**
  - "verify", "additional information" → **VERIFICATION NEEDED**

---

## 📂 Project Structure

```
privacy-deletion-tool/
├── launcher.py              # Interactive interface launcher
├── main.py                  # CLI application
├── main_gui.py              # Desktop GUI application
├── requirements.txt         # Python dependencies
├── .env.example             # Database configuration template
├── config/
│   └── google_credentials.json  # OAuth credentials (user-provided)
├── src/
│   ├── database.py          # PostgreSQL manager
│   ├── logger.py            # Logging configuration
│   ├── auth_manager.py      # Secure token storage
│   ├── gmail_auth.py        # Gmail OAuth 2.0
│   ├── account_manager.py   # Account CRUD operations
│   ├── email_scanner.py     # Company discovery from emails
│   ├── company_manager.py   # Company database management
│   ├── contact_finder.py    # Web scraping for privacy contacts
│   ├── manual_contact.py    # Interactive manual entry CLI
│   ├── templates.py         # Email templates (GDPR/CCPA/Generic)
│   ├── request_sender.py    # Gmail API email sender
│   ├── reply_tracker.py     # Reply monitoring and categorization
│   └── utils.py             # Shared utilities and validators
├── logs/                    # Application logs (auto-created)
└── tests/                   # Test suite
```

---

## 🛡️ Privacy & Security

### Data Storage
- **PostgreSQL Database**: Stores companies, accounts, and request metadata locally
- **OS Keychain**: OAuth tokens encrypted using your OS's secure storage (Windows Credential Manager, macOS Keychain, Linux Secret Service)
- **No Cloud Services**: Zero external dependencies for data processing

### What Data Is Collected?
- Email addresses (yours, companies' privacy contacts)
- Company domains discovered from your inbox
- Request status (sent/replied/completed)
- Email metadata (message IDs, thread IDs, dates)

### What Data Is NEVER Collected?
- ❌ Body content of your other emails (only replies to your deletion requests are read)
- ❌ Personal conversations
- ❌ Passwords or payment information
- ❌ Telemetry or usage analytics

### OAuth Scopes
- `gmail.readonly`: read access to Gmail. The scanner uses it for headers only; the reply tracker uses it to read replies to your requests
- `gmail.send`: Send deletion request emails

**You can revoke access anytime** at [Google Account Permissions](https://myaccount.google.com/permissions)

---

## 🔧 Configuration

### Database (.env file)
```bash
DB_NAME=privacy_deletion_db
DB_USER=postgres
DB_PASSWORD=your_password_here
DB_HOST=localhost
DB_PORT=5432
```

### Google OAuth (config/google_credentials.json)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Gmail API
4. Create OAuth 2.0 Client ID
   - Application type: **Desktop app**
   - Download JSON credentials
5. Save as `config/google_credentials.json`

---

## 📊 Database Schema

### Accounts Table
```sql
CREATE TABLE accounts (
    id SERIAL PRIMARY KEY,
    email_address VARCHAR(255) UNIQUE NOT NULL,
    service VARCHAR(50) NOT NULL,
    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Companies Table
```sql
CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    domain VARCHAR(255) UNIQUE NOT NULL,
    company_name VARCHAR(255),
    privacy_contact VARCHAR(255),
    contact_type VARCHAR(50) DEFAULT 'email',
    last_verified DATE,
    notes TEXT
);
```

### Requests Table
```sql
CREATE TABLE requests (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
    account_id INTEGER REFERENCES accounts(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'PENDING',
    sent_date TIMESTAMP,
    sent_message_id TEXT,
    reply_received_date TIMESTAMP,
    completion_date TIMESTAMP,
    notes TEXT
);
```

---

## 🧪 Testing

Run the test suite:
```bash
pytest tests/
```

Test individual modules:
```bash
python src/email_scanner.py  # Test email scanning
python src/contact_finder.py # Test contact finding
python src/utils.py           # Test utilities
```

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Additional dev dependencies
```

---

## ⚠️ Limitations and lessons

This project works only partly, and building it taught me more about the problem than about the solution:

- **Finding privacy contacts is unreliable.** The scraper finds a usable privacy contact for only about 40–70% of companies; many hide it behind web forms or in long privacy policies.
- **Data brokers are invisible from the inbox.** The companies that hold the most data about you (data brokers) have usually never emailed you, so inbox scanning cannot find them.
- **Many companies require web forms and identity checks.** An email request is often answered with "please use our form" or "please verify your identity", which this tool cannot automate.
- **The OAuth scope is broader than needed for scanning.** The app requests `gmail.readonly` because the reply tracker reads replies. A stricter design would use `gmail.metadata` for scanning (which blocks body access entirely) and ask for broader access only for request threads.
- **Reply classification is keyword-based**, so unusual wording is often misclassified and needs manual review.

---

## ⚖️ Legal

### GDPR (EU)
This tool helps you exercise your **Right to Erasure** under Article 17 of the General Data Protection Regulation (GDPR). Companies must comply within 30 days unless they have a legitimate reason to retain your data.

### CCPA (California)
This tool assists with **Deletion Requests** under the California Consumer Privacy Act (CCPA). Businesses must comply within 45 days (with a possible 45-day extension).

### Disclaimer
This tool is provided for informational and automation purposes only. It is not legal advice. Companies may reject deletion requests for legitimate reasons (e.g., legal obligations, contract fulfillment, fraud prevention). Always verify company responses and follow up as needed.

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🌟 Acknowledgments

- **CustomTkinter**: Modern UI framework by Tom Schimansky
- **Gmail API**: Google's email integration platform
- **BeautifulSoup4**: Web scraping library
- **PostgreSQL**: Reliable open-source database

---

<div align="center">

**Your Privacy Matters** 🔐

Made with ❤️ for a more privacy-respecting internet

[Report Bug](https://github.com/Derdev74/Privacy-App/issues) · [Request Feature](https://github.com/Derdev74/Privacy-App/issues)

</div>
