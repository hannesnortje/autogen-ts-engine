# IDE Integration for AutoGen Engine

This directory contains integrations that allow IDE agents (like Cursor or VSCode) to control and monitor the AutoGen Multi-Agent Development Engine through WebSocket communication.

## 🎯 **Overview**

The IDE integration provides:
- **Remote Control**: Start projects, run sprints, and manage development
- **Real-time Monitoring**: Watch sprint progress and agent activities
- **Status Visualization**: See project status in IDE status bars
- **Interactive Commands**: Control the engine through IDE interfaces

## 🏗️ **Architecture**

```
┌─────────────────┐    WebSocket    ┌──────────────────┐
│   IDE Agent     │ ◄─────────────► │  AutoGen Engine  │
│  (Cursor/VSCode) │                 │   (IDE Server)   │
└─────────────────┘                 └──────────────────┘
        │                                    │
        │ Commands                           │ Status Updates
        │ • start_project                    │ • Sprint Progress
        │ • run_sprint                       │ • Agent Activities
        │ • get_status                       │ • Results
        │ • get_results                      │
```

## 🚀 **Quick Start**

### 1. Start the AutoGen IDE Server

```bash
# Start the IDE interface server
autogen-ts-engine ide-server --host localhost --port 8765

# Or with custom settings
autogen-ts-engine ide-server \
  --host 0.0.0.0 \
  --port 8765 \
  --project-type typescript \
  --work-dir ./my-project
```

### 2. Connect IDE Agent

#### **Cursor IDE Agent**
```bash
# Run the Cursor agent
python examples/ide-integrations/cursor_agent.py --host localhost --port 8765

# Or with specific commands
python examples/ide-integrations/cursor_agent.py \
  --project-type typescript \
  --work-dir ./my-api \
  --project-goal "Build a REST API with Express.js" \
  --sprint 1
```

#### **VSCode Extension**
```javascript
// Install the VSCode extension and use commands:
// Ctrl+Shift+P -> "AutoGen: Connect"
// Ctrl+Shift+P -> "AutoGen: Start Project"
// Ctrl+Shift+P -> "AutoGen: Run Sprint"
```

## 📡 **WebSocket API**

### **Commands**

#### `start_project`
Start a new project with specified type and goal.

```json
{
  "command": "start_project",
  "params": {
    "project_type": "typescript",
    "work_dir": "./my-project",
    "project_goal": "Build a REST API with Express.js"
  },
  "timestamp": 1640995200.0,
  "request_id": "req_1640995200000"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "project_type": "typescript",
    "work_dir": "./my-project",
    "project_goal": "Build a REST API with Express.js",
    "agents": ["Planner", "Coder", "Tester", "Critic", "RAG"]
  },
  "message": "Project started successfully",
  "timestamp": 1640995200.0,
  "request_id": "req_1640995200000"
}
```

#### `run_sprint`
Run a specific sprint.

```json
{
  "command": "run_sprint",
  "params": {
    "sprint_number": 1
  },
  "timestamp": 1640995200.0,
  "request_id": "req_1640995200001"
}
```

#### `get_status`
Get current engine status.

```json
{
  "command": "get_status",
  "params": {},
  "timestamp": 1640995200.0,
  "request_id": "req_1640995200002"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "is_running": true,
    "current_sprint": {
      "sprint_number": 1,
      "status": "coding",
      "progress": 0.75,
      "current_agent": "Coder",
      "current_task": "Implementing API endpoints",
      "goals_achieved": ["Project setup", "Basic structure"],
      "goals_remaining": ["Add authentication", "Write tests"],
      "errors": [],
      "metrics": {"lines_of_code": 450, "test_coverage": 0.85}
    },
    "total_sprints": 4,
    "completed_sprints": 0,
    "project_type": "typescript",
    "project_goal": "Build a REST API with Express.js",
    "work_dir": "./my-project"
  },
  "message": "Status retrieved successfully",
  "timestamp": 1640995200.0,
  "request_id": "req_1640995200002"
}
```

#### `get_sprint_results`
Get sprint results.

