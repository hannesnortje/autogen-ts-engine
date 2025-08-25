#!/usr/bin/env python3
"""
Quick Gemini Test

This script quickly tests if Gemini is working with your API key.
"""

import os
import sys
from pathlib import Path

def test_gemini():
    """Test basic Gemini functionality."""
    print("🧪 Quick Gemini Test")
    print("=" * 30)
    
    # Check API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY not found!")
        print("💡 Set it with: export GOOGLE_API_KEY='your_key_here'")
        return False
    
    print(f"✅ API key found: {api_key[:10]}...")
    
    try:
        # Test Gemini adapter
        from autogen_ts_engine.gemini_adapter import create_gemini_adapter, is_gemini_available
        from autogen_ts_engine.schemas import LLMBinding, LLMProvider
        
        if not is_gemini_available():
            print("❌ Gemini not available")
            return False
        
        print("✅ Gemini adapter available")
        
        # Create adapter
        llm_binding = LLMBinding(
            provider=LLMProvider.GEMINI,
            model_name="gemini-1.5-flash",
            api_key=api_key
        )
        
        adapter = create_gemini_adapter(llm_binding)
        if not adapter:
            print("❌ Failed to create Gemini adapter")
            return False
        
        print("✅ Gemini adapter created")
        
        # Test simple response
        print("🤖 Testing response generation...")
        prompt = "Say 'Hello from Gemini!' in a creative way."
        response = adapter.generate_response(prompt)
        
        if response and len(response) > 10:
            print("✅ Gemini is working!")
            print(f"📝 Response: {response}")
            return True
        else:
            print("❌ Empty or invalid response")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_gemini()
    if success:
        print("\n🎉 Gemini is ready for testing!")
        print("💡 Now you can run: python run_gemini_test.py")
    else:
        print("\n❌ Gemini test failed. Check your setup.")
