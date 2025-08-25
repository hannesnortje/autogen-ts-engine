#!/usr/bin/env python3
"""
Demo script for Q&A and Improvement Sessions

This script demonstrates how to use the AutoGen TS Engine for Q&A and improvement sessions
on existing projects.
"""

import os
import sys
from pathlib import Path

# Add the autogen_ts_engine to the path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Demo the Q&A and improvement capabilities."""
    
    print("🚀 AutoGen TS Engine - Q&A and Improvement Demo")
    print("=" * 60)
    
    # Check if we have a project to analyze
    demo_project = "./python_project"  # Use the project created by the engine
    
    if not Path(demo_project).exists():
        print("❌ No existing project found for Q&A session.")
        print("Please run the engine first to create a project:")
        print("   python test_mock_engine.py")
        print()
        print("Then run this demo again.")
        return 1
    
    print(f"✅ Found project: {demo_project}")
    print()
    
    # Import the Q&A runner
    try:
        from qa_improvement_runner import QAImprovementRunner
    except ImportError as e:
        print(f"❌ Error importing Q&A runner: {e}")
        print("Make sure qa_improvement_runner.py exists in the current directory.")
        return 1
    
    # Initialize the Q&A runner
    print("🔧 Initializing Q&A and Improvement Runner...")
    runner = QAImprovementRunner(demo_project)
    
    # Index the project
    print("📚 Indexing project for Q&A sessions...")
    runner.index_project()
    
    print("\n🎯 Demo Options:")
    print("1. Quick Project Analysis")
    print("2. Interactive Q&A Session")
    print("3. Improvement Sprint Demo")
    print("4. Full Demo (Analysis + Q&A + Improvements)")
    
    choice = input("\nSelect demo option (1-4): ").strip()
    
    if choice == "1":
        print("\n📊 Running Quick Project Analysis...")
        analysis = runner.analyze_project()
        
        print("\n" + "="*50)
        print("📋 ANALYSIS RESULTS")
        print("="*50)
        
        for area, result in analysis.items():
            if result:  # Only show areas with results
                print(f"\n🔍 {area.upper().replace('_', ' ')}:")
                print("-" * 30)
                print(f"Agent: {result.get('agent', 'Unknown')}")
                print(f"Analysis: {result.get('analysis', 'No analysis available')[:200]}...")
    
    elif choice == "2":
        print("\n💬 Starting Interactive Q&A Session...")
        print("You can ask questions like:")
        print("- 'How does the main function work?'")
        print("- 'What tests are missing?'")
        print("- 'How can I improve error handling?'")
        print("- 'What's the project architecture?'")
        print()
        runner.interactive_qa_session()
    
    elif choice == "3":
        print("\n🔧 Running Improvement Sprint Demo...")
        improvements = runner.run_improvement_sprint()
        
        print("\n" + "="*50)
        print("🔧 IMPROVEMENT RESULTS")
        print("="*50)
        
        for agent, result in improvements.items():
            print(f"\n🤖 {agent}:")
            print("-" * 30)
            print(f"Implemented: {result.get('implemented', False)}")
            print(f"Suggestions: {result.get('suggestions', 'No suggestions')[:200]}...")
    
    elif choice == "4":
        print("\n🎯 Running Full Demo...")
        
        # 1. Analysis
        print("\n📊 Step 1: Project Analysis...")
        analysis = runner.analyze_project()
        print("✅ Analysis completed!")
        
        # 2. Improvements
        print("\n🔧 Step 2: Improvement Sprint...")
        improvements = runner.run_improvement_sprint()
        print("✅ Improvements completed!")
        
        # 3. Q&A Session
        print("\n💬 Step 3: Interactive Q&A Session...")
        print("Ask questions about your project!")
        runner.interactive_qa_session()
        
        print("\n🎉 Full demo completed!")
    
    else:
        print("❌ Invalid choice. Exiting.")
        return 1
    
    print("\n✅ Demo completed successfully!")
    print("\n💡 Next Steps:")
    print("1. Use the Q&A runner on your own projects:")
    print("   python qa_improvement_runner.py ./your_project")
    print()
    print("2. Customize the Q&A agents in config/qa_improvement_agents.md")
    print()
    print("3. Adjust settings in config/qa_improvement_settings.md")
    print()
    print("4. Run improvement sprints on your codebase")
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
