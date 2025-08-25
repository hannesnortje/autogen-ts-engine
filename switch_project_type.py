#!/usr/bin/env python3
"""
Project Type Switcher for AutoGen TS Engine

This script helps you switch between different project types by copying
the appropriate configuration files.
"""

import shutil
import sys
from pathlib import Path


def main():
    """Main function to switch project types."""
    
    print("🔄 AutoGen TS Engine - Project Type Switcher")
    print("=" * 50)
    
    # Check if config directory exists
    config_dir = Path("config")
    if not config_dir.exists():
        print("❌ Config directory not found!")
        print("Please run this script from the autogen-ts-engine directory.")
        sys.exit(1)
    
    # Available project types
    project_types = {
        "1": ("python", "Python (Default)"),
        "2": ("typescript", "TypeScript/React"),
        "3": ("java", "Java/Spring"),
        "4": ("go", "Go/Gin"),
        "5": ("rust", "Rust"),
        "6": ("custom", "Custom")
    }
    
    print("Available project types:")
    for key, (type_name, description) in project_types.items():
        print(f"  {key}. {description}")
    
    print()
    choice = input("Select project type (1-6): ").strip()
    
    if choice not in project_types:
        print("❌ Invalid choice. Exiting.")
        sys.exit(1)
    
    project_type, description = project_types[choice]
    
    if project_type == "python":
        # Python is the default, no need to copy
        print("✅ Python is already the default configuration.")
        print("Current settings in config/settings.md")
        
    elif project_type == "typescript":
        # Copy TypeScript example to settings
        source = config_dir / "typescript_example.md"
        target = config_dir / "settings.md"
        
        if source.exists():
            shutil.copy2(source, target)
            print("✅ Switched to TypeScript configuration!")
            print("Updated config/settings.md with TypeScript settings")
        else:
            print("❌ TypeScript example file not found!")
            print("Expected: config/typescript_example.md")
            
    elif project_type in ["java", "go", "rust"]:
        print(f"⚠️  {description} configuration not yet implemented.")
        print("You can create your own configuration by:")
        print("1. Copying config/settings.md to config/{project_type}_example.md")
        print("2. Modifying the project_type and project_config sections")
        print("3. Running this script again")
        
    elif project_type == "custom":
        print("📝 For custom project types:")
        print("1. Create your own config file (e.g., config/custom_example.md)")
        print("2. Modify the project_type and project_config sections")
        print("3. Copy it to config/settings.md when ready")
        
    print()
    print("🎯 Next steps:")
    print("1. Review the configuration in config/settings.md")
    print("2. Run the engine: python test_mock_engine.py")
    print("3. Or run with full LLM: python autogen_ts_engine/main.py")


if __name__ == "__main__":
    main()
