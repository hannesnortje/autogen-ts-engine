#!/usr/bin/env python3
"""
Quick Start Script for AutoGen TS Engine Projects

This script helps you quickly set up a new project with the AutoGen TS Engine.
"""

import os
import sys
import shutil
from pathlib import Path


def main():
    """Set up a new project with AutoGen TS Engine."""
    
    print("🚀 AutoGen TS Engine - Quick Project Setup")
    print("=" * 50)
    
    # Get project path
    if len(sys.argv) > 1:
        project_path = Path(sys.argv[1])
    else:
        project_path = Path(input("Enter project path (e.g., /media/hannesn/code/myproject): ").strip())
    
    # Validate project path
    if not project_path.parent.exists():
        print(f"❌ Parent directory does not exist: {project_path.parent}")
        sys.exit(1)
    
    # Create project directory
    if not project_path.exists():
        project_path.mkdir(parents=True)
        print(f"✅ Created project directory: {project_path}")
    else:
        print(f"✅ Using existing directory: {project_path}")
    
    # Change to project directory
    os.chdir(project_path)
    print(f"📁 Working directory: {project_path}")
    
    # Get engine path
    engine_path = Path(__file__).parent
    config_source = engine_path / "config"
    
    # Create config directory
    config_dir = project_path / "config"
    if not config_dir.exists():
        config_dir.mkdir()
        print("✅ Created config directory")
    
    # Copy configuration files
    print("\n📋 Setting up configuration files...")
    
    config_files = ["settings.md", "agents.md"]
    for file_name in config_files:
        source_file = config_source / file_name
        target_file = config_dir / file_name
        
        if source_file.exists():
            shutil.copy2(source_file, target_file)
            print(f"   ✅ Copied: {file_name}")
        else:
            print(f"   ❌ Missing: {file_name}")
    
    # Copy TypeScript example if needed
    typescript_example = config_source / "typescript_example.md"
    if typescript_example.exists():
        shutil.copy2(typescript_example, config_dir / "typescript_example.md")
        print("   ✅ Copied: typescript_example.md")
    
    # Copy Q&A configuration if needed
    qa_files = ["qa_improvement_settings.md", "qa_improvement_agents.md"]
    for file_name in qa_files:
        source_file = config_source / file_name
        if source_file.exists():
            shutil.copy2(source_file, config_dir / file_name)
            print(f"   ✅ Copied: {file_name}")
    
    print("\n🎯 Project setup complete!")
    print(f"\n📁 Project structure:")
    print(f"   {project_path}/")
    print(f"   ├── config/")
    for file_name in config_files:
        print(f"   │   ├── {file_name}")
    print(f"   │   ├── typescript_example.md")
    print(f"   │   ├── qa_improvement_settings.md")
    print(f"   │   └── qa_improvement_agents.md")
    print(f"   ├── src/ (will be created by engine)")
    print(f"   ├── tests/ (will be created by engine)")
    print(f"   └── scrum/ (will be created by engine)")
    
    print(f"\n🚀 To start your project:")
    print(f"1. Navigate to project directory:")
    print(f"   cd {project_path}")
    print(f"")
    print(f"2. Run the engine with mock LLM (fast):")
    print(f"   python {engine_path}/test_mock_engine.py")
    print(f"")
    print(f"3. Or run with full LLM (requires LM Studio):")
    print(f"   python {engine_path}/autogen_ts_engine/main.py")
    print(f"")
    print(f"4. For Q&A and improvements:")
    print(f"   python {engine_path}/qa_improvement_runner.py .")
    print(f"")
    print(f"💡 Tips:")
    print(f"   - Edit config/settings.md to customize your project")
    print(f"   - Use typescript_example.md for TypeScript projects")
    print(f"   - The engine will create all project files automatically")


if __name__ == "__main__":
    main()
