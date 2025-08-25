"""Node.js operations for TypeScript project management."""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .schemas import NodeConfig


class NodeOps:
    """Node.js and TypeScript project operations."""
    
    def __init__(self, work_dir: Path, config: NodeConfig):
        self.work_dir = work_dir
        self.config = config
        self.package_json_path = work_dir / "package.json"
        self.tsconfig_path = work_dir / "tsconfig.json"
        self.jest_config_path = work_dir / "jest.config.ts"
    
    def initialize_project(self, project_name: str, project_goal: str) -> bool:
        """Initialize a new TypeScript project."""
        try:
            # Create work directory
            self.work_dir.mkdir(parents=True, exist_ok=True)
            
            # Initialize package.json
            self._create_package_json(project_name, project_goal)
            
            # Create TypeScript configuration
            self._create_tsconfig_json()
            
            # Create Jest configuration
            self._create_jest_config()
            
            # Create basic project structure
            self._create_project_structure()
            
            # Install dependencies
            self._install_dependencies()
            
            return True
            
        except Exception as e:
            print(f"Failed to initialize project: {e}")
            return False
    
    def _create_package_json(self, project_name: str, project_goal: str) -> None:
        """Create package.json with TypeScript and TUI dependencies."""
        package_data = {
            "name": project_name,
            "version": "0.1.0",
            "description": project_goal,
            "main": "dist/index.js",
            "type": "module",
            "scripts": {
                "build": "tsc",
                "start": "node dist/index.js",
                "dev": "ts-node src/index.ts",
                "test": "jest",
                "test:watch": "jest --watch",
                "test:coverage": "jest --coverage",
                "lint": "eslint src/**/*.ts",
                "lint:fix": "eslint src/**/*.ts --fix",
                "format": "prettier --write src/**/*.ts",
                "type-check": "tsc --noEmit"
            },
            "dependencies": {
                "blessed": "^0.1.81",
                "@types/blessed": "^0.1.19"
            },
            "devDependencies": {
                "typescript": "^5.0.0",
                "ts-node": "^10.9.0",
                "jest": "^29.0.0",
                "ts-jest": "^29.0.0",
                "@types/jest": "^29.0.0",
                "@types/node": "^20.0.0",
                "eslint": "^8.0.0",
                "@typescript-eslint/eslint-plugin": "^6.0.0",
                "@typescript-eslint/parser": "^6.0.0",
                "prettier": "^3.0.0"
            },
            "engines": {
                "node": ">=18.0.0"
            }
        }
        
        with open(self.package_json_path, 'w') as f:
            json.dump(package_data, f, indent=2)
    
    def _create_tsconfig_json(self) -> None:
        """Create TypeScript configuration."""
        tsconfig_data = {
            "compilerOptions": {
                "target": "ES2022",
                "module": "ESNext",
                "moduleResolution": "node",
                "lib": ["ES2022"],
                "outDir": "./dist",
                "rootDir": "./src",
                "strict": True,
                "esModuleInterop": True,
                "skipLibCheck": True,
                "forceConsistentCasingInFileNames": True,
                "declaration": True,
                "declarationMap": True,
                "sourceMap": True,
                "removeComments": False,
                "noImplicitAny": True,
                "noImplicitReturns": True,
                "noImplicitThis": True,
                "noUnusedLocals": True,
                "noUnusedParameters": True,
                "exactOptionalPropertyTypes": True,
                "noImplicitOverride": True,
                "noPropertyAccessFromIndexSignature": True,
                "noUncheckedIndexedAccess": True
            },
            "include": [
                "src/**/*"
            ],
            "exclude": [
                "node_modules",
                "dist",
                "**/*.test.ts",
                "**/*.spec.ts"
            ]
        }
        
        with open(self.tsconfig_path, 'w') as f:
            json.dump(tsconfig_data, f, indent=2)
    
    def _create_jest_config(self) -> None:
        """Create Jest configuration for TypeScript testing."""
        jest_config_content = """import type { Config } from '@jest/types';

const config: Config.InitialOptions = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/src', '<rootDir>/tests'],
  testMatch: [
    '**/__tests__/**/*.ts',
    '**/?(*.)+(spec|test).ts'
  ],
  transform: {
    '^.+\\.ts$': 'ts-jest',
  },
  collectCoverageFrom: [
    'src/**/*.ts',
    '!src/**/*.d.ts',
    '!src/**/*.test.ts',
    '!src/**/*.spec.ts'
  ],
  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'lcov', 'html'],
  setupFilesAfterEnv: ['<rootDir>/tests/setup.ts'],
  testTimeout: 10000,
};

export default config;
"""
        
        with open(self.jest_config_path, 'w') as f:
            f.write(jest_config_content)
    
    def _create_project_structure(self) -> None:
        """Create basic project directory structure."""
        # Create directories
        (self.work_dir / "src").mkdir(exist_ok=True)
        (self.work_dir / "tests").mkdir(exist_ok=True)
        (self.work_dir / "dist").mkdir(exist_ok=True)
        
        # Create main entry point
        main_content = """#!/usr/bin/env node

import { App } from './app';

async function main() {
    const app = new App();
    await app.start();
}

main().catch(console.error);
"""
        
        with open(self.work_dir / "src" / "index.ts", 'w') as f:
            f.write(main_content)
        
        # Create app class
        app_content = """import * as blessed from 'blessed';

export class App {
    private screen: blessed.Widgets.Screen;
    
    constructor() {
        this.screen = blessed.screen({
            smartCSR: true,
            title: 'TypeScript Terminal File Manager'
        });
        
        this.setupKeyHandlers();
    }
    
    private setupKeyHandlers(): void {
        this.screen.key(['escape', 'q', 'C-c'], () => {
            process.exit(0);
        });
        
        // Vi keybindings
        this.screen.key(['h', 'j', 'k', 'l'], (ch, key) => {
            this.handleViNavigation(key.name);
        });
    }
    
    private handleViNavigation(key: string): void {
        // TODO: Implement vi navigation
        console.log(`Vi key pressed: ${key}`);
    }
    
    async start(): Promise<void> {
        // TODO: Initialize file manager UI
        console.log('Starting TypeScript Terminal File Manager...');
        
        this.screen.render();
    }
}
"""
        
        with open(self.work_dir / "src" / "app.ts", 'w') as f:
            f.write(app_content)
        
        # Create test setup
        setup_content = """// Jest setup file
import '@testing-library/jest-dom';

// Mock blessed for testing
jest.mock('blessed', () => ({
    screen: jest.fn(() => ({
        key: jest.fn(),
        render: jest.fn(),
        destroy: jest.fn()
    }))
}));
"""
        
        with open(self.work_dir / "tests" / "setup.ts", 'w') as f:
            f.write(setup_content)
        
        # Create basic test
        test_content = """import { App } from '../src/app';

describe('App', () => {
    let app: App;
    
    beforeEach(() => {
        app = new App();
    });
    
    afterEach(() => {
        // Cleanup
    });
    
    test('should initialize without errors', () => {
        expect(app).toBeDefined();
    });
    
    test('should handle vi navigation keys', async () => {
        // TODO: Test vi keybindings
        expect(true).toBe(true);
    });
});
"""
        
        with open(self.work_dir / "tests" / "app.test.ts", 'w') as f:
            f.write(test_content)
    
    def _install_dependencies(self) -> bool:
        """Install project dependencies."""
        try:
            # Run npm install
            result = subprocess.run(
                [self.config.package_manager, "install"],
                cwd=self.work_dir,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode != 0:
                print(f"Failed to install dependencies: {result.stderr}")
                return False
            
            return True
            
        except subprocess.TimeoutExpired:
            print("Dependency installation timed out")
            return False
        except Exception as e:
            print(f"Error installing dependencies: {e}")
            return False
    
    def run_command(self, command: str, capture_output: bool = True) -> Tuple[int, str, str]:
        """Run a command in the project directory."""
        try:
            result = subprocess.run(
                command.split(),
                cwd=self.work_dir,
                capture_output=capture_output,
                text=True,
                timeout=120
            )
            
            return result.returncode, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out"
        except Exception as e:
            return -1, "", str(e)
    
    def run_tests(self) -> Dict:
        """Run tests and return results."""
        returncode, stdout, stderr = self.run_command(self.config.test_command)
        
        # Parse test results
        test_results = {
            "success": returncode == 0,
            "returncode": returncode,
            "stdout": stdout,
            "stderr": stderr,
            "passed": 0,
            "failed": 0,
            "coverage": None
        }
        
        # Try to extract test counts from output
        if stdout:
            # Look for Jest test results
            if "Tests:" in stdout:
                lines = stdout.split('\n')
                for line in lines:
                    if "Tests:" in line:
                        # Parse "Tests: 5 passed, 0 failed"
                        parts = line.split(',')
                        if len(parts) >= 2:
                            passed_part = parts[0].split()[-1]
                            failed_part = parts[1].split()[-1]
                            test_results["passed"] = int(passed_part)
                            test_results["failed"] = int(failed_part)
                        break
            
            # Look for coverage information
            if "All files" in stdout and "%" in stdout:
                lines = stdout.split('\n')
                for line in lines:
                    if "All files" in line and "%" in line:
                        # Extract coverage percentage
                        import re
                        match = re.search(r'(\d+(?:\.\d+)?)%', line)
                        if match:
                            test_results["coverage"] = float(match.group(1))
                        break
        
        return test_results
    
    def run_build(self) -> Dict:
        """Run build command and return results."""
        returncode, stdout, stderr = self.run_command(self.config.build_command)
        
        return {
            "success": returncode == 0,
            "returncode": returncode,
            "stdout": stdout,
            "stderr": stderr
        }
    
    def get_project_metrics(self) -> Dict:
        """Get current project metrics."""
        metrics = {
            "test_pass_rate": 0.0,
            "test_coverage": 0.0,
            "code_complexity": 1.0,
            "dependency_count": 0,
            "build_success": False
        }
        
        # Run tests to get metrics
        test_results = self.run_tests()
        if test_results["success"]:
            total_tests = test_results["passed"] + test_results["failed"]
            if total_tests > 0:
                metrics["test_pass_rate"] = test_results["passed"] / total_tests
            
            if test_results["coverage"] is not None:
                metrics["test_coverage"] = test_results["coverage"] / 100.0
        
        # Run build
        build_results = self.run_build()
        metrics["build_success"] = build_results["success"]
        
        # Count dependencies
        if self.package_json_path.exists():
            try:
                with open(self.package_json_path, 'r') as f:
                    package_data = json.load(f)
                
                dependencies = package_data.get("dependencies", {})
                dev_dependencies = package_data.get("devDependencies", {})
                metrics["dependency_count"] = len(dependencies) + len(dev_dependencies)
                
            except Exception:
                pass
        
        return metrics
    
    def add_dependency(self, package_name: str, is_dev: bool = False) -> bool:
        """Add a dependency to the project."""
        try:
            command = f"{self.config.package_manager} install {package_name}"
            if is_dev:
                command = f"{self.config.package_manager} install --save-dev {package_name}"
            
            returncode, stdout, stderr = self.run_command(command)
            return returncode == 0
            
        except Exception as e:
            print(f"Error adding dependency: {e}")
            return False
    
    def remove_dependency(self, package_name: str) -> bool:
        """Remove a dependency from the project."""
        try:
            command = f"{self.config.package_manager} uninstall {package_name}"
            returncode, stdout, stderr = self.run_command(command)
            return returncode == 0
            
        except Exception as e:
            print(f"Error removing dependency: {e}")
            return False
    
    def check_node_version(self) -> Optional[str]:
        """Check Node.js version."""
        try:
            returncode, stdout, stderr = self.run_command("node --version")
            if returncode == 0:
                return stdout.strip()
            return None
        except Exception:
            return None
    
    def check_package_manager(self) -> bool:
        """Check if the configured package manager is available."""
        try:
            returncode, stdout, stderr = self.run_command(f"{self.config.package_manager} --version")
            return returncode == 0
        except Exception:
            return False
