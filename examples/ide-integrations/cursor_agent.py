#!/usr/bin/env python3
"""
Cursor IDE Agent Integration for AutoGen Engine

This script provides a Cursor IDE agent that can control and monitor
the AutoGen Multi-Agent Development Engine through WebSocket communication.

Usage:
    python cursor_agent.py --host localhost --port 8765
"""

import asyncio
import argparse
import json
import time
from typing import Dict, Any, Optional
from pathlib import Path

from autogen_ts_engine.ide_interface import IDEClient, IDEResponse


class CursorAgent:
    """Cursor IDE agent for controlling AutoGen engine."""
    
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.client = IDEClient(host, port)
        self.connected = False
        self.project_status = {}
        
    async def connect(self) -> bool:
        """Connect to AutoGen engine."""
        print(f"🔌 Connecting to AutoGen engine at ws://{self.client.host}:{self.client.port}...")
        self.connected = await self.client.connect()
        
        if self.connected:
            print("✅ Connected to AutoGen engine!")
            await self.update_status()
        else:
            print("❌ Failed to connect to AutoGen engine")
            
        return self.connected
    
    async def disconnect(self):
        """Disconnect from AutoGen engine."""
        if self.connected:
            await self.client.disconnect()
            self.connected = False
            print("🔌 Disconnected from AutoGen engine")
    
    async def update_status(self):
        """Update project status."""
        if not self.connected:
            return
            
        status = await self.client.get_status()
        if status:
            self.project_status = status
            self.display_status()
    
    def display_status(self):
        """Display current project status."""
        if not self.project_status:
            return
            
        print("\n📊 Project Status:")
        print(f"  • Project: {self.project_status.get('project_goal', 'Unknown')}")
        print(f"  • Type: {self.project_status.get('project_type', 'Unknown')}")
        print(f"  • Work Directory: {self.project_status.get('work_dir', 'Unknown')}")
        print(f"  • Engine Running: {'✅' if self.project_status.get('is_running') else '❌'}")
        print(f"  • Completed Sprints: {self.project_status.get('completed_sprints', 0)}/{self.project_status.get('total_sprints', 0)}")
        
        current_sprint = self.project_status.get('current_sprint')
        if current_sprint:
            print(f"  • Current Sprint: {current_sprint.get('sprint_number')} - {current_sprint.get('status')}")
            print(f"  • Progress: {current_sprint.get('progress', 0) * 100:.1f}%")
            print(f"  • Current Agent: {current_sprint.get('current_agent', 'Unknown')}")
            print(f"  • Current Task: {current_sprint.get('current_task', 'Unknown')}")
    
    async def start_project(self, project_type: str, work_dir: str, project_goal: str) -> bool:
        """Start a new project."""
        if not self.connected:
            print("❌ Not connected to AutoGen engine")
            return False
            
        print(f"🚀 Starting {project_type} project: {project_goal}")
        success = await self.client.start_project(project_type, work_dir, project_goal)
        
        if success:
            print("✅ Project started successfully!")
            await self.update_status()
        else:
            print("❌ Failed to start project")
            
        return success
    
    async def run_sprint(self, sprint_number: int = 1) -> bool:
        """Run a sprint."""
        if not self.connected:
            print("❌ Not connected to AutoGen engine")
            return False
            
        print(f"🏃 Running sprint {sprint_number}...")
        success = await self.client.run_sprint(sprint_number)
        
        if success:
            print("✅ Sprint started!")
            # Monitor sprint progress
            await self.monitor_sprint(sprint_number)
        else:
            print("❌ Failed to start sprint")
            
        return success
    
    async def monitor_sprint(self, sprint_number: int):
        """Monitor sprint progress."""
        print(f"👀 Monitoring sprint {sprint_number}...")
        
        # Poll for status updates
        for i in range(60):  # Monitor for up to 5 minutes
            await asyncio.sleep(5)  # Check every 5 seconds
            await self.update_status()
            
            current_sprint = self.project_status.get('current_sprint')
            if current_sprint and current_sprint.get('status') == 'completed':
                print("✅ Sprint completed!")
                await self.show_sprint_results(sprint_number)
                break
        else:
            print("⏰ Sprint monitoring timeout")
    
    async def show_sprint_results(self, sprint_number: int):
        """Show sprint results."""
        results = await self.client.get_sprint_results(sprint_number)
        if results:
            result = results[0] if results else {}
            print(f"\n📋 Sprint {sprint_number} Results:")
            print(f"  • Status: {'✅ Success' if result.get('success') else '❌ Failed'}")
            print(f"  • Iterations: {result.get('iterations_completed', 0)}")
            print(f"  • Goals Achieved: {len(result.get('goals_achieved', []))}")
            print(f"  • Goals Failed: {len(result.get('goals_failed', []))}")
            
            if result.get('errors'):
                print("  • Errors:")
                for error in result.get('errors', []):
                    print(f"    - {error}")
    
    async def interactive_mode(self):
        """Run interactive mode for manual control."""
        print("\n🎮 Interactive Mode - Type 'help' for commands")
        
        while self.connected:
            try:
                command = input("\n> ").strip().lower()
                
                if command == 'quit' or command == 'exit':
                    break
                elif command == 'help':
                    self.show_help()
                elif command == 'status':
                    await self.update_status()
                elif command.startswith('start '):
                    # start <type> <dir> <goal>
                    parts = command.split(' ', 3)
                    if len(parts) >= 4:
                        project_type = parts[1]
                        work_dir = parts[2]
                        project_goal = parts[3]
                        await self.start_project(project_type, work_dir, project_goal)
                    else:
                        print("Usage: start <type> <dir> <goal>")
                elif command.startswith('sprint '):
                    # sprint <number>
                    parts = command.split()
                    if len(parts) >= 2:
                        sprint_number = int(parts[1])
                        await self.run_sprint(sprint_number)
                    else:
                        print("Usage: sprint <number>")
                elif command == 'results':
                    results = await self.client.get_sprint_results()
                    if results:
                        print(f"📊 Total sprints: {len(results)}")
                        for result in results:
                            status = "✅" if result.get('success') else "❌"
                            print(f"  {status} Sprint {result.get('sprint_number')}: {result.get('iterations_completed')} iterations")
                    else:
                        print("No sprint results available")
                else:
                    print("Unknown command. Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def show_help(self):
        """Show available commands."""
        print("\n📖 Available Commands:")
        print("  status                    - Show current project status")
        print("  start <type> <dir> <goal> - Start a new project")
        print("  sprint <number>           - Run a sprint")
        print("  results                   - Show sprint results")
        print("  help                      - Show this help")
        print("  quit/exit                 - Exit interactive mode")
        print("\n📝 Examples:")
        print("  start typescript ./my-api 'Build a REST API with Express.js'")
        print("  start python ./ml-pipeline 'Build a machine learning pipeline'")
        print("  sprint 1")


async def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Cursor IDE Agent for AutoGen Engine")
    parser.add_argument("--host", default="localhost", help="AutoGen engine host")
    parser.add_argument("--port", type=int, default=8765, help="AutoGen engine port")
    parser.add_argument("--project-type", help="Project type to start")
    parser.add_argument("--work-dir", help="Work directory")
    parser.add_argument("--project-goal", help="Project goal")
    parser.add_argument("--sprint", type=int, help="Sprint number to run")
    
    args = parser.parse_args()
    
    # Create Cursor agent
    agent = CursorAgent(args.host, args.port)
    
    try:
        # Connect to AutoGen engine
        if not await agent.connect():
            return 1
        
        # If command line arguments provided, execute commands
        if args.project_type and args.work_dir and args.project_goal:
            await agent.start_project(args.project_type, args.work_dir, args.project_goal)
            
            if args.sprint:
                await agent.run_sprint(args.sprint)
        else:
            # Run interactive mode
            await agent.interactive_mode()
    
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    finally:
        await agent.disconnect()
    
    return 0


if __name__ == "__main__":
    exit(asyncio.run(main()))
