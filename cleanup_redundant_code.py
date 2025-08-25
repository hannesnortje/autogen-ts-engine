#!/usr/bin/env python3
"""
Redundant Code Cleanup Script for AutoGen TS Engine

This script identifies and helps clean up redundant code patterns.
"""

import re
from pathlib import Path
from typing import List, Dict, Any


def analyze_redundant_code():
    """Analyze the codebase for redundant patterns."""
    
    print("🔍 AutoGen TS Engine - Redundant Code Analysis")
    print("=" * 60)
    
    # Patterns to look for
    redundant_patterns = {
        "duplicate_main_functions": {
            "pattern": r"def main\(\):",
            "files": [],
            "description": "Multiple main functions in same file"
        },
        "duplicate_imports": {
            "pattern": r"import sys",
            "files": [],
            "description": "Multiple sys imports in same file"
        },
        "duplicate_try_blocks": {
            "pattern": r"try:",
            "files": [],
            "description": "Excessive try-except blocks"
        },
        "duplicate_test_methods": {
            "pattern": r"def _test_",
            "files": [],
            "description": "Similar test method patterns"
        },
        "duplicate_logging": {
            "pattern": r"logger\.info\(",
            "files": [],
            "description": "Excessive logging statements"
        }
    }
    
    # Analyze Python files
    python_files = list(Path(".").rglob("*.py"))
    
    for file_path in python_files:
        if "venv" in str(file_path) or "__pycache__" in str(file_path):
            continue
            
        try:
            content = file_path.read_text()
            
            # Check for duplicate main functions
            main_matches = re.findall(r"def main\(\):", content)
            if len(main_matches) > 1:
                redundant_patterns["duplicate_main_functions"]["files"].append({
                    "file": str(file_path),
                    "count": len(main_matches)
                })
            
            # Check for duplicate sys imports
            sys_imports = re.findall(r"import sys", content)
            if len(sys_imports) > 1:
                redundant_patterns["duplicate_imports"]["files"].append({
                    "file": str(file_path),
                    "count": len(sys_imports)
                })
            
            # Check for excessive try blocks
            try_blocks = re.findall(r"try:", content)
            if len(try_blocks) > 10:  # Threshold for excessive try blocks
                redundant_patterns["duplicate_try_blocks"]["files"].append({
                    "file": str(file_path),
                    "count": len(try_blocks)
                })
            
            # Check for test methods
            test_methods = re.findall(r"def _test_", content)
            if len(test_methods) > 15:  # Threshold for excessive test methods
                redundant_patterns["duplicate_test_methods"]["files"].append({
                    "file": str(file_path),
                    "count": len(test_methods)
                })
            
            # Check for excessive logging
            logging_statements = re.findall(r"logger\.info\(", content)
            if len(logging_statements) > 20:  # Threshold for excessive logging
                redundant_patterns["duplicate_logging"]["files"].append({
                    "file": str(file_path),
                    "count": len(logging_statements)
                })
                
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
    
    # Report findings
    print("\n📊 Redundant Code Analysis Results:")
    print("=" * 60)
    
    total_issues = 0
    for pattern_name, pattern_data in redundant_patterns.items():
        if pattern_data["files"]:
            print(f"\n🔍 {pattern_name.replace('_', ' ').title()}:")
            print(f"   Description: {pattern_data['description']}")
            for file_info in pattern_data["files"]:
                print(f"   📁 {file_info['file']}: {file_info['count']} instances")
                total_issues += 1
    
    if total_issues == 0:
        print("\n✅ No significant redundant code patterns found!")
    else:
        print(f"\n⚠️  Found {total_issues} files with potential redundant code")
    
    return redundant_patterns


