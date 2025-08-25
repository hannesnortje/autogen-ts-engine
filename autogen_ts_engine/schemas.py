"""Pydantic models for configuration schemas."""

from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field, validator


class HumanInputMode(str, Enum):
    """Human input mode options."""
    ALWAYS = "ALWAYS"
    NEVER = "NEVER"
    AUTO = "AUTO"


class ProjectType(str, Enum):
    """Supported project types."""
    TYPESCRIPT = "typescript"
    PYTHON = "python"
    REACT = "react"
    NODEJS = "nodejs"
    JAVA = "java"
    GO = "go"
    RUST = "rust"
    CUSTOM = "custom"


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    LM_STUDIO = "lm_studio"
    GEMINI = "gemini"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class LLMBinding(BaseModel):
    """LLM binding configuration."""
    provider: LLMProvider = Field(default=LLMProvider.LM_STUDIO, description="LLM provider")
    api_base: str = Field(default="http://localhost:1234/v1", description="API base URL")
    model_name: str = Field(default="llama3", description="Model name")
    api_type: str = Field(default="open_ai", description="API type")
    api_key: str = Field(default="lmstudio", description="API key")
    cache_seed: int = Field(default=42, description="Cache seed for reproducibility")
    
    @validator("api_base")
    def validate_api_base(cls, v, values):
        provider = values.get("provider", LLMProvider.LM_STUDIO)
        if provider == LLMProvider.GEMINI:
            # Gemini doesn't need api_base, it uses google-generativeai
            return ""
        return v
    
    @validator("api_type")
    def validate_api_type(cls, v, values):
        provider = values.get("provider", LLMProvider.LM_STUDIO)
        if provider == LLMProvider.GEMINI:
            return "google"
        elif provider == LLMProvider.LM_STUDIO:
            return "open_ai"
        return v


class RLConfig(BaseModel):
    """Reinforcement learning configuration."""
    epsilon: float = Field(default=0.1, description="Exploration rate")
    alpha: float = Field(default=0.1, description="Learning rate")
    gamma: float = Field(default=0.9, description="Discount factor")
    state_buckets: int = Field(default=10, description="Number of state buckets")


class RAGConfig(BaseModel):
    """RAG (Retrieval-Augmented Generation) configuration."""
    top_k: int = Field(default=5, description="Number of top documents to retrieve")
    max_doc_tokens: int = Field(default=4000, description="Maximum document tokens")


class NodeConfig(BaseModel):
    """Node.js toolchain configuration."""
    package_manager: str = Field(default="npm", description="Package manager (npm|pnpm|yarn)")
    test_command: str = Field(default="npm test", description="Test command")
    build_command: str = Field(default="npm run build", description="Build command")

    @validator("package_manager")
    def validate_package_manager(cls, v):
        if v not in ["npm", "pnpm", "yarn"]:
            raise ValueError("package_manager must be one of: npm, pnpm, yarn")
        return v


class PythonConfig(BaseModel):
    """Python toolchain configuration."""
    package_manager: str = Field(default="pip", description="Package manager (pip|poetry|pipenv)")
    test_command: str = Field(default="pytest", description="Test command")
    build_command: str = Field(default="python setup.py build", description="Build command")
    virtual_env: bool = Field(default=True, description="Use virtual environment")
    requirements_file: str = Field(default="requirements.txt", description="Requirements file name")

    @validator("package_manager")
    def validate_package_manager(cls, v):
        if v not in ["pip", "poetry", "pipenv"]:
            raise ValueError("package_manager must be one of: pip, poetry, pipenv")
        return v


class ProjectConfig(BaseModel):
    """Generic project configuration."""
    project_type: ProjectType = Field(default=ProjectType.TYPESCRIPT, description="Project type")
    language: str = Field(default="typescript", description="Primary language")
    framework: Optional[str] = Field(default=None, description="Framework (e.g., react, fastapi, express)")
    node: Optional[NodeConfig] = Field(default=None, description="Node.js specific config")
    python: Optional[PythonConfig] = Field(default=None, description="Python specific config")
    custom_config: Optional[Dict[str, Any]] = Field(default=None, description="Custom project configuration")


class AgentDefinition(BaseModel):
    """Agent definition with role and system message."""
    name: str = Field(description="Agent name")
    role: str = Field(description="Agent role")
    system_message: str = Field(description="System message for the agent")
    tools: Optional[List[str]] = Field(default=None, description="List of tools this agent can use")
    human_input_mode: Optional[HumanInputMode] = Field(default=None, description="Human input mode for this agent")


class Settings(BaseModel):
    """Main settings configuration."""
    project_name: str = Field(default="project", description="Project name")
    project_goal: str = Field(description="Project goal description")
    project_type: ProjectType = Field(default=ProjectType.TYPESCRIPT, description="Project type")
    
    num_sprints: int = Field(default=3, description="Number of sprints")
    iterations_per_sprint: int = Field(default=5, description="Iterations per sprint")
    
    llm_binding: LLMBinding = Field(default_factory=LLMBinding, description="LLM configuration")
    work_dir: str = Field(default="./project", description="Working directory")
    vector_db_path: str = Field(default="./project_db", description="Vector database path")
    git_branch_prefix: str = Field(default="sprint-", description="Git branch prefix")
    human_input_mode: HumanInputMode = Field(default=HumanInputMode.ALWAYS, description="Human input mode")
    
    rl: RLConfig = Field(default_factory=RLConfig, description="Reinforcement learning config")
    rag: RAGConfig = Field(default_factory=RAGConfig, description="RAG configuration")
    project_config: ProjectConfig = Field(default_factory=ProjectConfig, description="Project-specific configuration")
    
    debug_mode: bool = Field(default=False, description="Debug mode flag")
    auto_commit: bool = Field(default=True, description="Automatically commit after each sprint")
    create_pr: bool = Field(default=False, description="Create pull requests after sprints")

    @validator("work_dir", "vector_db_path")
    def validate_paths(cls, v):
        # Ensure paths are relative and don't contain dangerous characters
        path = Path(v)
        if path.is_absolute() and not path.parts[0].startswith("."):
            raise ValueError("Paths must be relative")
        return v

    @validator("num_sprints", "iterations_per_sprint")
    def validate_positive_integers(cls, v):
        if v <= 0:
            raise ValueError("Must be positive integer")
        return v


class SprintGoal(BaseModel):
    """Sprint goal definition."""
    sprint_number: int
    goals: List[str] = Field(description="List of goals for this sprint")
    focus_area: str = Field(description="Primary focus area (e.g., features, testing, refactoring)")
    dependencies: Optional[List[str]] = Field(default=None, description="Dependencies on other sprints")
    acceptance_criteria: List[str] = Field(description="Acceptance criteria for sprint completion")


class SprintResult(BaseModel):
    """Result of a sprint execution."""
    sprint_number: int
    success: bool
    iterations_completed: int
    goals_achieved: List[str] = Field(default_factory=list)
    goals_failed: List[str] = Field(default_factory=list)
    test_results: Optional[dict] = None
    reward: Optional[float] = None
    artifacts: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    metrics: Optional[Dict[str, Any]] = None


class ProjectState(BaseModel):
    """Current state of the project."""
    current_sprint: int = 0
    completed_sprints: List[SprintResult] = Field(default_factory=list)
    git_branch: Optional[str] = None
    last_commit: Optional[str] = None
    test_coverage: Optional[float] = None
    build_success: bool = False
    project_metrics: Dict[str, Any] = Field(default_factory=dict)
