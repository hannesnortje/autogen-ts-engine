"""Main CLI entry point for the AutoGen TS Engine."""

import argparse
import sys
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel

from .config_parser import ConfigParser
from .fs_bootstrap import FSBootstrap
from .logging_utils import setup_logging
from .sprint_runner import SprintRunner
from .schemas import ProjectType
from .ide_interface import IDEInterface
import asyncio


def check_lm_studio_connection(api_base: str) -> bool:
    """Check if LM Studio is running and accessible."""
    try:
        import requests
        
        response = requests.get(f"{api_base}/models", timeout=5)
        return response.status_code == 200
        
    except Exception:
        return False


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="AutoGen-based multi-agent TypeScript development engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default settings
  autogen-ts-engine run

  # Run with custom config and work directories
  autogen-ts-engine run --config-dir ./my-config --work-dir ./my-project

  # Run with debug mode and custom sprint limits
  autogen-ts-engine run --debug --max-sprint 2 --max-iters-per-sprint 3

  # Create project-local virtual environment
  autogen-ts-engine run --create-venv

  # Start IDE interface server
  autogen-ts-engine ide-server --host localhost --port 8765
        """
    )
    
    parser.add_argument(
        "command",
        choices=["run", "ide-server"],
        help="Command to execute"
    )
    
    parser.add_argument(
        "--config-dir",
        type=Path,
        default=Path("./config"),
        help="Configuration directory (default: ./config)"
    )
    
    parser.add_argument(
        "--work-dir",
        type=Path,
        default=Path("./ts_project"),
        help="Working directory (default: ./ts_project)"
    )
    
    parser.add_argument(
        "--create-venv",
        action="store_true",
        help="Create project-local virtual environment"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    
    parser.add_argument(
        "--max-sprint",
        type=int,
        help="Maximum number of sprints (overrides config)"
    )
    
    parser.add_argument(
        "--max-iters-per-sprint",
        type=int,
        help="Maximum iterations per sprint (overrides config)"
    )
    
    parser.add_argument(
        "--project-type",
        choices=["typescript", "python", "react", "nodejs", "java", "go", "rust", "custom"],
        help="Project type for default configuration"
    )
    
    parser.add_argument(
        "--host",
        default="localhost",
        help="Host for IDE server (default: localhost)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8765,
        help="Port for IDE server (default: 8765)"
    )
    
    args = parser.parse_args()
    
    # Setup console and logging
    console = Console()
    logger = setup_logging(debug_mode=args.debug)
    
    # Display welcome message
    welcome_text = """
[bold blue]AutoGen TS Engine[/bold blue]
[dim]Multi-agent TypeScript development with offline capabilities[/dim]

