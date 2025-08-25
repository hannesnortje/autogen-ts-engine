#!/usr/bin/env python3
"""
Fix Redundant Code Script for AutoGen TS Engine

This script fixes the identified redundant code issues.
"""

import re
from pathlib import Path
from typing import List, Dict, Any


def fix_duplicate_imports():
    """Fix duplicate import statements."""
    
    print("🔧 Fixing duplicate imports...")
    
    # Fix cleanup_redundant_code.py
    cleanup_file = Path("cleanup_redundant_code.py")
    if cleanup_file.exists():
        content = cleanup_file.read_text()
        # Remove duplicate import os (it's already imported)
        content = re.sub(r'import os\n', '', content, count=1)
        cleanup_file.write_text(content)
        print("   ✅ Fixed cleanup_redundant_code.py")
    
    # Fix code_generator.py
    code_gen_file = Path("autogen_ts_engine/code_generator.py")
    if code_gen_file.exists():
        content = code_gen_file.read_text()
        # Remove duplicate sys imports
        lines = content.split('\n')
        fixed_lines = []
        sys_imported = False
        
        for line in lines:
            if line.strip() == 'import sys':
                if not sys_imported:
                    fixed_lines.append(line)
                    sys_imported = True
            else:
                fixed_lines.append(line)
        
        code_gen_file.write_text('\n'.join(fixed_lines))
        print("   ✅ Fixed autogen_ts_engine/code_generator.py")


def fix_template_main_functions():
    """Remove or comment out template main functions in code_generator.py."""
    
    print("🔧 Fixing template main functions...")
    
    code_gen_file = Path("autogen_ts_engine/code_generator.py")
    if code_gen_file.exists():
        content = code_gen_file.read_text()
        
        # Comment out template main functions (keep only the real one)
        lines = content.split('\n')
        fixed_lines = []
        in_template_main = False
        template_main_count = 0
        
        for line in lines:
            if 'def main():' in line and '"""Main application entry point."""' in content:
                # This is a template main function
                if template_main_count == 0:
                    # Keep the first one but comment it
                    fixed_lines.append('# Template main function (commented out)')
                    fixed_lines.append('# ' + line)
                    in_template_main = True
                    template_main_count += 1
                else:
                    # Comment out additional template main functions
                    fixed_lines.append('# ' + line)
                    in_template_main = True
            elif in_template_main and line.strip() == '':
                # End of template main function
                fixed_lines.append(line)
                in_template_main = False
            elif in_template_main:
                # Comment out template main function content
                if line.strip() and not line.startswith('#'):
                    fixed_lines.append('# ' + line)
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        
        code_gen_file.write_text('\n'.join(fixed_lines))
        print("   ✅ Commented out template main functions in code_generator.py")


def consolidate_error_handling():
    """Consolidate error handling patterns."""
    
    print("🔧 Consolidating error handling patterns...")
    
    # Files that should use ErrorRecoveryManager instead of try-except
    files_to_consolidate = [
        "autogen_ts_engine/agent_factory.py",
        "autogen_ts_engine/test_runner.py", 
        "autogen_ts_engine/node_ops.py"
    ]
    
    for file_path in files_to_consolidate:
        path = Path(file_path)
        if path.exists():
            content = path.read_text()
            
            # Add ErrorRecoveryManager import if not present
            if 'from .error_recovery import ErrorRecoveryManager' not in content:
                # Find the right place to add the import
                lines = content.split('\n')
                import_section_end = 0
                
                for i, line in enumerate(lines):
                    if line.startswith('import ') or line.startswith('from '):
                        import_section_end = i + 1
                
                # Add the import
                lines.insert(import_section_end, 'from .error_recovery import ErrorRecoveryManager')
                content = '\n'.join(lines)
            
            # Add ErrorRecoveryManager initialization in __init__ methods
            if 'ErrorRecoveryManager' in content and 'self.error_recovery' not in content:
                # Find __init__ methods and add error recovery initialization
                content = re.sub(
                    r'(def __init__\(self[^)]*\):.*?\n)',
                    r'\1        self.error_recovery = ErrorRecoveryManager(self.project_dir)\n',
                    content,
                    flags=re.DOTALL
                )
            
            path.write_text(content)
            print(f"   ✅ Added ErrorRecoveryManager to {file_path}")


def optimize_logging():
    """Optimize excessive logging statements."""
    
    print("🔧 Optimizing logging statements...")
    
    # Files with excessive logging
    files_to_optimize = [
        "autogen_ts_engine/integration_tester.py",
        "autogen_ts_engine/sprint_runner.py"
    ]
    
    for file_path in files_to_optimize:
        path = Path(file_path)
        if path.exists():
            content = path.read_text()
            
            # Reduce verbose logging in production code
            # Replace some info logs with debug logs
            content = re.sub(
                r'logger\.info\(f"([^"]*)"\)',
                r'logger.debug(f"\1")',
                content,
                count=5  # Only replace first 5 to be conservative
            )
            
            path.write_text(content)
            print(f"   ✅ Optimized logging in {file_path}")


def remove_redundant_test_patterns():
    """Remove redundant test patterns in integration_tester.py."""
    
    print("🔧 Optimizing test patterns...")
    
    integration_file = Path("autogen_ts_engine/integration_tester.py")
    if integration_file.exists():
        content = integration_file.read_text()
        
        # Consolidate similar test result patterns
        # Replace repetitive success/failure patterns with helper methods
        
        # Add helper methods at the end of the class
        helper_methods = '''
    def _create_test_result(self, success: bool, details: Dict[str, Any] = None, error: str = None) -> Dict[str, Any]:
        """Helper method to create consistent test results."""
        result = {"success": success}
        if details:
            result["details"] = details
        if error:
            result["error"] = error
        return result
    
    def _log_test_result(self, test_name: str, success: bool, duration: float, error: str = None) -> None:
        """Helper method to log test results consistently."""
        if success:
            logger.info(f"✅ {test_name}: PASSED ({duration:.2f}s)")
        else:
            logger.warning(f"❌ {test_name}: FAILED ({duration:.2f}s)")
            if error:
                logger.error(f"   Error: {error}")
'''
        
        # Add helper methods before the last method
        if '_create_test_result' not in content:
            # Find the last method and add helpers before it
            lines = content.split('\n')
            last_method_index = -1
            
            for i, line in enumerate(lines):
                if line.strip().startswith('def _'):
                    last_method_index = i
            
            if last_method_index > 0:
                lines.insert(last_method_index, helper_methods)
                content = '\n'.join(lines)
        
        integration_file.write_text(content)
        print("   ✅ Added helper methods to integration_tester.py")


def main():
    """Main function to fix redundant code."""
    
    print("🛠️  AutoGen TS Engine - Fixing Redundant Code")
    print("=" * 60)
    
    try:
        # Fix duplicate imports
        fix_duplicate_imports()
        
        # Fix template main functions
        fix_template_main_functions()
        
        # Consolidate error handling
        consolidate_error_handling()
        
        # Optimize logging
        optimize_logging()
        
        # Remove redundant test patterns
        remove_redundant_test_patterns()
        
        print("\n✅ Redundant code fixes completed!")
        print("\n💡 Next steps:")
        print("1. Test the engine: python test_mock_engine.py")
        print("2. Run integration tests: python -m pytest")
        print("3. Check for any regressions")
        print("4. Commit the changes")
        
    except Exception as e:
        print(f"\n❌ Error during cleanup: {e}")
        print("Please review the changes manually before committing.")


if __name__ == "__main__":
    main()
