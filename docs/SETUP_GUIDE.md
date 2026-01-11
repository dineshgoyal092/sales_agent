# Setup Guide - Retail Insights Assistant

## 🎯 Quick Setup (5 minutes)

Follow these steps to get the Retail Insights Assistant running on your machine.

---

## Step 1: Prerequisites

### Required Software
- **Python 3.9+** - [Download here](https://www.python.org/downloads/)
- **pip** (comes with Python)
- **Git** (optional) - [Download here](https://git-scm.com/downloads)

### Required Account
- **OpenAI API Key** - [Get one here](https://platform.openai.com/api-keys)
  - You'll need an OpenAI account with billing enabled
  - Alternative: Google Gemini API key

### System Requirements
- **RAM**: 4GB minimum, 8GB recommended
- **Disk Space**: 2GB free
- **OS**: Windows 10+, macOS 10.14+, or Linux

---

## Step 2: Project Setup

### Option A: Extract from ZIP

1. Extract the ZIP file to a location of your choice:
   ```
   C:\Users\YourName\Documents\sales_agent\
   ```

2. Open a terminal/command prompt in that directory

### Option B: Clone from Git

```bash
git clone <repository-url>
cd sales_agent
```

---

## Step 3: Create Virtual Environment

### Windows (PowerShell)
```powershell
# Navigate to project directory
cd sales_agent

# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1

# If you get an error about execution policy:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Windows (Command Prompt)
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

### macOS/Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

---

## Step 4: Install Dependencies

With your virtual environment activated:

```bash
# Upgrade pip first
pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt
```

This will install:
- Streamlit (UI framework)
- LangChain & LangGraph (Agent framework)
- OpenAI (LLM API)
- Pandas & DuckDB (Data processing)
- And other dependencies

**Installation may take 2-5 minutes.**

---

## Step 5: Configure API Key

1. **Copy the example environment file:**
   ```bash
   # Windows
   copy .env.example .env
   
   # macOS/Linux
   cp .env.example .env
   ```

2. **Edit the `.env` file:**
   
   Open `.env` in any text editor (Notepad, VS Code, etc.) and add your API key:
   
   ```env
   OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

3. **Save the file**

### Getting Your OpenAI API Key

1. Go to [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)
5. Paste it in your `.env` file

**Note**: Keep this key secret! Never commit it to Git.

---

## Step 6: Verify Your Data

Your CSV files should be in the `Sales Dataset/` folder:

```
sales_agent/
├── Sales Dataset/
│   ├── International sale Report.csv
│   ├── Sale Report.csv
│   ├── May-2022.csv
│   ├── P  L March 2021.csv
│   └── ... (any other CSV files)
```

**The system will automatically load all CSV files from this directory.**

---

## Step 7: Test Your Setup

Run the test script to verify everything is configured correctly:

```bash
python test_setup.py
```

Expected output:
```
✓ Python version: 3.9.x
✓ All dependencies installed
✓ API key configured
✓ Found X CSV files
✓ DataManager loaded successfully
✓ Agent system initialized

🎉 All tests passed! You're ready to run the application.
```

If any tests fail, follow the suggestions in the output.

---

## Step 8: Run the Application

### Start the Streamlit App

```bash
# Navigate to src directory
cd src

# Run the app
streamlit run app.py
```

The application will automatically open in your browser at:
```
http://localhost:8501
```

### What You Should See

1. **Main Dashboard** with three tabs:
   - 📋 Summarization
   - 💬 Q&A Chat
   - 🔍 Data Explorer

2. **Sidebar** showing:
   - Number of loaded tables
   - Data overview
   - Example queries

---

## Step 9: Try Your First Query

### In Summarization Mode:
1. Go to the "📋 Summarization" tab
2. Select "Overall Performance"
3. Click "🔍 Generate Summary"
4. Wait 5-10 seconds for the AI to analyze your data

### In Q&A Mode:
1. Go to the "💬 Q&A Chat" tab
2. Type: "What are the top 5 customers by total sales?"
3. Press Enter
4. The multi-agent system will process your question

---

## 🎉 Success! You're All Set!

You now have a fully functional GenAI-powered retail insights assistant.

---

## Common Issues & Solutions

### Issue 1: "OPENAI_API_KEY not found"

**Cause**: The `.env` file is missing or doesn't contain the API key.

**Solution**:
1. Ensure `.env` file exists in the root directory
2. Open it and verify your API key is there
3. Make sure there are no quotes around the key
4. Restart the application

---

### Issue 2: "ModuleNotFoundError: No module named 'streamlit'"

**Cause**: Dependencies not installed or wrong virtual environment.

**Solution**:
```bash
# Make sure virtual environment is activated (you should see (venv))
pip install -r requirements.txt
```

---

### Issue 3: "No CSV files found"

**Cause**: CSV files not in the correct directory.

**Solution**:
1. Create `Sales Dataset` folder in project root
2. Copy all your CSV files there
3. Restart the application

---

### Issue 4: "Port 8501 already in use"

**Cause**: Another Streamlit app is running.

**Solution**:
```bash
# Option 1: Use a different port
streamlit run app.py --server.port 8502

# Option 2: Kill the other process and restart
```

---

### Issue 5: Virtual Environment Won't Activate (Windows)

**Cause**: PowerShell execution policy.

**Solution**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then try activating again.

---

### Issue 6: "Rate limit exceeded" from OpenAI

**Cause**: Free tier API limits reached.

**Solution**:
1. Wait a few minutes and try again
2. Upgrade to paid tier for higher limits
3. Use GPT-3.5-turbo instead of GPT-4 (edit `src/app.py` line 51)

---

## Next Steps

### Explore the Features
- ✅ Try different types of queries
- ✅ Explore the Data Explorer tab
- ✅ Generate various summaries
- ✅ Check the underlying SQL queries

### Customize for Your Data
- Add more CSV files to `Sales Dataset/` folder
- The system will automatically detect and load them
- No code changes needed!

### Learn About Scaling
- Read `docs/SCALABILITY_ARCHITECTURE.md`
- Learn how to handle 100GB+ datasets
- Understand the multi-agent architecture

---

## Optional: IDE Setup

### VS Code (Recommended)
1. Open the project folder in VS Code
2. Install Python extension
3. Select the virtual environment:
   - Press `Ctrl+Shift+P`
   - Type "Python: Select Interpreter"
   - Choose the `venv` environment

### PyCharm
1. Open project
2. Configure interpreter: Settings → Project → Python Interpreter
3. Add the `venv` environment

---

## Getting Help

### Check These Resources First:
1. **README.md** - Full documentation
2. **SCALABILITY_ARCHITECTURE.md** - Architecture details
3. **Test output** - Run `python test_setup.py`

### Still Having Issues?
1. Check your Python version: `python --version`
2. Check installed packages: `pip list`
3. Verify API key is valid
4. Check CSV file formats

---

## Development Workflow

### Making Changes

1. Edit files in `src/` directory
2. Streamlit auto-reloads on file changes
3. Refresh browser to see updates

### Running Tests

```bash
python test_setup.py
```

### Checking Logs

Streamlit logs appear in the terminal where you ran the app.

---

## Deployment Considerations

### For Production Use:

1. **Security**
   - Use environment variables (not .env files)
   - Implement authentication
   - Use HTTPS

2. **Performance**
   - Deploy on cloud (AWS, Azure, GCP)
   - Use Redis for caching
   - Consider GPT-3.5-turbo for cost savings

3. **Monitoring**
   - Set up logging
   - Track API usage
   - Monitor query performance

See `docs/SCALABILITY_ARCHITECTURE.md` for full details.

---

## Summary Checklist

Before running the app, ensure:

- [x] Python 3.9+ installed
- [x] Virtual environment created and activated
- [x] Dependencies installed (`pip install -r requirements.txt`)
- [x] `.env` file created with valid API key
- [x] CSV files in `Sales Dataset/` folder
- [x] Test script passed (`python test_setup.py`)

If all checked, run:
```bash
cd src
streamlit run app.py
```

---

**Happy analyzing! 🚀📊**
