"""Git operations for the AutoGen TS Engine."""

import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class GitOps:
    """Git operations for version control."""
    
    def __init__(self, work_dir: Path, branch_prefix: str = "sprint-"):
        self.work_dir = work_dir
        self.branch_prefix = branch_prefix
        self.github_token = os.environ.get("GH_TOKEN")
    
    def initialize_repo(self) -> bool:
        """Initialize Git repository if it doesn't exist."""
        try:
            if not (self.work_dir / ".git").exists():
                # Initialize git repository
                result = subprocess.run(
                    ["git", "init"],
                    cwd=self.work_dir,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    print(f"Failed to initialize git repo: {result.stderr}")
                    return False
                
                # Create initial commit
                self._create_initial_commit()
                
            return True
            
        except Exception as e:
            print(f"Error initializing git repo: {e}")
            return False
    
    def _create_initial_commit(self) -> None:
        """Create initial commit with project structure."""
        try:
            # Add all files
            subprocess.run(
                ["git", "add", "."],
                cwd=self.work_dir,
                capture_output=True,
                text=True
            )
            
            # Create initial commit
            subprocess.run(
                ["git", "commit", "-m", "Initial project setup"],
                cwd=self.work_dir,
                capture_output=True,
                text=True
            )
            
        except Exception as e:
            print(f"Error creating initial commit: {e}")
    
    def _commit_changes(self, message: str) -> bool:
        """Commit any uncommitted changes."""
        try:
            # Check if there are any changes to commit
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.work_dir,
                capture_output=True,
                text=True
            )
            
            if result.stdout.strip():
                # Add all changes
                subprocess.run(
                    ["git", "add", "."],
                    cwd=self.work_dir,
                    capture_output=True,
                    text=True
                )
                
                # Commit changes
                commit_result = subprocess.run(
                    ["git", "commit", "-m", message],
                    cwd=self.work_dir,
                    capture_output=True,
                    text=True
                )
                
                return commit_result.returncode == 0
            
            return True  # No changes to commit
            
        except Exception as e:
            print(f"Error committing changes: {e}")
            return False
    
    def create_sprint_branch(self, sprint_number: int) -> bool:
        """Create a new branch for the sprint."""
        try:
            branch_name = f"{self.branch_prefix}{sprint_number}"
            
            # First, commit any uncommitted changes
            self._commit_changes(f"Auto-commit before sprint {sprint_number}")
            
            # Check if branch already exists
            result = subprocess.run(
                ["git", "branch", "--list", branch_name],
                cwd=self.work_dir,
                capture_output=True,
                text=True
            )
            
            if result.stdout.strip():
                # Branch exists, switch to it
                result = subprocess.run(
                    ["git", "checkout", branch_name],
                    cwd=self.work_dir,
                    capture_output=True,
                    text=True
                )
            else:
                # Create new branch
                result = subprocess.run(
                    ["git", "checkout", "-b", branch_name],
                    cwd=self.work_dir,
                    capture_output=True,
                    text=True
                )
            
            if result.returncode != 0:
                print(f"Failed to create/switch to branch: {result.stderr}")
                return False
            
            return True
            
        except Exception as e:
            print(f"Error creating sprint branch: {e}")
            return False
    
    def get_current_branch(self) -> Optional[str]:
        """Get the current branch name."""
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.work_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            return None
            
        except Exception as e:
            print(f"Error getting current branch: {e}")
            return None
    
    def get_status(self) -> Dict:
        """Get Git status information."""
        try:
            # Get current branch
            current_branch = self.get_current_branch()
            
            # Get status
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.work_dir,
                capture_output=True,
                text=True
            )
            
            status_lines = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            # Get last commit
            commit_result = subprocess.run(
                ["git", "log", "-1", "--oneline"],
                cwd=self.work_dir,
                capture_output=True,
                text=True
            )
            
            last_commit = commit_result.stdout.strip() if commit_result.returncode == 0 else None
            
            return {
                "current_branch": current_branch,
                "modified_files": len(status_lines),
                "status_lines": status_lines,
                "last_commit": last_commit
            }
            
        except Exception as e:
            print(f"Error getting git status: {e}")
            return {}
    
    def stage_files(self, file_patterns: Optional[List[str]] = None) -> bool:
        """Stage files for commit."""
        try:
            if file_patterns:
                # Stage specific files
                for pattern in file_patterns:
                    result = subprocess.run(
                        ["git", "add", pattern],
                        cwd=self.work_dir,
                        capture_output=True,
                        text=True
                    )
                    
                    if result.returncode != 0:
                        print(f"Failed to stage {pattern}: {result.stderr}")
                        return False
            else:
                # Stage all changes
                result = subprocess.run(
                    ["git", "add", "."],
                    cwd=self.work_dir,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    print(f"Failed to stage files: {result.stderr}")
                    return False
            
            return True
            
        except Exception as e:
            print(f"Error staging files: {e}")
            return False
    
    def commit_changes(self, message: str) -> bool:
        """Commit staged changes."""
        try:
            result = subprocess.run(
                ["git", "commit", "-m", message],
                cwd=self.work_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print(f"Failed to commit changes: {result.stderr}")
                return False
            
            return True
            
        except Exception as e:
            print(f"Error committing changes: {e}")
            return False
    
    def create_sprint_commit(self, sprint_number: int, sprint_summary: str) -> bool:
        """Create a commit for sprint completion."""
        try:
            # Stage all changes
            if not self.stage_files():
                return False
            
            # Create commit message
            commit_message = f"Sprint {sprint_number} completion\n\n{sprint_summary}"
            
            return self.commit_changes(commit_message)
            
        except Exception as e:
            print(f"Error creating sprint commit: {e}")
            return False
    
    def push_branch(self, branch_name: Optional[str] = None) -> bool:
        """Push branch to remote repository."""
        try:
            if not branch_name:
                branch_name = self.get_current_branch()
            
            if not branch_name:
                print("No branch name provided or current branch could not be determined")
                return False
            
            result = subprocess.run(
                ["git", "push", "origin", branch_name],
                cwd=self.work_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print(f"Failed to push branch: {result.stderr}")
                return False
            
            return True
            
        except Exception as e:
            print(f"Error pushing branch: {e}")
            return False
    
    def create_pull_request(self, sprint_number: int, title: str, body: str) -> Optional[str]:
        """Create a pull request using GitHub CLI."""
        try:
            if not self.github_token:
                print("GitHub token not found. Skipping PR creation.")
                return None
            
            # Set GitHub token
            env = os.environ.copy()
            env["GH_TOKEN"] = self.github_token
            
            # Create PR using GitHub CLI
            result = subprocess.run(
                [
                    "gh", "pr", "create",
                    "--title", title,
                    "--body", body,
                    "--base", "main"
                ],
                cwd=self.work_dir,
                env=env,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print(f"Failed to create PR: {result.stderr}")
                return None
            
            # Extract PR URL from output
            output_lines = result.stdout.strip().split('\n')
            for line in output_lines:
                if line.startswith("https://github.com/"):
                    return line.strip()
            
            return None
            
        except Exception as e:
            print(f"Error creating pull request: {e}")
            return None
    
    def merge_to_main(self) -> bool:
        """Merge current branch to main."""
        try:
            # Switch to main branch
            result = subprocess.run(
                ["git", "checkout", "main"],
                cwd=self.work_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print(f"Failed to switch to main: {result.stderr}")
                return False
            
            # Get the sprint branch name
            sprint_branch = self.get_current_branch()
            if not sprint_branch or not sprint_branch.startswith(self.branch_prefix):
                print("Not on a sprint branch")
                return False
            
            # Merge the sprint branch
            result = subprocess.run(
                ["git", "merge", sprint_branch],
                cwd=self.work_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print(f"Failed to merge branch: {result.stderr}")
                return False
            
            return True
            
        except Exception as e:
            print(f"Error merging to main: {e}")
            return False
    
    def get_commit_history(self, limit: int = 10) -> List[Dict]:
        """Get recent commit history."""
        try:
            result = subprocess.run(
                ["git", "log", f"-{limit}", "--oneline", "--format=%H|%an|%ad|%s"],
                cwd=self.work_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return []
            
            commits = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('|')
                    if len(parts) >= 4:
                        commits.append({
                            "hash": parts[0],
                            "author": parts[1],
                            "date": parts[2],
                            "message": parts[3]
                        })
            
            return commits
            
        except Exception as e:
            print(f"Error getting commit history: {e}")
            return []
    
    def get_diff(self, file_path: Optional[str] = None) -> str:
        """Get diff of changes."""
        try:
            if file_path:
                result = subprocess.run(
                    ["git", "diff", file_path],
                    cwd=self.work_dir,
                    capture_output=True,
                    text=True
                )
            else:
                result = subprocess.run(
                    ["git", "diff"],
                    cwd=self.work_dir,
                    capture_output=True,
                    text=True
                )
            
            if result.returncode == 0:
                return result.stdout
            else:
                return ""
                
        except Exception as e:
            print(f"Error getting diff: {e}")
            return ""
    
    def reset_to_main(self) -> bool:
        """Reset current branch to match main."""
        try:
            # Switch to main
            result = subprocess.run(
                ["git", "checkout", "main"],
                cwd=self.work_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return False
            
            # Pull latest changes
            result = subprocess.run(
                ["git", "pull", "origin", "main"],
                cwd=self.work_dir,
                capture_output=True,
                text=True
            )
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"Error resetting to main: {e}")
            return False
    
    def cleanup_branch(self, branch_name: str) -> bool:
        """Delete a branch after merging."""
        try:
            # Switch to main first
            if not self.reset_to_main():
                return False
            
            # Delete local branch
            result = subprocess.run(
                ["git", "branch", "-d", branch_name],
                cwd=self.work_dir,
                capture_output=True,
                text=True
            )
            
            # Delete remote branch if it exists
            subprocess.run(
                ["git", "push", "origin", "--delete", branch_name],
                cwd=self.work_dir,
                capture_output=True,
                text=True
            )
            
            return True
            
        except Exception as e:
            print(f"Error cleaning up branch: {e}")
            return False
