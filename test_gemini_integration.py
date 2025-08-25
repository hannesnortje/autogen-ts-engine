#!/usr/bin/env python3
"""
Test Gemini Integration for AutoGen TS Engine

This script tests the Gemini LLM integration.
"""

import os
import sys
from pathlib import Path

# Add the autogen_ts_engine to the path
sys.path.insert(0, str(Path(__file__).parent))

def test_gemini_availability():
    """Test if Gemini is available."""
    print("🔍 Testing Gemini Availability...")
    
    try:
        from autogen_ts_engine.gemini_adapter import is_gemini_available, get_gemini_models
        from autogen_ts_engine.schemas import LLMBinding, LLMProvider
        
        if is_gemini_available():
            print("✅ Gemini is available!")
            models = get_gemini_models()
            print(f"📋 Available models: {', '.join(models)}")
            return True
        else:
            print("❌ Gemini is not available")
            print("💡 Install with: pip install google-generativeai")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_gemini_configuration():
    """Test Gemini configuration."""
    print("\n🔧 Testing Gemini Configuration...")
    
    try:
        from autogen_ts_engine.schemas import LLMBinding, LLMProvider
        
        # Test with environment variable
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("⚠️  GOOGLE_API_KEY not set")
            print("💡 Set with: export GOOGLE_API_KEY='your_api_key_here'")
            return False
        
        # Create LLM binding
        llm_binding = LLMBinding(
            provider=LLMProvider.GEMINI,
            model_name="gemini-1.5-flash",
            api_key=api_key
        )
        
        print("✅ Gemini configuration created successfully!")
        print(f"   Provider: {llm_binding.provider}")
        print(f"   Model: {llm_binding.model_name}")
        print(f"   API Type: {llm_binding.api_type}")
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_gemini_adapter():
    """Test Gemini adapter creation."""
    print("\n🤖 Testing Gemini Adapter...")
    
    try:
        from autogen_ts_engine.gemini_adapter import create_gemini_adapter
        from autogen_ts_engine.schemas import LLMBinding, LLMProvider
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("⚠️  GOOGLE_API_KEY not set, skipping adapter test")
            return False
        
        llm_binding = LLMBinding(
            provider=LLMProvider.GEMINI,
            model_name="gemini-1.5-flash",
            api_key=api_key
        )
        
        adapter = create_gemini_adapter(llm_binding)
        if adapter:
            print("✅ Gemini adapter created successfully!")
            return True
        else:
            print("❌ Failed to create Gemini adapter")
            return False
            
    except Exception as e:
        print(f"❌ Adapter error: {e}")
        return False

def test_gemini_response():
    """Test Gemini response generation."""
    print("\n💬 Testing Gemini Response Generation...")
    
    try:
        from autogen_ts_engine.gemini_adapter import create_gemini_adapter
        from autogen_ts_engine.schemas import LLMBinding, LLMProvider
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("⚠️  GOOGLE_API_KEY not set, skipping response test")
            return False
        
        llm_binding = LLMBinding(
            provider=LLMProvider.GEMINI,
            model_name="gemini-1.5-flash",
            api_key=api_key
        )
        
        adapter = create_gemini_adapter(llm_binding)
        if not adapter:
            print("❌ Failed to create adapter")
            return False
        
        # Test simple response
        prompt = "Hello! Can you help me write a simple Python function that adds two numbers?"
        response = adapter.generate_response(prompt)
        
        if response and len(response) > 10:
            print("✅ Gemini response generated successfully!")
            print(f"📝 Response preview: {response[:100]}...")
            return True
        else:
            print("❌ Empty or invalid response from Gemini")
            return False
            
    except Exception as e:
        print(f"❌ Response error: {e}")
        return False

def test_agent_factory_integration():
    """Test Gemini integration with AgentFactory."""
    print("\n🏭 Testing AgentFactory Integration...")
    
    try:
        from autogen_ts_engine.agent_factory import AgentFactory
        from autogen_ts_engine.schemas import Settings, LLMBinding, LLMProvider, ProjectType
        from autogen_ts_engine.rag_store import RAGStore
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("⚠️  GOOGLE_API_KEY not set, skipping integration test")
            return False
        
        # Create settings with Gemini
        llm_binding = LLMBinding(
            provider=LLMProvider.GEMINI,
            model_name="gemini-1.5-flash",
            api_key=api_key
        )
        
        settings = Settings(
            project_name="gemini_test",
            project_goal="Test Gemini integration",
            project_type=ProjectType.PYTHON,
            llm_binding=llm_binding,
            work_dir="./gemini_test_project"
        )
        
        # Create RAG store
        rag_store = RAGStore(Path(settings.work_dir), settings)
        
        # Create agent factory
        factory = AgentFactory(settings, rag_store, use_mock_llm=False)
        
        print("✅ AgentFactory with Gemini created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Integration error: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 AutoGen TS Engine - Gemini Integration Test")
    print("=" * 60)
    
    tests = [
        ("Gemini Availability", test_gemini_availability),
        ("Gemini Configuration", test_gemini_configuration),
        ("Gemini Adapter", test_gemini_adapter),
        ("Gemini Response", test_gemini_response),
        ("AgentFactory Integration", test_agent_factory_integration),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Gemini integration tests passed!")
        print("\n💡 Next steps:")
        print("1. Use Gemini for fast testing:")
        print("   python switch_project_type.py  # Select option 8")
        print("2. Run the engine with Gemini:")
        print("   python autogen_ts_engine/main.py")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        print("\n💡 Troubleshooting:")
        print("1. Install Gemini: pip install google-generativeai")
        print("2. Set API key: export GOOGLE_API_KEY='your_api_key_here'")
        print("3. Get API key from: https://makersuite.google.com/app/apikey")

if __name__ == "__main__":
    main()
