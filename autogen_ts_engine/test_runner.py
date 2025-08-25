"""
Test Runner for AutoGen TS Engine.
Executes tests, code quality checks, and generates reports.
"""

import subprocess
import sys
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Result of a test execution."""
    success: bool
    total_tests: int
    passed_tests: int
    failed_tests: int
    coverage_percentage: Optional[float] = None
    execution_time: Optional[float] = None
    error_message: Optional[str] = None


@dataclass
class QualityResult:
    """Result of a code quality check."""
    tool: str
    success: bool
    issues_found: int
    error_message: Optional[str] = None
    output: Optional[str] = None


@dataclass
class ProjectMetrics:
    """Overall project metrics."""
    test_results: TestResult
    quality_results: List[QualityResult]
    build_success: bool
    total_issues: int
    overall_score: float


class TestRunner:
    """Runs tests and quality checks for generated projects."""
    
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.python_executable = sys.executable
    
    def run_all_checks(self) -> ProjectMetrics:
        """Run all tests and quality checks."""
        logger.info("Starting comprehensive project testing...")
        
        # Run tests
        test_result = self.run_tests()
        
        # Run quality checks
        quality_results = self.run_quality_checks()
        
        # Check build
        build_success = self.check_build()
        
        # Calculate metrics
        total_issues = sum(qr.issues_found for qr in quality_results)
        overall_score = self._calculate_score(test_result, quality_results, build_success)
        
        return ProjectMetrics(
            test_results=test_result,
            quality_results=quality_results,
            build_success=build_success,
            total_issues=total_issues,
            overall_score=overall_score
        )
    
    def run_tests(self) -> TestResult:
        """Run pytest with coverage."""
        try:
            logger.info("Running tests with pytest...")
            
            # Run pytest with coverage
            cmd = [
                self.python_executable, "-m", "pytest",
                "tests/",
                "--cov=src",
                "--cov-report=term-missing",
                "--cov-report=xml",
                "--cov-report=html",
                "-v"
            ]
            
            result = subprocess.run(
                cmd,
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            # Parse results
            if result.returncode == 0:
                # Extract test counts from output
                lines = result.stdout.split('\n')
                total_tests = 0
                passed_tests = 0
                failed_tests = 0
                
                for line in lines:
                    if 'collected' in line:
                        total_tests = int(line.split()[0])
                    elif 'PASSED' in line:
                        passed_tests += 1
                    elif 'FAILED' in line:
                        failed_tests += 1
                
                # Parse coverage from XML
                coverage_percentage = self._parse_coverage_xml()
                
                return TestResult(
                    success=True,
                    total_tests=total_tests,
                    passed_tests=passed_tests,
                    failed_tests=failed_tests,
                    coverage_percentage=coverage_percentage
                )
            else:
                return TestResult(
                    success=False,
                    total_tests=0,
                    passed_tests=0,
                    failed_tests=0,
                    error_message=result.stderr
                )
                
        except subprocess.TimeoutExpired:
            return TestResult(
                success=False,
                total_tests=0,
                passed_tests=0,
                failed_tests=0,
                error_message="Test execution timed out"
            )
        except Exception as e:
            return TestResult(
                success=False,
                total_tests=0,
                passed_tests=0,
                failed_tests=0,
                error_message=str(e)
            )
    
    def run_quality_checks(self) -> List[QualityResult]:
        """Run code quality checks."""
        results = []
        
        # Run black (code formatting)
        results.append(self._run_black())
        
        # Run flake8 (linting)
        results.append(self._run_flake8())
        
        # Run mypy (type checking)
        results.append(self._run_mypy())
        
        # Run bandit (security)
        results.append(self._run_bandit())
        
        return results
    
    def _run_black(self) -> QualityResult:
        """Run black code formatter check."""
        try:
            cmd = [self.python_executable, "-m", "black", "--check", "src/", "tests/"]
            result = subprocess.run(cmd, cwd=self.project_dir, capture_output=True, text=True)
            
            return QualityResult(
                tool="black",
                success=result.returncode == 0,
                issues_found=0 if result.returncode == 0 else 1,
                output=result.stdout + result.stderr
            )
        except Exception as e:
            return QualityResult(
                tool="black",
                success=False,
                issues_found=1,
                error_message=str(e)
            )
    
    def _run_flake8(self) -> QualityResult:
        """Run flake8 linting."""
        try:
            cmd = [self.python_executable, "-m", "flake8", "src/", "tests/"]
            result = subprocess.run(cmd, cwd=self.project_dir, capture_output=True, text=True)
            
            # Count issues from output
            issues_found = len(result.stdout.split('\n')) - 1 if result.stdout.strip() else 0
            
            return QualityResult(
                tool="flake8",
                success=result.returncode == 0,
                issues_found=issues_found,
                output=result.stdout
            )
        except Exception as e:
            return QualityResult(
                tool="flake8",
                success=False,
                issues_found=1,
                error_message=str(e)
            )
    
    def _run_mypy(self) -> QualityResult:
        """Run mypy type checking."""
        try:
            cmd = [self.python_executable, "-m", "mypy", "src/"]
            result = subprocess.run(cmd, cwd=self.project_dir, capture_output=True, text=True)
            
            # Count issues from output
            issues_found = len(result.stdout.split('\n')) - 1 if result.stdout.strip() else 0
            
            return QualityResult(
                tool="mypy",
                success=result.returncode == 0,
                issues_found=issues_found,
                output=result.stdout
            )
        except Exception as e:
            return QualityResult(
                tool="mypy",
                success=False,
                issues_found=1,
                error_message=str(e)
            )
    
    def _run_bandit(self) -> QualityResult:
        """Run bandit security check."""
        try:
            cmd = [self.python_executable, "-m", "bandit", "-r", "src/"]
            result = subprocess.run(cmd, cwd=self.project_dir, capture_output=True, text=True)
            
            # Count security issues
            issues_found = 0
            if result.stdout:
                for line in result.stdout.split('\n'):
                    if '>> Issue:' in line:
                        issues_found += 1
            
            return QualityResult(
                tool="bandit",
                success=result.returncode == 0,
                issues_found=issues_found,
                output=result.stdout
            )
        except Exception as e:
            return QualityResult(
                tool="bandit",
                success=False,
                issues_found=1,
                error_message=str(e)
            )
    
    def check_build(self) -> bool:
        """Check if the project builds successfully."""
        try:
            # Try to build the project
            cmd = [self.python_executable, "setup.py", "build"]
            result = subprocess.run(cmd, cwd=self.project_dir, capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False
    
    def _parse_coverage_xml(self) -> Optional[float]:
        """Parse coverage percentage from XML report."""
        try:
            coverage_file = self.project_dir / "htmlcov" / "coverage.xml"
            if coverage_file.exists():
                tree = ET.parse(coverage_file)
                root = tree.getroot()
                
                # Find the coverage percentage
                for elem in root.iter():
                    if elem.tag.endswith('coverage'):
                        line_rate = elem.get('line-rate')
                        if line_rate:
                            return float(line_rate) * 100
            return None
        except Exception:
            return None
    
    def _calculate_score(self, test_result: TestResult, quality_results: List[QualityResult], build_success: bool) -> float:
        """Calculate overall project score."""
        score = 0.0
        
        # Test score (40% weight)
        if test_result.success and test_result.total_tests > 0:
            test_score = (test_result.passed_tests / test_result.total_tests) * 100
            coverage_bonus = test_result.coverage_percentage or 0
            score += (test_score + coverage_bonus) * 0.4
        
        # Quality score (40% weight)
        quality_score = 0
        for qr in quality_results:
            if qr.success:
                quality_score += 25  # 25 points per passing tool
        score += quality_score * 0.4
        
        # Build score (20% weight)
        if build_success:
            score += 100 * 0.2
        
        return min(score, 100.0)  # Cap at 100
    
    def generate_report(self, metrics: ProjectMetrics) -> str:
        """Generate a comprehensive test report."""
        report = []
        report.append("# Project Quality Report")
        report.append("")
        
        # Test Results
        report.append("## Test Results")
        report.append(f"- **Status**: {'✅ PASSED' if metrics.test_results.success else '❌ FAILED'}")
        report.append(f"- **Total Tests**: {metrics.test_results.total_tests}")
        report.append(f"- **Passed**: {metrics.test_results.passed_tests}")
        report.append(f"- **Failed**: {metrics.test_results.failed_tests}")
        if metrics.test_results.coverage_percentage:
            report.append(f"- **Coverage**: {metrics.test_results.coverage_percentage:.1f}%")
        if metrics.test_results.error_message:
            report.append(f"- **Error**: {metrics.test_results.error_message}")
        report.append("")
        
        # Quality Results
        report.append("## Code Quality")
        for qr in metrics.quality_results:
            status = "✅ PASSED" if qr.success else "❌ FAILED"
            report.append(f"- **{qr.tool}**: {status} ({qr.issues_found} issues)")
        report.append("")
        
        # Build Status
        report.append("## Build Status")
        report.append(f"- **Build**: {'✅ SUCCESS' if metrics.build_success else '❌ FAILED'}")
        report.append("")
        
        # Overall Score
        report.append("## Overall Score")
        report.append(f"- **Score**: {metrics.overall_score:.1f}/100")
        report.append(f"- **Total Issues**: {metrics.total_issues}")
        report.append("")
        
        # Recommendations
        report.append("## Recommendations")
        if metrics.overall_score < 80:
            report.append("- Consider improving test coverage")
            report.append("- Fix code quality issues")
            report.append("- Address security concerns")
        else:
            report.append("- Excellent code quality!")
            report.append("- Maintain current standards")
        
        return "\n".join(report)
    
    def install_dependencies(self) -> bool:
        """Install required testing dependencies."""
        try:
            logger.info("Installing testing dependencies...")
            
            # Install development dependencies
            cmd = [self.python_executable, "-m", "pip", "install", "-e", ".[dev]"]
            result = subprocess.run(cmd, cwd=self.project_dir, capture_output=True, text=True)
            
            if result.returncode != 0:
                # Try installing individual packages
                packages = ["pytest", "pytest-cov", "black", "flake8", "mypy", "bandit"]
                for package in packages:
                    cmd = [self.python_executable, "-m", "pip", "install", package]
                    subprocess.run(cmd, cwd=self.project_dir, capture_output=True, text=True)
            
            return True
        except Exception as e:
            logger.error(f"Failed to install dependencies: {e}")
            return False
