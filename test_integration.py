#!/usr/bin/env python3
"""
Comprehensive Integration Test for AutoGen TS Engine.
Tests all components, workflows, and system integration.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from autogen_ts_engine.integration_tester import IntegrationTester
from autogen_ts_engine.config_parser import ConfigParser
from autogen_ts_engine.sprint_runner import SprintRunner
from autogen_ts_engine.logging_utils import EngineLogger
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def main():
    """Run comprehensive integration testing."""
    print("🚀 AutoGen TS Engine - Comprehensive Integration Testing")
    print("=" * 60)
    
    # Create test project directory
    test_project_dir = Path("integration_test_project")
    test_project_dir.mkdir(exist_ok=True)
    
    try:
        # Initialize integration tester
        print("📋 Initializing integration tester...")
        tester = IntegrationTester(test_project_dir)
        
        # Run full integration test suite
        print("🔧 Running comprehensive integration tests...")
        health_report = tester.run_full_integration_test()
        
        # Display results
        print("\n" + "=" * 60)
        print("📊 INTEGRATION TEST RESULTS")
        print("=" * 60)
        
        # Overall health
        print(f"🏥 Overall System Health: {health_report.overall_health.upper()}")
        
        # Component status
        print("\n🔧 Component Status:")
        for component, status in health_report.component_status.items():
            status_icon = "✅" if status == "healthy" else "❌"
            print(f"   {status_icon} {component}: {status}")
        
        # Performance metrics
        print("\n⚡ Performance Metrics:")
        for metric, value in health_report.performance_metrics.items():
            if "time" in metric:
                print(f"   📈 {metric}: {value:.2f}s")
            elif "rate" in metric:
                print(f"   📊 {metric}: {value:.1f}%")
            else:
                print(f"   📈 {metric}: {value}")
        
        # Recommendations
        print("\n💡 Recommendations:")
        for rec in health_report.recommendations:
            print(f"   • {rec}")
        
        # Test summary
        total_tests = len(tester.test_results)
        passed_tests = sum(1 for r in tester.test_results if r.success)
        failed_tests = total_tests - passed_tests
        
        print(f"\n📋 Test Summary:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests} ✅")
        print(f"   Failed: {failed_tests} ❌")
        print(f"   Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        # Detailed test results
        print(f"\n🔍 Detailed Test Results:")
        for result in tester.test_results:
            status_icon = "✅" if result.success else "❌"
            print(f"   {status_icon} {result.test_name}: {result.duration:.2f}s")
            if not result.success and result.error_message:
                print(f"      Error: {result.error_message}")
        
        # Check if system is ready for production
        if health_report.overall_health == "healthy":
            print("\n🎉 SYSTEM STATUS: PRODUCTION READY!")
            print("   All critical components are functioning correctly.")
            print("   The AutoGen TS Engine is ready for deployment.")
        elif health_report.overall_health == "degraded":
            print("\n⚠️  SYSTEM STATUS: DEGRADED")
            print("   Some components have issues but the system is functional.")
            print("   Review recommendations before production deployment.")
        else:
            print("\n🚨 SYSTEM STATUS: UNHEALTHY")
            print("   Critical components are failing.")
            print("   System requires fixes before production deployment.")
        
        # Additional validation tests
        print("\n" + "=" * 60)
        print("🔍 ADDITIONAL VALIDATION TESTS")
        print("=" * 60)
        
        # Test configuration loading
        print("📖 Testing configuration loading...")
        try:
            config_parser = ConfigParser()
            settings = config_parser.parse_settings(Path("config"))
            agents = config_parser.parse_agents(Path("config"))
            print(f"   ✅ Configuration loaded successfully")
            print(f"   📋 Project: {settings.project_name}")
            print(f"   🤖 Agents: {len(agents)}")
        except Exception as e:
            print(f"   ❌ Configuration loading failed: {e}")
        
        # Test sprint runner initialization
        print("\n🏃 Testing sprint runner initialization...")
        try:
            logger = EngineLogger(debug_mode=False)
            sprint_runner = SprintRunner(
                settings=settings,
                logger=logger
            )
            print(f"   ✅ Sprint runner initialized successfully")
        except Exception as e:
            print(f"   ❌ Sprint runner initialization failed: {e}")
        
        # Test file generation
        print("\n📝 Testing file generation...")
        try:
            from autogen_ts_engine.code_generator import CodeGenerator
            generator = CodeGenerator(test_project_dir)
            success = generator.generate_project_structure(
                "integration_test_app",
                "Integration test application"
            )
            if success:
                print(f"   ✅ Project structure generated successfully")
                
                # Check generated files
                expected_files = [
                    "src/integration_test_app/main.py",
                    "tests/test_main.py",
                    "requirements.txt",
                    "README.md"
                ]
                
                created_files = []
                for file_path in expected_files:
                    if (test_project_dir / file_path).exists():
                        created_files.append(file_path)
                
                print(f"   📁 Files created: {len(created_files)}/{len(expected_files)}")
            else:
                print(f"   ❌ Project structure generation failed")
        except Exception as e:
            print(f"   ❌ File generation test failed: {e}")
        
        # Test error recovery system
        print("\n🛡️ Testing error recovery system...")
        try:
            from autogen_ts_engine.error_recovery import ErrorRecoveryManager
            error_recovery = ErrorRecoveryManager(test_project_dir)
            
            # Test error statistics
            stats = error_recovery.get_error_statistics()
            print(f"   ✅ Error recovery system active")
            print(f"   📊 Total errors handled: {stats.get('total_errors', 0)}")
            print(f"   📈 Recovery rate: {stats.get('recovery_rate', 0.0):.1f}%")
        except Exception as e:
            print(f"   ❌ Error recovery test failed: {e}")
        
        # Test artifact generation
        print("\n📊 Testing artifact generation...")
        try:
            from autogen_ts_engine.sprint_artifacts import SprintArtifactsManager
            artifacts_manager = SprintArtifactsManager(test_project_dir)
            
            # Test sprint summary generation
            test_data = {
                "start_time": "2025-08-25T10:00:00",
                "end_time": "2025-08-25T10:30:00",
                "success": True,
                "iterations_completed": 1,
                "total_iterations": 2,
                "artifacts_created": 1,
                "errors": [],
                "metrics": {"test_coverage": 85.0}
            }
            
            summary = artifacts_manager.create_sprint_summary(1, test_data)
            artifacts_manager.save_sprint_summary(summary)
            print(f"   ✅ Sprint summary generated successfully")
            
            # Test project report generation
            report_file = artifacts_manager.generate_project_report([summary])
            if report_file.exists():
                print(f"   ✅ Project report generated successfully")
            
        except Exception as e:
            print(f"   ❌ Artifact generation test failed: {e}")
        
        print("\n" + "=" * 60)
        print("🎯 INTEGRATION TESTING COMPLETE")
        print("=" * 60)
        
        if health_report.overall_health == "healthy":
            print("✅ All systems operational!")
            print("🚀 AutoGen TS Engine is ready for production use.")
            return 0
        else:
            print("⚠️  Some issues detected. Review recommendations above.")
            return 1
            
    except Exception as e:
        print(f"💥 Integration testing failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
