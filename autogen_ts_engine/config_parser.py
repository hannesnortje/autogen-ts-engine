"""Configuration parser for Markdown files with YAML blocks."""

import re
from pathlib import Path
from typing import List, Optional

import yaml
from markdown_it import MarkdownIt
from markdown_it.tree import SyntaxTreeNode

from .schemas import AgentDefinition, Settings, ProjectType


class ConfigParser:
    """Parser for Markdown configuration files with YAML blocks."""

    def __init__(self):
        self.md = MarkdownIt()

    def parse_settings(self, config_dir: Path) -> Settings:
        """Parse settings from config/settings.md."""
        settings_file = config_dir / "settings.md"
        
        if not settings_file.exists():
            return Settings()
        
        content = settings_file.read_text()
        yaml_block = self._extract_yaml_block(content)
        
        if yaml_block:
            try:
                settings_dict = yaml.safe_load(yaml_block)
                return Settings(**settings_dict)
            except Exception as e:
                raise ValueError(f"Failed to parse settings.yaml: {e}")
        
        return Settings()

    def parse_agents(self, config_dir: Path) -> List[AgentDefinition]:
        """Parse agents from config/agents.md."""
        agents_file = config_dir / "agents.md"
        
        if not agents_file.exists():
            return self._get_default_agents()
        
        content = agents_file.read_text()
        
        # Try YAML block first
        yaml_block = self._extract_yaml_block(content)
        if yaml_block:
            try:
                agents_data = yaml.safe_load(yaml_block)
                if isinstance(agents_data, list):
                    return [AgentDefinition(**agent) for agent in agents_data]
                elif isinstance(agents_data, dict) and "agents" in agents_data:
                    return [AgentDefinition(**agent) for agent in agents_data["agents"]]
            except Exception as e:
                raise ValueError(f"Failed to parse agents.yaml: {e}")
        
        # Fallback to table parsing
        return self._parse_agents_table(content)

    def _extract_yaml_block(self, content: str) -> Optional[str]:
        """Extract YAML block from Markdown content."""
        # Look for YAML code blocks
        lines = content.split('\n')
        in_yaml_block = False
        yaml_lines = []
        
        for line in lines:
            if line.strip() == '```yaml':
                in_yaml_block = True
                continue
            elif line.strip() == '```' and in_yaml_block:
                in_yaml_block = False
                break
            
            if in_yaml_block:
                yaml_lines.append(line)
        
        if yaml_lines:
            return '\n'.join(yaml_lines).strip()
        
        return None

    def _parse_agents_table(self, content: str) -> List[AgentDefinition]:
        """Parse agents from Markdown table format."""
        agents = []
        
        # Parse markdown to get table structure
        tokens = self.md.parse(content)
        
        for token in tokens:
            if token.type == "table_open":
                # Find the table content
                table_tokens = self._extract_table_tokens(tokens, token)
                agents = self._parse_table_agents(table_tokens)
                break
        
        return agents if agents else self._get_default_agents()

    def _extract_table_tokens(self, tokens: List, table_open_token) -> List:
        """Extract tokens that belong to a table."""
        table_tokens = []
        in_table = False
        
        for token in tokens:
            if token == table_open_token:
                in_table = True
            elif token.type == "table_close":
                in_table = False
                break
            
            if in_table:
                table_tokens.append(token)
        
        return table_tokens

    def _parse_table_agents(self, table_tokens: List) -> List[AgentDefinition]:
        """Parse agent definitions from table tokens."""
        agents = []
        headers = []
        rows = []
        
        for token in table_tokens:
            if token.type == "thead_open":
                # Extract headers
                header_row = self._extract_row_content(token)
                headers = [h.strip() for h in header_row]
            elif token.type == "tbody_open":
                # Extract data rows
                for child in token.children or []:
                    if child.type == "tr":
                        row = self._extract_row_content(child)
                        if row:
                            rows.append(row)
        
        # Map table data to agent definitions
        for row in rows:
            if len(row) >= 3:
                agent_data = {
                    "name": row[0].strip(),
                    "role": row[1].strip(),
                    "system_message": row[2].strip()
                }
                agents.append(AgentDefinition(**agent_data))
        
        return agents

    def _extract_row_content(self, row_token) -> List[str]:
        """Extract content from a table row."""
        content = []
        
        for child in row_token.children or []:
            if child.type == "td" or child.type == "th":
                cell_content = ""
                for grandchild in child.children or []:
                    if grandchild.type == "text":
                        cell_content += grandchild.content
                    elif grandchild.type == "inline":
                        for text_token in grandchild.children or []:
                            if text_token.type == "text":
                                cell_content += text_token.content
                content.append(cell_content.strip())
        
        return content

    def _get_default_agents(self) -> List[AgentDefinition]:
        """Get default agent definitions."""
        return [
            AgentDefinition(
                name="Planner",
                role="Plan sprint goals and tasks",
                system_message="Plan incremental features for the project; ensure testability and maintainability; consult RAG for prior art and best practices."
            ),
            AgentDefinition(
                name="Coder",
                role="Implement features",
                system_message="Write clean, idiomatic code in the project's language, add unit/integration tests, keep functions small and focused, follow project conventions."
            ),
            AgentDefinition(
                name="Tester",
                role="Author & run tests",
                system_message="Use the project's testing framework; add comprehensive test coverage; verify functionality and edge cases; ensure tests are maintainable."
            ),
            AgentDefinition(
                name="Critic",
                role="Review & suggest fixes",
                system_message="Focus on architecture, code quality, error handling, security, performance, and adherence to best practices for the project's technology stack."
            ),
            AgentDefinition(
                name="RAG",
                role="Retrieval agent",
                system_message="Supply relevant snippets from project history, documentation, and codebase to reduce token usage and provide context for decisions."
            ),
        ]

    def create_default_configs(self, config_dir: Path, project_type: ProjectType = ProjectType.TYPESCRIPT) -> None:
        """Create default configuration files if they don't exist."""
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # Create default settings.md based on project type
        settings_file = config_dir / "settings.md"
        if not settings_file.exists():
            default_settings = self._get_default_settings(project_type)
            settings_file.write_text(default_settings)
        
        # Create default agents.md
        agents_file = config_dir / "agents.md"
        if not agents_file.exists():
            default_agents = self._get_default_agents_md(project_type)
            agents_file.write_text(default_agents)

    def _get_default_settings(self, project_type: ProjectType) -> str:
        """Get default settings content based on project type."""
        if project_type == ProjectType.PYTHON:
            return """# Settings

```yaml
project_name: "python_project"
project_goal: "Build a Python application with modern best practices."
project_type: "python"
num_sprints: 4
iterations_per_sprint: 8

llm_binding:
  api_base: "http://localhost:1234/v1"
  model_name: "llama3"
  api_type: "open_ai"
  api_key: "lmstudio"
  cache_seed: 42

work_dir: "./python_project"
vector_db_path: "./project_db"
git_branch_prefix: "sprint-"
human_input_mode: "NEVER"

rl:
  epsilon: 0.1
  alpha: 0.1
  gamma: 0.9
  state_buckets: 10

rag:
  top_k: 5
  max_doc_tokens: 4000

project_config:
  project_type: "python"
  language: "python"
  python:
    package_manager: "pip"
    test_command: "pytest"
    build_command: "python setup.py build"
    virtual_env: true
    requirements_file: "requirements.txt"

debug_mode: false
auto_commit: true
create_pr: false
```
"""
        elif project_type == ProjectType.REACT:
            return """# Settings

```yaml
project_name: "react_app"
project_goal: "Build a React application with modern UI/UX patterns."
project_type: "react"
num_sprints: 4
iterations_per_sprint: 8

llm_binding:
  api_base: "http://localhost:1234/v1"
  model_name: "llama3"
  api_type: "open_ai"
  api_key: "lmstudio"
  cache_seed: 42

work_dir: "./react_app"
vector_db_path: "./project_db"
git_branch_prefix: "sprint-"
human_input_mode: "NEVER"

rl:
  epsilon: 0.1
  alpha: 0.1
  gamma: 0.9
  state_buckets: 10

rag:
  top_k: 5
  max_doc_tokens: 4000

project_config:
  project_type: "react"
  language: "javascript"
  framework: "react"
  node:
    package_manager: "npm"
    test_command: "npm test"
    build_command: "npm run build"

debug_mode: false
auto_commit: true
create_pr: false
```
"""
        else:  # Default TypeScript
            return """# Settings

```yaml
project_name: "ts_project"
project_goal: "Build a TypeScript application with modern development practices."
project_type: "typescript"
num_sprints: 4
iterations_per_sprint: 8

llm_binding:
  api_base: "http://localhost:1234/v1"
  model_name: "llama3"
  api_type: "open_ai"
  api_key: "lmstudio"
  cache_seed: 42

work_dir: "./ts_project"
vector_db_path: "./project_db"
git_branch_prefix: "sprint-"
human_input_mode: "NEVER"

rl:
  epsilon: 0.1
  alpha: 0.1
  gamma: 0.9
  state_buckets: 10

rag:
  top_k: 5
  max_doc_tokens: 4000

project_config:
  project_type: "typescript"
  language: "typescript"
  node:
    package_manager: "npm"
    test_command: "npm test"
    build_command: "npm run build"

debug_mode: false
auto_commit: true
create_pr: false
```
"""

    def _get_default_agents_md(self, project_type: ProjectType) -> str:
        """Get default agents markdown content based on project type."""
        if project_type == ProjectType.PYTHON:
            return """# Agents

| Agent Name | Role  | System Message |
|------------|-------|----------------|
| Planner    | Plan sprint goals and tasks. | "Plan incremental Python features; ensure testability with pytest; consult RAG for Python best practices and patterns." |
| Coder      | Implement features in Python.    | "Write clean, idiomatic Python code, add unit/integration tests with pytest, keep functions small; follow PEP 8 and type hints." |
| Tester     | Author & run tests.          | "Use pytest; add comprehensive test coverage; verify functionality and edge cases; use pytest-cov for coverage." |
| Critic     | Review & suggest fixes.      | "Focus on Python architecture, code quality, error handling, security, and adherence to PEP standards." |
| RAG        | Retrieval agent.             | "Supply relevant snippets from project history and Python documentation to reduce token usage." |
"""
        elif project_type == ProjectType.REACT:
            return """# Agents

| Agent Name | Role  | System Message |
|------------|-------|----------------|
| Planner    | Plan sprint goals and tasks. | "Plan incremental React features; ensure component testability; consult RAG for React patterns and best practices." |
| Coder      | Implement features in React.    | "Write clean React components with hooks, add unit tests with Jest/React Testing Library, keep components focused and reusable." |
| Tester     | Author & run tests.          | "Use Jest and React Testing Library; add component and integration tests; verify user interactions and accessibility." |
| Critic     | Review & suggest fixes.      | "Focus on React architecture, component design, performance, accessibility, and modern React patterns." |
| RAG        | Retrieval agent.             | "Supply relevant snippets from project history and React documentation to reduce token usage." |
"""
        else:  # Default TypeScript
            return """# Agents

| Agent Name | Role  | System Message |
|------------|-------|----------------|
| Planner    | Plan sprint goals and tasks. | "Plan incremental TypeScript features; ensure testability and type safety; consult RAG for TypeScript patterns and best practices." |
| Coder      | Implement features in TS.    | "Write idiomatic TypeScript, add unit/integration tests, keep functions small; use strict mode and proper typing." |
| Tester     | Author & run tests.          | "Use Jest; add comprehensive test coverage; verify functionality and type safety; test edge cases." |
| Critic     | Review & suggest fixes.      | "Focus on TypeScript architecture, code quality, error handling, and adherence to TypeScript best practices." |
| RAG        | Retrieval agent.             | "Supply relevant snippets from project history and TypeScript documentation to reduce token usage." |
"""
