"""Sprint runner for orchestrating multi-agent development sprints."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

import autogen

from .agent_factory import AgentFactory
from .git_ops import GitOps
from .logging_utils import EngineLogger
from .node_ops import NodeOps
from .rag_store import RAGStore
from .rl_module import RLModule
from .schemas import AgentDefinition, Settings, SprintResult, ProjectType
from .code_generator import CodeGenerator
from .test_runner import TestRunner
from .sprint_artifacts import SprintArtifactsManager
from .error_recovery import ErrorRecoveryManager


class SprintRunner:
    """Orchestrates multi-agent development sprints."""
    
    def __init__(self, settings: Settings, logger: EngineLogger):
        self.settings = settings
        self.logger = logger
        
        # Initialize components
        self.work_dir = Path(settings.work_dir)
        self.scrum_dir = self.work_dir / "scrum"
        self.scrum_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize RAG store
        self.rag_store = RAGStore(settings.vector_db_path, settings.rag)
        
        # Initialize agents
        self.agent_factory = AgentFactory(settings, self.rag_store, use_mock_llm=True)
        
        # Initialize Node.js operations (only for TypeScript/Node.js projects)
        if settings.project_config.node is not None:
            self.node_ops = NodeOps(self.work_dir, settings.project_config.node)
        else:
            self.node_ops = None
        
        # Initialize Git operations
        self.git_ops = GitOps(self.work_dir, settings.git_branch_prefix)
        
        # Initialize RL module
        rl_data_path = self.work_dir / "rl_data"
        self.rl_module = RLModule(settings.rl, rl_data_path)
        
        # Initialize code generator
        self.code_generator = CodeGenerator(self.work_dir)
        
        # Initialize test runner
        self.test_runner = TestRunner(self.work_dir)
        
        # Initialize sprint artifacts manager
        self.artifacts_manager = SprintArtifactsManager(self.work_dir)
        
        # Initialize error recovery manager
        self.error_recovery = ErrorRecoveryManager(self.work_dir)
        
        # Agent instances
        self.agents = {}
        
        # Sprint state
        self.current_sprint = 0
        self.sprint_results = []
    
    def run_sprints(self, agent_definitions: List[AgentDefinition]) -> List[SprintResult]:
        """Run all configured sprints."""
        # Initialize project if needed
        if not self._initialize_project():
            return []
        
        # Create agents
        self.agents = self.agent_factory.create_agents(agent_definitions)
        
        # Index existing project files
        self._index_project_files()
        
        # Run sprints
        for sprint_num in range(1, self.settings.num_sprints + 1):
            self.current_sprint = sprint_num
            
            self.logger.sprint_start(sprint_num, self.settings.project_goal)
            
            # Run single sprint
            result = self._run_single_sprint(sprint_num, agent_definitions)
            self.sprint_results.append(result)
            
            self.logger.sprint_end(sprint_num, result.success, result.iterations_completed)
            
            # Save RL state
            self.rl_module.save_state()
            
            # Check if we should continue
            if not result.success and self.settings.debug_mode:
                self.logger.warning(f"Sprint {sprint_num} failed, stopping due to debug mode")
                break
        
        # Generate final project report
        self._generate_final_report()
        
        return self.sprint_results
    
    def _initialize_project(self) -> bool:
        """Initialize the project structure."""
        try:
            # Initialize Git repository
            if not self.git_ops.initialize_repo():
                self.logger.error("Failed to initialize Git repository")
                return False
            
            # Initialize project based on type
            if self.settings.project_type == ProjectType.TYPESCRIPT and self.node_ops is not None:
                if not (self.work_dir / "package.json").exists():
                    self.logger.info("Initializing TypeScript project...")
                    if not self.node_ops.initialize_project(
                        self.settings.project_name, 
                        self.settings.project_goal
                    ):
                        self.logger.error("Failed to initialize TypeScript project")
                        return False
            elif self.settings.project_type == ProjectType.PYTHON:
                if not (self.work_dir / "requirements.txt").exists():
                    self.logger.info("Initializing Python project...")
                    if not self._initialize_python_project():
                        self.logger.error("Failed to initialize Python project")
                        return False
            
            return True
            
        except Exception as e:
            # Handle error with recovery manager
            recovery_result = self.error_recovery.handle_error(e, {
                'component': 'project',
                'operation': 'initialization',
                'project_type': self.settings.project_type.value,
                'retry_count': 0,
                'max_retries': 1
            })
            
            if recovery_result.success:
                self.logger.info(f"Project initialization recovery successful: {recovery_result.action_taken.value}")
                return True
            else:
                self.logger.error(f"Project initialization recovery failed: {recovery_result.new_error}")
                return False
    
    def _index_project_files(self) -> None:
        """Index project files for RAG."""
        try:
            # Index source code
            self.rag_store.index_directory(self.work_dir / "src")
            
            # Index tests
            self.rag_store.index_directory(self.work_dir / "tests")
            
            # Index scrum artifacts
            self.rag_store.index_directory(self.scrum_dir)
            
            self.logger.info("Project files indexed for RAG")
            
        except Exception as e:
            self.logger.error_with_context(e, "File indexing")
    
    def _get_project_metrics(self) -> Dict:
        """Get project metrics based on project type."""
        if self.settings.project_type == ProjectType.TYPESCRIPT and self.node_ops is not None:
            return self.node_ops.get_project_metrics()
        elif self.settings.project_type == ProjectType.PYTHON:
            return self._get_python_project_metrics()
        else:
            # Default metrics for unsupported project types
            return {
                "test_pass_rate": 0.0,
                "test_coverage": 0.0,
                "code_complexity": 1.0,
                "dependency_count": 0,
                "build_success": False
            }
    
    def _get_python_project_metrics(self) -> Dict:
        """Get comprehensive metrics for Python projects using test runner."""
        try:
            # Install dependencies if needed
            self.test_runner.install_dependencies()
            
            # Run comprehensive tests and quality checks
            metrics = self.test_runner.run_all_checks()
            
            # Count dependencies
            requirements_path = self.work_dir / "requirements.txt"
            dependency_count = 0
            if requirements_path.exists():
                with open(requirements_path, 'r') as f:
                    lines = f.readlines()
                    # Count non-comment, non-empty lines
                    dependencies = [line.strip() for line in lines 
                                  if line.strip() and not line.startswith('#')]
                    dependency_count = len(dependencies)
            
            return {
                "test_pass_rate": (metrics.test_results.passed_tests / max(metrics.test_results.total_tests, 1)) * 100,
                "test_coverage": metrics.test_results.coverage_percentage or 0.0,
                "code_complexity": 1.0,  # Placeholder for now
                "dependency_count": dependency_count,
                "build_success": metrics.build_success,
                "overall_score": metrics.overall_score,
                "total_issues": metrics.total_issues,
                "quality_results": [
                    {
                        "tool": qr.tool,
                        "success": qr.success,
                        "issues": qr.issues_found
                    }
                    for qr in metrics.quality_results
                ]
            }
                
        except Exception as e:
            # Handle error with recovery manager
            recovery_result = self.error_recovery.handle_error(e, {
                'component': 'test',
                'operation': 'metrics_collection',
                'retry_count': 0,
                'max_retries': 2
            })
            
            if recovery_result.success:
                self.logger.info(f"Test metrics recovery successful: {recovery_result.action_taken.value}")
                # Could retry the operation here
                pass
            else:
                self.logger.error(f"Test metrics recovery failed: {recovery_result.new_error}")
            
            return {
                "test_pass_rate": 0.0,
                "test_coverage": 0.0,
                "code_complexity": 1.0,
                "dependency_count": 0,
                "build_success": False,
                "overall_score": 0.0,
                "total_issues": 0,
                "quality_results": []
            }
    
    def _count_modified_files(self) -> int:
        """Count modified files in the project."""
        try:
            # Get git status
            git_status = self.git_ops.get_status()
            return git_status.get('modified_files', 0)
        except Exception:
            return 0
    
    def _run_single_sprint(self, sprint_num: int, agent_definitions: List[AgentDefinition]) -> SprintResult:
        """Run a single sprint."""
        sprint_start_time = datetime.now().isoformat()
        
        try:
            # Create sprint branch
            if not self.git_ops.create_sprint_branch(sprint_num):
                return SprintResult(
                    sprint_number=sprint_num,
                    success=False,
                    iterations_completed=0,
                    errors=["Failed to create sprint branch"]
                )
            
            # Get sprint focus from RL
            sprint_focus = self.rl_module.get_sprint_focus()
            
            # Create sprint context
            sprint_context = self._create_sprint_context(sprint_num, sprint_focus)
            
            # Run group chat
            chat_result = self._run_group_chat(sprint_context, sprint_num)
            
            # Get project metrics
            metrics = self._get_project_metrics()
            
            # Save metrics for analysis
            self.artifacts_manager.save_metrics_json(sprint_num, metrics)
            
            # Update RL with sprint results
            sprint_reward = self._calculate_sprint_reward(metrics, chat_result)
            self.rl_module.update_outer_loop(sprint_reward, metrics)
            
            # Create sprint commit
            self._create_sprint_commit(sprint_num, chat_result)
            
            # Log sprint results
            self._log_sprint_results(sprint_num, chat_result, metrics)
            
            # Create sprint result
            sprint_result = SprintResult(
                sprint_number=sprint_num,
                success=chat_result["success"],
                iterations_completed=chat_result["iterations"],
                test_results=metrics,
                reward=sprint_reward,
                artifacts=chat_result["artifacts"],
                errors=chat_result["errors"]
            )
            
            # Create comprehensive sprint summary
            sprint_end_time = datetime.now().isoformat()
            sprint_data = {
                "start_time": sprint_start_time,
                "end_time": sprint_end_time,
                "success": sprint_result.success,
                "iterations_completed": sprint_result.iterations_completed,
                "total_iterations": self.settings.iterations_per_sprint,
                "artifacts_created": len(chat_result["artifacts"]),
                "errors": sprint_result.errors,
                "metrics": metrics
            }
            
            summary = self.artifacts_manager.create_sprint_summary(sprint_num, sprint_data)
            self.artifacts_manager.save_sprint_summary(summary)
            
            return sprint_result
            
        except Exception as e:
            self.logger.error_with_context(e, f"Sprint {sprint_num}")
            return SprintResult(
                sprint_number=sprint_num,
                success=False,
                iterations_completed=0,
                errors=[str(e)]
            )
    
    def _create_sprint_context(self, sprint_num: int, sprint_focus: str) -> str:
        """Create context for the sprint."""
        # Get project status
        git_status = self.git_ops.get_status()
        metrics = self._get_project_metrics()
        
        # Get previous sprint results
        previous_sprints = []
        for result in self.sprint_results:
            if result.sprint_number < sprint_num:
                previous_sprints.append(f"Sprint {result.sprint_number}: {'Success' if result.success else 'Failed'}")
        
        context = f"""
