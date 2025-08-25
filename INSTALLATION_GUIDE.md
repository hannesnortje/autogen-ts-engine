# AutoGen Engine - Installation Guide

## 🎯 **Overview**

The AutoGen Multi-Agent Development Engine can be installed in multiple ways depending on your needs. This guide covers all installation methods and their use cases.

## 📦 **Installation Methods**

### **1. pipx Installation (Recommended for Users)**

`pipx` installs Python applications in isolated environments, making it perfect for command-line tools.

```bash
# Install globally with pipx
pipx install autogen-ts-engine

# Or install from local directory
pipx install .

# Verify installation
autogen-ts-engine --help
```

**Benefits:**
- ✅ Isolated environment (no conflicts with other packages)
- ✅ Global availability (`autogen-ts-engine` command works everywhere)
- ✅ Easy updates (`pipx upgrade autogen-ts-engine`)
- ✅ Clean uninstall (`pipx uninstall autogen-ts-engine`)

### **2. pip Installation**

Standard pip installation for development or when you need the package in your current environment.

```bash
# Install from PyPI (when published)
pip install autogen-ts-engine

# Or install from local directory
pip install -e .

# Or install with requirements.txt
pip install -r requirements.txt
```

**Benefits:**
- ✅ Works with existing virtual environments
- ✅ Can be used in scripts and other Python code
- ✅ Easy to modify and develop

### **3. Development Installation**

For contributors and developers who want to modify the engine.

```bash
# Install with development dependencies
pip install -e ".[dev]"

# Or install with requirements-dev.txt
pip install -r requirements-dev.txt
```

**Benefits:**
- ✅ Includes testing and development tools
- ✅ Editable installation (changes are immediately available)
- ✅ All development dependencies included

## 🔧 **Dependencies**

### **Core Dependencies**

The engine requires these core packages:

```txt
# AutoGen framework
pyautogen>=0.2.0

# Vector database and embeddings
chromadb>=0.4.0
sentence-transformers>=2.2.0

# Reinforcement learning
gymnasium>=0.29.0
numpy>=1.21.0

# Data validation and configuration
pydantic>=2.0.0
markdown-it-py>=3.0.0
pyyaml>=6.0

# User interface and logging
rich>=13.0.0

# HTTP and API communication
requests>=2.28.0
openai>=1.0.0

# WebSocket communication for IDE integration
websockets>=11.0.0
```

### **Development Dependencies**

For development and testing:

```txt
# Testing
pytest>=7.0.0
pytest-cov>=4.0.0

# Code formatting and linting
black>=23.0.0
isort>=5.12.0
mypy>=1.0.0
ruff>=0.1.0
```

## 🚀 **Quick Start**

### **1. Install the Engine**

```bash
# Recommended: Install with pipx
pipx install autogen-ts-engine

# Alternative: Install with pip
pip install autogen-ts-engine
```

### **2. Set up LM Studio**

