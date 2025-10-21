# WSL OAuth Authentication Guide

## The Problem
WSL (Windows Subsystem for Linux) doesn't have a browser, so the automatic OAuth flow won't work.

## The Solution
The app now uses a **manual OAuth flow** for WSL. Here's how it works:

---

## Step-by-Step Process

### When you run the authentication:

```bash
python src/gmail_auth.py
```

### You'll see this:

```
==============================================================
  MANUAL AUTHORIZATION (WSL/No Browser)
==============================================================

📋 STEP 1: Copy this URL and open it in your Windows browser:

------------------------------------------------------------
https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=...
------------------------------------------------------------

📋 STEP 2: After authorizing, you'll see a success page.
           Look at the URL in your browser's address bar.
           It will look like: http://localhost/?code=XXXXX&scope=...

📋 STEP 3: Copy the ENTIRE URL from your browser and paste it below.
==============================================================

Paste the full redirect URL here:
```

---

## What to Do:

### 1. **Copy the Authorization URL**
   - The long URL shown in STEP 1
   - Select it and copy (Ctrl+C or right-click → Copy)

### 2. **Open in Windows Browser**
   - Open Chrome/Edge/Firefox on your Windows machine
   - Paste the URL in the address bar
   - Press Enter

### 3. **Sign In and Authorize**
   - Sign in to your Gmail account
   - Click "Allow" to grant permissions
   - You'll see a success page

### 4. **Copy the Redirect URL**
   - **IMPORTANT**: Look at your browser's address bar (not the page content!)
   - The URL will look like: `http://localhost/?code=4/0AanRRrt...&scope=...`
   - Copy the **ENTIRE URL** from the address bar

### 5. **Paste in WSL Terminal**
   - Go back to your WSL terminal
   - Right-click to paste the URL
   - Press Enter

### 6. **Done!**
   - The app will exchange the code for a token
   - Token is saved securely in Windows Credential Manager
   - You won't need to do this again (token auto-refreshes)

---

## Example

**What you copy from browser's address bar:**
```
http://localhost:42249/?code=4/0AanRRrtJKxS...&scope=https://www.googleapis.com/auth/gmail.readonly...
```

**Paste this ENTIRE URL in the WSL terminal.**

---

## Troubleshooting

### Error: "No authorization code found in URL"
- Make sure you copied the URL from the **address bar**, not the page text
- The URL must start with `http://localhost/`
- The URL must contain `?code=`

### Error: "Site can't be reached" in browser
- This is NORMAL! The browser can't connect to localhost, but that's okay
- Just copy the URL from the address bar anyway
- The authorization code is in the URL parameters

### Error: "Invalid grant"
- The authorization code expired (only valid for ~10 minutes)
- Start over and copy/paste faster
- Or run the command again to get a new URL

---

## Why This Works

1. **Authorization URL**: Contains your client ID and requested permissions
2. **User Authorization**: You grant permissions on Google's server
3. **Redirect**: Google sends you back to `localhost` with an authorization code
4. **Code Exchange**: The app exchanges the code for an access token
5. **Token Storage**: Token saved in Windows Credential Manager (secure!)

---

## Security Notes

✅ **Safe**:
- The URL contains no passwords or sensitive data
- The authorization code is single-use and expires quickly
- Tokens are encrypted in Windows Credential Manager

✅ **Private**:
- All data stays local on your machine
- Google OAuth is the standard authentication method
- Same process used by official Google apps

---

## Alternative: Use Native Windows Python (Advanced)

If you prefer automatic browser opening, you can:

1. Install Python on Windows (not WSL)
2. Run the script from Windows CMD/PowerShell
3. Browser will open automatically

But WSL works fine with the manual method! 🎉
