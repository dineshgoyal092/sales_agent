"""
Test script to verify the Retail Insights Assistant setup
Run this before using the main application
"""

import sys
import os
from pathlib import Path

def check_python_version():
    """Check if Python version is sufficient"""
    version = sys.version_info
    print(f"✓ Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("❌ Python 3.9+ required")
        return False
    return True

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'streamlit',
        'pandas',
        'openai',
        'langchain',
        'langgraph',
        'duckdb',
        'dotenv',
    ]
    
    print("\n📦 Checking dependencies...")
    all_installed = True
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✓ {package}")
        except ImportError:
            print(f"❌ {package} not installed")
            all_installed = False
    
    return all_installed

def check_env_file():
    """Check if .env file exists and has API key"""
    print("\n🔑 Checking environment configuration...")
    
    if not os.path.exists('.env'):
        print("❌ .env file not found")
        print("   Create .env file from .env.example and add your API key")
        return False
    
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not set in .env file")
        return False
    
    if api_key == 'your_openai_api_key_here':
        print("❌ Please replace placeholder API key with your actual key")
        return False
    
    print(f"✓ API key configured (starts with: {api_key[:7]}...)")
    return True

def check_data_directory():
    """Check if Sales Dataset directory exists and has CSV files"""
    print("\n📁 Checking data directory...")
    
    data_dir = Path("Sales Dataset")
    if not data_dir.exists():
        print(f"❌ Sales Dataset directory not found")
        return False
    
    csv_files = list(data_dir.glob("*.csv"))
    if not csv_files:
        print("❌ No CSV files found in Sales Dataset directory")
        return False
    
    print(f"✓ Found {len(csv_files)} CSV files:")
    for csv_file in csv_files:
        print(f"  - {csv_file.name}")
    
    return True

def test_data_manager():
    """Test if DataManager can load data"""
    print("\n🧪 Testing DataManager...")
    
    try:
        sys.path.append('src')
        from data_manager import DataManager
        
        dm = DataManager()
        tables = dm.load_all_datasets()
        
        if not tables:
            print("❌ No tables loaded")
            return False
        
        print(f"✓ Successfully loaded {len(tables)} tables:")
        for table_name in tables.keys():
            info = dm.get_table_info(table_name)
            print(f"  - {table_name}: {info['rows']:,} rows")
        
        return True
        
    except Exception as e:
        print(f"❌ DataManager test failed: {str(e)}")
        return False

def test_agent_system():
    """Test if agent system initializes"""
    print("\n🤖 Testing Agent System...")
    
    try:
        sys.path.append('src')
        from data_manager import DataManager
        from agents import MultiAgentSystem
        from dotenv import load_dotenv
        
        load_dotenv()
        api_key = os.getenv('OPENAI_API_KEY')
        
        dm = DataManager()
        dm.load_all_datasets()
        
        agent_system = MultiAgentSystem(dm, api_key, model="gpt-3.5-turbo")
        print("✓ Agent system initialized successfully")
        
        # Test a simple query
        print("\n  Testing simple query: 'How many tables do we have?'")
        result = agent_system.process_query(
            "How many tables are loaded in the system?",
            mode="qa"
        )
        
        if result['error']:
            print(f"  ⚠️  Query returned error: {result['error']}")
        else:
            print(f"  ✓ Query executed successfully")
            print(f"  Response preview: {result['response'][:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent system test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 Retail Insights Assistant - Setup Verification")
    print("=" * 60)
    
    tests = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Environment File", check_env_file),
        ("Data Directory", check_data_directory),
        ("Data Manager", test_data_manager),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! You're ready to run the application.")
        print("\nTo start the application, run:")
        print("  cd src")
        print("  streamlit run app.py")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above before running the application.")
        print("\nCommon fixes:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Create .env file: cp .env.example .env")
        print("  3. Add your OpenAI API key to .env file")
        print("  4. Ensure CSV files are in Sales Dataset/ directory")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
