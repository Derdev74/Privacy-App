# Privacy Data Deletion Tool - Project Roadmap

## 🎯 Project Overview
A **local-first, Gmail-only** privacy automation tool for exercising GDPR/CCPA data deletion rights.

**Platform**: WSL (Windows Subsystem for Linux) on Windows
**Database**: PostgreSQL (running on WSL)
**Email Provider**: Gmail only (via OAuth Desktop app)
**Architecture**: Python CLI → Future GUI (Tauri/Electron)

---

## ✅ All Steps Completed

- [x] Project structure created (`src/`, `tests/`, `docs/`, `config/`)
- [x] Python virtual environment setup
- [x] Dependencies installed (including PostgreSQL driver)
- [x] PostgreSQL database manager created
- [x] Token manager (OS keychain) created
- [x] Google OAuth credentials obtained
- [x] `.env.example` and `.gitignore` created
- [x] Setup documentation created

---

## 📋 Remaining Implementation Steps

### **Phase 1: Database & Configuration** (Steps 1-2)

#### ☐ Step 1: Database Initialization
**File**: `src/database.py` ✅ (Already created)

**Your Action**:
```bash
# 1. Create .env file with your PostgreSQL password
cp .env.example .env
nano .env  # Add your PostgreSQL password

# 2. Initialize the database
source venv/bin/activate
python src/database.py
```

**Expected Output**:
```
✓ Database 'privacy_deletion_db' created successfully
✓ Database schema initialized successfully
```

---

#### ☐ Step 2: Verify OAuth Credentials
**File**: `config/google_credentials.json` ✅ (Already added)

**Verification**:
```bash
# Check credentials file exists
ls -la config/google_credentials.json
```

---

### **Phase 2: Gmail Authentication** (Steps 3-4)

#### ☐ Step 3: Gmail OAuth Authenticator
**File**: `src/gmail_auth.py` (To be created)

**Features**:
- OAuth 2.0 flow for Gmail
- Browser-based authentication
- Token refresh handling
- Integration with TokenManager

**Scopes needed**:
- `gmail.readonly` (for scanning emails)
- `gmail.send` (for sending deletion requests)

---

#### ☐ Step 4: Account Manager
**File**: `src/account_manager.py` (To be created)

**Features**:
- Add Gmail account to database
- List registered accounts
- Remove accounts
- Link with OAuth tokens

**Database Table**: `accounts`

---

### **Phase 3: Company Discovery** (Steps 5-6)

#### ☐ Step 5: Email Scanner
**File**: `src/email_scanner.py` (To be created)

**Features**:
- Search Gmail for signup/welcome emails
- Optimized query: `from:(-me) AND ("welcome to" OR "verify your email" OR "account created")`
- Extract sender domains
- Fetch only headers (privacy-preserving)
- Deduplicate results

**Output**: List of company domains

---

#### ☐ Step 6: Company Manager
**File**: `src/company_manager.py` (To be created)

**Features**:
- Save discovered companies to database
- Bulk import from email scan
- Update company information
- Search/filter companies

**Database Table**: `companies`

---

### **Phase 4: Contact Discovery** (Steps 7-8)

#### ☐ Step 7: Privacy Contact Finder
**File**: `src/contact_finder.py` (To be created)

**Features**:
- Automatic contact discovery via web scraping
- Check common URLs: `/privacy`, `/privacy-policy`, `/legal/privacy`
- Extract email addresses: `privacy@domain.com`, `dpo@domain.com`
- Detect web forms
- Pattern matching for email addresses

**Success Rate**: ~40-70% automatic

---

#### ☐ Step 8: Manual Contact Entry CLI
**File**: `src/manual_contact.py` (To be created)

**Features**:
- Interactive CLI for missing contacts
- Google search link helper
- Save contact to database
- Mark as "webform required"
- One-time effort per company

---

### **Phase 5: Deletion Requests** (Steps 9-10)

#### ☐ Step 9: Template System
**File**: `src/templates.py` (To be created)

**Features**:
- GDPR template (EU)
- CCPA template (California)
- Generic template
- Variable substitution: `{company_name}`, `{account_email}`, `{date}`

---

#### ☐ Step 10: Request Sender
**File**: `src/request_sender.py` (To be created)

**Features**:
- Send emails via Gmail API
- Use templates
- Store Message-ID for tracking
- Update database (status: SENT)
- Rate limiting (avoid spam filters)

**Database Table**: `requests`

---

