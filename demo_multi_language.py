#!/usr/bin/env python3
"""
Multi-Language Demonstration for AutoGen TS Engine.
Shows all supported project types and languages.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from autogen_ts_engine.schemas import ProjectType
from autogen_ts_engine.config_parser import ConfigParser
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def main():
    """Demonstrate multi-language capabilities."""
    print("🚀 AutoGen TS Engine - Multi-Language Support")
    print("=" * 60)
    
    # Show all supported project types
    print("📋 SUPPORTED PROJECT TYPES:")
    print("=" * 60)
    
    project_types = [
        (ProjectType.PYTHON, "Python", "pip/setuptools", "pytest", "Modern Python applications"),
        (ProjectType.TYPESCRIPT, "TypeScript", "npm/yarn", "jest", "TypeScript applications"),
        (ProjectType.REACT, "React", "npm/yarn", "jest", "React applications with TypeScript"),
        (ProjectType.NODEJS, "Node.js", "npm/yarn", "jest", "Node.js server applications"),
        (ProjectType.JAVA, "Java", "maven/gradle", "junit", "Java applications with Spring"),
        (ProjectType.GO, "Go", "go modules", "testing", "Go applications with Gin"),
        (ProjectType.RUST, "Rust", "cargo", "builtin", "Rust applications with Actix"),
        (ProjectType.CUSTOM, "Custom", "configurable", "configurable", "Custom project types")
    ]
    
    for project_type, name, package_manager, test_framework, description in project_types:
        print(f"   🔧 {name}")
        print(f"      📦 Package Manager: {package_manager}")
        print(f"      🧪 Test Framework: {test_framework}")
        print(f"      📝 Description: {description}")
        print()
    
    # Show configuration examples
    print("⚙️ CONFIGURATION EXAMPLES:")
    print("=" * 60)
    
    config_examples = {
        "Python": {
            "project_type": "python",
            "language": "python",
            "python": {
                "package_manager": "pip",
                "test_command": "pytest",
                "build_command": "python setup.py build"
            }
        },
        "TypeScript": {
            "project_type": "typescript",
            "language": "typescript",
            "node": {
                "package_manager": "npm",
                "test_command": "npm test",
                "build_command": "npm run build"
            }
        },
        "React": {
            "project_type": "react",
            "language": "typescript",
            "framework": "react",
            "node": {
                "package_manager": "npm",
                "test_command": "npm test",
                "build_command": "npm run build"
            }
        },
        "Node.js": {
            "project_type": "nodejs",
            "language": "javascript",
            "framework": "express",
            "node": {
                "package_manager": "npm",
                "test_command": "npm test",
                "build_command": "npm run build"
            }
        },
        "Java": {
            "project_type": "java",
            "language": "java",
            "framework": "spring",
            "java": {
                "build_tool": "maven",
                "test_command": "mvn test",
                "build_command": "mvn clean install"
            }
        },
        "Go": {
            "project_type": "go",
            "language": "go",
            "framework": "gin",
            "go": {
                "go_version": "1.21",
                "test_command": "go test ./...",
                "build_command": "go build"
            }
        },
        "Rust": {
            "project_type": "rust",
            "language": "rust",
            "framework": "actix",
            "rust": {
                "cargo_version": "1.70",
                "test_command": "cargo test",
                "build_command": "cargo build"
            }
        }
    }
    
    for language, config in config_examples.items():
        print(f"   🔧 {language} Configuration:")
        print(f"      Project Type: {config['project_type']}")
        print(f"      Language: {config['language']}")
        if 'framework' in config:
            print(f"      Framework: {config['framework']}")
        print()
    
    # Show current configuration
    print("📖 CURRENT CONFIGURATION:")
    print("=" * 60)
    
    try:
        config_parser = ConfigParser()
        settings = config_parser.parse_settings(Path("config"))
        agents = config_parser.parse_agents(Path("config"))
        
        print(f"   📋 Project: {settings.project_name}")
        print(f"   🎯 Goal: {settings.project_goal}")
        print(f"   🔧 Type: {settings.project_type}")
        print(f"   🤖 Agents: {len(agents)}")
        print(f"   📁 Work Directory: {settings.work_dir}")
        print()
        
        # Show project config
        if hasattr(settings, 'project_config') and settings.project_config:
            print(f"   ⚙️ Project Configuration:")
            print(f"      Type: {settings.project_config.project_type}")
            print(f"      Language: {settings.project_config.language}")
            if settings.project_config.framework:
                print(f"      Framework: {settings.project_config.framework}")
            print()
            
    except Exception as e:
        print(f"   ❌ Error loading configuration: {e}")
        print()
    
    # Show how to switch project types
    print("🔄 HOW TO SWITCH PROJECT TYPES:")
    print("=" * 60)
    
    print("   1. Update config/settings.md:")
    print("      - Change project_type to desired type")
    print("      - Update project_config section")
    print("      - Modify work_dir if needed")
    print()
    
    print("   2. Example TypeScript configuration:")
    print("      project_type: \"typescript\"")
    print("      project_config:")
    print("        project_type: \"typescript\"")
    print("        language: \"typescript\"")
    print("        framework: \"react\"")
    print("        node:")
    print("          package_manager: \"npm\"")
    print("          test_command: \"npm test\"")
    print("          build_command: \"npm run build\"")
    print()
    
    print("   3. Run the engine:")
    print("      python test_mock_engine.py")
    print()
    
    # Show benefits of multi-language support
    print("🎯 BENEFITS OF MULTI-LANGUAGE SUPPORT:")
    print("=" * 60)
    
    benefits = [
        "🔧 **Flexible Development**: Choose the best language for your project",
        "🚀 **Modern Frameworks**: Support for React, Spring, Gin, Actix, and more",
        "📦 **Package Managers**: npm, pip, maven, cargo, go modules",
        "🧪 **Testing Frameworks**: jest, pytest, junit, builtin testing",
        "🏗️ **Build Systems**: webpack, vite, maven, cargo, go build",
        "📊 **Quality Tools**: ESLint, Prettier, Black, Flake8, and more",
        "🔍 **Type Safety**: TypeScript, mypy, Java generics, Rust types",
        "⚡ **Performance**: Choose high-performance languages when needed",
        "🔄 **Migration**: Easy to switch between languages as requirements change",
        "📈 **Scalability**: Support for microservices and distributed systems"
    ]
    
    for benefit in benefits:
        print(f"   {benefit}")
    
    print()
    
    # Show next steps
    print("🚀 NEXT STEPS:")
    print("=" * 60)
    
    next_steps = [
        "1. Choose your preferred project type",
        "2. Update the configuration in config/settings.md",
        "3. Run the engine to generate your project",
        "4. The engine will create the appropriate project structure",
        "5. All testing, quality checks, and documentation will be adapted",
        "6. Enjoy your multi-language development experience!"
    ]
    
    for step in next_steps:
        print(f"   {step}")
    
    print()
    print("🎉 The AutoGen TS Engine supports ALL major programming languages!")
    print("   From Python to TypeScript, Java to Rust, and everything in between.")
    print("   Choose the right tool for the job and let the engine handle the rest!")
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
