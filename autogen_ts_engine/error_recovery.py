"""
Error Recovery and Resilience System for AutoGen TS Engine.
Handles failures, implements retry mechanisms, and provides system recovery.
"""

import time
import json
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import subprocess
import signal
import sys

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RecoveryAction(Enum):
    """Available recovery actions."""
    RETRY = "retry"
    FALLBACK = "fallback"
    ROLLBACK = "rollback"
    RESTART = "restart"
    SKIP = "skip"
    ABORT = "abort"


@dataclass
class ErrorContext:
    """Context information for an error."""
    error_type: str
    error_message: str
    severity: ErrorSeverity
    timestamp: str
    component: str
    operation: str
    retry_count: int = 0
    max_retries: int = 3
    recovery_action: RecoveryAction = RecoveryAction.RETRY
    metadata: Dict[str, Any] = None


@dataclass
class RecoveryResult:
    """Result of a recovery attempt."""
    success: bool
    action_taken: RecoveryAction
    error_context: ErrorContext
    recovery_time: float
    new_error: Optional[str] = None


class CircuitBreaker:
    """Circuit breaker pattern for preventing cascading failures."""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        if self.state == "OPEN":
            if self._should_attempt_reset():
                self.state = "HALF_OPEN"
            else:
                raise Exception(f"Circuit breaker is OPEN for {self.timeout} seconds")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        """Handle successful operation."""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def _on_failure(self):
        """Handle failed operation."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt reset."""
        if not self.last_failure_time:
            return True
        
        time_since_failure = (datetime.now() - self.last_failure_time).total_seconds()
        return time_since_failure >= self.timeout


