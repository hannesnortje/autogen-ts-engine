"""
Code Generation Engine for AutoGen TS Engine.
Generates Python code, tests, and documentation based on project requirements.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class CodeTemplate:
    """Template for generating code."""
    name: str
    content: str
    placeholders: List[str]


class CodeGenerator:
    """Generates Python code, tests, and documentation."""
    
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, CodeTemplate]:
        """Load code templates."""
        return {
            "main_app": CodeTemplate(
                name="main_app",
                content="""#!/usr/bin/env python3
\"\"\"
{app_name} - {description}

A Python application built with modern best practices.
\"\"\"

import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    \"\"\"Main application entry point.\"\"\"
    logger.info("Starting {app_name}")

    try:
        # TODO: Implement main application logic
        logger.info("Application logic placeholder")

        # Example: Process command line arguments
        if len(sys.argv) > 1:
            logger.info(f"Arguments: {sys.argv[1:]}")

        logger.info("Application completed successfully")
        return 0

    except Exception as e:
        logger.error(f"Application failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
""",
                placeholders=["app_name", "description"]
            ),
            
            "requirements": CodeTemplate(
                name="requirements",
                content="""# Core dependencies
pytest>=7.0.0
pytest-cov>=4.0.0
black>=23.0.0
flake8>=6.0.0
mypy>=1.0.0

# Development dependencies
pre-commit>=3.0.0
tox>=4.0.0

# Application specific dependencies
# TODO: Add your application dependencies here
""",
                placeholders=[]
            ),
            
            "setup_py": CodeTemplate(
                name="setup_py",
                content="""#!/usr/bin/env python3
\"\"\"
Setup script for {app_name}.
\"\"\"

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="{app_name_lower}",
    version="0.1.0",
    author="AutoGen TS Engine",
    author_email="dev@example.com",
    description="{description}",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/example/{app_name_lower}",
    packages=find_packages(where="src"),
    package_dir={{"": "src"}},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
            "tox>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "{app_name_lower}={app_name_lower}.main:main",
        ],
    },
)
""",
                placeholders=["app_name", "app_name_lower", "description"]
            ),
            
            "test_main": CodeTemplate(
                name="test_main",
                content="""\"\"\"
Tests for main application module.
\"\"\"

from pathlib import Path
from unittest.mock import patch

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from {app_name_lower}.main import main


class TestMain:
    \"\"\"Test cases for main function.\"\"\"

    @patch('{app_name_lower}.main.logger')
    def test_main_success(self, mock_logger):
        \"\"\"Test successful main execution.\"\"\"
        with patch('sys.argv', ['{app_name_lower}']):
            result = main()
            assert result == 0
            mock_logger.info.assert_called()

    @patch('{app_name_lower}.main.logger')
    def test_main_with_arguments(self, mock_logger):
        \"\"\"Test main execution with command line arguments.\"\"\"
        with patch('sys.argv', ['{app_name_lower}', 'arg1', 'arg2']):
            result = main()
            assert result == 0
            mock_logger.info.assert_called()

    @patch('{app_name_lower}.main.logger')
    def test_main_exception_handling(self, mock_logger):
        \"\"\"Test main execution with exception handling.\"\"\"
        with patch('{app_name_lower}.main.logger') as mock_logger:
            # Simulate an exception
            with patch(
                '{app_name_lower}.main.logger.info',
                side_effect=Exception("Test error")
            ):
                result = main()
                assert result == 1
                mock_logger.error.assert_called()


if __name__ == "__main__":
    pytest.main([__file__])
""",
                placeholders=["app_name_lower"]
            ),
            
            "readme": CodeTemplate(
                name="readme",
                content="""# {app_name}

{description}

## Features

- Modern Python development practices
- Comprehensive testing with pytest
- Code quality tools (black, flake8, mypy)
- Pre-commit hooks for code quality
- Tox for multi-environment testing

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd {app_name_lower}

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -e .
pip install -e ".[dev]"
```

## Development

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov={app_name_lower}

# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/

# Run all quality checks
pre-commit run --all-files
```

## Usage

```bash
# Run the application
python -m {app_name_lower}.main

# Or use the installed command
{app_name_lower}
```

## Project Structure

