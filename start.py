"""
Quick start script for Retail Insights Assistant
Runs basic checks and provides instructions
"""

import os
import sys
from pathlib import Path

def print_header():
    print("\n" + "=" * 70)
    print("  🤖 RETAIL INSIGHTS ASSISTANT - Quick Start")
    print("=" * 70 + "\n")

def check_env():
    """Check if .env file exists"""
    if not os.path.exists('.env'):
        print("❌ .env file not found!\n")
        print("📋 Quick Fix:")
        print("   1. Copy .env.example to .env")
        print("   2. Edit .env and add your OpenAI API key")
        print("   3. Run this script again\n")
        print("Commands:")
        print("   Windows: copy .env.example .env")
        print("   Linux/Mac: cp .env.example .env\n")
        return False
    
    # Check if API key is set
    with open('.env', 'r') as f:
        content = f.read()
        if 'your_openai_api_key_here' in content:
            print("⚠️  .env file exists but API key needs to be updated!\n")
            print("📋 Quick Fix:")
            print("   1. Open .env file in a text editor")
            print("   2. Replace 'your_openai_api_key_here' with your actual key")
            print("   3. Run this script again\n")
            return False
    
    print("✅ .env file configured")
    return True

def check_data():
    """Check if data files exist"""
    data_dir = Path("Sales Dataset")
    if not data_dir.exists():
        print("❌ Sales Dataset folder not found!\n")
        print("📋 Quick Fix:")
        print("   1. Create 'Sales Dataset' folder in project root")
        print("   2. Add your CSV files to this folder")
        print("   3. Run this script again\n")
        return False
    
    csv_files = list(data_dir.glob("*.csv"))
    if not csv_files:
        print("⚠️  Sales Dataset folder exists but no CSV files found!\n")
        print("📋 Quick Fix:")
        print("   1. Add your CSV files to 'Sales Dataset' folder")
        print("   2. Run this script again\n")
        return False
    
    print(f"✅ Found {len(csv_files)} CSV file(s) in Sales Dataset")
    return True

def check_venv():
    """Check if virtual environment is activated"""
    if sys.prefix == sys.base_prefix:
        print("⚠️  Virtual environment not activated!\n")
        print("📋 Quick Fix:")
        print("   Windows PowerShell: .\\venv\\Scripts\\Activate.ps1")
        print("   Windows CMD: venv\\Scripts\\activate.bat")
        print("   Linux/Mac: source venv/bin/activate\n")
        return False
    
    print("✅ Virtual environment activated")
    return True

def check_packages():
    """Check if key packages are installed"""
    try:
        import streamlit
        import pandas
        import openai
        import langchain
        print("✅ Key packages installed")
        return True
    except ImportError as e:
        print(f"❌ Some packages not installed!\n")
        print("📋 Quick Fix:")
        print("   pip install -r requirements.txt\n")
        return False

def main():
    print_header()
    
    # Run checks
    checks = [
        ("Virtual Environment", check_venv()),
        ("Dependencies", check_packages()),
        ("Environment Config", check_env()),
        ("Data Files", check_data()),
    ]
    
    # Summary
    print("\n" + "-" * 70)
    print("CHECKLIST SUMMARY")
    print("-" * 70)
    
    all_passed = True
    for name, passed in checks:
        status = "✅" if passed else "❌"
        print(f"{status} {name}")
        if not passed:
            all_passed = False
    
    print("-" * 70 + "\n")
    
    # Instructions
    if all_passed:
        print("🎉 All checks passed! You're ready to start!\n")
        print("🚀 NEXT STEPS:\n")
        print("   1. Run: cd src")
        print("   2. Run: streamlit run app.py")
        print("   3. Your browser will open automatically\n")
        print("📚 HELPFUL RESOURCES:\n")
        print("   • README.md - Full documentation")
        print("   • docs/TESTING_INSTRUCTIONS.md - Testing guide")
        print("   • docs/EXAMPLE_QUERIES.md - Sample queries")
        print("   • PROJECT_SUMMARY.md - Quick reference\n")
    else:
        print("⚠️  Some checks failed. Please fix the issues above.\n")
        print("💡 COMMON SOLUTIONS:\n")
        print("   1. Create virtual environment: python -m venv venv")
        print("   2. Activate it (see commands above)")
        print("   3. Install dependencies: pip install -r requirements.txt")
        print("   4. Configure .env file with your API key")
        print("   5. Add CSV files to Sales Dataset folder\n")
        print("📖 For detailed help, see: docs/SETUP_GUIDE.md\n")
    
    print("=" * 70)

if __name__ == "__main__":
    main()
