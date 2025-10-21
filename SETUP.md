# Privacy Data Deletion Tool - Setup Guide

## Overview
A local-first privacy tool to help you exercise your GDPR/CCPA data deletion rights. All data processing happens on your machine—no cloud services involved.

---

## Step 1: Database Setup

### 1.1 Configure PostgreSQL Connection

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your PostgreSQL credentials:

```env
DB_NAME=privacy_deletion_db
DB_USER=postgres
DB_PASSWORD=your_actual_password
DB_HOST=localhost
DB_PORT=5432
```

### 1.2 Initialize the Database

Run the database setup script:

```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Initialize database
python src/database.py
```

You should see:
```
✓ Database 'privacy_deletion_db' created successfully
✓ Database schema initialized successfully
  - accounts table created
  - companies table created
  - requests table created
  - indexes created
```

---

## Step 2: OAuth Credentials Setup

### 2.1 Google Cloud Console (Gmail)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project: "Personal-Data-Deletion"
3. Enable **Gmail API**:
   - APIs & Services → Library
   - Search "Gmail API" → Enable

4. Create OAuth 2.0 credentials:
   - APIs & Services → Credentials
   - Click **Create Credentials** → **OAuth 2.0 Client ID**
   - Application type: **Desktop app**
   - Name: "Privacy Data Deletion Tool"
   - Click **Create**

5. Download credentials:
   - Click the download icon
   - Save as `config/google_credentials.json`

### 2.2 Microsoft Azure (Outlook) - Optional

1. Go to [Azure Portal](https://portal.azure.com/)
2. Navigate to **Azure Active Directory** → **App registrations**
3. Click **New registration**:
   - Name: "Privacy Data Deletion Tool"
   - Supported account types: **Accounts in any organizational directory and personal Microsoft accounts**
   - Redirect URI: Leave blank for now

4. Add permissions:
   - API permissions → Add permission
   - Microsoft Graph → Delegated permissions
   - Add: `Mail.Read`, `Mail.Send`

5. Create client secret:
   - Certificates & secrets → New client secret
   - Copy the secret value

6. Save credentials to `config/microsoft_credentials.json`:
```json
{
  "client_id": "your-client-id",
  "client_secret": "your-client-secret",
  "tenant": "common"
}
```

---

## Step 3: Test the Setup

### 3.1 Test Token Manager

```bash
python src/auth_manager.py
```

Expected output:
```
✓ Token saved securely for test@example.com
✓ Token retrieved successfully
✓ Token successfully deleted
```

### 3.2 Test Database Connection

```bash
python -c "from src.database import DatabaseManager; db = DatabaseManager(); conn = db.get_connection(); print('✓ Database connection successful'); conn.close()"
```

---

## Project Structure

```
Privacy App/
├── src/
│   ├── database.py          # PostgreSQL database management
│   ├── auth_manager.py      # Secure OAuth token storage
│   └── (more modules coming)
├── config/
│   ├── google_credentials.json    # Your Google OAuth credentials
│   └── microsoft_credentials.json # Your Microsoft OAuth credentials
├── tests/
├── docs/
├── venv/                    # Python virtual environment
├── .env                     # Database configuration (DO NOT COMMIT)
├── .env.example             # Template for .env
├── requirements.txt         # Python dependencies
└── SETUP.md                 # This file
```

---

## Security Notes

### What's Stored Locally:
- ✅ OAuth tokens (OS keychain - encrypted)
- ✅ Email metadata (PostgreSQL - local database)
- ✅ Company contact information (PostgreSQL)
- ✅ Deletion request tracking (PostgreSQL)

### What's Never Stored:
- ❌ Email content/body
- ❌ Passwords
- ❌ Credit card information

### What Never Leaves Your Machine:
- ✅ **Everything** - This tool is 100% local
- ✅ No cloud services
- ✅ No analytics
- ✅ No telemetry

---

## Next Steps

After completing setup:
1. ✅ Database initialized
2. ✅ OAuth credentials configured
3. ⏭️ Ready to implement email scanning (Step 4)
4. ⏭️ Ready to implement company discovery (Step 5)

---

## Troubleshooting

### Database Connection Failed
- Ensure PostgreSQL is running: `sudo systemctl status postgresql`
- Check credentials in `.env` file
- Verify database exists: `psql -U postgres -l`

### OAuth Credentials Not Found
- Check file paths: `config/google_credentials.json`
- Ensure JSON format is valid
- Download credentials again from console

### Token Storage Failed
- OS keychain must be available
- On Linux, ensure `libsecret` is installed: `sudo apt install libsecret-1-dev`
- On Windows, uses Windows Credential Manager (built-in)

---

## Support

For issues, refer to the implementation guide in `Gitlab Token.txt`.
