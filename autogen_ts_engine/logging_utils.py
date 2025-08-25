"""Logging utilities for the AutoGen TS Engine."""

import logging
import sys
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table


class EngineLogger:
    """Centralized logging for the AutoGen TS Engine."""
    
    def __init__(self, debug_mode: bool = False, log_file: Optional[Path] = None):
        self.debug_mode = debug_mode
        self.console = Console()
        
        # Configure logging level
        level = logging.DEBUG if debug_mode else logging.INFO
        
        # Create logger
        self.logger = logging.getLogger("autogen_ts_engine")
        self.logger.setLevel(level)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Console handler with rich formatting
        console_handler = RichHandler(
            console=self.console,
            show_time=True,
            show_path=debug_mode,
            markup=True
        )
        console_handler.setLevel(level)
        self.logger.addHandler(console_handler)
        
        # File handler if specified
        if log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def info(self, message: str) -> None:
        """Log info message."""
        self.logger.info(message)
    
    def debug(self, message: str) -> None:
        """Log debug message."""
        self.logger.debug(message)
    
    def warning(self, message: str) -> None:
        """Log warning message."""
        self.logger.warning(message)
    
    def error(self, message: str) -> None:
        """Log error message."""
        self.logger.error(message)
    
    def critical(self, message: str) -> None:
        """Log critical message."""
        self.logger.critical(message)
    
    def sprint_start(self, sprint_number: int, goal: str) -> None:
        """Log sprint start with rich formatting."""
        self.console.print(f"\n[bold blue]🚀 Starting Sprint {sprint_number}[/bold blue]")
        self.console.print(f"[dim]Goal: {goal}[/dim]\n")
    
    def sprint_end(self, sprint_number: int, success: bool, iterations: int) -> None:
        """Log sprint end with results."""
        status = "[bold green]✅ SUCCESS[/bold green]" if success else "[bold red]❌ FAILED[/bold red]"
        self.console.print(f"\n[bold]Sprint {sprint_number} Complete[/bold] {status}")
        self.console.print(f"[dim]Iterations: {iterations}[/dim]\n")
    
    def agent_message(self, agent_name: str, message: str) -> None:
        """Log agent message with formatting."""
        self.console.print(f"[bold cyan]{agent_name}[/bold cyan]: {message}")
    
    def test_results(self, passed: int, failed: int, coverage: Optional[float] = None) -> None:
        """Log test results."""
        table = Table(title="Test Results")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")
        
        table.add_row("Passed", str(passed))
        table.add_row("Failed", str(failed))
        if coverage is not None:
            table.add_row("Coverage", f"{coverage:.1f}%")
        
        self.console.print(table)
    
    def rl_update(self, reward: float, action: str, state: str) -> None:
        """Log reinforcement learning update."""
        self.console.print(f"[dim]🤖 RL Update: Action={action}, State={state}, Reward={reward:.3f}[/dim]")
    
    def git_operation(self, operation: str, details: str) -> None:
        """Log git operation."""
        self.console.print(f"[dim]🔧 Git: {operation} - {details}[/dim]")
    
    def error_with_context(self, error: Exception, context: str) -> None:
        """Log error with context."""
        self.console.print(f"[bold red]Error in {context}:[/bold red]")
        self.console.print(f"[red]{str(error)}[/red]")
        if self.debug_mode:
            import traceback
            self.console.print(f"[dim]{traceback.format_exc()}[/dim]")


class ProgressTracker:
    """Progress tracking with rich UI."""
    
    def __init__(self, console: Console):
        self.console = console
        self.progress = None
    
    def __enter__(self):
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        )
        self.progress.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.progress:
            self.progress.stop()
    
    def update(self, description: str) -> None:
        """Update progress description."""
        if self.progress and self.progress.tasks:
            self.progress.update(self.progress.tasks[0].id, description=description)


def setup_logging(debug_mode: bool = False, log_file: Optional[Path] = None) -> EngineLogger:
    """Setup and return the engine logger."""
    return EngineLogger(debug_mode=debug_mode, log_file=log_file)


def log_function_call(logger: EngineLogger, func_name: str):
    """Decorator to log function calls."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger.debug(f"Calling {func_name}")
            try:
                result = func(*args, **kwargs)
                logger.debug(f"Completed {func_name}")
                return result
            except Exception as e:
                logger.error(f"Error in {func_name}: {e}")
                raise
        return wrapper
    return decorator
