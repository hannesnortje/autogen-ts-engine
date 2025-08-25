"""File system bootstrap for creating default project structure."""

from pathlib import Path
from typing import Optional, Dict

from .config_parser import ConfigParser
from .logging_utils import EngineLogger
from .schemas import ProjectType


class FSBootstrap:
    """Bootstrap file system structure and configurations."""
    
    def __init__(self, logger: EngineLogger):
        self.logger = logger
        self.config_parser = ConfigParser()

    def bootstrap_project(self, work_dir: Path, config_dir: Path,
                         project_name: str, project_goal: str, 
                         project_type: ProjectType = ProjectType.TYPESCRIPT) -> bool:
        """Bootstrap the complete project structure."""
        try:
            self.logger.info("Bootstrapping project structure...")
            
            # Create directories
            self._create_directories(work_dir)
            
            # Create default configurations
            self._create_default_configs(config_dir, project_name, project_goal, project_type)
            
            # Create project structure
            self._create_project_structure(work_dir)
            
            self.logger.info("Project bootstrap completed successfully")
            return True
            
        except Exception as e:
            self.logger.error_with_context(e, "Project bootstrap")
            return False
    
    def _create_directories(self, work_dir: Path) -> None:
        """Create the basic directory structure."""
        directories = [
            work_dir / "config",
            work_dir / "scrum",
            work_dir / "src",
            work_dir / "tests",
            work_dir / "project_db",
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"Created directory: {directory}")
    
    def _create_default_configs(self, config_dir: Path, project_name: str, project_goal: str, project_type: ProjectType) -> None:
        """Create default configuration files."""
        # Use the config parser to create default configs based on project type
        self.config_parser.create_default_configs(config_dir, project_type)
        
        # Update the project name and goal in the settings file
        settings_file = config_dir / "settings.md"
        if settings_file.exists():
            content = settings_file.read_text()
            content = content.replace('project_name: "project"', f'project_name: "{project_name}"')
            content = content.replace('project_goal: "Build a', f'project_goal: "{project_goal}"')
            settings_file.write_text(content)
            self.logger.debug(f"Updated settings file: {settings_file}")
    
    def _create_project_structure(self, work_dir: Path) -> None:
        """Create the basic project file structure."""
        # Create .gitignore
        gitignore_content = """# Dependencies
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Build outputs
dist/
build/
*.tsbuildinfo

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# IDE files
.vscode/
.idea/
*.swp
*.swo

# OS files
.DS_Store
Thumbs.db

# Logs
logs/
*.log

# Runtime data
pids/
*.pid
*.seed
*.pid.lock

# Coverage directory used by tools like istanbul
coverage/
*.lcov

# nyc test coverage
.nyc_output

# Dependency directories
jspm_packages/

# Optional npm cache directory
.npm

# Optional eslint cache
.eslintcache

# Microbundle cache
.rpt2_cache/
.rts2_cache_cjs/
.rts2_cache_es/
.rts2_cache_umd/

# Optional REPL history
.node_repl_history

# Output of 'npm pack'
*.tgz

# Yarn Integrity file
.yarn-integrity

# parcel-bundler cache (https://parceljs.org/)
.cache
.parcel-cache

# Next.js build output
.next

# Nuxt.js build / generate output
.nuxt

# Storybook build outputs
.out
.storybook-out

# Temporary folders
tmp/
temp/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
env.bak/
venv.bak/

# RL data
rl_data/

# ChromaDB
project_db/
"""
        
        gitignore_file = work_dir / ".gitignore"
        if not gitignore_file.exists():
            gitignore_file.write_text(gitignore_content)
            self.logger.debug(f"Created .gitignore: {gitignore_file}")
        
        # Create README.md
        readme_content = f"""# {work_dir.name}

A TypeScript project built with the AutoGen TS Engine.

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Run tests:
   ```bash
   npm test
   ```

3. Build the project:
   ```bash
   npm run build
   ```

4. Start the application:
   ```bash
   npm start
   ```

## Development

- `npm run dev` - Start development server
- `npm run lint` - Run ESLint
- `npm run format` - Format code with Prettier
- `npm run type-check` - Run TypeScript type checking

## Project Structure

- `src/` - Source code
- `tests/` - Test files
- `config/` - Configuration files
- `scrum/` - Sprint artifacts and logs
- `project_db/` - Vector database for RAG
"""
        
        readme_file = work_dir / "README.md"
        if not readme_file.exists():
            readme_file.write_text(readme_content)
            self.logger.debug(f"Created README.md: {readme_file}")
        
        # Create initial scrum file
        scrum_content = """# Sprint Log

This file tracks the development progress and decisions made during sprints.

## Sprint 1 - Project Initialization

### Goals
- Set up basic project structure
- Implement core TUI framework
- Add vi keybindings foundation

### Decisions
- Using Blessed.js for TUI
- Jest for testing framework
- TypeScript strict mode enabled

### Notes
- Project initialized with AutoGen TS Engine
- Basic file structure created
- Development environment configured
"""
        
        scrum_file = work_dir / "scrum" / "sprint_1.md"
        if not scrum_file.exists():
            scrum_file.write_text(scrum_content)
            self.logger.debug(f"Created initial scrum file: {scrum_file}")
    
    def create_venv(self, work_dir: Path) -> bool:
        """Create a virtual environment in the work directory."""
        try:
            import venv
            
            venv_path = work_dir / "venv"
            if venv_path.exists():
                self.logger.info("Virtual environment already exists")
                return True
            
            self.logger.info("Creating virtual environment...")
            venv.create(venv_path, with_pip=True)
            
            self.logger.info(f"Virtual environment created at: {venv_path}")
            return True
            
        except Exception as e:
            self.logger.error_with_context(e, "Virtual environment creation")
            return False
    
    def check_prerequisites(self) -> Dict[str, bool]:
        """Check if all prerequisites are available."""
        prerequisites = {
            "node": False,
            "npm": False,
            "git": False,
            "python": True,  # We're running Python
        }
        
        try:
            import subprocess
            
            # Check Node.js
            result = subprocess.run(["node", "--version"], 
                                  capture_output=True, text=True)
            prerequisites["node"] = result.returncode == 0
            
            # Check npm
            result = subprocess.run(["npm", "--version"], 
                                  capture_output=True, text=True)
            prerequisites["npm"] = result.returncode == 0
            
            # Check git
            result = subprocess.run(["git", "--version"], 
                                  capture_output=True, text=True)
            prerequisites["git"] = result.returncode == 0
            
        except Exception as e:
            self.logger.error(f"Error checking prerequisites: {e}")
        
        return prerequisites
    
    def validate_project_structure(self, work_dir: Path) -> Dict[str, bool]:
        """Validate that the project structure is correct."""
        validation = {
            "config_dir": False,
            "src_dir": False,
            "tests_dir": False,
            "scrum_dir": False,
            "project_db_dir": False,
            "settings_file": False,
            "agents_file": False,
        }
        
        try:
            # Check directories
            validation["config_dir"] = (work_dir / "config").exists()
            validation["src_dir"] = (work_dir / "src").exists()
            validation["tests_dir"] = (work_dir / "tests").exists()
            validation["scrum_dir"] = (work_dir / "scrum").exists()
            validation["project_db_dir"] = (work_dir / "project_db").exists()
            
            # Check config files
            validation["settings_file"] = (work_dir / "config" / "settings.md").exists()
            validation["agents_file"] = (work_dir / "config" / "agents.md").exists()
            
        except Exception as e:
            self.logger.error(f"Error validating project structure: {e}")
        
        return validation
    
    def cleanup_project(self, work_dir: Path) -> bool:
        """Clean up project files (for testing/reset)."""
        try:
            import shutil
            
            if work_dir.exists():
                shutil.rmtree(work_dir)
                self.logger.info(f"Cleaned up project directory: {work_dir}")
            
            return True
            
        except Exception as e:
            self.logger.error_with_context(e, "Project cleanup")
            return False
