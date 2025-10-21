# Quick Start Guide

Get up and running in 5 minutes!

---

## Prerequisites

Before you begin, ensure you have:

- ✅ **Python 3.11+** installed
- ✅ **PostgreSQL** installed and running
- ✅ **Gmail account**
- ✅ **Google Cloud Project** (free)

---

## Step 1: Install Dependencies

```bash
# Navigate to project directory
cd "Privacy App"

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows (WSL):
source venv/bin/activate
# On Windows (CMD):
venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt
```

---

## Step 2: Configure Database

1. **Create `.env` file** from template:
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` file** with your PostgreSQL credentials:
   ```bash
   DB_NAME=privacy_deletion_db
   DB_USER=postgres
   DB_PASSWORD=YOUR_PASSWORD_HERE
   DB_HOST=localhost
   DB_PORT=5432
   ```

3. **Initialize database**:
   ```bash
   python src/database.py
   ```

   You should see:
   ```
   ✓ Database 'privacy_deletion_db' created successfully
   ✓ Database schema initialized successfully
   ```

---

## Step 3: Set Up Google OAuth

### A. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "NEW PROJECT"
3. Name it: "Privacy Deletion Tool" → Create

### B. Enable Gmail API

1. In the dashboard, go to "APIs & Services" → "Library"
2. Search for "Gmail API"
3. Click "ENABLE"

### C. Create OAuth Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "CREATE CREDENTIALS" → "OAuth client ID"
3. If prompted, configure OAuth consent screen:
   - User Type: **External**
   - App name: "Privacy Deletion Tool"
   - User support email: (your email)
   - Add test users: (your Gmail address)
   - Scopes: Select `gmail.readonly` and `gmail.send`
4. Back to "Create OAuth client ID":
   - Application type: **Desktop app**
   - Name: "Privacy Tool Desktop"
5. Click "CREATE"
6. Download the JSON file
7. Save it as `config/google_credentials.json`

---

## Step 4: Launch the Application

### Using the Startup Script (Recommended - Auto-activates venv)

**For WSL/Linux**:
```bash
./start.sh
```

**For Windows CMD/PowerShell**:
```cmd
start.bat
```

**For Windows (Double-click)**:
- Just double-click `start.bat` in File Explorer

### Using the Launcher (Manual venv activation)

**Activate virtual environment first**:
```bash
# On WSL/Linux:
source venv/bin/activate

# On Windows CMD:
venv\Scripts\activate.bat

# On Windows PowerShell:
venv\Scripts\Activate.ps1
```

**Then launch**:
```bash
python launcher.py
```

Choose your interface:
- **[1] CLI Mode** - Fast, terminal-based
- **[2] Desktop App** - Modern, graphical

### Direct Launch (Advanced)

**CLI Mode**:
```bash
source venv/bin/activate  # Activate venv first!
python main.py
```

**GUI Mode**:
```bash
source venv/bin/activate  # Activate venv first!
python main_gui.py
```

---

## Step 5: First-Time Setup

1. **Add Your Gmail Account**
   - Select "Add Email Account" (CLI) or click "Add Gmail Account" (GUI)
   - Enter your Gmail address
   - A browser window will open for OAuth authentication
   - **If in WSL**: Copy the URL and open in Windows browser
   - Sign in and grant permissions
   - Copy the authorization code back to the terminal

2. **Scan for Companies**
   - Select "Scan for Companies"
   - The tool will search your inbox for signup emails
   - This may take a few minutes depending on your inbox size
   - Example: Finds Spotify, Netflix, Amazon, etc.

3. **Find Privacy Contacts**
   - Select "Find Privacy Contacts"
   - The tool will automatically search for privacy emails
   - Success rate: 40-70%
   - Manually enter remaining contacts when prompted

4. **Send Deletion Requests**
   - Select "Send Deletion Requests"
   - Choose template: Generic, GDPR, or CCPA
   - The tool will batch-send emails
   - Status is tracked automatically

5. **Check for Replies**
   - Select "Check for Replies"
   - The tool monitors your inbox for responses
   - Automatically categorizes: COMPLETED, REPLIED, PENDING

6. **View Dashboard**
   - See statistics and progress
   - Track completion rate
   - Review account details

---

## Troubleshooting

### "CustomTkinter not installed" even though requirements.txt was installed
**Problem**: Virtual environment not activated

**Solution**:
```bash
# ALWAYS activate venv before running!
source venv/bin/activate

# Or use the startup script:
./start.sh
```

**Why**: Python packages installed in venv are only available when venv is activated.

---

### "UTF-8 codec can't decode byte 0x92" error in CLI mode
**Problem**: File encoding issue (Windows smart quotes)

**Solution**: Already fixed in the latest code. If you still see this:
```bash
# Re-download the reply_tracker.py file or:
cd "/mnt/c/Users/pc/Desktop/Privacy App"
iconv -f WINDOWS-1252 -t UTF-8 src/reply_tracker.py > temp.py
mv temp.py src/reply_tracker.py
```

---

### "Database connection failed"
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Verify credentials in .env file
cat .env
```

---

### "OAuth credentials not found"
```bash
# Ensure file exists
ls -la config/google_credentials.json

# Check file contents (should be valid JSON)
cat config/google_credentials.json
```

---

### "Browser not found" (WSL users)
- This is expected in WSL
- The tool will automatically switch to manual OAuth flow
- Copy the URL and paste in your Windows browser
- Then copy the authorization code back to the terminal

---

### "Keyring backend error"
```bash
# For WSL users
source venv/bin/activate
pip install keyrings.alt
```

---

### General Installation Issues

**Problem**: Packages not installing properly

**Solution**:
```bash
# 1. Make sure you're in the project directory
cd "/mnt/c/Users/pc/Desktop/Privacy App"

# 2. Activate virtual environment
source venv/bin/activate

# 3. Upgrade pip
pip install --upgrade pip

# 4. Install requirements
pip install -r requirements.txt

# 5. Verify installation
pip list | grep customtkinter
# Should show: customtkinter 5.2.1
```

---

## Usage Tips

### CLI Shortcuts
- Type the number and press Enter
- Navigate with arrow keys (where supported)
- `Ctrl+C` to exit at any time

### GUI Tips
- Use the sidebar for navigation
- Switch themes: Settings → Appearance
- Check logs in `logs/` directory for detailed output

### Best Practices
- Start with **100-200 companies** for testing
- Use **Generic template** for initial requests
- Check replies **weekly**
- Keep track of companies that need webforms

---

## What's Next?

After your first scan, you'll likely have:
- 50-200 companies discovered
- 20-100 privacy contacts found automatically
- 10-50 requiring manual entry

**Recommended workflow**:
1. Scan companies (once)
2. Find contacts (automated + manual)
3. Send deletion requests (batch)
4. Wait 1-2 weeks
5. Check for replies
6. Follow up on pending requests

---

## Getting Help

- **Documentation**: See `README.md` for full details
- **Issues**: Check `IMPLEMENTATION_SUMMARY.md` for known issues
- **Tests**: Run `python tests/test_utils.py` to verify setup
- **Logs**: Check `logs/` directory for detailed debugging

---

## Security Reminder

- ✅ All data is stored **locally** on your machine
- ✅ OAuth tokens are **encrypted** in your OS keychain
- ✅ Email content is **never accessed** (headers only)
- ✅ No telemetry, no tracking, no external services

Your privacy is protected! 🔐

---

**Ready to start?**

```bash
python launcher.py
```

Enjoy reclaiming your digital privacy! 🎉
