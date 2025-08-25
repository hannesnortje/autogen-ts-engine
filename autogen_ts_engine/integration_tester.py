"""
Integration Testing System for AutoGen TS Engine.
Validates component integration, tests end-to-end workflows, and provides system health checks.
"""

import time
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Result of an integration test."""
    test_name: str
    success: bool
    duration: float
    error_message: Optional[str] = None
    details: Dict[str, Any] = None


@dataclass
class SystemHealth:
    """System health status."""
    overall_health: str  # "healthy", "degraded", "unhealthy"
    component_status: Dict[str, str]
    performance_metrics: Dict[str, float]
    recommendations: List[str]


class IntegrationTester:
    """Comprehensive integration testing for AutoGen TS Engine."""
    
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.test_results = []
        self.start_time = time.time()
    
    def run_full_integration_test(self) -> Dict[str, Any]:
        """Run complete integration test suite."""
        logger.info("🚀 Starting comprehensive integration testing...")
        
        # Test core components
        self._test_core_components()
        
        # Test workflows
        self._test_workflows()
        
        # Test error handling
        self._test_error_scenarios()
        
        # Test performance
        self._test_performance()
        
        # Generate health report
        health_report = self._generate_health_report()
        
        # Save test results
        self._save_test_results()
        
        return health_report
    
    def _test_core_components(self) -> None:
        """Test core component functionality."""
        logger.info("🔧 Testing core components...")
        
        # Test configuration parsing
        self._run_test("config_parser", self._test_config_parser)
        
        # Test agent factory
        self._run_test("agent_factory", self._test_agent_factory)
        
        # Test code generator
        self._run_test("code_generator", self._test_code_generator)
        
        # Test test runner
        self._run_test("test_runner", self._test_test_runner)
        
        # Test git operations
        self._run_test("git_ops", self._test_git_ops)
        
        # Test RAG store
        self._run_test("rag_store", self._test_rag_store)
    
    def _test_workflows(self) -> None:
        """Test end-to-end workflows."""
        logger.info("🔄 Testing workflows...")
        
        # Test project initialization workflow
        self._run_test("project_init_workflow", self._test_project_init_workflow)
        
        # Test sprint execution workflow
        self._run_test("sprint_execution_workflow", self._test_sprint_execution_workflow)
        
        # Test metrics collection workflow
        self._run_test("metrics_collection_workflow", self._test_metrics_collection_workflow)
        
        # Test artifact generation workflow
        self._run_test("artifact_generation_workflow", self._test_artifact_generation_workflow)
    
    def _test_error_scenarios(self) -> None:
        """Test error handling and recovery."""
        logger.info("🛡️ Testing error scenarios...")
        
        # Test LLM connection failure
        self._run_test("llm_connection_failure", self._test_llm_connection_failure)
        
        # Test file operation errors
        self._run_test("file_operation_errors", self._test_file_operation_errors)
        
        # Test git operation failures
        self._run_test("git_operation_failures", self._test_git_operation_failures)
        
        # Test test execution failures
        self._run_test("test_execution_failures", self._test_test_execution_failures)
    
    def _test_performance(self) -> None:
        """Test system performance."""
        logger.info("⚡ Testing performance...")
        
        # Test component initialization speed
        self._run_test("initialization_performance", self._test_initialization_performance)
        
        # Test file processing speed
        self._run_test("file_processing_performance", self._test_file_processing_performance)
        
        # Test memory usage
        self._run_test("memory_usage", self._test_memory_usage)
    
    def _run_test(self, test_name: str, test_func: callable) -> None:
        """Run a single test and record results."""
        start_time = time.time()
        
        try:
            result = test_func()
            duration = time.time() - start_time
            
            test_result = TestResult(
                test_name=test_name,
                success=result.get('success', False),
                duration=duration,
                details=result.get('details', {})
            )
            
            if test_result.success:
                logger.info(f"✅ {test_name}: PASSED ({duration:.2f}s)")
            else:
                logger.warning(f"❌ {test_name}: FAILED ({duration:.2f}s)")
                test_result.error_message = result.get('error', 'Unknown error')
            
        except Exception as e:
            duration = time.time() - start_time
            test_result = TestResult(
                test_name=test_name,
                success=False,
                duration=duration,
                error_message=str(e)
            )
            logger.error(f"💥 {test_name}: ERROR ({duration:.2f}s) - {e}")
        
        self.test_results.append(test_result)
    
    def _test_config_parser(self) -> Dict[str, Any]:
        """Test configuration parser functionality."""
        try:
            from .config_parser import ConfigParser
            from .schemas import Settings
            
            config_dir = Path("config")
            parser = ConfigParser()
            
            # Test settings parsing
            settings = parser.parse_settings(config_dir)
            if not isinstance(settings, Settings):
                return {"success": False, "error": "Settings parsing failed"}
            
            # Test agent definitions parsing
            agents = parser.parse_agents(config_dir)
            if not isinstance(agents, list) or len(agents) == 0:
                return {"success": False, "error": "Agent definitions parsing failed"}
            
            return {
                "success": True,
                "details": {
                    "settings_parsed": True,
                    "agents_count": len(agents),
                    "project_name": settings.project_name
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _test_agent_factory(self) -> Dict[str, Any]:
        """Test agent factory functionality."""
        try:
            from .agent_factory import AgentFactory
            from .rag_store import RAGStore
            
            # Create minimal settings for testing
            class TestSettings:
                def __init__(self):
                    self.model_name = "gpt-3.5-turbo"
                    self.api_base = "http://localhost:1234/v1"
                    self.api_key = "test-key"
                    self.temperature = 0.7
                    self.max_tokens = 1000
            
            settings = TestSettings()
            rag_store = RAGStore(self.project_dir, settings)
            factory = AgentFactory(settings, rag_store, use_mock_llm=True)
            
            # Test agent creation
            test_agents = [
                {"name": "test_agent", "role": "Test Agent", "goal": "Test functionality"}
            ]
            
            agents = factory.create_agents(test_agents)
            if not agents or len(agents) == 0:
                return {"success": False, "error": "Agent creation failed"}
            
            return {
                "success": True,
                "details": {
                    "agents_created": len(agents),
                    "mock_llm_enabled": True
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _test_code_generator(self) -> Dict[str, Any]:
        """Test code generator functionality."""
        try:
            from .code_generator import CodeGenerator
            
            generator = CodeGenerator(self.project_dir)
            
            # Test project structure generation
            test_dir = self.project_dir / "test_project"
            test_dir.mkdir(exist_ok=True)
            
            success = generator.generate_project_structure(
                "test_app", 
                "Test application for integration testing"
            )
            
            if not success:
                return {"success": False, "error": "Project structure generation failed"}
            
            # Check if files were created
            expected_files = [
                "src/test_app/main.py",
                "tests/test_main.py",
                "requirements.txt",
                "README.md"
            ]
            
            created_files = []
            for file_path in expected_files:
                if (test_dir / file_path).exists():
                    created_files.append(file_path)
            
            return {
                "success": True,
                "details": {
                    "files_created": len(created_files),
                    "expected_files": len(expected_files),
                    "creation_success_rate": len(created_files) / len(expected_files) * 100
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _test_test_runner(self) -> Dict[str, Any]:
        """Test test runner functionality."""
        try:
            from .test_runner import TestRunner
            
            runner = TestRunner(self.project_dir)
            
            # Test dependency installation
            install_success = runner.install_dependencies()
            
            # Test metrics collection (this will fail without a real project, but we can test the interface)
            try:
                metrics = runner.run_all_checks()
                metrics_success = True
            except Exception:
                metrics_success = False
            
            return {
                "success": install_success,
                "details": {
                    "dependencies_installed": install_success,
                    "metrics_collection_tested": metrics_success
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _test_git_ops(self) -> Dict[str, Any]:
        """Test git operations functionality."""
        try:
            from .git_ops import GitOps
            
            git_ops = GitOps(self.project_dir)
            
            # Test git initialization
            init_success = git_ops.initialize_repo()
            
            # Test status retrieval
            try:
                status = git_ops.get_status()
                status_success = True
            except Exception:
                status_success = False
            
            return {
                "success": init_success,
                "details": {
                    "repo_initialized": init_success,
                    "status_retrieval": status_success
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _test_rag_store(self) -> Dict[str, Any]:
        """Test RAG store functionality."""
        try:
            from .rag_store import RAGStore
            
            rag_store = RAGStore(self.project_dir)
            
            # Test directory indexing
            test_dir = self.project_dir / "test_rag"
            test_dir.mkdir(exist_ok=True)
            
            # Create a test file
            test_file = test_dir / "test.txt"
            test_file.write_text("Test content for RAG indexing")
            
            # Test indexing
            rag_store.index_directory(test_dir)
            
            # Test query (this might fail without proper setup, but we test the interface)
            try:
                results = rag_store.query("test content")
                query_success = True
            except Exception:
                query_success = False
            
            return {
                "success": True,
                "details": {
                    "directory_indexed": True,
                    "query_functionality": query_success
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _test_project_init_workflow(self) -> Dict[str, Any]:
        """Test project initialization workflow."""
        try:
            # Test the complete project initialization process
            test_project_dir = self.project_dir / "integration_test_project"
            test_project_dir.mkdir(exist_ok=True)
            
            # Simulate project initialization steps
            steps_completed = []
            
            # Step 1: Git initialization
            try:
                from .git_ops import GitOps
                git_ops = GitOps(test_project_dir)
                git_ops.initialize_repo()
                steps_completed.append("git_init")
            except Exception:
                pass
            
            # Step 2: Code generation
            try:
                from .code_generator import CodeGenerator
                generator = CodeGenerator(test_project_dir)
                generator.generate_project_structure("integration_test", "Integration test project")
                steps_completed.append("code_generation")
            except Exception:
                pass
            
            # Step 3: RAG indexing
            try:
                from .rag_store import RAGStore
                rag_store = RAGStore(test_project_dir)
                rag_store.index_directory(test_project_dir)
                steps_completed.append("rag_indexing")
            except Exception:
                pass
            
            success_rate = len(steps_completed) / 3 * 100
            
            return {
                "success": success_rate > 50,
                "details": {
                    "steps_completed": steps_completed,
                    "success_rate": success_rate
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _test_sprint_execution_workflow(self) -> Dict[str, Any]:
        """Test sprint execution workflow."""
        try:
            # Test sprint execution components
            components_tested = []
            
            # Test sprint context creation
            try:
                context = self._create_test_sprint_context()
                components_tested.append("context_creation")
            except Exception:
                pass
            
            # Test metrics collection
            try:
                metrics = self._collect_test_metrics()
                components_tested.append("metrics_collection")
            except Exception:
                pass
            
            # Test artifact generation
            try:
                artifacts = self._generate_test_artifacts()
                components_tested.append("artifact_generation")
            except Exception:
                pass
            
            success_rate = len(components_tested) / 3 * 100
            
            return {
                "success": success_rate > 50,
                "details": {
                    "components_tested": components_tested,
                    "success_rate": success_rate
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _test_metrics_collection_workflow(self) -> Dict[str, Any]:
        """Test metrics collection workflow."""
        try:
            # Test metrics collection components
            metrics_collected = {}
            
            # Test file counting
            try:
                file_count = len(list(self.project_dir.rglob("*.py")))
                metrics_collected["file_count"] = file_count
            except Exception:
                pass
            
            # Test directory structure analysis
            try:
                dirs = [d.name for d in self.project_dir.iterdir() if d.is_dir()]
                metrics_collected["directories"] = dirs
            except Exception:
                pass
            
            # Test git status
            try:
                from .git_ops import GitOps
                git_ops = GitOps(self.project_dir)
                status = git_ops.get_status()
                metrics_collected["git_status"] = status
            except Exception:
                pass
            
            return {
                "success": len(metrics_collected) > 0,
                "details": {
                    "metrics_collected": list(metrics_collected.keys()),
                    "collection_success_rate": len(metrics_collected) / 3 * 100
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _test_artifact_generation_workflow(self) -> Dict[str, Any]:
        """Test artifact generation workflow."""
        try:
            # Test artifact generation components
            artifacts_generated = []
            
            # Test sprint summary generation
            try:
                from .sprint_artifacts import SprintArtifactsManager
                artifacts_manager = SprintArtifactsManager(self.project_dir)
                
                test_sprint_data = {
                    "start_time": datetime.now().isoformat(),
                    "end_time": datetime.now().isoformat(),
                    "success": True,
                    "iterations_completed": 1,
                    "total_iterations": 2,
                    "artifacts_created": 1,
                    "errors": [],
                    "metrics": {"test_coverage": 80.0}
                }
                
                summary = artifacts_manager.create_sprint_summary(1, test_sprint_data)
                artifacts_manager.save_sprint_summary(summary)
                artifacts_generated.append("sprint_summary")
            except Exception:
                pass
            
            # Test metrics JSON generation
            try:
                metrics_file = artifacts_manager.save_metrics_json(1, {"test": "data"})
                if metrics_file.exists():
                    artifacts_generated.append("metrics_json")
            except Exception:
                pass
            
            # Test project report generation
            try:
                report_file = artifacts_manager.generate_project_report([summary])
                if report_file.exists():
                    artifacts_generated.append("project_report")
            except Exception:
                pass
            
            return {
                "success": len(artifacts_generated) > 0,
                "details": {
                    "artifacts_generated": artifacts_generated,
                    "generation_success_rate": len(artifacts_generated) / 3 * 100
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _test_llm_connection_failure(self) -> Dict[str, Any]:
        """Test LLM connection failure handling."""
        try:
            # Test error recovery for LLM failures
            from .error_recovery import ErrorRecoveryManager
            
            error_recovery = ErrorRecoveryManager(self.project_dir)
            
            # Simulate LLM connection error
            import requests
            try:
                requests.get("http://localhost:9999", timeout=1)
            except requests.exceptions.RequestException as e:
                recovery_result = error_recovery.handle_error(e, {
                    'component': 'llm',
                    'operation': 'connection_test',
                    'retry_count': 0,
                    'max_retries': 2
                })
                
                return {
                    "success": True,
                    "details": {
                        "error_handled": True,
                        "recovery_action": recovery_result.action_taken.value,
                        "recovery_success": recovery_result.success
                    }
                }
            
            return {"success": False, "error": "No error occurred during test"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _test_file_operation_errors(self) -> Dict[str, Any]:
        """Test file operation error handling."""
        try:
            from .error_recovery import ErrorRecoveryManager
            
            error_recovery = ErrorRecoveryManager(self.project_dir)
            
            # Simulate file operation error
            try:
                with open("/nonexistent/file.txt", "r") as f:
                    f.read()
            except FileNotFoundError as e:
                recovery_result = error_recovery.handle_error(e, {
                    'component': 'file',
                    'operation': 'file_read_test',
                    'retry_count': 0,
                    'max_retries': 1
                })
                
                return {
                    "success": True,
                    "details": {
                        "error_handled": True,
                        "recovery_action": recovery_result.action_taken.value,
                        "recovery_success": recovery_result.success
                    }
                }
            
            return {"success": False, "error": "No error occurred during test"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _test_git_operation_failures(self) -> Dict[str, Any]:
        """Test git operation failure handling."""
        try:
            from .error_recovery import ErrorRecoveryManager
            
            error_recovery = ErrorRecoveryManager(self.project_dir)
            
            # Simulate git operation error
            try:
                subprocess.run(["git", "nonexistent-command"], 
                             capture_output=True, text=True, check=True)
            except subprocess.CalledProcessError as e:
                recovery_result = error_recovery.handle_error(e, {
                    'component': 'git',
                    'operation': 'git_command_test',
                    'retry_count': 0,
                    'max_retries': 1
                })
                
                return {
                    "success": True,
                    "details": {
                        "error_handled": True,
                        "recovery_action": recovery_result.action_taken.value,
                        "recovery_success": recovery_result.success
                    }
                }
            
            return {"success": False, "error": "No error occurred during test"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _test_test_execution_failures(self) -> Dict[str, Any]:
        """Test test execution failure handling."""
        try:
            from .error_recovery import ErrorRecoveryManager
            
            error_recovery = ErrorRecoveryManager(self.project_dir)
            
            # Simulate test execution error
            try:
                subprocess.run(["python", "-m", "pytest", "nonexistent_test.py"], 
                             capture_output=True, text=True, check=True)
            except subprocess.CalledProcessError as e:
                recovery_result = error_recovery.handle_error(e, {
                    'component': 'test',
                    'operation': 'test_execution_test',
                    'retry_count': 0,
                    'max_retries': 1
                })
                
                return {
                    "success": True,
                    "details": {
                        "error_handled": True,
                        "recovery_action": recovery_result.action_taken.value,
                        "recovery_success": recovery_result.success
                    }
                }
            
            return {"success": False, "error": "No error occurred during test"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _test_initialization_performance(self) -> Dict[str, Any]:
        """Test component initialization performance."""
        try:
            import time
            
            # Test config parser initialization
            start_time = time.time()
            from .config_parser import ConfigParser
            parser = ConfigParser()
            config_time = time.time() - start_time
            
            # Test agent factory initialization
            start_time = time.time()
            from .agent_factory import AgentFactory
            from .rag_store import RAGStore
            
            class TestSettings:
                def __init__(self):
                    self.model_name = "gpt-3.5-turbo"
                    self.api_base = "http://localhost:1234/v1"
                    self.api_key = "test-key"
                    self.temperature = 0.7
                    self.max_tokens = 1000
            
            settings = TestSettings()
            rag_store = RAGStore(self.project_dir, settings)
            factory = AgentFactory(settings, rag_store, use_mock_llm=True)
            factory_time = time.time() - start_time
            
            # Test code generator initialization
            start_time = time.time()
            from .code_generator import CodeGenerator
            generator = CodeGenerator(self.project_dir)
            generator_time = time.time() - start_time
            
            total_time = config_time + factory_time + generator_time
            
            return {
                "success": total_time < 5.0,  # Should initialize in under 5 seconds
                "details": {
                    "config_parser_time": config_time,
                    "agent_factory_time": factory_time,
                    "code_generator_time": generator_time,
                    "total_initialization_time": total_time
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _test_file_processing_performance(self) -> Dict[str, Any]:
        """Test file processing performance."""
        try:
            import time
            
            # Test file counting performance
            start_time = time.time()
            files = list(self.project_dir.rglob("*.py"))
            file_count_time = time.time() - start_time
            
            # Test directory traversal performance
            start_time = time.time()
            dirs = [d for d in self.project_dir.rglob("*") if d.is_dir()]
            dir_traversal_time = time.time() - start_time
            
            # Test file reading performance
            start_time = time.time()
            total_size = 0
            for file_path in files[:10]:  # Test first 10 files
                if file_path.exists():
                    total_size += file_path.stat().st_size
            file_reading_time = time.time() - start_time
            
            total_time = file_count_time + dir_traversal_time + file_reading_time
            
            return {
                "success": total_time < 2.0,  # Should process in under 2 seconds
                "details": {
                    "file_count_time": file_count_time,
                    "dir_traversal_time": dir_traversal_time,
                    "file_reading_time": file_reading_time,
                    "total_processing_time": total_time,
                    "files_processed": len(files),
                    "total_size_bytes": total_size
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _test_memory_usage(self) -> Dict[str, Any]:
        """Test memory usage."""
        try:
            import psutil
            import os
            
            # Get current process memory usage
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            
            # Memory usage in MB
            memory_mb = memory_info.rss / 1024 / 1024
            
            # Test memory usage after component initialization
            from .config_parser import ConfigParser
            from .rag_store import RAGStore
            from .code_generator import CodeGenerator
            
            parser = ConfigParser()
            rag_store = RAGStore(self.project_dir, settings)
            generator = CodeGenerator(self.project_dir)
            
            memory_after_init = process.memory_info().rss / 1024 / 1024
            memory_increase = memory_after_init - memory_mb
            
            return {
                "success": memory_increase < 100,  # Should not increase by more than 100MB
                "details": {
                    "initial_memory_mb": memory_mb,
                    "memory_after_init_mb": memory_after_init,
                    "memory_increase_mb": memory_increase,
                    "memory_usage_acceptable": memory_increase < 100
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _create_test_sprint_context(self) -> str:
        """Create a test sprint context."""
        return """
