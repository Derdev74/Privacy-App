# 🚀 START HERE - Quick Launch Guide

## ⚡ Fastest Way to Start

### Method 1: Super Simple (Recommended)
```bash
python3 run.py
```

**No need to activate venv manually!** The script does it automatically.

### Method 2: Using Startup Script
```bash
./start.sh
```

Both methods will:
- ✅ Activate your virtual environment automatically
- ✅ Check if dependencies are installed
- ✅ Launch the application

---

## 🎯 Step-by-Step (If First Time)

### 1. Install Dependencies

```bash
# Make sure you're in the project directory
cd "/mnt/c/Users/pc/Desktop/Privacy App"

# Activate virtual environment
source venv/bin/activate

# Install all requirements
pip install -r requirements.txt
```

### 2. Configure Database

```bash
# Copy the example file
cp .env.example .env

# Edit with your PostgreSQL password
nano .env
```

### 3. Initialize Database

```bash
# Still in activated venv
python src/database.py
```

### 4. Launch!

```bash
# Option A: Use the startup script (recommended)
./start.sh

# Option B: Manual launch
source venv/bin/activate
python launcher.py
```

---

## ❌ Common Errors & Fixes

### Error: "CustomTkinter not installed"

**Cause**: Virtual environment not activated

**Fix**:
```bash
source venv/bin/activate
./start.sh
```

---

### Error: "UTF-8 codec can't decode byte"

**Cause**: File encoding issue (already fixed in latest version)

**Fix**: Make sure you're using the latest files. If issue persists:
```bash
cd "/mnt/c/Users/pc/Desktop/Privacy App"
iconv -f WINDOWS-1252 -t UTF-8 src/reply_tracker.py > temp.py && mv temp.py src/reply_tracker.py
```

---

### Error: "Database connection failed"

**Cause**: PostgreSQL not configured

**Fix**:
```bash
# 1. Make sure PostgreSQL is running
sudo systemctl status postgresql

# 2. Check your .env file has correct credentials
cat .env

# 3. Initialize database
source venv/bin/activate
python src/database.py
```

---

## 📖 Full Documentation

- **Quick Start**: See `QUICKSTART.md`
- **Full README**: See `README.md`
- **Test Results**: See `TEST_RESULTS.md`

---

## 🆘 Still Having Issues?

1. Make sure virtual environment is activated:
   ```bash
   source venv/bin/activate
   ```

2. Verify packages are installed:
   ```bash
   pip list | grep customtkinter
   # Should show: customtkinter 5.2.1
   ```

3. Check Python version:
   ```bash
   python --version
   # Should be: Python 3.11 or higher
   ```

4. Reinstall dependencies:
   ```bash
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

---

## ✅ Ready to Go?

```bash
./start.sh
```

**Choose your interface:**
- [1] CLI Mode - Fast, terminal interface
- [2] Desktop GUI - Modern graphical interface

Enjoy! 🎉