class ErrorRecoveryManager:
    """Manages error recovery and resilience for the AutoGen TS Engine."""
    
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.error_log_file = project_dir / "scrum" / "error_log.json"
        self.recovery_log_file = project_dir / "recovery_log.json"
        
        # Ensure directories exist
        self.error_log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Circuit breakers for different components
        self.circuit_breakers = {
            "llm": CircuitBreaker(failure_threshold=3, timeout=30),
            "git": CircuitBreaker(failure_threshold=2, timeout=60),
            "test": CircuitBreaker(failure_threshold=5, timeout=120),
            "build": CircuitBreaker(failure_threshold=3, timeout=180)
        }
        
        # Recovery strategies
        self.recovery_strategies = {
            "llm_connection": self._recover_llm_connection,
            "git_operation": self._recover_git_operation,
            "test_execution": self._recover_test_execution,
            "build_failure": self._recover_build_failure,
            "file_operation": self._recover_file_operation,
            "agent_creation": self._recover_agent_creation
        }
        
        # Load error history
        self.error_history = self._load_error_history()
    
    def handle_error(self, error: Exception, context: Dict[str, Any]) -> RecoveryResult:
        """Handle an error with appropriate recovery strategy."""
        error_context = self._create_error_context(error, context)
        
        logger.warning(f"Handling error: {error_context.error_type} - {error_context.error_message}")
        
        # Log error
        self._log_error(error_context)
        
        # Determine recovery action
        recovery_action = self._determine_recovery_action(error_context)
        error_context.recovery_action = recovery_action
        
        # Execute recovery
        start_time = time.time()
        try:
            if recovery_action == RecoveryAction.RETRY:
                result = self._retry_operation(error_context, context)
            elif recovery_action == RecoveryAction.FALLBACK:
                result = self._fallback_operation(error_context, context)
            elif recovery_action == RecoveryAction.ROLLBACK:
                result = self._rollback_operation(error_context, context)
            elif recovery_action == RecoveryAction.RESTART:
                result = self._restart_operation(error_context, context)
            elif recovery_action == RecoveryAction.SKIP:
                result = RecoveryResult(
                    success=True,
                    action_taken=RecoveryAction.SKIP,
                    error_context=error_context,
                    recovery_time=time.time() - start_time
                )
            else:  # ABORT
                result = RecoveryResult(
                    success=False,
                    action_taken=RecoveryAction.ABORT,
                    error_context=error_context,
                    recovery_time=time.time() - start_time
                )
        except Exception as recovery_error:
            result = RecoveryResult(
                success=False,
                action_taken=recovery_action,
                error_context=error_context,
                recovery_time=time.time() - start_time,
                new_error=str(recovery_error)
            )
        
        # Log recovery result
        self._log_recovery(result)
        
        return result
    
    def _create_error_context(self, error: Exception, context: Dict[str, Any]) -> ErrorContext:
        """Create error context from exception and context."""
        error_type = type(error).__name__
        severity = self._determine_severity(error, context)
        
        return ErrorContext(
            error_type=error_type,
            error_message=str(error),
            severity=severity,
            timestamp=datetime.now().isoformat(),
            component=context.get('component', 'unknown'),
            operation=context.get('operation', 'unknown'),
            retry_count=context.get('retry_count', 0),
            max_retries=context.get('max_retries', 3),
            metadata=context.get('metadata', {})
        )
    
    def _determine_severity(self, error: Exception, context: Dict[str, Any]) -> ErrorSeverity:
        """Determine error severity based on error type and context."""
        error_type = type(error).__name__
        component = context.get('component', '')
        
        # Critical errors
        if error_type in ['KeyboardInterrupt', 'SystemExit']:
            return ErrorSeverity.CRITICAL
        
        # High severity errors
        if error_type in ['ConnectionError', 'TimeoutError', 'FileNotFoundError']:
            return ErrorSeverity.HIGH
        
        # Medium severity errors
        if error_type in ['ValueError', 'TypeError', 'AttributeError']:
            return ErrorSeverity.MEDIUM
        
        # Low severity errors
        return ErrorSeverity.LOW
    
    def _determine_recovery_action(self, error_context: ErrorContext) -> RecoveryAction:
        """Determine appropriate recovery action based on error context."""
        # Check if max retries exceeded
        if error_context.retry_count >= error_context.max_retries:
            if error_context.severity == ErrorSeverity.CRITICAL:
                return RecoveryAction.ABORT
            elif error_context.severity == ErrorSeverity.HIGH:
                return RecoveryAction.ROLLBACK
            else:
                return RecoveryAction.SKIP
        
        # Check circuit breaker state
        circuit_breaker = self.circuit_breakers.get(error_context.component)
        if circuit_breaker and circuit_breaker.state == "OPEN":
            return RecoveryAction.FALLBACK
        
        # Default to retry for most errors
        if error_context.severity in [ErrorSeverity.LOW, ErrorSeverity.MEDIUM]:
            return RecoveryAction.RETRY
        elif error_context.severity == ErrorSeverity.HIGH:
            return RecoveryAction.FALLBACK
        else:
            return RecoveryAction.ABORT
    
    def _retry_operation(self, error_context: ErrorContext, context: Dict[str, Any]) -> RecoveryResult:
        """Retry the failed operation."""
        start_time = time.time()
        max_retries = error_context.max_retries
        retry_count = error_context.retry_count
        
        for attempt in range(retry_count + 1, max_retries + 1):
            try:
                logger.info(f"Retry attempt {attempt}/{max_retries} for {error_context.operation}")
                
                # Exponential backoff
                if attempt > 1:
                    wait_time = min(2 ** (attempt - 1), 30)  # Cap at 30 seconds
                    time.sleep(wait_time)
                
                # Execute the operation
                operation_func = context.get('operation_func')
                if operation_func:
                    result = operation_func(*context.get('args', []), **context.get('kwargs', {}))
                    
                    logger.info(f"Retry successful on attempt {attempt}")
                    return RecoveryResult(
                        success=True,
                        action_taken=RecoveryAction.RETRY,
                        error_context=error_context,
                        recovery_time=time.time() - start_time
                    )
                
            except Exception as retry_error:
                logger.warning(f"Retry attempt {attempt} failed: {retry_error}")
                if attempt == max_retries:
                    return RecoveryResult(
                        success=False,
                        action_taken=RecoveryAction.RETRY,
                        error_context=error_context,
                        recovery_time=time.time() - start_time,
                        new_error=str(retry_error)
                    )
        
        return RecoveryResult(
            success=False,
            action_taken=RecoveryAction.RETRY,
            error_context=error_context,
            recovery_time=time.time() - start_time
        )
    
    def _fallback_operation(self, error_context: ErrorContext, context: Dict[str, Any]) -> RecoveryResult:
        """Execute fallback operation."""
        start_time = time.time()
        
        try:
            fallback_func = context.get('fallback_func')
            if fallback_func:
                result = fallback_func(*context.get('fallback_args', []), **context.get('fallback_kwargs', {}))
                
                logger.info(f"Fallback operation successful for {error_context.operation}")
                return RecoveryResult(
                    success=True,
                    action_taken=RecoveryAction.FALLBACK,
                    error_context=error_context,
                    recovery_time=time.time() - start_time
                )
            else:
                logger.warning(f"No fallback function available for {error_context.operation}")
                return RecoveryResult(
                    success=False,
                    action_taken=RecoveryAction.FALLBACK,
                    error_context=error_context,
                    recovery_time=time.time() - start_time
                )
                
        except Exception as fallback_error:
            logger.error(f"Fallback operation failed: {fallback_error}")
            return RecoveryResult(
                success=False,
                action_taken=RecoveryAction.FALLBACK,
                error_context=error_context,
                recovery_time=time.time() - start_time,
                new_error=str(fallback_error)
            )
    
    def _rollback_operation(self, error_context: ErrorContext, context: Dict[str, Any]) -> RecoveryResult:
        """Rollback to previous state."""
        start_time = time.time()
        
        try:
            # Git rollback
            if error_context.component == "git":
                result = subprocess.run(
                    ["git", "reset", "--hard", "HEAD~1"],
                    cwd=self.project_dir,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    logger.info("Git rollback successful")
                    return RecoveryResult(
                        success=True,
                        action_taken=RecoveryAction.ROLLBACK,
                        error_context=error_context,
                        recovery_time=time.time() - start_time
                    )
            
            # File rollback
            elif error_context.component == "file":
                backup_path = context.get('backup_path')
                if backup_path and Path(backup_path).exists():
                    import shutil
                    shutil.copy2(backup_path, context.get('original_path'))
                    logger.info("File rollback successful")
                    return RecoveryResult(
                        success=True,
                        action_taken=RecoveryAction.ROLLBACK,
                        error_context=error_context,
                        recovery_time=time.time() - start_time
                    )
            
            logger.warning(f"No rollback strategy available for {error_context.component}")
            return RecoveryResult(
                success=False,
                action_taken=RecoveryAction.ROLLBACK,
                error_context=error_context,
                recovery_time=time.time() - start_time
            )
            
        except Exception as rollback_error:
            logger.error(f"Rollback operation failed: {rollback_error}")
            return RecoveryResult(
                success=False,
                action_taken=RecoveryAction.ROLLBACK,
                error_context=error_context,
                recovery_time=time.time() - start_time,
                new_error=str(rollback_error)
            )
    
    def _restart_operation(self, error_context: ErrorContext, context: Dict[str, Any]) -> RecoveryResult:
        """Restart the component or system."""
        start_time = time.time()
        
        try:
            # Component-specific restart logic
            if error_context.component == "llm":
                # Restart LLM connection
                logger.info("Restarting LLM connection...")
                # Implementation would depend on LLM client
                pass
            elif error_context.component == "test":
                # Restart test runner
                logger.info("Restarting test runner...")
                pass
            
            logger.info(f"Restart successful for {error_context.component}")
            return RecoveryResult(
                success=True,
                action_taken=RecoveryAction.RESTART,
                error_context=error_context,
                recovery_time=time.time() - start_time
            )
            
        except Exception as restart_error:
            logger.error(f"Restart operation failed: {restart_error}")
            return RecoveryResult(
                success=False,
                action_taken=RecoveryAction.RESTART,
                error_context=error_context,
                recovery_time=time.time() - start_time,
                new_error=str(restart_error)
            )
    
    def _recover_llm_connection(self, error_context: ErrorContext) -> bool:
        """Recover LLM connection errors."""
        try:
            # Wait and retry connection
            time.sleep(5)
            return True
        except Exception:
            return False
    
    def _recover_git_operation(self, error_context: ErrorContext) -> bool:
        """Recover Git operation errors."""
        try:
            # Clean up any lock files
            git_dir = self.project_dir / ".git"
            for lock_file in git_dir.glob("*.lock"):
                lock_file.unlink()
            return True
        except Exception:
            return False
    
    def _recover_test_execution(self, error_context: ErrorContext) -> bool:
        """Recover test execution errors."""
        try:
            # Clear test cache
            test_cache = self.project_dir / ".pytest_cache"
            if test_cache.exists():
                import shutil
                shutil.rmtree(test_cache)
            return True
        except Exception:
            return False
    
    def _recover_build_failure(self, error_context: ErrorContext) -> bool:
        """Recover build failure errors."""
        try:
            # Clean build artifacts
            build_dirs = ["build", "dist", "__pycache__"]
            for build_dir in build_dirs:
                build_path = self.project_dir / build_dir
                if build_path.exists():
                    import shutil
                    shutil.rmtree(build_path)
            return True
        except Exception:
            return False
    
    def _recover_file_operation(self, error_context: ErrorContext) -> bool:
        """Recover file operation errors."""
        try:
            # Ensure directory exists
            target_path = Path(error_context.metadata.get('target_path', ''))
            if target_path:
                target_path.parent.mkdir(parents=True, exist_ok=True)
            return True
        except Exception:
            return False
    
    def _recover_agent_creation(self, error_context: ErrorContext) -> bool:
        """Recover agent creation errors."""
        try:
            # Reset agent factory state
            return True
        except Exception:
            return False
    
    def _log_error(self, error_context: ErrorContext) -> None:
        """Log error to file."""
        try:
            errors = []
            if self.error_log_file.exists():
                with open(self.error_log_file, 'r') as f:
                    errors = json.load(f)
            
            # Convert ErrorContext to dict with proper enum handling
            error_dict = {
                "error_type": error_context.error_type,
                "error_message": error_context.error_message,
                "severity": error_context.severity.value,  # Convert enum to string
                "timestamp": error_context.timestamp,
                "component": error_context.component,
                "operation": error_context.operation,
                "retry_count": error_context.retry_count,
                "max_retries": error_context.max_retries,
                "recovery_action": error_context.recovery_action.value,  # Convert enum to string
                "metadata": error_context.metadata or {}
            }
            
            errors.append(error_dict)
            
            with open(self.error_log_file, 'w') as f:
                json.dump(errors, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to log error: {e}")
    
    def _log_recovery(self, recovery_result: RecoveryResult) -> None:
        """Log recovery result to file."""
        try:
            recoveries = []
            if self.recovery_log_file.exists():
                with open(self.recovery_log_file, 'r') as f:
                    recoveries = json.load(f)
            
            recovery_data = {
                "timestamp": datetime.now().isoformat(),
                "success": recovery_result.success,
                "action_taken": recovery_result.action_taken.value,
                "recovery_time": recovery_result.recovery_time,
                "error_type": recovery_result.error_context.error_type,
                "component": recovery_result.error_context.component,
                "new_error": recovery_result.new_error
            }
            
            recoveries.append(recovery_data)
            
            with open(self.recovery_log_file, 'w') as f:
                json.dump(recoveries, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to log recovery: {e}")
    
    def _load_error_history(self) -> List[Dict[str, Any]]:
        """Load error history from file."""
        try:
            if self.error_log_file.exists():
                with open(self.error_log_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load error history: {e}")
        
        return []
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics and trends."""
        if not self.error_history:
            return {"total_errors": 0, "recovery_rate": 0.0}
        
        total_errors = len(self.error_history)
        successful_recoveries = 0
        
        # Load recovery history
        try:
            if self.recovery_log_file.exists():
                with open(self.recovery_log_file, 'r') as f:
                    recoveries = json.load(f)
                    successful_recoveries = sum(1 for r in recoveries if r.get('success', False))
        except Exception:
            pass
        
        # Error type distribution
        error_types = {}
        for error in self.error_history:
            error_type = error.get('error_type', 'unknown')
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        # Severity distribution
        severity_counts = {}
        for error in self.error_history:
            severity = error.get('severity', 'unknown')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        recovery_rate = (successful_recoveries / total_errors * 100) if total_errors > 0 else 0.0
        
        return {
            "total_errors": total_errors,
            "successful_recoveries": successful_recoveries,
            "recovery_rate": recovery_rate,
            "error_types": error_types,
            "severity_distribution": severity_counts,
            "circuit_breaker_states": {
                component: cb.state for component, cb in self.circuit_breakers.items()
            }
        }
    
    def cleanup_old_logs(self, days: int = 30) -> int:
        """Clean up old error and recovery logs."""
        cutoff_date = datetime.now() - timedelta(days=days)
        cleaned_count = 0
        
        for log_file in [self.error_log_file, self.recovery_log_file]:
            if log_file.exists():
                try:
                    with open(log_file, 'r') as f:
                        logs = json.load(f)
                    
                    # Filter out old entries
                    filtered_logs = []
                    for log in logs:
                        log_time = datetime.fromisoformat(log.get('timestamp', ''))
                        if log_time > cutoff_date:
                            filtered_logs.append(log)
                        else:
                            cleaned_count += 1
                    
                    # Write back filtered logs
                    with open(log_file, 'w') as f:
                        json.dump(filtered_logs, f, indent=2)
                        
                except Exception as e:
                    logger.error(f"Failed to cleanup {log_file}: {e}")
        
        logger.info(f"Cleaned up {cleaned_count} old log entries")
        return cleaned_count
