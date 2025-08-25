#!/usr/bin/env python3
"""
Simple Q&A Test with Gemini

This script demonstrates the Q&A functionality using Gemini as the LLM provider.
"""

import os
import sys
from pathlib import Path

# Add the autogen_ts_engine to the path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Test Q&A functionality with Gemini."""
    print("🚀 AutoGen TS Engine - Q&A Test with Gemini")
    print("=" * 60)
    
    # Check API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY not found!")
        print("💡 Please set your API key:")
        print("   export GOOGLE_API_KEY='your_api_key_here'")
        return 1
    
    print("✅ Google API key found")
    
    # Create a simple test project
    test_project = Path("./qa_test_project")
    test_project.mkdir(exist_ok=True)
    
    # Create a simple Python file for testing
    test_file = test_project / "calculator.py"
    test_file.write_text("""
def add(a, b):
    \"\"\"Add two numbers.\"\"\"
    return a + b

def subtract(a, b):
    \"\"\"Subtract b from a.\"\"\"
    return a - b

def multiply(a, b):
    \"\"\"Multiply two numbers.\"\"\"
    return a * b

def divide(a, b):
    \"\"\"Divide a by b.\"\"\"
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

class Calculator:
    \"\"\"A simple calculator class.\"\"\"
    
    def __init__(self):
        self.history = []
    
    def calculate(self, operation, a, b):
        \"\"\"Perform a calculation and store in history.\"\"\"
        if operation == "add":
            result = add(a, b)
        elif operation == "subtract":
            result = subtract(a, b)
        elif operation == "multiply":
            result = multiply(a, b)
        elif operation == "divide":
            result = divide(a, b)
        else:
            raise ValueError(f"Unknown operation: {operation}")
        
        self.history.append({
            "operation": operation,
            "a": a,
            "b": b,
            "result": result
        })
        
        return result
    
    def get_history(self):
        \"\"\"Get calculation history.\"\"\"
        return self.history
""")
    
    print("✅ Created test project with calculator.py")
    
    # Test Gemini adapter directly
    try:
        from autogen_ts_engine.gemini_adapter import create_gemini_adapter, is_gemini_available
        from autogen_ts_engine.schemas import LLMBinding, LLMProvider
        
        if not is_gemini_available():
            print("❌ Gemini not available")
            return 1
        
        print("✅ Gemini is available")
        
        # Create Gemini binding
        llm_binding = LLMBinding(
            provider=LLMProvider.GEMINI,
            model_name="gemini-1.5-flash",
            api_key=api_key
        )
        
        # Create adapter
        adapter = create_gemini_adapter(llm_binding)
        if not adapter:
            print("❌ Failed to create Gemini adapter")
            return 1
        
        print("✅ Gemini adapter created successfully")
        
        # Test Q&A functionality
        print("\n🧪 Testing Q&A with Gemini...")
        print("-" * 40)
        
        # Read the test file
        with open(test_file, 'r') as f:
            code_content = f.read()
        
        # Test questions
        questions = [
            "What does the add function do?",
            "How does the Calculator class work?",
            "What happens if you divide by zero?",
            "How can I improve the error handling in this code?",
            "What tests should I write for this calculator?"
        ]
        
        for i, question in enumerate(questions, 1):
            print(f"\n❓ Question {i}: {question}")
            print("-" * 30)
            
            # Create context with the code
            context = f"""
Here's the Python code to analyze:

```python
{code_content}
```

Question: {question}

Please provide a detailed answer based on the code above.
"""
            
            try:
                response = adapter.generate_response(context)
                print(f"🤖 Answer: {response[:300]}...")
                if len(response) > 300:
                    print("   (truncated for display)")
            except Exception as e:
                print(f"❌ Error: {e}")
        
        print("\n✅ Q&A test completed successfully!")
        print("\n📁 Test files created:")
        print(f"   - {test_file}")
        
        return 0
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