```json
{
  "command": "get_sprint_results",
  "params": {
    "sprint_number": 1
  },
  "timestamp": 1640995200.0,
  "request_id": "req_1640995200003"
}
```

### **Status Updates**

The server broadcasts status updates to all connected clients:

```json
{
  "type": "status_update",
  "data": {
    "sprint_number": 1,
    "status": "testing",
    "progress": 0.9,
    "current_agent": "Tester",
    "current_task": "Running integration tests",
    "goals_achieved": ["Project setup", "Basic structure", "API endpoints"],
    "goals_remaining": ["Add authentication"],
    "errors": [],
    "metrics": {"lines_of_code": 650, "test_coverage": 0.92}
  },
  "timestamp": 1640995200.0
}
```

## 🎮 **IDE Agent Examples**

### **Cursor Agent Interactive Mode**

```bash
$ python cursor_agent.py --host localhost --port 8765

🔌 Connecting to AutoGen engine at ws://localhost:8765...
✅ Connected to AutoGen engine!

📊 Project Status:
  • Project: Build a REST API with Express.js
  • Type: typescript
  • Work Directory: ./my-project
  • Engine Running: ❌
  • Completed Sprints: 0/4

🎮 Interactive Mode - Type 'help' for commands

> help

📖 Available Commands:
  status                    - Show current project status
  start <type> <dir> <goal> - Start a new project
  sprint <number>           - Run a sprint
  results                   - Show sprint results
  help                      - Show this help
  quit/exit                 - Exit interactive mode

📝 Examples:
  start typescript ./my-api 'Build a REST API with Express.js'
  start python ./ml-pipeline 'Build a machine learning pipeline'
  sprint 1

> start typescript ./my-api 'Build a REST API with Express.js'
🚀 Starting typescript project: Build a REST API with Express.js
✅ Project started successfully!

> sprint 1
🏃 Running sprint 1...
✅ Sprint started!
👀 Monitoring sprint 1...
✅ Sprint completed!

📋 Sprint 1 Results:
  • Status: ✅ Success
  • Iterations: 8
  • Goals Achieved: 4
  • Goals Failed: 0
```

### **VSCode Extension Commands**

```javascript
// Available VSCode commands:
// autogen.connect - Connect to AutoGen engine
// autogen.disconnect - Disconnect from AutoGen engine
// autogen.startProject - Start a new project
// autogen.runSprint - Run a sprint
// autogen.showStatus - Show current status
// autogen.showResults - Show sprint results
```

## 🔧 **Custom IDE Integration**

### **Creating a Custom IDE Agent**

```python
import asyncio
from autogen_ts_engine.ide_interface import IDEClient

class CustomIDEAgent:
    def __init__(self, host="localhost", port=8765):
        self.client = IDEClient(host, port)
    
    async def connect(self):
        return await self.client.connect()
    
    async def start_project(self, project_type, work_dir, project_goal):
        return await self.client.start_project(project_type, work_dir, project_goal)
    
    async def run_sprint(self, sprint_number=1):
        return await self.client.run_sprint(sprint_number)
    
    async def get_status(self):
        return await self.client.get_status()
    
    async def get_sprint_results(self, sprint_number=None):
        return await self.client.get_sprint_results(sprint_number)

# Usage
async def main():
    agent = CustomIDEAgent()
    await agent.connect()
    
    # Start a project
    success = await agent.start_project(
        "typescript", 
        "./my-project", 
        "Build a REST API"
    )
    
    if success:
        # Run a sprint
        await agent.run_sprint(1)

asyncio.run(main())
```

### **WebSocket Client Example**

```javascript
const WebSocket = require('ws');

class AutoGenClient {
    constructor(host = 'localhost', port = 8765) {
        this.ws = new WebSocket(`ws://${host}:${port}`);
        this.setupEventHandlers();
    }
    
    setupEventHandlers() {
        this.ws.on('open', () => {
            console.log('Connected to AutoGen engine');
        });
        
        this.ws.on('message', (data) => {
            const message = JSON.parse(data);
            this.handleMessage(message);
        });
    }
    
    handleMessage(message) {
        if (message.type === 'status_update') {
            console.log('Status update:', message.data);
        }
    }
    
    async sendCommand(command, params = {}) {
        const message = {
            command: command,
            params: params,
            timestamp: Date.now() / 1000,
            request_id: `req_${Date.now()}`
        };
        
        this.ws.send(JSON.stringify(message));
    }
    
    startProject(projectType, workDir, projectGoal) {
        return this.sendCommand('start_project', {
            project_type: projectType,
            work_dir: workDir,
            project_goal: projectGoal
        });
    }
    
    runSprint(sprintNumber = 1) {
        return this.sendCommand('run_sprint', {
            sprint_number: sprintNumber
        });
    }
}

