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
    
    # Available LLM providers
    llm_providers = {
        "7": ("lm_studio", "LM Studio (Production)"),
        "8": ("gemini", "Gemini (Fast Testing)")
    }
    
    print("Available project types:")
    for key, (type_name, description) in project_types.items():
        print(f"  {key}. {description}")
    
    print("\nAvailable LLM providers:")
    for key, (provider_name, description) in llm_providers.items():
        print(f"  {key}. {description}")
    
    print()
    choice = input("Select option (1-8): ").strip()
    
    if choice not in project_types and choice not in llm_providers:
        print("❌ Invalid choice. Exiting.")
        sys.exit(1)
    
    if choice in project_types:
        project_type, description = project_types[choice]
        is_llm_switch = False
    else:
        provider_type, description = llm_providers[choice]
        is_llm_switch = True
    
    if is_llm_switch:
        # Handle LLM provider switching
        if provider_type == "lm_studio":
            # Switch to LM Studio configuration
            source = config_dir / "settings.md"
            target = config_dir / "settings.md"
            
            # Read current settings and update LLM provider
            if source.exists():
                content = source.read_text()
                # Update provider to LM Studio
                content = content.replace('provider: "gemini"', 'provider: "lm_studio"')
                content = content.replace('api_type: "google"', 'api_type: "open_ai"')
                content = content.replace('model_name: "gemini-1.5-flash"', 'model_name: "llama3"')
                content = content.replace('api_key: "your_google_api_key_here"', 'api_key: "lmstudio"')
                target.write_text(content)
                print("✅ Switched to LM Studio configuration!")
                print("Updated config/settings.md with LM Studio settings")
            else:
                print("❌ Current settings file not found!")
                
        elif provider_type == "gemini":
            # Switch to Gemini configuration
            source = config_dir / "gemini_settings.md"
            target = config_dir / "settings.md"
            
            if source.exists():
                shutil.copy2(source, target)
                print("✅ Switched to Gemini configuration!")
                print("Updated config/settings.md with Gemini settings")
                print("⚠️  Remember to set your Google API key!")
            else:
                print("❌ Gemini configuration file not found!")
                print("Expected: config/gemini_settings.md")
    else:
        # Handle project type switching
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
