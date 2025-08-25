# AutoGen Multi-Agent Development Engine

A comprehensive Python package that orchestrates an AutoGen multi-agent system to build any type of project in sprints (plan → code → test → review → commit/PR). Runs fully offline by default using LM Studio as an OpenAI-compatible API, manages context with a local vector DB (Chroma), and supports inner/outer reinforcement learning. Supports TypeScript, Python, React, Node.js, Java, Go, Rust, and custom project types.

## 🚀 Features

- 🤖 **Multi-Agent Development**: Planner, Coder, Tester, Critic, and RAG agents working together
- 🏠 **Offline-First**: Uses LM Studio for local LLM inference with mock LLM fallback
- 📚 **Context Management**: ChromaDB vector store for project memory and RAG
- 🧠 **Reinforcement Learning**: Inner/outer loop RL for continuous improvement
- ⚡ **Multi-Language Support**: TypeScript, Python, React, Node.js, Java, Go, Rust, and custom project types
- 📝 **Markdown Configs**: Easy configuration via Markdown files with YAML blocks
- 🔧 **Git Integration**: Automatic branching, commits, and optional PR creation
- 🧪 **Comprehensive Testing**: pytest, coverage, quality checks (black, flake8, mypy, bandit)
- 🛡️ **Error Recovery**: Circuit breakers, retry mechanisms, and system resilience
- 📊 **Sprint Artifacts**: Detailed reports, metrics, and burndown charts
- 🔍 **Integration Testing**: End-to-end validation and system health monitoring
- 📈 **Performance Analytics**: Real-time metrics and quality scoring

## 🎯 Quick Start

### 1. Install LM Studio (Optional)