// Usage
const client = new AutoGenClient();
client.startProject('typescript', './my-project', 'Build a REST API');
```

## 📊 **Status Monitoring**

### **Sprint Status Types**

- `planning` - Agents are planning the sprint
- `coding` - Agents are implementing features
- `testing` - Agents are running tests
- `reviewing` - Agents are reviewing code
- `completed` - Sprint is finished

### **Progress Tracking**

The engine provides real-time progress updates:

```json
{
  "sprint_number": 1,
  "status": "coding",
  "progress": 0.75,
  "current_agent": "Coder",
  "current_task": "Implementing user authentication",
  "goals_achieved": ["Project setup", "Basic API structure"],
  "goals_remaining": ["Add tests", "Documentation"],
  "errors": [],
  "metrics": {
    "lines_of_code": 450,
    "test_coverage": 0.85,
    "functions": 12,
    "files": 8
  }
}
```

## 🎯 **Use Cases**

### **1. Automated Development**
```bash
# Start a project and run all sprints automatically
python cursor_agent.py \
  --project-type typescript \
  --work-dir ./my-api \
  --project-goal "Build a REST API with Express.js" \
  --sprint 1
```

### **2. Interactive Development**
```bash
# Connect and control manually
python cursor_agent.py
> start python ./ml-pipeline 'Build a machine learning pipeline'
> sprint 1
> status
> results
```

### **3. CI/CD Integration**
```javascript
// Integrate with CI/CD pipelines
const agent = new AutoGenClient();
await agent.startProject('typescript', './build', 'Build production API');
await agent.runSprint(1);
const results = await agent.getSprintResults(1);
```

### **4. Team Collaboration**
```bash
# Multiple team members can monitor the same project
# Each connects to the same AutoGen engine instance
python cursor_agent.py --host team-server --port 8765
```

## 🔒 **Security Considerations**

### **Network Security**
- Use HTTPS/WSS for production deployments
- Implement authentication for remote access
- Restrict access to trusted networks

### **Access Control**
```python
# Example: Add authentication to IDE interface
class SecureIDEInterface(IDEInterface):
    def __init__(self, settings, logger, api_key=None):
        super().__init__(settings, logger)
        self.api_key = api_key
    
    async def authenticate_client(self, websocket, message):
        if self.api_key and message.get('api_key') != self.api_key:
            await websocket.close(1008, 'Unauthorized')
            return False
        return True
```

## 🚀 **Deployment**

### **Local Development**
```bash
# Start AutoGen engine with IDE server
autogen-ts-engine ide-server --host localhost --port 8765

# Connect IDE agent
python cursor_agent.py --host localhost --port 8765
```

### **Remote Development**
```bash
# Start AutoGen engine on remote server
autogen-ts-engine ide-server --host 0.0.0.0 --port 8765

# Connect from local machine
python cursor_agent.py --host remote-server --port 8765
```

### **Docker Deployment**
```dockerfile
# Dockerfile for AutoGen engine with IDE interface
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install -e .

EXPOSE 8765

CMD ["autogen-ts-engine", "ide-server", "--host", "0.0.0.0", "--port", "8765"]
```

## 📚 **Next Steps**

1. **Install Dependencies**: `pip install websockets`
2. **Start IDE Server**: `autogen-ts-engine ide-server`
3. **Connect IDE Agent**: Use provided examples or create custom integration
4. **Monitor Development**: Watch real-time progress and results
5. **Extend Functionality**: Add custom commands and monitoring

The IDE integration transforms the AutoGen engine into a collaborative development platform that can be controlled and monitored from any IDE or development environment!
