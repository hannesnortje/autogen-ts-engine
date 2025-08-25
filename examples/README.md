# AutoGen TS Engine - Project Templates

This directory contains example configuration templates for different project types that the AutoGen TS Engine can build.

## 📁 Template Structure

Each template includes:
- `config/settings.md` - Project configuration and settings
- `config/agents.md` - Agent definitions and roles
- `scrum/` - Sprint goals and results (created during development)

## 🚀 Available Templates

### 1. **TypeScript Application** (`typescript-app/`)
A modern TypeScript application with Node.js backend.

**Use case**: APIs, CLI tools, libraries, backend services

### 2. **React Application** (`react-app/`)
A React frontend application with modern UI/UX.

**Use case**: Web applications, dashboards, user interfaces

### 3. **Python Application** (`python-app/`)
A Python application with modern development practices.

**Use case**: Data science, APIs, automation, machine learning

### 4. **Full-Stack Application** (`fullstack-app/`)
A complete full-stack application with frontend and backend.

**Use case**: Complete web applications, SaaS products

### 5. **Library/Framework** (`library/`)
A reusable library or framework.

**Use case**: Open source libraries, frameworks, tools

### 6. **CLI Tool** (`cli-tool/`)
A command-line interface tool.

**Use case**: Developer tools, automation scripts, utilities

## 🎯 How to Use Templates

### Option 1: Copy Template
```bash
# Copy a template to your project
cp -r examples/typescript-app/config ./my-project/

# Run the engine
autogen-ts-engine run --config-dir ./my-project/config --work-dir ./my-project
```

### Option 2: Use as Reference
```bash
# Create your own config based on templates
mkdir -p my-project/config
# Copy and modify settings.md and agents.md from templates
```

### Option 3: Let Engine Create Defaults
```bash
# The engine will create default configs based on project type
autogen-ts-engine run --work-dir ./my-project
```

## 📋 Template Customization

Each template can be customized by editing:

### `config/settings.md`
```yaml
project_name: "your-project-name"
project_goal: "Your specific project goal and requirements"
project_type: "typescript"  # or "python", "react", etc.
num_sprints: 4
iterations_per_sprint: 8
# ... other settings
```

### `config/agents.md`
```markdown
| Agent Name | Role  | System Message |
|------------|-------|----------------|
| Planner    | Plan sprint goals and tasks. | "Custom planning instructions..." |
| Coder      | Implement features.    | "Custom coding guidelines..." |
# ... customize for your project
```

## 🔧 Advanced Configuration

### Custom Project Types
You can create custom project types by:

1. Adding new `ProjectType` enum values in `schemas.py`
2. Creating custom configuration templates
3. Extending the engine with project-specific tools

### Multi-Language Projects
For projects using multiple languages:

```yaml
project_config:
  project_type: "custom"
  language: "multi"
  frameworks: ["react", "fastapi", "postgresql"]
  custom_config:
    frontend: "react"
    backend: "python"
    database: "postgresql"
```

### Specialized Agents
Add project-specific agents:

```markdown
| Agent Name | Role  | System Message |
|------------|-------|----------------|
| Security   | Security review. | "Focus on security best practices..." |
| DevOps     | Infrastructure. | "Handle deployment and CI/CD..." |
```

## 📊 Sprint Management

As the engine runs, it creates:

- `scrum/sprint_1.md` - Initial sprint goals and results
- `scrum/sprint_2.md` - Subsequent sprint progress
- `scrum/sprint_N.md` - Ongoing development tracking

Each sprint file contains:
- Sprint goals and focus areas
- Achievements and failures
- Test results and metrics
- Code changes and artifacts
- Next sprint planning

## 🎨 Example Projects

### TypeScript API Server
```yaml
project_goal: "Build a REST API server with Express.js, TypeScript, and PostgreSQL"
project_type: "typescript"
framework: "express"
```

### React Dashboard
```yaml
project_goal: "Create a data visualization dashboard with React, D3.js, and Material-UI"
project_type: "react"
framework: "react"
```

### Python ML Pipeline
```yaml
project_goal: "Develop a machine learning pipeline with scikit-learn, pandas, and FastAPI"
project_type: "python"
framework: "fastapi"
```

### Full-Stack App
```yaml
project_goal: "Build a task management app with React frontend and Node.js backend"
project_type: "custom"
frameworks: ["react", "express", "mongodb"]
```

## 🚀 Getting Started

1. **Choose a template** that matches your project type
2. **Copy the config files** to your project directory
3. **Customize the settings** for your specific needs
4. **Run the engine** and watch your project come to life!

The AutoGen TS Engine will use these configurations to guide the multi-agent development process, creating a complete, working project based on your specifications.