For full LLM functionality, download and install [LM Studio](https://lmstudio.ai/), then:
1. Load a model (e.g., Llama 3, Phi-3 Mini)
2. Start the server on port 1234
3. Enable the OpenAI-compatible API

**Note**: The engine includes a mock LLM system for development and testing without requiring LM Studio.

### 2. Install the Engine

#### Option 1: Install with pipx (Recommended)
```bash
# Install globally with pipx
pipx install autogen-ts-engine

# Or install from local directory
pipx install .
```

#### Option 2: Install with pip
```bash
# Install from PyPI (when published)
pip install autogen-ts-engine

# Or install from local directory
pip install -e .

# Or install with requirements.txt
pip install -r requirements.txt
```

#### Option 3: Development Installation
```bash
# Install with development dependencies
pip install -e ".[dev]"

# Or install with requirements-dev.txt
pip install -r requirements-dev.txt
```

### 3. Create a Project

```bash
# Initialize a new Python project (default)
python test_mock_engine.py

# Or run with full LLM support
python autogen_ts_engine/main.py

# For TypeScript projects, update config/settings.md first
```

## ⚙️ Configuration

The engine uses Markdown files with YAML blocks for configuration:

### `config/settings.md`

```markdown
# Settings

```yaml
project_name: "python_project"
project_goal: "Build a Python application with modern best practices."
project_type: "python"
num_sprints: 2
iterations_per_sprint: 2

llm_binding:
  api_base: "http://localhost:1234/v1"
  model_name: "phi-3-mini-4k-instruct"
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

### `config/agents.md`

```markdown
# Agents

| Agent Name | Role  | System Message |
|------------|-------|----------------|
| Planner    | Plan sprint goals and tasks. | "Plan incremental features; ensure testability and best practices; consult RAG for prior art." |
| Coder      | Implement features.    | "Write idiomatic code, add unit/integration tests, keep functions small; follow language best practices." |
| Tester     | Author & run tests.          | "Use appropriate testing framework; add comprehensive tests; verify functionality." |
| Critic     | Review & suggest fixes.      | "Focus on architecture, code quality, error handling, and best practices." |
| RAG        | Retrieval agent.             | "Supply relevant snippets from scrum history and src/ to reduce token usage." |
```

## 🔧 Multi-Language Support

The engine supports multiple programming languages and frameworks:

### TypeScript/React Configuration
```yaml
project_type: "typescript"
project_config:
  project_type: "typescript"
  language: "typescript"
  framework: "react"
  node:
    package_manager: "npm"
    test_command: "npm test"
    build_command: "npm run build"
```

### Java/Spring Configuration
```yaml
project_type: "java"
project_config:
  project_type: "java"
  language: "java"
  framework: "spring"
  java:
    build_tool: "maven"
    test_command: "mvn test"
    build_command: "mvn clean install"
```

### Go/Gin Configuration
```yaml
project_type: "go"
project_config:
  project_type: "go"
  language: "go"
  framework: "gin"
  go:
    go_version: "1.21"
    test_command: "go test ./..."
    build_command: "go build"
```

## 📊 Testing and Quality Assurance

The engine includes comprehensive testing and quality checks:

### Automated Testing
- **Unit Tests**: pytest for Python, jest for TypeScript/Node.js
- **Integration Tests**: End-to-end functionality testing
- **Coverage Reports**: Code coverage analysis and reporting
- **Quality Checks**: Black (formatting), flake8 (linting), mypy (type checking), bandit (security)

### Test Runner Features
```python
# Run comprehensive tests
test_runner = TestRunner(project_dir)
metrics = test_runner.run_all_checks()

# Results include:
# - Test pass rate and coverage
# - Code quality scores
# - Security analysis
# - Build verification
# - Overall project score
```

## 🛡️ Error Recovery and Resilience

The engine includes robust error handling and recovery mechanisms:

### Circuit Breaker Pattern
- Prevents cascading failures
- Configurable failure thresholds
- Automatic recovery after timeout

### Retry Mechanisms
- Exponential backoff for transient failures
- Configurable retry counts per operation type
- Graceful degradation for non-critical failures

### Recovery Strategies
- **RETRY**: Attempt operation again with backoff
- **FALLBACK**: Use alternative implementation
- **ROLLBACK**: Revert to previous state
- **RESTART**: Restart component or service
- **SKIP**: Skip non-critical operations
- **ABORT**: Stop execution for critical failures

## 📈 Sprint Artifacts and Reporting

The engine generates comprehensive sprint artifacts:

### Sprint Summaries
- Detailed sprint reports in Markdown
- Metrics and performance data
- Error logs and recovery statistics
- Recommendations for improvement

### Project Reports
- Overall project health assessment
- Quality trends and metrics
- Burndown chart data for visualization
- Component status and recommendations

### Metrics Tracking
```json
{
  "test_pass_rate": 95.5,
  "test_coverage": 87.2,
  "build_success": true,
  "overall_score": 92.1,
  "total_issues": 3,
  "quality_results": [...]
}
```

## 🔍 Integration Testing

The engine includes comprehensive integration testing:

### System Health Monitoring
- Component initialization testing
- Workflow validation
- Performance benchmarking
- Memory usage monitoring

### End-to-End Validation
- Complete project lifecycle testing
- Multi-language project generation
- Error scenario testing
- Recovery mechanism validation

## 📁 Project Structure

When initialized, the engine creates:

```
work_dir/
├─ src/                      # Source code
│  └─ project_name/
│     ├─ main.py            # Main application
│     └─ __init__.py
├─ tests/                    # Test files
│  ├─ test_main.py
│  └─ __init__.py
├─ scrum/                    # Sprint artifacts
│  ├─ sprints/              # Sprint summaries
│  ├─ reports/              # Project reports
│  └─ metrics/              # JSON metrics
├─ config/                   # Configuration files
├─ project_db/               # ChromaDB persistence
├─ requirements.txt          # Python dependencies
├─ setup.py                 # Package setup
├─ pyproject.toml           # Modern Python config
└─ README.md                # Project documentation
```

## 🚀 CLI Usage

```bash
# Run with mock LLM (recommended for development)
python test_mock_engine.py

# Run with full LLM support
python autogen_ts_engine/main.py

# Run integration tests
python test_integration.py

# Run multi-language demonstration
python demo_multi_language.py

# Run final system test
python test_final_system.py
```

## 🏗️ Architecture

### Core Components

- **SprintRunner**: Orchestrates multi-agent development sprints
- **AgentFactory**: Creates and configures AutoGen agents
- **CodeGenerator**: Generates project structures and code
- **TestRunner**: Executes tests and quality checks
- **SprintArtifactsManager**: Manages reports and documentation
- **ErrorRecoveryManager**: Handles failures and recovery
- **IntegrationTester**: Validates system health

### Agents

- **Planner**: Synthesizes goals and creates task breakdowns
- **Coder**: Implements features and tests
- **Tester**: Runs tests and validates functionality
- **Critic**: Reviews code and suggests improvements
- **RAG**: Provides context from project history

### Reinforcement Learning

- **Inner Loop**: Bandit/Q-learning for action selection
- **Outer Loop**: Sprint-level policy updates based on reward trends
- **Rewards**: Test pass rate, coverage, linting, performance metrics

### RAG System

- **Embeddings**: Sentence-Transformers for semantic search
- **Storage**: ChromaDB for local vector persistence
- **Context**: Indexes source code, tests, and sprint artifacts

## 🧪 Development

### Local Development Setup

```bash
git clone https://github.com/your-org/autogen-ts-engine.git
cd autogen-ts-engine
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test suites
python test_mock_engine.py
python test_integration.py
python test_final_system.py
```

### Code Quality

```bash
# Format code
black autogen_ts_engine/

# Sort imports
isort autogen_ts_engine/

# Type checking
mypy autogen_ts_engine/

# Linting
ruff check autogen_ts_engine/
```

## 🔧 Troubleshooting

### Mock LLM Mode

If you encounter LLM connection issues, the engine automatically falls back to mock LLM mode for development and testing.

### LM Studio Connection Issues

If you see connection errors:

1. Ensure LM Studio is running
2. Check that the server is enabled on port 1234
3. Verify a model is loaded
4. Test with: `curl http://localhost:1234/v1/models`

### ChromaDB Issues

- Clear `project_db/` directory to reset vector store
- Check disk space for embeddings storage

### Build Issues

- Ensure appropriate language toolchain is installed
- Check configuration for correct package managers
- Verify project-specific configuration files

## 📊 Performance Metrics

The engine tracks comprehensive performance metrics:

- **Test Coverage**: Code coverage percentage
- **Quality Score**: Overall project quality (0-100)
- **Build Success**: Successful compilation rate
- **Error Recovery**: Recovery success rate
- **Sprint Success**: Sprint completion rate

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run integration tests: `python test_integration.py`
6. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🎉 Status

**Production Ready**: The AutoGen TS Engine is fully functional and ready for production use with comprehensive testing, error recovery, and multi-language support.