[bold]Features:[/bold]
• 🤖 Multi-agent development (Planner, Coder, Tester, Critic, RAG)
• 🏠 Offline-first with LM Studio
• 📚 Context management with ChromaDB
• 🧠 Reinforcement learning optimization
• ⚡ TypeScript focus with Jest testing
• 📝 Markdown configuration
• 🔧 Git integration with automatic PRs
    """
    
    console.print(Panel(welcome_text, title="Welcome", border_style="blue"))
    
    try:
        if args.command == "run":
            return run_engine(args, logger, console)
        elif args.command == "ide-server":
            return run_ide_server(args, logger, console)
        else:
            console.print(f"[red]Unknown command: {args.command}[/red]")
            return 1
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        return 130
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        if args.debug:
            import traceback
            console.print(traceback.format_exc())
        return 1


def run_engine(args, logger, console) -> int:
    """Run the main engine workflow."""
    try:
        # Check prerequisites
        fs_bootstrap = FSBootstrap(logger)
        prerequisites = fs_bootstrap.check_prerequisites()
        
        missing_prereqs = [name for name, available in prerequisites.items() if not available]
        if missing_prereqs:
            console.print(f"[red]Missing prerequisites: {', '.join(missing_prereqs)}[/red]")
            console.print("[yellow]Please install the missing tools and try again.[/yellow]")
            return 1
        
        # Create directories if they don't exist
        args.config_dir.mkdir(parents=True, exist_ok=True)
        args.work_dir.mkdir(parents=True, exist_ok=True)
        
        # Parse configuration
        config_parser = ConfigParser()
        
        # Create default configs if they don't exist
        if not (args.config_dir / "settings.md").exists():
            logger.info("Creating default configuration files...")
            project_type = args.project_type if args.project_type else "typescript"
            config_parser.create_default_configs(args.config_dir, ProjectType(project_type))
        
        # Parse settings and agents
        settings = config_parser.parse_settings(args.config_dir)
        agent_definitions = config_parser.parse_agents(args.config_dir)
        
        # Override settings with command line arguments
        if args.max_sprint:
            settings.num_sprints = args.max_sprint
        if args.max_iters_per_sprint:
            settings.iterations_per_sprint = args.max_iters_per_sprint
        if args.debug:
            settings.debug_mode = True
        
        # Update work directory if specified
        if args.work_dir != Path("./ts_project"):
            settings.work_dir = str(args.work_dir)
        
        # Check LM Studio connection
        console.print("[dim]Checking LM Studio connection...[/dim]")
        if not check_lm_studio_connection(settings.llm_binding.api_base):
            console.print(Panel(
                "[red]❌ LM Studio is not accessible![/red]\n\n"
                "Please ensure:\n"
                "1. LM Studio is running\n"
                "2. A model is loaded\n"
                "3. Server is enabled on port 1234\n"
                "4. OpenAI-compatible API is enabled\n\n"
                "Test with: curl http://localhost:1234/v1/models",
                title="LM Studio Connection Failed",
                border_style="red"
            ))
            return 1
        
        console.print("[green]✅ LM Studio connection successful[/green]")
        
        # Bootstrap project if needed
        project_type = args.project_type if args.project_type else settings.project_type
        if not (args.work_dir / "package.json").exists():
            console.print("[dim]Bootstrapping project structure...[/dim]")
            if not fs_bootstrap.bootstrap_project(
                args.work_dir, 
                args.config_dir,
                settings.project_name,
                settings.project_goal,
                project_type
            ):
                console.print("[red]Failed to bootstrap project[/red]")
                return 1
        
        # Create virtual environment if requested
        if args.create_venv:
            console.print("[dim]Creating virtual environment...[/dim]")
            if not fs_bootstrap.create_venv(args.work_dir):
                console.print("[red]Failed to create virtual environment[/red]")
                return 1
        
        # Validate project structure
        validation = fs_bootstrap.validate_project_structure(args.work_dir)
        missing_items = [name for name, exists in validation.items() if not exists]
        if missing_items:
            console.print(f"[yellow]Warning: Missing project items: {', '.join(missing_items)}[/yellow]")
        
        # Display configuration summary
        console.print(Panel(
            f"[bold]Configuration Summary:[/bold]\n"
            f"• Project: {settings.project_name}\n"
            f"• Goal: {settings.project_goal}\n"
            f"• Sprints: {settings.num_sprints}\n"
            f"• Iterations per sprint: {settings.iterations_per_sprint}\n"
            f"• Work directory: {settings.work_dir}\n"
            f"• Agents: {len(agent_definitions)}\n"
            f"• Debug mode: {settings.debug_mode}",
            title="Engine Configuration",
            border_style="green"
        ))
        
        # Confirm before starting
        if settings.human_input_mode.value == "ALWAYS":
            response = console.input("[bold]Press Enter to start the engine, or 'q' to quit: [/bold]")
            if response.lower() == 'q':
                console.print("[yellow]Operation cancelled[/yellow]")
                return 0
        
        # Initialize and run sprints
        console.print("[bold blue]🚀 Starting AutoGen TS Engine...[/bold blue]")
        
        sprint_runner = SprintRunner(settings, logger)
        results = sprint_runner.run_sprints(agent_definitions)
        
        # Display results summary
        successful_sprints = sum(1 for result in results if result.success)
        total_sprints = len(results)
        
        console.print(Panel(
            f"[bold]Sprint Results Summary:[/bold]\n"
            f"• Total sprints: {total_sprints}\n"
            f"• Successful: {successful_sprints}\n"
            f"• Failed: {total_sprints - successful_sprints}\n"
            f"• Success rate: {successful_sprints/total_sprints*100:.1f}%",
            title="Engine Complete",
            border_style="green" if successful_sprints == total_sprints else "yellow"
        ))
        
        # Display detailed results
        for result in results:
            status = "✅" if result.success else "❌"
            console.print(f"{status} Sprint {result.sprint_number}: {result.iterations_completed} iterations")
            if result.errors:
                for error in result.errors:
                    console.print(f"  [red]Error: {error}[/red]")
        
        # Final status
        if successful_sprints == total_sprints:
            console.print("[green]🎉 All sprints completed successfully![/green]")
            return 0
        else:
            console.print(f"[yellow]⚠️  {total_sprints - successful_sprints} sprints failed[/yellow]")
            return 1 if successful_sprints == 0 else 0
            
    except Exception as e:
        logger.error_with_context(e, "Engine execution")
        console.print(f"[red]Engine execution failed: {e}[/red]")
        if args.debug:
            import traceback
            console.print(traceback.format_exc())
        return 1


def run_ide_server(args, logger, console) -> int:
    """Run the IDE interface server."""
    try:
        # Parse configuration
        config_parser = ConfigParser()
        
        # Create default configs if they don't exist
        if not (args.config_dir / "settings.md").exists():
            logger.info("Creating default configuration files...")
            project_type = args.project_type if args.project_type else "typescript"
            config_parser.create_default_configs(args.config_dir, ProjectType(project_type))
        
        # Parse settings
        settings = config_parser.parse_settings(args.config_dir)
        
        # Override settings with command line arguments
        if args.max_sprint:
            settings.num_sprints = args.max_sprint
        if args.max_iters_per_sprint:
            settings.iterations_per_sprint = args.max_iters_per_sprint
        if args.debug:
            settings.debug_mode = True
        
        # Update work directory if specified
        if args.work_dir != Path("./ts_project"):
            settings.work_dir = str(args.work_dir)
        
        # Display IDE server info
        console.print(Panel(
            f"[bold]IDE Interface Server[/bold]\n"
            f"• Host: {args.host}\n"
            f"• Port: {args.port}\n"
            f"• WebSocket URL: ws://{args.host}:{args.port}\n"
            f"• Project: {settings.project_name}\n"
            f"• Project Type: {settings.project_type.value}\n\n"
            f"[dim]Connect your IDE agent to control the AutoGen engine[/dim]",
            title="IDE Server Starting",
            border_style="blue"
        ))
        
        # Create IDE interface
        ide_interface = IDEInterface(settings, logger)
        
        # Start WebSocket server
        console.print(f"[green]✅ IDE Interface server started on ws://{args.host}:{args.port}[/green]")
        console.print("[dim]Waiting for IDE connections...[/dim]")
        
        # Run the async server
        asyncio.run(ide_interface.start_websocket_server(args.host, args.port))
        
        return 0
        
    except KeyboardInterrupt:
        console.print("\n[yellow]IDE server stopped by user[/yellow]")
        return 0
    except Exception as e:
        logger.error_with_context(e, "IDE server execution")
        console.print(f"[red]IDE server failed: {e}[/red]")
        if args.debug:
            import traceback
            console.print(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main())