# Sprint {sprint_num} Context

## Project Goal
{self.settings.project_goal}

## Sprint Focus
{sprint_focus}

## Current Project Status
- Git Branch: {git_status.get('current_branch', 'unknown')}
- Modified Files: {metrics.get('modified_files', 0)}
- Test Pass Rate: {metrics.get('test_pass_rate', 0.0):.2f}%
- Test Coverage: {metrics.get('test_coverage', 0.0):.2f}%
- Build Success: {metrics.get('build_success', False)}
- Overall Score: {metrics.get('overall_score', 0.0):.1f}/100
- Total Issues: {metrics.get('total_issues', 0)}

## Previous Sprints
{chr(10).join(previous_sprints) if previous_sprints else 'No previous sprints'}

## Instructions
1. Review the current project state
2. Plan and implement features for this sprint
3. Ensure all code is tested and documented
4. Follow TypeScript best practices
5. Use vi keybindings for the TUI interface
6. Focus on: {sprint_focus}

## Success Criteria
- All tests pass
- Code coverage > 80%
- Build succeeds
- Features are functional and well-documented
"""
        
        return context
    
    def _run_group_chat(self, context: str, sprint_num: int) -> Dict:
        """Run the multi-agent group chat."""
        try:
            # Create group chat
            groupchat = autogen.GroupChat(
                agents=list(self.agents.values()),
                messages=[],
                max_round=self.settings.iterations_per_sprint
            )
            
            manager = autogen.GroupChatManager(
                groupchat=groupchat,
                llm_config=self.agent_factory.llm_config
            )
            
            # Start the conversation
            self.logger.info(f"Starting group chat for sprint {sprint_num}")
            
            # Get the user proxy agent
            user_proxy = self.agents["user_proxy"]
            
            # Start the chat with context
            chat_result = user_proxy.initiate_chat(
                manager,
                message=context,
                silent=False
            )
            
            # Process chat results
            return self._process_chat_result(chat_result, sprint_num)
            
        except Exception as e:
            # Handle error with recovery manager
            recovery_result = self.error_recovery.handle_error(e, {
                'component': 'llm',
                'operation': 'group_chat',
                'sprint_num': sprint_num,
                'retry_count': 0,
                'max_retries': 2
            })
            
            if recovery_result.success:
                self.logger.info(f"Recovery successful: {recovery_result.action_taken.value}")
                # Could retry the operation here
                pass
            else:
                self.logger.error(f"Recovery failed: {recovery_result.new_error}")
            
            return {
                "success": False,
                "iterations": 0,
                "artifacts": [],
                "errors": [str(e)]
            }
    
    def _process_chat_result(self, chat_result, sprint_num: int) -> Dict:
        """Process the results of a group chat."""
        try:
            # Extract messages and artifacts
            messages = chat_result.chat_history if hasattr(chat_result, 'chat_history') else []
            artifacts = []
            errors = []
            
            # Look for code files created/modified
            for message in messages:
                if hasattr(message, 'content') and message.content:
                    # Check if message contains code blocks
                    if '```' in message.content:
                        artifacts.append(f"Code changes in message from {message.name}")
            
            # Check for actual file changes
            git_status = self.git_ops.get_status()
            if git_status.get('modified_files', 0) > 0:
                artifacts.append(f"{git_status['modified_files']} files modified")
            
            # Run tests to check success based on project type
            if self.settings.project_type == ProjectType.TYPESCRIPT and self.node_ops is not None:
                test_results = self.node_ops.run_tests()
                build_results = self.node_ops.run_build()
                
                success = test_results["success"] and build_results["success"]
                
                if not test_results["success"]:
                    errors.append("Tests failed")
                if not build_results["success"]:
                    errors.append("Build failed")
            elif self.settings.project_type == ProjectType.PYTHON:
                # For Python projects, check if tests exist and run them
                import subprocess
                try:
                    # Check if pytest is available and run tests
                    result = subprocess.run(
                        ["python", "-m", "pytest", "--tb=short"],
                        cwd=self.work_dir,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    test_success = result.returncode == 0
                    
                    # Check build success by trying to install the package
                    build_result = subprocess.run(
                        ["python", "-m", "pip", "install", "-e", "."],
                        cwd=self.work_dir,
                        capture_output=True,
                        text=True,
                        timeout=60
                    )
                    build_success = build_result.returncode == 0
                    
                    success = test_success and build_success
                    
                    if not test_success:
                        errors.append("Python tests failed")
                    if not build_success:
                        errors.append("Python build failed")
                        
                except Exception as e:
                    success = False
                    errors.append(f"Python test/build error: {str(e)}")
            else:
                # For other project types, assume success
                success = True
            
            return {
                "success": success,
                "iterations": len(messages),
                "artifacts": artifacts,
                "errors": errors,
                "messages": messages
            }
            
        except Exception as e:
            return {
                "success": False,
                "iterations": 0,
                "artifacts": [],
                "errors": [str(e)]
            }
    
    def _calculate_sprint_reward(self, metrics: Dict, chat_result: Dict) -> float:
        """Calculate reward for the sprint."""
        reward = 0.0
        
        # Base reward for completion
        if chat_result["success"]:
            reward += 10.0
        
        # Test pass rate reward
        test_pass_rate = metrics.get("test_pass_rate", 0.0)
        reward += test_pass_rate * 20.0
        
        # Coverage reward
        coverage = metrics.get("test_coverage", 0.0)
        reward += coverage * 10.0
        
        # Build success reward
        if metrics.get("build_success", False):
            reward += 5.0
        
        # Penalty for errors
        reward -= len(chat_result.get("errors", [])) * 5.0
        
        return reward
    
    def _create_sprint_commit(self, sprint_num: int, chat_result: Dict) -> None:
        """Create a commit for the sprint."""
        try:
            # Create sprint summary
            summary = f"Sprint {sprint_num} completed with {len(chat_result.get('artifacts', []))} artifacts"
            if chat_result.get("errors"):
                summary += f" and {len(chat_result['errors'])} errors"
            
            # Commit changes
            self.git_ops.create_sprint_commit(sprint_num, summary)
            
            # Optionally create PR
            if self.settings.human_input_mode.value == "NEVER":
                pr_url = self.git_ops.create_pull_request(
                    sprint_num,
                    f"Sprint {sprint_num} - {self.settings.project_name}",
                    f"Automated sprint completion\n\n{summary}"
                )
                if pr_url:
                    self.logger.info(f"Created PR: {pr_url}")
            
        except Exception as e:
            self.logger.error_with_context(e, "Sprint commit creation")
    
    def _log_sprint_results(self, sprint_num: int, chat_result: Dict, metrics: Dict) -> None:
        """Log sprint results to file."""
        try:
            sprint_file = self.scrum_dir / f"sprint_{sprint_num}.md"
            
            with open(sprint_file, 'w') as f:
                f.write(f"# Sprint {sprint_num} Results\n\n")
                f.write(f"**Date:** {datetime.now().isoformat()}\n")
                f.write(f"**Status:** {'✅ Success' if chat_result['success'] else '❌ Failed'}\n")
                f.write(f"**Iterations:** {chat_result['iterations']}\n\n")
                
                f.write("## Metrics\n\n")
                f.write(f"- Test Pass Rate: {metrics.get('test_pass_rate', 0.0):.2f}\n")
                f.write(f"- Test Coverage: {metrics.get('test_coverage', 0.0):.2f}\n")
                f.write(f"- Build Success: {metrics.get('build_success', False)}\n")
                f.write(f"- Dependencies: {metrics.get('dependency_count', 0)}\n\n")
                
                f.write("## Artifacts\n\n")
                for artifact in chat_result.get("artifacts", []):
                    f.write(f"- {artifact}\n")
                f.write("\n")
                
                if chat_result.get("errors"):
                    f.write("## Errors\n\n")
                    for error in chat_result["errors"]:
                        f.write(f"- {error}\n")
                    f.write("\n")
                
                f.write("## Git Status\n\n")
                git_status = self.git_ops.get_status()
                f.write(f"- Branch: {git_status.get('current_branch', 'unknown')}\n")
                f.write(f"- Modified Files: {git_status.get('modified_files', 0)}\n")
                if git_status.get('last_commit'):
                    f.write(f"- Last Commit: {git_status['last_commit']}\n")
            
            # Index the sprint file for RAG
            self.rag_store.index_file(sprint_file)
            
        except Exception as e:
            self.logger.error_with_context(e, "Sprint logging")
    
    def _initialize_python_project(self) -> bool:
        """Initialize Python project structure using code generator."""
        try:
            # Use code generator to create complete project structure
            app_name = self.settings.project_name
            description = self.settings.project_goal
            
            success = self.code_generator.generate_project_structure(app_name, description)
            
            if success:
                self.logger.info(f"Generated Python project structure for {app_name}")
                return True
            else:
                self.logger.error("Failed to generate Python project structure")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to initialize Python project: {e}")
            return False
    
    def _generate_final_report(self) -> None:
        """Generate final project report with all sprint summaries."""
        try:
            # Load all sprint summaries
            all_sprints = []
            for result in self.sprint_results:
                # Create summary from sprint result
                sprint_data = {
                    "start_time": datetime.now().isoformat(),  # Placeholder
                    "end_time": datetime.now().isoformat(),    # Placeholder
                    "success": result.success,
                    "iterations_completed": result.iterations_completed,
                    "total_iterations": self.settings.iterations_per_sprint,
                    "artifacts_created": len(result.artifacts) if hasattr(result, 'artifacts') else 0,
                    "errors": result.errors,
                    "metrics": result.test_results if hasattr(result, 'test_results') else {}
                }
                
                summary = self.artifacts_manager.create_sprint_summary(
                    result.sprint_number, sprint_data
                )
                all_sprints.append(summary)
            
            # Generate comprehensive project report
            if all_sprints:
                self.artifacts_manager.generate_project_report(all_sprints)
                self.artifacts_manager.generate_burndown_chart_data(all_sprints)
                
                # Generate error statistics report
                error_stats = self.error_recovery.get_error_statistics()
                self._generate_error_report(error_stats)
                
                self.logger.info("📊 Generated comprehensive project report")
                self.logger.info(f"📁 Reports available in: {self.work_dir}/scrum/reports/")
                self.logger.info(f"📈 Metrics available in: {self.work_dir}/scrum/metrics/")
                self.logger.info(f"🛡️ Error recovery rate: {error_stats.get('recovery_rate', 0.0):.1f}%")
            
        except Exception as e:
            self.logger.error(f"Failed to generate final report: {e}")
    
    def _generate_error_report(self, error_stats: Dict[str, Any]) -> None:
        """Generate error statistics report."""
        try:
            report_file = self.work_dir / "scrum" / "reports" / "error_report.md"
            
            lines = []
            lines.append("# Error Recovery Report")
            lines.append("")
            lines.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append("")
            
            # Summary
            lines.append("## Summary")
            lines.append(f"- **Total Errors**: {error_stats.get('total_errors', 0)}")
            lines.append(f"- **Successful Recoveries**: {error_stats.get('successful_recoveries', 0)}")
            lines.append(f"- **Recovery Rate**: {error_stats.get('recovery_rate', 0.0):.1f}%")
            lines.append("")
            
            # Error Types
            error_types = error_stats.get('error_types', {})
            if error_types:
                lines.append("## Error Types")
                for error_type, count in error_types.items():
                    lines.append(f"- **{error_type}**: {count}")
                lines.append("")
            
            # Severity Distribution
            severity_dist = error_stats.get('severity_distribution', {})
            if severity_dist:
                lines.append("## Severity Distribution")
                for severity, count in severity_dist.items():
                    lines.append(f"- **{severity}**: {count}")
                lines.append("")
            
            # Circuit Breaker States
            circuit_states = error_stats.get('circuit_breaker_states', {})
            if circuit_states:
                lines.append("## Circuit Breaker States")
                for component, state in circuit_states.items():
                    status = "🟢 CLOSED" if state == "CLOSED" else "🔴 OPEN" if state == "OPEN" else "🟡 HALF_OPEN"
                    lines.append(f"- **{component}**: {status}")
                lines.append("")
            
            # Recommendations
            lines.append("## Recommendations")
            recovery_rate = error_stats.get('recovery_rate', 0.0)
            if recovery_rate < 80:
                lines.append("- Consider improving error handling strategies")
                lines.append("- Review circuit breaker configurations")
                lines.append("- Implement additional fallback mechanisms")
            else:
                lines.append("- Excellent error recovery performance!")
                lines.append("- Maintain current error handling practices")
            
            with open(report_file, 'w') as f:
                f.write('\n'.join(lines))
            
            self.logger.info(f"Generated error report: {report_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to generate error report: {e}")
