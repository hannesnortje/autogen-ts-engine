#!/usr/bin/env python3
"""
Simple Gemini Test Runner

This script prompts for your API key and runs the comprehensive test.
"""

import os
import sys
from pathlib import Path

def main():
    """Run Gemini test with API key input."""
    print("🚀 AutoGen TS Engine - Gemini Test Runner")
    print("=" * 50)
    
    # Check if API key is already set
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("🔑 Please enter your Google API key:")
        print("   Get it from: https://makersuite.google.com/app/apikey")
        print()
        api_key = input("API Key: ").strip()
        
        if not api_key:
            print("❌ No API key provided. Exiting.")
            return
        
        # Set the environment variable for this session
        os.environ["GOOGLE_API_KEY"] = api_key
        print("✅ API key set for this session")
    else:
        print(f"✅ API key found: {api_key[:10]}...")
    
    print("\n🧪 Running comprehensive Gemini test...")
    print("-" * 50)
    
    # Import and run the test
    try:
        from test_with_gemini import main as run_test
        run_test()
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you're running this from the project root directory")
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    main()
