# AutoGen Engine - Usage Examples

This document shows how to use the AutoGen Multi-Agent Development Engine for different project types.

## 🚀 Quick Start Examples

### 1. TypeScript API Server

```bash
# Create a TypeScript API server
autogen-ts-engine run \
  --project-type typescript \
  --work-dir ./my-api-server \
  --config-dir ./my-api-config
```

**Configuration** (`config/settings.md`):
```yaml
project_name: "api-server"
project_goal: "Build a REST API server with Express.js, TypeScript, and PostgreSQL for a task management system"
project_type: "typescript"
num_sprints: 4
iterations_per_sprint: 8
```

### 2. Python ML Pipeline

```bash
# Create a Python machine learning pipeline
autogen-ts-engine run \
  --project-type python \
  --work-dir ./my-ml-pipeline \
  --config-dir ./my-ml-config
```

**Configuration** (`config/settings.md`):
```yaml
project_name: "ml-pipeline"
project_goal: "Build a machine learning API with FastAPI, scikit-learn, and PostgreSQL for predictive analytics"
project_type: "python"
num_sprints: 4
iterations_per_sprint: 8
```

### 3. React Dashboard

```bash
# Create a React dashboard application
autogen-ts-engine run \
  --project-type react \
  --work-dir ./my-dashboard \
  --config-dir ./my-dashboard-config
```

**Configuration** (`config/settings.md`):
```yaml
project_name: "data-dashboard"
project_goal: "Build a data visualization dashboard with React, D3.js, and Material-UI for real-time analytics"
project_type: "react"
num_sprints: 4
iterations_per_sprint: 8
```

## 📁 Project Structure

After running the engine, you'll have:

```
my-project/
├── config/
│   ├── settings.md          # Project configuration
│   └── agents.md            # Agent definitions
├── scrum/
│   ├── sprint_1.md          # Sprint goals and results
│   ├── sprint_2.md          # Ongoing development
│   └── sprint_N.md          # Sprint tracking
├── src/                     # Source code
├── tests/                   # Test files
├── project_db/              # Vector database
├── package.json             # Node.js dependencies (if applicable)
├── requirements.txt         # Python dependencies (if applicable)
└── README.md               # Project documentation
```

## 🎯 Custom Project Types

### Full-Stack Application

```bash
# Create a full-stack application
autogen-ts-engine run \
  --project-type custom \
  --work-dir ./my-fullstack-app
```

**Configuration** (`config/settings.md`):
```yaml
project_name: "fullstack-app"
project_goal: "Build a task management app with React frontend and Node.js backend"
project_type: "custom"
project_config:
  project_type: "custom"
  language: "multi"
  frameworks: ["react", "express", "mongodb"]
  custom_config:
    frontend: "react"
    backend: "nodejs"
    database: "mongodb"
```

### CLI Tool

```bash
# Create a command-line tool
autogen-ts-engine run \
  --project-type typescript \
  --work-dir ./my-cli-tool
```

**Configuration** (`config/settings.md`):
```yaml
project_name: "cli-tool"
project_goal: "Build a command-line interface tool for data processing with TypeScript"
project_type: "typescript"
project_config:
  framework: "cli"
  node:
    package_manager: "npm"
    test_command: "npm test"
    build_command: "npm run build"
```

## 🔧 Advanced Configuration

### Custom Agents

**Configuration** (`config/agents.md`):
```markdown
| Agent Name | Role  | System Message |
|------------|-------|----------------|
| Planner    | Plan sprint goals and tasks. | "Plan incremental features for {project_type}; ensure testability and maintainability." |
| Coder      | Implement features.    | "Write clean, idiomatic {language} code, add unit/integration tests." |
| Tester     | Author & run tests.          | "Use {test_framework}; add comprehensive test coverage." |
| Critic     | Review & suggest fixes.      | "Focus on architecture, code quality, error handling." |
| Security   | Security review. | "Focus on security best practices, input validation, and secure coding patterns." |
| DevOps     | Infrastructure. | "Handle deployment configuration, CI/CD setup, and infrastructure as code." |
| RAG        | Retrieval agent.             | "Supply relevant snippets from project history and documentation." |
```

