"""IDE Interface for AutoGen Engine Integration."""

import json
import asyncio
import websockets
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
import threading
import time

from .schemas import Settings, AgentDefinition, SprintResult, ProjectType
from .sprint_runner import SprintRunner
from .config_parser import ConfigParser
from .logging_utils import setup_logging


@dataclass
class IDECommand:
    """Command from IDE agent."""
    command: str
    params: Dict[str, Any]
    timestamp: float
    request_id: str


@dataclass
class IDEResponse:
    """Response to IDE agent."""
    success: bool
    data: Dict[str, Any]
    message: str
    timestamp: float
    request_id: str


@dataclass
class SprintStatus:
    """Current sprint status for IDE monitoring."""
    sprint_number: int
    status: str  # "planning", "coding", "testing", "reviewing", "completed"
    progress: float  # 0.0 to 1.0
    current_agent: str
    current_task: str
    goals_achieved: List[str]
    goals_remaining: List[str]
    errors: List[str]
    metrics: Dict[str, Any]


class IDEInterface:
    """Interface for IDE agents to control and monitor the AutoGen engine."""
    
    def __init__(self, settings: Settings, logger=None):
        self.settings = settings
        self.logger = logger or setup_logging(debug_mode=settings.debug_mode)
        self.sprint_runner = SprintRunner(settings, self.logger)
        self.config_parser = ConfigParser()
        
        # Status tracking
        self.current_sprint: Optional[SprintStatus] = None
        self.sprint_results: List[SprintResult] = []
        self.is_running = False
        self.websocket_server = None
        self.clients: List[websockets.WebSocketServerProtocol] = []
        
        # Callbacks for IDE integration
        self.on_sprint_start: Optional[Callable] = None
        self.on_sprint_progress: Optional[Callable] = None
        self.on_sprint_complete: Optional[Callable] = None
        self.on_error: Optional[Callable] = None

    async def start_websocket_server(self, host: str = "localhost", port: int = 8765):
        """Start WebSocket server for IDE communication."""
        self.websocket_server = await websockets.serve(
            self.handle_client, host, port
        )
        self.logger.info(f"IDE Interface WebSocket server started on ws://{host}:{port}")
        
        # Keep server running
        await self.websocket_server.wait_closed()

    async def handle_client(self, websocket, path):
        """Handle WebSocket client connections."""
        self.clients.append(websocket)
        self.logger.info("IDE client connected")
        
        try:
            async for message in websocket:
                await self.process_command(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.clients.remove(websocket)
            self.logger.info("IDE client disconnected")

    async def process_command(self, websocket, message: str):
        """Process command from IDE agent."""
        try:
            data = json.loads(message)
            command = IDECommand(**data)
            
            # Process command
            response = await self.execute_command(command)
            
            # Send response
            await websocket.send(json.dumps(asdict(response)))
            
        except Exception as e:
            error_response = IDEResponse(
                success=False,
                data={},
                message=f"Error processing command: {str(e)}",
                timestamp=time.time(),
                request_id=data.get("request_id", "unknown")
            )
            await websocket.send(json.dumps(asdict(error_response)))

    async def execute_command(self, command: IDECommand) -> IDEResponse:
        """Execute command from IDE agent."""
        try:
            if command.command == "start_project":
                return await self._start_project(command.params)
            elif command.command == "run_sprint":
                return await self._run_sprint(command.params)
            elif command.command == "get_status":
                return await self._get_status(command.params)
            elif command.command == "stop_engine":
                return await self._stop_engine(command.params)
            elif command.command == "update_config":
                return await self._update_config(command.params)
            elif command.command == "get_sprint_results":
                return await self._get_sprint_results(command.params)
            else:
                return IDEResponse(
                    success=False,
                    data={},
                    message=f"Unknown command: {command.command}",
                    timestamp=time.time(),
                    request_id=command.request_id
                )
        except Exception as e:
            return IDEResponse(
                success=False,
                data={},
                message=f"Command execution failed: {str(e)}",
                timestamp=time.time(),
                request_id=command.request_id
            )

    async def _start_project(self, params: Dict[str, Any]) -> IDEResponse:
        """Start a new project."""
        try:
            project_type = params.get("project_type", "typescript")
            work_dir = params.get("work_dir", "./project")
            project_goal = params.get("project_goal", "Build a new project")
            
            # Update settings
            self.settings.project_type = ProjectType(project_type)
            self.settings.work_dir = work_dir
            self.settings.project_goal = project_goal
            
            # Initialize project
            work_path = Path(work_dir)
            config_path = work_path / "config"
            
            # Create default configs
            self.config_parser.create_default_configs(config_path, self.settings.project_type)
            
            # Parse agents
            agent_definitions = self.config_parser.parse_agents(config_path)
            
            return IDEResponse(
                success=True,
                data={
                    "project_type": project_type,
                    "work_dir": work_dir,
                    "project_goal": project_goal,
                    "agents": [agent.name for agent in agent_definitions]
                },
                message="Project started successfully",
                timestamp=time.time(),
                request_id=params.get("request_id", "")
            )
        except Exception as e:
            return IDEResponse(
                success=False,
                data={},
                message=f"Failed to start project: {str(e)}",
                timestamp=time.time(),
                request_id=params.get("request_id", "")
            )

    async def _run_sprint(self, params: Dict[str, Any]) -> IDEResponse:
        """Run a sprint."""
        try:
            sprint_number = params.get("sprint_number", 1)
            
            # Parse agents
            work_path = Path(self.settings.work_dir)
            config_path = work_path / "config"
            agent_definitions = self.config_parser.parse_agents(config_path)
            
            # Run sprint in background
            def run_sprint():
                try:
                    results = self.sprint_runner.run_sprints(agent_definitions)
                    self.sprint_results = results
                except Exception as e:
                    self.logger.error(f"Sprint execution failed: {e}")
            
            # Start sprint in thread
            sprint_thread = threading.Thread(target=run_sprint)
            sprint_thread.start()
            
            return IDEResponse(
                success=True,
                data={"sprint_number": sprint_number},
                message="Sprint started",
                timestamp=time.time(),
                request_id=params.get("request_id", "")
            )
        except Exception as e:
            return IDEResponse(
                success=False,
                data={},
                message=f"Failed to run sprint: {str(e)}",
                timestamp=time.time(),
                request_id=params.get("request_id", "")
            )

    async def _get_status(self, params: Dict[str, Any]) -> IDEResponse:
        """Get current engine status."""
        try:
            status_data = {
                "is_running": self.is_running,
                "current_sprint": asdict(self.current_sprint) if self.current_sprint else None,
                "total_sprints": len(self.sprint_results),
                "completed_sprints": len([r for r in self.sprint_results if r.success]),
                "project_type": self.settings.project_type.value,
                "project_goal": self.settings.project_goal,
                "work_dir": self.settings.work_dir
            }
            
            return IDEResponse(
                success=True,
                data=status_data,
                message="Status retrieved successfully",
                timestamp=time.time(),
                request_id=params.get("request_id", "")
            )
        except Exception as e:
            return IDEResponse(
                success=False,
                data={},
                message=f"Failed to get status: {str(e)}",
                timestamp=time.time(),
                request_id=params.get("request_id", "")
            )

    async def _stop_engine(self, params: Dict[str, Any]) -> IDEResponse:
        """Stop the engine."""
        try:
            self.is_running = False
            return IDEResponse(
                success=True,
                data={},
                message="Engine stopped",
                timestamp=time.time(),
                request_id=params.get("request_id", "")
            )
        except Exception as e:
            return IDEResponse(
                success=False,
                data={},
                message=f"Failed to stop engine: {str(e)}",
                timestamp=time.time(),
                request_id=params.get("request_id", "")
            )

    async def _update_config(self, params: Dict[str, Any]) -> IDEResponse:
        """Update configuration."""
        try:
            config_updates = params.get("config", {})
            
            # Update settings
            for key, value in config_updates.items():
                if hasattr(self.settings, key):
                    setattr(self.settings, key, value)
            
            return IDEResponse(
                success=True,
                data={"updated_keys": list(config_updates.keys())},
                message="Configuration updated successfully",
                timestamp=time.time(),
                request_id=params.get("request_id", "")
            )
        except Exception as e:
            return IDEResponse(
                success=False,
                data={},
                message=f"Failed to update config: {str(e)}",
                timestamp=time.time(),
                request_id=params.get("request_id", "")
            )

    async def _get_sprint_results(self, params: Dict[str, Any]) -> IDEResponse:
        """Get sprint results."""
        try:
            sprint_number = params.get("sprint_number")
            
            if sprint_number is not None:
                # Get specific sprint
                results = [r for r in self.sprint_results if r.sprint_number == sprint_number]
            else:
                # Get all results
                results = self.sprint_results
            
            results_data = [asdict(result) for result in results]
            
            return IDEResponse(
                success=True,
                data={"results": results_data},
                message="Sprint results retrieved successfully",
                timestamp=time.time(),
                request_id=params.get("request_id", "")
            )
        except Exception as e:
            return IDEResponse(
                success=False,
                data={},
                message=f"Failed to get sprint results: {str(e)}",
                timestamp=time.time(),
                request_id=params.get("request_id", "")
            )

    async def broadcast_status(self, status: SprintStatus):
        """Broadcast status update to all connected IDE clients."""
        if not self.clients:
            return
        
        message = {
            "type": "status_update",
            "data": asdict(status),
            "timestamp": time.time()
        }
        
        # Send to all connected clients
        await asyncio.gather(
            *[client.send(json.dumps(message)) for client in self.clients],
            return_exceptions=True
        )

    def update_sprint_status(self, status: SprintStatus):
        """Update current sprint status."""
        self.current_sprint = status
        
        # Broadcast to IDE clients if running
        if self.clients:
            asyncio.create_task(self.broadcast_status(status))


class IDEClient:
    """Client for IDE agents to communicate with the AutoGen engine."""
    
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.websocket = None
        self.connected = False

    async def connect(self):
        """Connect to the AutoGen engine."""
        try:
            self.websocket = await websockets.connect(f"ws://{self.host}:{self.port}")
            self.connected = True
            return True
        except Exception as e:
            print(f"Failed to connect to AutoGen engine: {e}")
            return False

    async def disconnect(self):
        """Disconnect from the AutoGen engine."""
        if self.websocket:
            await self.websocket.close()
            self.connected = False

    async def send_command(self, command: str, params: Dict[str, Any]) -> Optional[IDEResponse]:
        """Send command to AutoGen engine."""
        if not self.connected:
            return None
        
        try:
            message = {
                "command": command,
                "params": params,
                "timestamp": time.time(),
                "request_id": f"req_{int(time.time() * 1000)}"
            }
            
            await self.websocket.send(json.dumps(message))
            response = await self.websocket.recv()
            
            data = json.loads(response)
            return IDEResponse(**data)
        except Exception as e:
            print(f"Failed to send command: {e}")
            return None

    async def start_project(self, project_type: str, work_dir: str, project_goal: str) -> bool:
        """Start a new project."""
        response = await self.send_command("start_project", {
            "project_type": project_type,
            "work_dir": work_dir,
            "project_goal": project_goal
        })
        return response.success if response else False

    async def run_sprint(self, sprint_number: int = 1) -> bool:
        """Run a sprint."""
        response = await self.send_command("run_sprint", {
            "sprint_number": sprint_number
        })
        return response.success if response else False

    async def get_status(self) -> Optional[Dict[str, Any]]:
        """Get engine status."""
        response = await self.send_command("get_status", {})
        return response.data if response and response.success else None

    async def get_sprint_results(self, sprint_number: Optional[int] = None) -> Optional[List[Dict[str, Any]]]:
        """Get sprint results."""
        params = {}
        if sprint_number is not None:
            params["sprint_number"] = sprint_number
        
        response = await self.send_command("get_sprint_results", params)
        return response.data.get("results") if response and response.success else None
