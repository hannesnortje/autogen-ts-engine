#!/usr/bin/env python3
"""
Q&A and Improvement Session Runner for AutoGen TS Engine

This script provides an interactive Q&A and improvement session for existing projects.
It allows users to ask questions about their codebase and get automated improvements.
"""

import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add the autogen_ts_engine to the path
sys.path.insert(0, str(Path(__file__).parent))

from autogen_ts_engine.config_parser import ConfigParser
from autogen_ts_engine.sprint_runner import SprintRunner
from autogen_ts_engine.agent_factory import AgentFactory
from autogen_ts_engine.rag_store import RAGStore
from autogen_ts_engine.logging_utils import EngineLogger
from autogen_ts_engine.schemas import Settings, AgentDefinition
from autogen_ts_engine.error_recovery import ErrorRecoveryManager


class QAImprovementRunner:
    """Specialized runner for Q&A and improvement sessions."""
    
    def __init__(self, project_path: str, config_dir: str = "./config"):
        self.project_path = Path(project_path)
        self.config_dir = Path(config_dir)
        self.logger = EngineLogger("qa_improvement")
        self.error_recovery = ErrorRecoveryManager(self.project_path)
        
        # Load configurations
        self.config_parser = ConfigParser()
        self.settings = self._load_qa_settings()
        self.agents = self._load_qa_agents()
        
        # Initialize components
        self.rag_store = RAGStore(self.project_path, self.settings)
        self.agent_factory = AgentFactory(self.settings, self.rag_store, self.logger)
        
    def _load_qa_settings(self) -> Settings:
        """Load Q&A specific settings."""
        # For now, use default settings with Q&A mode
        settings = self.config_parser.parse_settings(self.config_dir)
        settings.work_dir = str(self.project_path)
        return settings
    
    def _load_qa_agents(self) -> List[AgentDefinition]:
        """Load Q&A specific agents."""
        # For now, use default agents
        return self.config_parser.parse_agents(self.config_dir)
    
    def index_project(self) -> None:
        """Index the existing project for RAG."""
        self.logger.info("Indexing project for Q&A sessions...")
        
        try:
            # Index source code
            src_path = self.project_path / "src"
            if src_path.exists():
                self.rag_store.index_directory(src_path)
            
            # Index tests
            tests_path = self.project_path / "tests"
            if tests_path.exists():
                self.rag_store.index_directory(tests_path)
            
            # Index documentation
            docs_path = self.project_path / "docs"
            if docs_path.exists():
                self.rag_store.index_directory(docs_path)
            
            # Index README and config files
            for file in ["README.md", "pyproject.toml", "requirements.txt"]:
                file_path = self.project_path / file
                if file_path.exists():
                    self.rag_store.index_file(str(file_path))
            
            self.logger.info("Project indexing completed successfully!")
            
        except Exception as e:
            self.error_recovery.handle_error(
                error=e,
                context={
                    "component": "qa_improvement",
                    "operation": "index_project",
                    "metadata": {"project_path": str(self.project_path)}
                }
            )
    
    def analyze_project(self) -> Dict[str, Any]:
        """Perform comprehensive project analysis."""
        self.logger.info("Starting comprehensive project analysis...")
        
        analysis_results = {
            "code_quality": {},
            "performance": {},
            "security": {},
            "testing": {},
            "documentation": {},
            "architecture": {}
        }
        
        try:
            # Create analysis agents
            analysis_agents = [
                agent for agent in self.agents 
                if agent.name in ["Code Analyst", "Performance Optimizer", "Security Auditor", 
                                "Testing Specialist", "Documentation Expert", "Architecture Reviewer"]
            ]
            
            # Run analysis for each focus area
            for agent_def in analysis_agents:
                self.logger.info(f"Running {agent_def.name} analysis...")
                
                agent = self.agent_factory.create_agent(agent_def)
                
                # Create analysis prompt
                analysis_prompt = f"""
                Please analyze the project at {self.project_path} focusing on your area of expertise.
                
                For {agent_def.name}:
                - Provide a comprehensive analysis
                - Identify specific issues and opportunities
                - Suggest concrete improvements
                - Prioritize recommendations by impact
                
                Please structure your response as a detailed report with:
                1. Executive Summary
                2. Key Findings
                3. Specific Issues Identified
                4. Improvement Recommendations
                5. Priority Ranking
                6. Implementation Suggestions
                """
                
                # Get analysis from agent
                response = agent.generate_response(analysis_prompt)
                
                # Store results
                focus_area = agent_def.name.lower().replace(" ", "_")
                analysis_results[focus_area] = {
                    "agent": agent_def.name,
                    "analysis": response,
                    "timestamp": str(Path().cwd())
                }
            
            self.logger.info("Project analysis completed successfully!")
            return analysis_results
            
        except Exception as e:
            self.error_recovery.handle_error(
                error=e,
                context={
                    "component": "qa_improvement",
                    "operation": "analyze_project",
                    "metadata": {"project_path": str(self.project_path)}
                }
            )
            return analysis_results
    
    def interactive_qa_session(self) -> None:
        """Start an interactive Q&A session."""
        self.logger.info("Starting interactive Q&A session...")
        print("\n" + "="*60)
        print("🤖 AutoGen TS Engine - Interactive Q&A Session")
        print("="*60)
        print("Ask questions about your project and get AI-powered answers!")
        print("Type 'quit' to exit, 'help' for available commands.")
        print("="*60)
        
        # Create Q&A coordinator agent
        qa_coordinator = None
        for agent_def in self.agents:
            if agent_def.name == "Q&A Coordinator":
                qa_coordinator = self.agent_factory.create_agent(agent_def)
                break
        
        if not qa_coordinator:
            self.logger.warning("Q&A Coordinator agent not found, using default agent")
            qa_coordinator = self.agent_factory.create_agent(self.agents[0])
        
        while True:
            try:
                # Get user question
                question = input("\n❓ Your question: ").strip()
                
                if question.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye! Q&A session ended.")
                    break
                
                if question.lower() == 'help':
                    self._show_help()
                    continue
                
                if not question:
                    continue
                
                # Generate response using RAG and agent
                print("🤔 Thinking...")
                
                # Use RAG to get relevant context
                relevant_docs = self.rag_store.search(question, top_k=5)
                
                # Create enhanced prompt with context
                enhanced_prompt = f"""
                Question: {question}
                
                Project Context: {self.project_path}
                
                Relevant Code/Documentation:
                {self._format_relevant_docs(relevant_docs)}
                
                Please provide a comprehensive answer that:
                1. Directly addresses the question
                2. References relevant code/documentation
                3. Suggests specific improvements if applicable
                4. Provides actionable recommendations
                5. Includes code examples when helpful
                """
                
                response = qa_coordinator.generate_response(enhanced_prompt)
                
                print("\n💡 Answer:")
                print("-" * 40)
                print(response)
                print("-" * 40)
                
            except KeyboardInterrupt:
                print("\n👋 Q&A session interrupted. Goodbye!")
                break
            except Exception as e:
                self.error_recovery.handle_error(
                    error=e,
                    context={
                        "component": "qa_improvement",
                        "operation": "process_question",
                        "metadata": {"question": question}
                    }
                )
                print(f"❌ Error processing question: {e}")
    
    def _format_relevant_docs(self, docs: List[Dict[str, Any]]) -> str:
        """Format relevant documents for the prompt."""
        if not docs:
            return "No relevant documentation found."
        
        formatted = []
        for i, doc in enumerate(docs, 1):
            formatted.append(f"Document {i}:")
            formatted.append(f"Source: {doc.get('source', 'Unknown')}")
            formatted.append(f"Content: {doc.get('content', 'No content')}")
            formatted.append("")
        
        return "\n".join(formatted)
    
    def _show_help(self) -> None:
        """Show help information."""
        help_text = """
        📚 Available Commands:
        
        General Questions:
        - "How does the authentication work?"
        - "What's the main architecture pattern?"
        - "How can I improve performance?"
        - "What security vulnerabilities exist?"
        
        Code-Specific Questions:
        - "Explain the user service implementation"
        - "How does the database connection work?"
        - "What's wrong with this function?"
        - "How can I refactor this code?"
        
        Improvement Questions:
        - "What tests should I add?"
        - "How can I improve error handling?"
        - "What documentation is missing?"
        - "How can I optimize this algorithm?"
        
        Commands:
        - help: Show this help
        - quit/exit/q: Exit the session
        
        💡 Tips:
        - Be specific in your questions
        - Ask about specific files or functions
        - Request code examples when needed
        - Ask for improvement suggestions
        """
        print(help_text)
    
    def run_improvement_sprint(self, focus_areas: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run an improvement sprint on the project."""
        self.logger.info("Starting improvement sprint...")
        
        if focus_areas is None:
            focus_areas = ["code_quality", "performance", "security", "testing"]
        
        improvement_results = {}
        
        try:
            # Create improvement agents
            improvement_agents = [
                agent for agent in self.agents 
                if any(area in agent.name.lower() for area in focus_areas)
            ]
            
            for agent_def in improvement_agents:
                self.logger.info(f"Running {agent_def.name} improvements...")
                
                agent = self.agent_factory.create_agent(agent_def)
                
                # Create improvement prompt
                improvement_prompt = f"""
                Please analyze and improve the project at {self.project_path} focusing on your area of expertise.
                
                For {agent_def.name}:
                1. Identify specific issues in your area
                2. Propose concrete improvements
                3. Implement the most impactful changes
                4. Ensure changes maintain functionality
                5. Update relevant documentation
                
                Focus on practical, implementable improvements that will have the most impact.
                """
                
                # Get improvement suggestions and implementations
                response = agent.generate_response(improvement_prompt)
                
                improvement_results[agent_def.name] = {
                    "suggestions": response,
                    "implemented": True,  # Agent can implement changes
                    "timestamp": str(Path().cwd())
                }
            
            self.logger.info("Improvement sprint completed successfully!")
            return improvement_results
            
        except Exception as e:
            self.error_recovery.handle_error(
                error=e,
                context={
                    "component": "qa_improvement",
                    "operation": "run_improvement_sprint",
                    "metadata": {"focus_areas": focus_areas}
                }
            )
            return improvement_results


def main():
    """Main entry point for Q&A and improvement sessions."""
    if len(sys.argv) < 2:
        print("Usage: python qa_improvement_runner.py <project_path> [config_dir]")
        print("Example: python qa_improvement_runner.py ./my_project ./config")
        sys.exit(1)
    
    project_path = sys.argv[1]
    config_dir = sys.argv[2] if len(sys.argv) > 2 else "./config"
    
    if not Path(project_path).exists():
        print(f"❌ Project path does not exist: {project_path}")
        sys.exit(1)
    
    try:
        # Initialize Q&A runner
        runner = QAImprovementRunner(project_path, config_dir)
        
        # Index the project
        runner.index_project()
        
        print("\n🎯 Q&A and Improvement Session Options:")
        print("1. Interactive Q&A Session")
        print("2. Comprehensive Project Analysis")
        print("3. Improvement Sprint")
        print("4. All of the above")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == "1":
            runner.interactive_qa_session()
        elif choice == "2":
            analysis = runner.analyze_project()
            print("\n📊 Analysis Results:")
            print(json.dumps(analysis, indent=2))
        elif choice == "3":
            improvements = runner.run_improvement_sprint()
            print("\n🔧 Improvement Results:")
            print(json.dumps(improvements, indent=2))
        elif choice == "4":
            # Run comprehensive analysis
            analysis = runner.analyze_project()
            print("\n📊 Analysis Results:")
            print(json.dumps(analysis, indent=2))
            
            # Run improvement sprint
            improvements = runner.run_improvement_sprint()
            print("\n🔧 Improvement Results:")
            print(json.dumps(improvements, indent=2))
            
            # Start interactive Q&A
            runner.interactive_qa_session()
        else:
            print("❌ Invalid choice. Exiting.")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