### **Phase 6: Reply Tracking** (Step 11)

#### ☐ Step 11: Reply Monitor
**File**: `src/reply_tracker.py` (To be created)

**Features**:
- Check for replies using Message-ID threading
- Auto-categorize responses:
  - ✅ "Deletion confirmed" → COMPLETED
  - ⏳ "Processing request" → REPLIED
  - ❓ "Need verification" → FLAG
- Daily automated check
- Update request status

---

### **Phase 7: Main Application** (Steps 12-13)

#### ☐ Step 12: CLI Interface
**File**: `main.py` (To be created)

**Features**:
```
Main Menu:
1. Add Email Account (OAuth flow)
2. Scan for Companies (email discovery)
3. Find Privacy Contacts (auto + manual)
4. Send Deletion Requests (batch)
5. Check for Replies (tracking)
6. View Dashboard (statistics)
7. Exit
```

---

#### ☐ Step 13: Dashboard & Statistics
**File**: `src/dashboard.py` (To be created)

**Features**:
- Total companies discovered
- Contacts found (auto vs manual)
- Requests sent
- Replies received
- Completion rate
- Success metrics

---

### **Phase 8: Polish & Testing** (Steps 14-16)

#### ☐ Step 14: Error Handling & Logging
**Files**: Throughout codebase

**Features**:
- Try-catch blocks for all API calls
- Proper error messages
- Logging to file (optional)
- Graceful degradation

---

#### ☐ Step 15: End-to-End Testing
**File**: `tests/` directory

**Test Cases**:
- Database initialization
- OAuth flow
- Email scanning
- Contact finding
- Request sending
- Reply tracking

---

#### ☐ Step 16: User Documentation
**File**: `README.md` (To be created)

**Contents**:
- Quick start guide
- Feature overview
- Screenshots/demos
- Troubleshooting
- FAQ

---

## 🔧 Technical Stack Summary

### Core Technologies:
- **Language**: Python 3.11+
- **Database**: PostgreSQL (WSL)
- **Email API**: Gmail API (OAuth 2.0)
- **Security**: OS Keychain (keyring library)
- **Web Scraping**: BeautifulSoup4 + Requests
- **Interface**: CLI (with Tauri/PyQt planned for future)

### Key Libraries:
```
google-api-python-client==2.100.0
google-auth-oauthlib==1.1.0
psycopg2-binary==2.9.9
keyring==24.2.0
beautifulsoup4==4.12.2
requests==2.31.0
```

---

## 📊 Project Progress

**Overall Completion**: ~25%

| Phase | Status | Progress |
|-------|--------|----------|
| Phase 1: Database & Config | 🟢 Complete | 100% |
| Phase 2: Gmail Auth | 🔴 Not Started | 0% |
| Phase 3: Company Discovery | 🔴 Not Started | 0% |
| Phase 4: Contact Discovery | 🔴 Not Started | 0% |
| Phase 5: Deletion Requests | 🔴 Not Started | 0% |
| Phase 6: Reply Tracking | 🔴 Not Started | 0% |
| Phase 7: Main Application | 🔴 Not Started | 0% |
| Phase 8: Polish & Testing | 🔴 Not Started | 0% |

---

## 🎯 Next Immediate Steps

1. **Initialize Database** (Your action):
   ```bash
   cp .env.example .env
   # Edit .env with your PostgreSQL password
   python src/database.py
   ```

2. **Start Phase 2** (Gmail Authentication):
   - Create `src/gmail_auth.py`
   - Implement OAuth flow
   - Test authentication

---

## 🚀 Future Enhancements (Post-MVP)

- [ ] GUI with Tauri or PyQt
- [ ] Scheduled/automated reply checking
- [ ] Export reports (PDF/CSV)
- [ ] Community database (opt-in contact sharing)
- [ ] Multi-account support
- [ ] Email template customization
- [ ] Analytics dashboard

---

## 📝 Notes

- **WSL-specific**: Database runs on WSL, credentials stored in Windows keychain
- **Gmail-only**: No Microsoft/Outlook support in this version
- **Local-first**: 100% privacy-preserving architecture
- **Desktop app**: OAuth configured for desktop application type

---

## 📚 References

- Implementation guide: `Gitlab Token.txt`
- Setup instructions: `SETUP.md`
- Database schema: `src/database.py`
- Token security: `src/auth_manager.py`

---

**Last Updated**: 2025-10-21
**Current Phase**: Phase 1 ✅ → Phase 2 ⏭️
