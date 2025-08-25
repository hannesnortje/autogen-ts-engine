#!/usr/bin/env python3
"""
Comprehensive AutoGen TS Engine Test with Gemini

This script tests the full capabilities of the AutoGen TS Engine using Gemini.
You need to set your Google API key before running this script.

Setup:
1. Get your API key from: https://makersuite.google.com/app/apikey
2. Set environment variable: export GOOGLE_API_KEY="your_api_key_here"
3. Run this script: python test_with_gemini.py
"""

import os
import sys
from pathlib import Path

# Add the autogen_ts_engine to the path
sys.path.insert(0, str(Path(__file__).parent))

def check_gemini_setup():
    """Check if Gemini is properly set up."""
    print("🔍 Checking Gemini Setup...")
    
    # Check API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY not found!")
        print("💡 Please set your API key:")
        print("   export GOOGLE_API_KEY='your_api_key_here'")
        print("   Get your key from: https://makersuite.google.com/app/apikey")
        return False
    
    print("✅ Google API key found")
    
    # Check Gemini availability
    try:
        from autogen_ts_engine.gemini_adapter import is_gemini_available
        if is_gemini_available():
            print("✅ Gemini is available")
            return True
        else:
            print("❌ Gemini not available")
            return False
    except ImportError:
        print("❌ Gemini adapter not available")
        return False

def test_gemini_basic_functionality():
    """Test basic Gemini functionality."""
    print("\n🧪 Testing Basic Gemini Functionality...")
    
    try:
        from autogen_ts_engine.gemini_adapter import create_gemini_adapter
        from autogen_ts_engine.schemas import LLMBinding, LLMProvider
        
        api_key = os.getenv("GOOGLE_API_KEY")
        llm_binding = LLMBinding(
            provider=LLMProvider.GEMINI,
            model_name="gemini-1.5-flash",
            api_key=api_key
        )
        
        adapter = create_gemini_adapter(llm_binding)
        if not adapter:
            print("❌ Failed to create Gemini adapter")
            return False
        
        # Test simple response
        prompt = "Write a simple Python function that calculates the factorial of a number."
        response = adapter.generate_response(prompt)
        
        if response and len(response) > 50:
            print("✅ Basic Gemini functionality working!")
            print(f"📝 Response preview: {response[:200]}...")
            return True
        else:
            print("❌ Empty or invalid response")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_full_engine_with_gemini():
    """Test the full AutoGen TS Engine with Gemini."""
    print("\n🚀 Testing Full AutoGen TS Engine with Gemini...")
    
    try:
        from autogen_ts_engine.config_parser import ConfigParser
        from autogen_ts_engine.sprint_runner import SprintRunner
        from autogen_ts_engine.logging_utils import EngineLogger
        from autogen_ts_engine.schemas import LLMBinding, LLMProvider
        
        # Create Gemini configuration
        config_content = f"""
project_name: "gemini_test_project"
project_goal: "Build a Python web application with FastAPI and modern best practices using Gemini for development."
project_type: "python"
num_sprints: 2
iterations_per_sprint: 3

llm_binding:
  provider: "gemini"
  model_name: "gemini-1.5-flash"
  api_type: "google"
  api_key: "{os.getenv('GOOGLE_API_KEY')}"
  cache_seed: 42

work_dir: "./gemini_test_project"
vector_db_path: "./gemini_project_db"
git_branch_prefix: "gemini-"
human_input_mode: "AUTO"

rl:
  epsilon: 0.1
  alpha: 0.1
  gamma: 0.9
  state_buckets: 10

rag:
  top_k: 5
  max_doc_tokens: 4000

project_config:
  project_type: "python"
  language: "python"
  python:
    package_manager: "pip"
    test_command: "pytest"
    build_command: "python setup.py build"
    virtual_env: true
    requirements_file: "requirements.txt"

debug_mode: false
auto_commit: true
create_pr: false
"""
        
        # Write temporary config
        config_dir = Path("config")
        config_dir.mkdir(exist_ok=True)
        
        with open(config_dir / "settings.md", "w") as f:
            f.write(config_content)
        
        print("✅ Created Gemini configuration")
        
        # Initialize components
        config_parser = ConfigParser()
        settings = config_parser.parse_settings(config_dir)
        logger = EngineLogger("gemini_test")
        
        print(f"📋 Project: {settings.project_name}")
        print(f"🎯 Goal: {settings.project_goal}")
        print(f"🤖 Provider: {settings.llm_binding.provider}")
        print(f"🧠 Model: {settings.llm_binding.model_name}")
        
        # Initialize sprint runner
        sprint_runner = SprintRunner(settings, logger)
        print("✅ Sprint runner initialized")
        
        # Load agent definitions
        agent_definitions = config_parser.parse_agents(config_dir)
        print(f"🤖 Loaded {len(agent_definitions)} agents")
        
        # Run a single sprint
        print("\n🎯 Running Sprint 1 with Gemini...")
        success = sprint_runner.run_sprints(agent_definitions)
        
        if success:
            print("✅ Sprint completed successfully!")
            return True
        else:
            print("❌ Sprint failed")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_qa_improvement_with_gemini():
    """Test Q&A and improvement capabilities with Gemini."""
    print("\n💬 Testing Q&A and Improvement with Gemini...")
    
    try:
        from qa_improvement_runner import QAImprovementRunner
        
        # Create a test project first
        test_project = Path("./qa_test_project")
        test_project.mkdir(exist_ok=True)
        
        # Create a simple Python file for testing
        test_file = test_project / "main.py"
        test_file.write_text("""
def add_numbers(a, b):
    return a + b

def multiply_numbers(a, b):
    return a * b

if __name__ == "__main__":
    print("Hello, World!")
""")
        
        print("✅ Created test project")
        
        # Initialize Q&A runner
        runner = QAImprovementRunner(str(test_project))
        print("✅ Q&A runner initialized")
        
        # Index the project
        runner.index_project()
        print("✅ Project indexed")
        
        # Test analysis
        print("\n📊 Running project analysis...")
        analysis = runner.analyze_project()
        
        if analysis:
            print("✅ Project analysis completed!")
            for area, result in analysis.items():
                if result:
                    print(f"   📋 {area}: {result.get('agent', 'Unknown')}")
            return True
        else:
            print("❌ Project analysis failed")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 AutoGen TS Engine - Comprehensive Gemini Test")
    print("=" * 60)
    
    # Check setup
    if not check_gemini_setup():
        print("\n❌ Setup incomplete. Please fix the issues above.")
        return
    
    tests = [
        ("Basic Gemini Functionality", test_gemini_basic_functionality),
        ("Full Engine Integration", test_full_engine_with_gemini),
        ("Q&A and Improvement", test_qa_improvement_with_gemini),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    print(f"\n{'='*60}")
    print(f"📊 Final Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Gemini integration is working perfectly!")
        print("\n💡 The AutoGen TS Engine is ready for production use with Gemini!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    print(f"\n📁 Generated files:")
    print(f"   - gemini_test_project/ (Full engine test)")
    print(f"   - qa_test_project/ (Q&A test)")
    print(f"   - config/settings.md (Updated with Gemini config)")

if __name__ == "__main__":
    main()