```
{app_name_lower}/
├── src/
│   └── {app_name_lower}/
│       ├── __init__.py
│       └── main.py
├── tests/
│   ├── __init__.py
│   └── test_main.py
├── requirements.txt
├── setup.py
├── README.md
└── pyproject.toml
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
""",
                placeholders=["app_name", "app_name_lower", "description"]
            ),
            
            "pyproject_toml": CodeTemplate(
                name="pyproject_toml",
                content="""[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{app_name_lower}"
version = "0.1.0"
description = "{description}"
readme = "README.md"
requires-python = ">=3.8"
license = {{text = "MIT"}}
authors = [
    {{name = "AutoGen TS Engine", email = "dev@example.com"}},
]
keywords = ["python", "development", "automation"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]

dependencies = [
    # Core dependencies will be read from requirements.txt
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "black>=23.0.0",
    "flake8>=6.0.0",
    "mypy>=1.0.0",
    "pre-commit>=3.0.0",
    "tox>=4.0.0",
]

[project.scripts]
{app_name_lower} = "{app_name_lower}.main:main"
""",
                placeholders=["app_name", "app_name_lower", "description"]
            ),
            
            "init_py": CodeTemplate(
                name="init_py",
                content="""\"\"\"
{app_name} package.

{description}
\"\"\"

__version__ = "0.1.0"
__author__ = "AutoGen TS Engine"
__email__ = "dev@example.com"

# Import main components for easy access
from .main import main

__all__ = ["main"]
""",
                placeholders=["app_name", "description"]
            )
        }
    
    def generate_project_structure(self, app_name: str, description: str) -> bool:
        """Generate complete Python project structure."""
        try:
            # Create project directories
            src_dir = self.project_dir / "src" / app_name.lower()
            tests_dir = self.project_dir / "tests"
            
            src_dir.mkdir(parents=True, exist_ok=True)
            tests_dir.mkdir(exist_ok=True)
            
            # Generate main application file
            self._generate_file(
                src_dir / "main.py",
                self.templates["main_app"],
                app_name=app_name,
                description=description
            )
            
            # Generate __init__.py files
            self._generate_file(
                src_dir / "__init__.py",
                self.templates["init_py"],
                app_name=app_name,
                description=description
            )
            
            self._generate_file(
                tests_dir / "__init__.py",
                CodeTemplate("init_py", "", []),
                app_name=app_name,
                description=description
            )
            
            # Generate test file
            self._generate_file(
                tests_dir / "test_main.py",
                self.templates["test_main"],
                app_name_lower=app_name.lower()
            )
            
            # Generate configuration files
            self._generate_file(
                self.project_dir / "requirements.txt",
                self.templates["requirements"]
            )
            
            self._generate_file(
                self.project_dir / "setup.py",
                self.templates["setup_py"],
                app_name=app_name,
                app_name_lower=app_name.lower(),
                description=description
            )
            
            self._generate_file(
                self.project_dir / "README.md",
                self.templates["readme"],
                app_name=app_name,
                app_name_lower=app_name.lower(),
                description=description
            )
            
            self._generate_file(
                self.project_dir / "pyproject.toml",
                self.templates["pyproject_toml"],
                app_name=app_name,
                app_name_lower=app_name.lower(),
                description=description
            )
            
            return True
            
        except Exception as e:
            print(f"Error generating project structure: {e}")
            return False
    
    def _generate_file(self, file_path: Path, template: CodeTemplate, **kwargs) -> None:
        """Generate a file from a template."""
        content = template.content
        
        # Replace placeholders
        for placeholder in template.placeholders:
            if placeholder in kwargs:
                content = content.replace(f"{{{placeholder}}}", str(kwargs[placeholder]))
        
        # Write file
        file_path.write_text(content)
        print(f"Generated: {file_path}")
    
    def generate_feature(self, feature_name: str, feature_description: str) -> bool:
        """Generate a new feature module."""
        try:
            src_dir = self.project_dir / "src" / self._get_app_name()
            
            # Create feature module
            feature_file = src_dir / f"{feature_name.lower()}.py"
            feature_content = f'''"""
{feature_name} module.

{feature_description}
"""

import logging

logger = logging.getLogger(__name__)


class {feature_name.title().replace('_', '')}:
    """{feature_description}"""
    
    def __init__(self):
        """Initialize {feature_name}."""
        self.logger = logger
    
    def process(self, data):
        """Process data with {feature_name}."""
        self.logger.info(f"Processing data with {{feature_name}}")
        # TODO: Implement feature logic
        return data
    
    def validate(self, data):
        """Validate data for {feature_name}."""
        self.logger.info(f"Validating data for {{feature_name}}")
        # TODO: Implement validation logic
        return True


def create_{feature_name.lower()}():
    """Factory function to create {feature_name} instance."""
    return {feature_name.title().replace('_', '')}()
'''
            
            feature_file.write_text(feature_content)
            print(f"Generated feature: {feature_file}")
            
            # Generate test for feature
            tests_dir = self.project_dir / "tests"
            test_file = tests_dir / f"test_{feature_name.lower()}.py"
            test_content = f'''"""
Tests for {feature_name} module.
"""

import pytest
from unittest.mock import patch, MagicMock

from {self._get_app_name()}.{feature_name.lower()} import {feature_name.title().replace('_', '')}, create_{feature_name.lower()}


class Test{feature_name.title().replace('_', '')}:
    """Test cases for {feature_name} class."""
    
    def test_init(self):
        """Test {feature_name} initialization."""
        feature = {feature_name.title().replace('_', '')}()
        assert feature is not None
        assert hasattr(feature, 'logger')
    
    def test_process(self):
        """Test {feature_name} processing."""
        feature = {feature_name.title().replace('_', '')}()
        test_data = {{"test": "data"}}
        
        with patch.object(feature.logger, 'info') as mock_logger:
            result = feature.process(test_data)
            assert result == test_data
            mock_logger.assert_called_once()
    
    def test_validate(self):
        """Test {feature_name} validation."""
        feature = {feature_name.title().replace('_', '')}()
        test_data = {{"test": "data"}}
        
        with patch.object(feature.logger, 'info') as mock_logger:
            result = feature.validate(test_data)
            assert result is True
            mock_logger.assert_called_once()


class Test{feature_name.title().replace('_', '')}Factory:
    """Test cases for {feature_name} factory function."""
    
    def test_create_{feature_name.lower()}(self):
        """Test factory function."""
        feature = create_{feature_name.lower()}()
        assert isinstance(feature, {feature_name.title().replace('_', '')})
'''
            
            test_file.write_text(test_content)
            print(f"Generated test: {test_file}")
            
            return True
            
        except Exception as e:
            print(f"Error generating feature: {e}")
            return False
    
    def _get_app_name(self) -> str:
        """Get the application name from the project structure."""
        # Try to find the app name from src directory
        src_dir = self.project_dir / "src"
        if src_dir.exists():
            for item in src_dir.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    return item.name
        return "app"  # Default fallback