### Multi-Language Projects

```yaml
project_config:
  project_type: "custom"
  language: "multi"
  frameworks: ["react", "fastapi", "postgresql"]
  custom_config:
    frontend:
      language: "typescript"
      framework: "react"
      build_tool: "vite"
    backend:
      language: "python"
      framework: "fastapi"
      database: "postgresql"
    deployment:
      platform: "docker"
      orchestration: "kubernetes"
```

## 📊 Sprint Management

The engine creates sprint files automatically:

### Sprint Goals (`scrum/sprint_1.md`)
```markdown
# Sprint 1 Goals

## Focus Area
- Project setup and basic structure
- Core functionality implementation

## Goals
- [ ] Initialize project structure
- [ ] Set up development environment
- [ ] Implement basic API endpoints
- [ ] Add unit tests

## Acceptance Criteria
- Project builds successfully
- All tests pass
- Basic functionality works
- Documentation is complete
```

### Sprint Results (`scrum/sprint_1.md` - after completion)
```markdown
# Sprint 1 Results

## Status: ✅ Completed

## Goals Achieved
- [x] Initialize project structure
- [x] Set up development environment
- [x] Implement basic API endpoints
- [x] Add unit tests

## Test Results
- Tests: 15 passed, 0 failed
- Coverage: 85%
- Build: ✅ Success

## Metrics
- Lines of code: 450
- Functions: 12
- Files: 8

## Next Sprint Planning
- Add authentication system
- Implement database integration
- Add API documentation
```

## 🎨 Example Project Templates

### 1. E-commerce API
```yaml
project_goal: "Build a RESTful e-commerce API with user authentication, product catalog, and order management"
project_type: "typescript"
framework: "express"
```

### 2. Data Science Dashboard
```yaml
project_goal: "Create an interactive dashboard for data visualization with real-time analytics and ML model monitoring"
project_type: "python"
framework: "streamlit"
```

### 3. Mobile App Backend
```yaml
project_goal: "Develop a scalable backend for a mobile app with user management, push notifications, and real-time features"
project_type: "nodejs"
framework: "express"
```

### 4. Microservices Architecture
```yaml
project_goal: "Build a microservices architecture with service discovery, load balancing, and distributed tracing"
project_type: "custom"
frameworks: ["docker", "kubernetes", "golang"]
```

## 🚀 Getting Started

1. **Choose your project type**:
   ```bash
   autogen-ts-engine run --project-type typescript
   ```

2. **Customize configuration**:
   - Edit `config/settings.md` for project settings
   - Edit `config/agents.md` for agent behavior

3. **Run the engine**:
   ```bash
   autogen-ts-engine run --work-dir ./my-project
   ```

4. **Monitor progress**:
   - Check `scrum/` folder for sprint progress
   - Review generated code in `src/`
   - Run tests and build commands

5. **Iterate and improve**:
   - Modify configurations based on results
   - Add custom agents for specific needs
   - Extend with project-specific tools

## 🔧 Troubleshooting

### Common Issues

1. **LM Studio not running**:
   ```bash
   # Start LM Studio and load a model
   # Enable OpenAI-compatible API on port 1234
   ```

2. **Missing dependencies**:
   ```bash
   # Install project dependencies
   cd my-project
   npm install  # for Node.js projects
   pip install -r requirements.txt  # for Python projects
   ```

3. **Configuration errors**:
   ```bash
   # Validate configuration
   autogen-ts-engine run --debug
   ```

### Debug Mode

```bash
# Run with debug output
autogen-ts-engine run --debug --work-dir ./my-project
```

This will show detailed logs of agent interactions, configuration parsing, and error details.

## 📚 Next Steps

1. **Explore templates** in the `examples/` directory
2. **Customize agents** for your specific needs
3. **Add project-specific tools** and integrations
4. **Extend the engine** with new project types
5. **Contribute** to the project and share your templates

The AutoGen Multi-Agent Development Engine is designed to be flexible and extensible. You can build any type of project by customizing the configuration and agent definitions!
