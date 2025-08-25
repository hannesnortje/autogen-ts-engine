#!/usr/bin/env python3
"""
Quick Setup for Gemini Testing

This script helps you set up Gemini testing quickly.
"""

import os
import sys
from pathlib import Path

def main():
    """Set up Gemini testing."""
    print("🚀 AutoGen TS Engine - Gemini Test Setup")
    print("=" * 50)
    
    # Check if API key is set
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY not found!")
        print("\n💡 To set up Gemini testing:")
        print("1. Get your API key from: https://makersuite.google.com/app/apikey")
        print("2. Set the environment variable:")
        print("   export GOOGLE_API_KEY='your_api_key_here'")
        print("3. Run the test script:")
        print("   python test_with_gemini.py")
        return
    
    print("✅ Google API key found!")
    print(f"🔑 Key preview: {api_key[:10]}...")
    
    # Create Gemini configuration
    config_content = f"""# Gemini Test Configuration

```yaml
project_name: "gemini_test_project"
project_goal: "Build a Python web application with FastAPI and modern best practices using Gemini for development."
project_type: "python"
num_sprints: 2
iterations_per_sprint: 3

llm_binding:
  provider: "gemini"
  model_name: "gemini-1.5-flash"
  api_type: "google"
  api_key: "{api_key}"
  cache_seed: 42

work_dir: "./gemini_test_project"
vector_db_path: "./gemini_project_db"
git_branch_prefix: "gemini-"
human_input_mode: "NEVER"

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
```
"""
    
    # Write configuration
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    
    with open(config_dir / "settings.md", "w") as f:
        f.write(config_content)
    
    print("✅ Created Gemini configuration in config/settings.md")
    
    print("\n🎯 Ready to test! Run one of these commands:")
    print("\n1. Full comprehensive test:")
    print("   python test_with_gemini.py")
    print("\n2. Quick engine test:")
    print("   python autogen_ts_engine/main.py")
    print("\n3. Q&A test:")
    print("   python qa_improvement_runner.py ./qa_test_project")
    
    print("\n📋 What will be tested:")
    print("   ✅ Basic Gemini functionality")
    print("   ✅ Full AutoGen TS Engine integration")
    print("   ✅ Multi-agent development sprints")
    print("   ✅ Q&A and improvement capabilities")
    print("   ✅ Code generation and analysis")
    print("   ✅ Project structure generation")
    print("   ✅ Testing and quality checks")

if __name__ == "__main__":
    main()