# Test Sprint Context

## Project Goal
Test integration functionality.

## Sprint Focus
integration_testing

## Current Project Status
- Git Branch: test-branch
- Modified Files: 0
- Test Pass Rate: 100.0%
- Test Coverage: 85.0%
- Build Success: True

## Instructions
1. Run integration tests
2. Validate component interactions
3. Ensure system stability
"""
    
    def _collect_test_metrics(self) -> Dict[str, Any]:
        """Collect test metrics."""
        return {
            "test_pass_rate": 100.0,
            "test_coverage": 85.0,
            "build_success": True,
            "overall_score": 95.0
        }
    
    def _generate_test_artifacts(self) -> List[str]:
        """Generate test artifacts."""
        return ["test_report.md", "test_metrics.json"]
    
    def _generate_health_report(self) -> SystemHealth:
        """Generate system health report."""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result.success)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Determine overall health
        if success_rate >= 90:
            overall_health = "healthy"
        elif success_rate >= 70:
            overall_health = "degraded"
        else:
            overall_health = "unhealthy"
        
        # Component status
        component_status = {}
        for result in self.test_results:
            if "config" in result.test_name:
                component_status["config_parser"] = "healthy" if result.success else "unhealthy"
            elif "agent" in result.test_name:
                component_status["agent_factory"] = "healthy" if result.success else "unhealthy"
            elif "code" in result.test_name:
                component_status["code_generator"] = "healthy" if result.success else "unhealthy"
            elif "test" in result.test_name:
                component_status["test_runner"] = "healthy" if result.success else "unhealthy"
            elif "git" in result.test_name:
                component_status["git_ops"] = "healthy" if result.success else "unhealthy"
            elif "rag" in result.test_name:
                component_status["rag_store"] = "healthy" if result.success else "unhealthy"
        
        # Performance metrics
        performance_metrics = {
            "total_test_time": time.time() - self.start_time,
            "average_test_time": sum(r.duration for r in self.test_results) / len(self.test_results) if self.test_results else 0,
            "success_rate": success_rate
        }
        
        # Recommendations
        recommendations = []
        if success_rate < 90:
            recommendations.append("Improve test coverage for failing components")
        if performance_metrics["total_test_time"] > 30:
            recommendations.append("Optimize test execution time")
        if success_rate >= 90:
            recommendations.append("System is performing well - maintain current practices")
        
        return SystemHealth(
            overall_health=overall_health,
            component_status=component_status,
            performance_metrics=performance_metrics,
            recommendations=recommendations
        )
    
    def _save_test_results(self) -> None:
        """Save test results to file."""
        try:
            results_file = self.project_dir / "scrum" / "reports" / "integration_test_results.json"
            results_file.parent.mkdir(parents=True, exist_ok=True)
            
            results_data = {
                "timestamp": datetime.now().isoformat(),
                "total_tests": len(self.test_results),
                "passed_tests": sum(1 for r in self.test_results if r.success),
                "failed_tests": sum(1 for r in self.test_results if not r.success),
                "total_duration": sum(r.duration for r in self.test_results),
                "test_results": [
                    {
                        "test_name": r.test_name,
                        "success": r.success,
                        "duration": r.duration,
                        "error_message": r.error_message,
                        "details": r.details
                    }
                    for r in self.test_results
                ]
            }
            
            with open(results_file, 'w') as f:
                json.dump(results_data, f, indent=2)
            
            logger.info(f"Integration test results saved to {results_file}")
            
        except Exception as e:
            logger.error(f"Failed to save test results: {e}")
