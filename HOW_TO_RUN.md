# 🎯 How to Run - Complete Guide

## The Problem You Had

When you ran `python launcher.py` without activating the virtual environment:
- ❌ CustomTkinter wasn't found
- ❌ CLI mode launched but exited immediately
- ❌ Dependencies appeared missing even though installed

**Root Cause**: Packages were installed IN the virtual environment, but you were running with SYSTEM Python.

---

## ✅ The Solution - 3 Easy Ways

### Option 1: Super Simple (Zero Manual Steps) ⭐ RECOMMENDED

```bash
cd "/mnt/c/Users/pc/Desktop/Privacy App"
python3 run.py
```

**What it does**:
1. Detects if venv is activated
2. If not, automatically re-runs itself with venv Python
3. Launches the interface selector
4. **You don't do anything!**

---

### Option 2: Use Startup Script

```bash
cd "/mnt/c/Users/pc/Desktop/Privacy App"
./start.sh
```

**What it does**:
1. Activates venv
2. Checks dependencies
3. Launches launcher.py
4. **Handles everything for you**

---

### Option 3: Manual (If you prefer control)

```bash
cd "/mnt/c/Users/pc/Desktop/Privacy App"

# STEP 1: Activate venv (IMPORTANT!)
source venv/bin/activate

# STEP 2: Launch
python launcher.py

# When done, deactivate
deactivate
```

**Why this works**: You manually activate venv first, so Python finds CustomTkinter.

---

## 🎬 Quick Demo

### What Works ✅

```bash
# This WORKS because run.py handles venv automatically
$ python3 run.py

Activating virtual environment automatically...

╔══════════════════════════════════════╗
║  🔐 PRIVACY DATA DELETION TOOL       ║
╚══════════════════════════════════════╝

Choose Your Interface:
[1] 🖥️  CLI Mode
[2] 🎨 Desktop App
[3] ℹ️  About
[4] ❌ Exit

Enter your choice (1-4):
```

### What Doesn't Work ❌

```bash
# This FAILS because no venv activation
$ python launcher.py

✗ Error: CustomTkinter not installed!
```

**Fix**: Use `python3 run.py` instead!

---

## 📋 First Time Setup

If you haven't set up the project yet:

```bash
# 1. Navigate to project
cd "/mnt/c/Users/pc/Desktop/Privacy App"

# 2. Create virtual environment (if not exists)
python3 -m venv venv

# 3. Activate venv
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Configure database
cp .env.example .env
nano .env  # Add your PostgreSQL password

# 6. Initialize database
python src/database.py

# 7. Done! Now you can use any launch method
python3 run.py
```

---

## 🔍 Understanding Virtual Environments

### Why Use Venv?

Virtual environments isolate project dependencies. Think of it as a "bubble" where your packages live.

```
System Python (no CustomTkinter)
    vs
Venv Python (has CustomTkinter, psycopg2, etc.)
```

### How It Works

```bash
# BEFORE activation
$ which python
/usr/bin/python  ← System Python (no packages)

# AFTER activation
$ source venv/bin/activate
$ which python
/path/to/venv/bin/python  ← Venv Python (has packages)
```

### Installed Packages Location

```
System packages: /usr/lib/python3.12/site-packages/
Venv packages:   /path/to/venv/lib/python3.12/site-packages/ ✅

When you run:
  pip install customtkinter
  → Goes to VENV (if activated)
  → Goes to SYSTEM (if not activated)
```

---

## 🎯 Recommended Workflow

### Daily Usage

```bash
# Just run this every time:
python3 run.py
```

**That's it!** No activation needed.

---

### Development/Debugging

```bash
# Activate venv for development
source venv/bin/activate

# Now you can run any Python command
python src/database.py
python tests/test_utils.py
python main.py
python main_gui.py

# When done
deactivate
```

---

## 🐛 Troubleshooting

### "python3: command not found"

Try `python` instead:
```bash
python run.py
```

---

### "run.py: No such file or directory"

Make sure you're in the project directory:
```bash
cd "/mnt/c/Users/pc/Desktop/Privacy App"
ls run.py  # Should exist
python3 run.py
```

---

### "Virtual environment not found"

Create it:
```bash
python3 -m venv venv
```

---

### Still getting "CustomTkinter not installed"

Reinstall in venv:
```bash
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python3 run.py
```

---

## 📊 Launch Methods Comparison

| Method | Pros | Cons | Recommended? |
|--------|------|------|--------------|
| `python3 run.py` | ✅ Zero manual steps<br>✅ Auto venv | ⚠️ Slightly slower first run | ⭐ YES |
| `./start.sh` | ✅ Full control<br>✅ Checks dependencies | ⚠️ Shell script only | ✅ YES |
| Manual activation | ✅ Educational<br>✅ Flexible | ❌ Must remember to activate | 🤔 Optional |
| Direct `python launcher.py` | None | ❌ Doesn't work without venv | ❌ NO |

---

## 🎉 Summary

### To Launch the App:

```bash
python3 run.py
```

### That's All!

Everything else is handled automatically. The app will:
1. ✅ Use venv Python
2. ✅ Find all dependencies
3. ✅ Show you the interface selector
4. ✅ Let you choose CLI or GUI

### Choose Your Interface:
- **Option 1**: CLI Mode → Terminal-based
- **Option 2**: Desktop GUI → Graphical interface

Both work perfectly now! 🚀

---

**Created**: 2025-10-21
**Status**: All issues resolved ✅
