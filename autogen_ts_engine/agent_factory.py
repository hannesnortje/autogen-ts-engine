"""Agent factory for creating AutoGen agents."""

import os
import logging
from pathlib import Path
from typing import Dict, List, Optional

import autogen
from autogen import AssistantAgent, UserProxyAgent

from .schemas import AgentDefinition, Settings, LLMProvider
from .rag_store import RAGStore
from .mock_llm import enable_mock_llm
from .error_recovery import ErrorRecoveryManager
from .gemini_adapter import create_gemini_adapter, is_gemini_available


class AgentFactory:
    """Factory for creating AutoGen agents."""
    
    def __init__(self, settings: Settings, rag_store: RAGStore, use_mock_llm: bool = False):
        self.settings = settings
        self.rag_store = rag_store
        self.use_mock_llm = use_mock_llm
        self.error_recovery = ErrorRecoveryManager(Path(settings.work_dir))
        self.logger = logging.getLogger(__name__)
        
        # Configure LLM based on provider
        if settings.llm_binding.provider == LLMProvider.GEMINI:
            # Use Gemini adapter
            if is_gemini_available():
                gemini_adapter = create_gemini_adapter(settings.llm_binding)
                if gemini_adapter:
                    self.llm_config = gemini_adapter.get_autogen_config()
                    self.gemini_adapter = gemini_adapter
                    self.logger.info("Using Gemini LLM provider")
                else:
                    self.logger.warning("Failed to create Gemini adapter, falling back to mock LLM")
                    self.use_mock_llm = True
            else:
                self.logger.warning("Gemini not available, falling back to mock LLM")
                self.use_mock_llm = True
        else:
            # Use standard LLM configuration (LM Studio, OpenAI, etc.)
            api_type = settings.llm_binding.api_type
            if api_type == "open_ai":
                api_type = "openai"  # Fix for newer autogen version
                
            self.llm_config = {
                "config_list": [{
                    "model": settings.llm_binding.model_name,
                    "base_url": settings.llm_binding.api_base,
                    "api_type": api_type,
                    "api_key": settings.llm_binding.api_key,
                }],
                "cache_seed": settings.llm_binding.cache_seed,
                "temperature": 0.7,
                "timeout": 300,  # Increased timeout for slow LM Studio
            }
        
        # Enable mock LLM if requested
        if self.use_mock_llm:
            self.mock_patchers = enable_mock_llm()
            for patcher in self.mock_patchers:
                patcher.start()
    
    def create_agents(self, agent_definitions: List[AgentDefinition]) -> Dict[str, AssistantAgent]:
        """Create all agents from definitions."""
        agents = {}
        
        for agent_def in agent_definitions:
            agent = self._create_agent(agent_def)
            agents[agent_def.name] = agent
        
        # Create user proxy agent
        user_proxy = self._create_user_proxy()
        agents["user_proxy"] = user_proxy
        
        return agents
    
    def _create_agent(self, agent_def: AgentDefinition) -> AssistantAgent:
        """Create a single assistant agent."""
        # Customize system message based on agent type
        system_message = self._customize_system_message(agent_def)
        
        # Add tools based on agent type
        tools = self._get_agent_tools(agent_def.name)
        
        agent = AssistantAgent(
            name=agent_def.name,
            system_message=system_message,
            llm_config=self.llm_config,
            human_input_mode="NEVER"
        )
        
        return agent
    
    def _create_user_proxy(self) -> UserProxyAgent:
        """Create user proxy agent."""
        return UserProxyAgent(
            name="user_proxy",
            human_input_mode=self.settings.human_input_mode.value,
            max_consecutive_auto_reply=10,
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
            code_execution_config={
                "work_dir": self.settings.work_dir,
                "use_docker": False,
            },
            llm_config=self.llm_config,
        )
    
    def _customize_system_message(self, agent_def: AgentDefinition) -> str:
        """Customize system message based on agent type."""
        base_message = agent_def.system_message
        
        # Add RAG context capability for all agents
        rag_context = """
        
        You have access to a RAG (Retrieval-Augmented Generation) system that can provide relevant context from the project. When you need information about:
        - Existing code structure
        - Previous sprint decisions
        - Test patterns
        - Documentation
        
        Use the retrieve_context tool to get relevant information before making decisions.
        """
        
        # Agent-specific customizations
        if agent_def.name == "Planner":
            planning_context = """
            
            As a Planner, your responsibilities include:
            1. Breaking down the project goal into manageable sprints
            2. Prioritizing features based on dependencies and user value
            3. Ensuring each sprint has clear, testable deliverables
            4. Consulting the RAG system for insights from previous work
            5. Creating detailed task breakdowns for the Coder
            
            Always consider:
            - Testability of proposed features
            - Technical dependencies
            - User experience impact
            - Code maintainability
            """
            return base_message + rag_context + planning_context
        
        elif agent_def.name == "Coder":
            coding_context = """
            
            As a Coder, your responsibilities include:
            1. Writing clean, idiomatic TypeScript code
            2. Following established patterns from the codebase
            3. Adding comprehensive tests for new features
            4. Ensuring code passes linting and type checking
            5. Documenting complex logic and APIs
            
            Code quality standards:
            - Use TypeScript strict mode
            - Prefer functional programming where appropriate
            - Keep functions small and focused
            - Add JSDoc comments for public APIs
            - Follow the existing code style
            """
            return base_message + rag_context + coding_context
        
        elif agent_def.name == "Tester":
            testing_context = """
            
            As a Tester, your responsibilities include:
            1. Writing comprehensive unit and integration tests
            2. Ensuring test coverage meets project standards
            3. Creating test scenarios for edge cases
            4. Validating that features work as specified
            5. Running performance tests when relevant
            
            Testing standards:
            - Use Jest as the testing framework
            - Aim for >80% code coverage
            - Test both happy path and error cases
            - Mock external dependencies appropriately
            - Write tests that are easy to understand and maintain
            """
            return base_message + rag_context + testing_context
        
        elif agent_def.name == "Critic":
            critic_context = """
            
            As a Critic, your responsibilities include:
            1. Reviewing code for architectural issues
            2. Identifying potential performance problems
            3. Ensuring consistent user experience
            4. Checking for security vulnerabilities
            5. Suggesting improvements for maintainability
            
            Review focus areas:
            - Code architecture and design patterns
            - Error handling and edge cases
            - Performance implications
            - Security considerations
            - User experience consistency
            - Documentation quality
            """
            return base_message + rag_context + critic_context
        
        elif agent_def.name == "RAG":
            rag_context = """
            
            As a RAG agent, your responsibilities include:
            1. Providing relevant context from the project history
            2. Retrieving code examples and patterns
            3. Summarizing previous sprint decisions
            4. Identifying similar problems and solutions
            5. Maintaining context across conversations
            
            When retrieving information:
            - Focus on the most relevant documents
            - Provide concise summaries
            - Include code examples when helpful
            - Highlight important decisions and their rationale
            """
            return base_message + rag_context
        
        return base_message + rag_context
    
    def _get_agent_tools(self, agent_name: str) -> List:
        """Get tools for a specific agent."""
        tools = []
        
        # All agents get RAG tools
        tools.extend([
            {
                "name": "retrieve_context",
                "description": "Retrieve relevant context from the project",
                "function": self._retrieve_context_tool
            },
            {
                "name": "search_code",
                "description": "Search for specific code patterns or functions",
                "function": self._search_code_tool
            }
        ])
        
        # Agent-specific tools
        if agent_name == "Coder":
            tools.extend([
                {
                    "name": "analyze_code_complexity",
                    "description": "Analyze code complexity metrics",
                    "function": self._analyze_complexity_tool
                },
                {
                    "name": "check_dependencies",
                    "description": "Check project dependencies",
                    "function": self._check_dependencies_tool
                }
            ])
        
        elif agent_name == "Tester":
            tools.extend([
                {
                    "name": "run_tests",
                    "description": "Run the test suite",
                    "function": self._run_tests_tool
                },
                {
                    "name": "check_coverage",
                    "description": "Check test coverage",
                    "function": self._check_coverage_tool
                }
            ])
        
        elif agent_name == "Planner":
            tools.extend([
                {
                    "name": "get_project_status",
                    "description": "Get current project status and metrics",
                    "function": self._get_project_status_tool
                },
                {
                    "name": "analyze_dependencies",
                    "description": "Analyze feature dependencies",
                    "function": self._analyze_dependencies_tool
                }
            ])
        
        return tools
    
    def _retrieve_context_tool(self, query: str, top_k: int = 5) -> str:
        """Tool for retrieving context from RAG store."""
        try:
            context = self.rag_store.retrieve_with_context(query, top_k=top_k)
            return context if context else "No relevant context found."
        except Exception as e:
            return f"Error retrieving context: {str(e)}"
    
    def _search_code_tool(self, pattern: str, file_type: str = "*.ts") -> str:
        """Tool for searching code patterns."""
        try:
            # This would be implemented with actual file search
            # For now, return a placeholder
            return f"Searching for '{pattern}' in {file_type} files..."
        except Exception as e:
            return f"Error searching code: {str(e)}"
    
    def _analyze_complexity_tool(self, file_path: str) -> str:
        """Tool for analyzing code complexity."""
        try:
            # This would use tools like cyclomatic complexity analysis
            return f"Analyzing complexity of {file_path}..."
        except Exception as e:
            return f"Error analyzing complexity: {str(e)}"
    
    def _check_dependencies_tool(self) -> str:
        """Tool for checking project dependencies."""
        try:
            # This would analyze package.json and node_modules
            return "Checking project dependencies..."
        except Exception as e:
            return f"Error checking dependencies: {str(e)}"
    
    def _run_tests_tool(self) -> str:
        """Tool for running tests."""
        try:
            # This would execute the test command
            return "Running test suite..."
        except Exception as e:
            return f"Error running tests: {str(e)}"
    
    def _check_coverage_tool(self) -> str:
        """Tool for checking test coverage."""
        try:
            # This would run coverage analysis
            return "Checking test coverage..."
        except Exception as e:
            return f"Error checking coverage: {str(e)}"
    
    def _get_project_status_tool(self) -> str:
        """Tool for getting project status."""
        try:
            # This would analyze current project state
            return "Getting project status..."
        except Exception as e:
            return f"Error getting project status: {str(e)}"
    
    def _analyze_dependencies_tool(self, feature: str) -> str:
        """Tool for analyzing feature dependencies."""
        try:
            # This would analyze what other features depend on this one
            return f"Analyzing dependencies for feature: {feature}"
        except Exception as e:
            return f"Error analyzing dependencies: {str(e)}"