def suggest_cleanup_actions(redundant_patterns: Dict[str, Any]):
    """Suggest specific cleanup actions."""
    
    print("\n🛠️  Suggested Cleanup Actions:")
    print("=" * 60)
    
    # Check for specific issues
    if redundant_patterns["duplicate_main_functions"]["files"]:
        print("\n1. 🔧 Duplicate Main Functions:")
        for file_info in redundant_patterns["duplicate_main_functions"]["files"]:
            print(f"   📁 {file_info['file']}")
            print(f"      → Remove duplicate main functions (keep only one)")
            print(f"      → Consider moving test main functions to separate files")
    
    if redundant_patterns["duplicate_imports"]["files"]:
        print("\n2. 📦 Duplicate Imports:")
        for file_info in redundant_patterns["duplicate_imports"]["files"]:
            print(f"   📁 {file_info['file']}")
            print(f"      → Consolidate duplicate import statements")
            print(f"      → Use import grouping (standard library, third-party, local)")
    
    if redundant_patterns["duplicate_try_blocks"]["files"]:
        print("\n3. 🛡️  Excessive Try-Except Blocks:")
        for file_info in redundant_patterns["duplicate_try_blocks"]["files"]:
            print(f"   📁 {file_info['file']}")
            print(f"      → Consider using error recovery manager instead of try-except")
            print(f"      → Consolidate error handling logic")
    
    if redundant_patterns["duplicate_test_methods"]["files"]:
        print("\n4. 🧪 Excessive Test Methods:")
        for file_info in redundant_patterns["duplicate_test_methods"]["files"]:
            print(f"   📁 {file_info['file']}")
            print(f"      → Consider using parameterized tests")
            print(f"      → Consolidate similar test patterns")
    
    if redundant_patterns["duplicate_logging"]["files"]:
        print("\n5. 📝 Excessive Logging:")
        for file_info in redundant_patterns["duplicate_logging"]["files"]:
            print(f"   📁 {file_info['file']}")
            print(f"      → Consider using structured logging")
            print(f"      → Reduce verbose logging in production code")


def identify_specific_issues():
    """Identify specific redundant code issues."""
    
    print("\n🎯 Specific Issues Found:")
    print("=" * 60)
    
    # Check code_generator.py for duplicate main functions
    code_gen_file = Path("autogen_ts_engine/code_generator.py")
    if code_gen_file.exists():
        content = code_gen_file.read_text()
        main_functions = re.findall(r"def main\(\):", content)
        if len(main_functions) > 1:
            print(f"\n❌ {code_gen_file}: Multiple main functions detected")
            print("   → This file contains template code with main functions")
            print("   → These are for code generation, not actual execution")
            print("   → Consider: Remove or comment out template main functions")
    
    # Check integration_tester.py for excessive test methods
    integration_file = Path("autogen_ts_engine/integration_tester.py")
    if integration_file.exists():
        content = integration_file.read_text()
        test_methods = re.findall(r"def _test_", content)
        if len(test_methods) > 15:
            print(f"\n⚠️  {integration_file}: Many test methods ({len(test_methods)})")
            print("   → This is expected for comprehensive integration testing")
            print("   → Consider: Keep as is - this is intentional for thorough testing")
    
    # Check for redundant error handling patterns
    print(f"\n🔍 Checking for redundant error handling patterns...")
    redundant_error_handling = []
    
    for file_path in Path("autogen_ts_engine").rglob("*.py"):
        if file_path.name in ["error_recovery.py", "logging_utils.py"]:
            continue  # Skip files that should have error handling
            
        try:
            content = file_path.read_text()
            try_blocks = re.findall(r"try:", content)
            if len(try_blocks) > 5:
                redundant_error_handling.append({
                    "file": str(file_path),
                    "try_blocks": len(try_blocks)
                })
        except Exception:
            pass
    
    if redundant_error_handling:
        print(f"\n⚠️  Files with potential redundant error handling:")
        for file_info in redundant_error_handling:
            print(f"   📁 {file_info['file']}: {file_info['try_blocks']} try blocks")
            print(f"      → Consider using ErrorRecoveryManager instead")


def main():
    """Main function to run the redundant code analysis."""
    
    # Analyze redundant patterns
    redundant_patterns = analyze_redundant_code()
    
    # Suggest cleanup actions
    suggest_cleanup_actions(redundant_patterns)
    
    # Identify specific issues
    identify_specific_issues()
    
    print(f"\n✅ Analysis complete!")
    print(f"\n💡 Recommendations:")
    print(f"1. Review the specific issues identified above")
    print(f"2. Focus on code_generator.py template cleanup")
    print(f"3. Consider consolidating error handling patterns")
    print(f"4. Review logging verbosity in production code")
    print(f"5. Test thoroughly after any cleanup changes")


if __name__ == "__main__":
    main()