1. Download and install [LM Studio](https://lmstudio.ai/)
2. Load a model (e.g., Llama 3)
3. Start the server on port 1234
4. Enable the OpenAI-compatible API

### **3. Create Your First Project**

```bash
# Create a TypeScript project
autogen-ts-engine run --project-type typescript --work-dir ./my-project

# Create a Python project
autogen-ts-engine run --project-type python --work-dir ./my-python-project

# Create a React project
autogen-ts-engine run --project-type react --work-dir ./my-react-app
```

## 🎮 **IDE Integration**

### **Start IDE Server**

```bash
# Start the IDE interface server
autogen-ts-engine ide-server --host localhost --port 8765
```

### **Connect IDE Agent**

```bash
# Run the Cursor agent
python examples/ide-integrations/cursor_agent.py

# Or connect from VSCode extension
# Use the AutoGen extension commands
```

## 📁 **Project Structure**

After installation, your project will have this structure:

```
my-project/
├── config/
│   ├── settings.md          # Project configuration
│   └── agents.md            # Agent definitions
├── scrum/
│   ├── sprint_1.md          # Sprint goals and results
│   └── sprint_N.md          # Ongoing development
├── src/                     # Source code
├── tests/                   # Test files
├── project_db/              # Vector database
├── package.json             # Node.js dependencies (if applicable)
├── requirements.txt         # Python dependencies (if applicable)
└── README.md               # Project documentation
```

## 🔧 **Configuration**

### **Project Settings** (`config/settings.md`)

```yaml
project_name: "my-project"
project_goal: "Build a REST API with Express.js"
project_type: "typescript"
num_sprints: 4
iterations_per_sprint: 8

llm_binding:
  api_base: "http://localhost:1234/v1"
  model_name: "llama3"
  api_type: "open_ai"
  api_key: "lmstudio"

work_dir: "./my-project"
vector_db_path: "./project_db"
git_branch_prefix: "sprint-"
human_input_mode: "NEVER"
```

### **Agent Configuration** (`config/agents.md`)

```markdown
| Agent Name | Role  | System Message |
|------------|-------|----------------|
| Planner    | Plan sprint goals and tasks. | "Plan incremental features..." |
| Coder      | Implement features.    | "Write clean, idiomatic code..." |
| Tester     | Author & run tests.          | "Use testing framework..." |
| Critic     | Review & suggest fixes.      | "Focus on architecture..." |
| RAG        | Retrieval agent.             | "Supply relevant snippets..." |
```

## 🎯 **Use Cases**

### **1. Individual Developer**

```bash
# Install for personal use
pipx install autogen-ts-engine

# Create projects
autogen-ts-engine run --project-type typescript --work-dir ./my-api
autogen-ts-engine run --project-type python --work-dir ./my-ml-pipeline
```

### **2. Team Development**

```bash
# Install in team environment
pip install autogen-ts-engine

# Use with shared configuration
autogen-ts-engine run --config-dir ./team-config --work-dir ./team-project
```

### **3. CI/CD Pipeline**

```bash
# Install in CI environment
pip install autogen-ts-engine

# Run automated development
autogen-ts-engine run --project-type typescript --work-dir ./build
```

### **4. IDE Integration**

```bash
# Start IDE server
autogen-ts-engine ide-server --host 0.0.0.0 --port 8765

# Connect from IDE
python examples/ide-integrations/cursor_agent.py --host server-ip --port 8765
```

## 🔒 **Security Considerations**

### **Network Security**

- Use HTTPS/WSS for production deployments
- Implement authentication for remote access
- Restrict access to trusted networks

### **Environment Variables**

```bash
# Set environment variables for sensitive data
export AUTOGEN_API_KEY="your-api-key"
export AUTOGEN_HOST="your-host"
export AUTOGEN_PORT="8765"
```

## 🚀 **Deployment Options**

### **Local Development**

```bash
# Install locally
pip install -e .

# Run with local LM Studio
autogen-ts-engine run --work-dir ./local-project
```

### **Remote Development**

```bash
# Install on remote server
pip install autogen-ts-engine

# Start IDE server
autogen-ts-engine ide-server --host 0.0.0.0 --port 8765

# Connect from local machine
python cursor_agent.py --host remote-server --port 8765
```

### **Docker Deployment**

```dockerfile
# Dockerfile for AutoGen engine
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install -e .

EXPOSE 8765

CMD ["autogen-ts-engine", "ide-server", "--host", "0.0.0.0", "--port", "8765"]
```

## 🔧 **Troubleshooting**

### **Common Issues**

1. **Import Errors**
   ```bash
   # Reinstall with correct dependencies
   pip uninstall autogen-ts-engine
   pip install -r requirements.txt
   ```

2. **LM Studio Connection**
   ```bash
   # Check if LM Studio is running
   curl http://localhost:1234/v1/models
   ```

3. **Permission Errors**
   ```bash
   # Use pipx for global installation
   pipx install autogen-ts-engine
   ```

### **Debug Mode**

```bash
# Run with debug output
autogen-ts-engine run --debug --work-dir ./my-project
```

## 📚 **Next Steps**

1. **Install the engine** using your preferred method
2. **Set up LM Studio** for local LLM inference
3. **Create your first project** with `autogen-ts-engine run`
4. **Explore IDE integration** for enhanced development experience
5. **Customize agents** and configurations for your specific needs

The AutoGen Multi-Agent Development Engine is now ready to help you build any type of project with AI-powered multi-agent collaboration! 🚀
