"""
Sprint Artifacts Manager for AutoGen TS Engine.
Generates comprehensive documentation, progress reports, and sprint summaries.
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class SprintArtifact:
    """Represents a sprint artifact."""
    sprint_number: int
    timestamp: str
    artifact_type: str
    content: str
    metadata: Dict[str, Any]


@dataclass
class SprintSummary:
    """Comprehensive sprint summary."""
    sprint_number: int
    start_time: str
    end_time: str
    duration_minutes: float
    success: bool
    iterations_completed: int
    total_iterations: int
    artifacts_created: int
    files_modified: int
    test_results: Dict[str, Any]
    quality_results: List[Dict[str, Any]]
    errors: List[str]
    recommendations: List[str]


class SprintArtifactsManager:
    """Manages sprint artifacts and documentation generation."""
    
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.artifacts_dir = project_dir / "scrum"
        self.artifacts_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.artifacts_dir / "sprints").mkdir(exist_ok=True)
        (self.artifacts_dir / "reports").mkdir(exist_ok=True)
        (self.artifacts_dir / "metrics").mkdir(exist_ok=True)
    
    def create_sprint_summary(self, sprint_num: int, sprint_data: Dict) -> SprintSummary:
        """Create a comprehensive sprint summary."""
        start_time = sprint_data.get('start_time', datetime.now().isoformat())
        end_time = sprint_data.get('end_time', datetime.now().isoformat())
        
        # Calculate duration
        start_dt = datetime.fromisoformat(start_time)
        end_dt = datetime.fromisoformat(end_time)
        duration = (end_dt - start_dt).total_seconds() / 60
        
        # Extract metrics
        metrics = sprint_data.get('metrics', {})
        test_results = metrics.get('test_results', {})
        quality_results = metrics.get('quality_results', [])
        
        # Generate recommendations
        recommendations = self._generate_recommendations(metrics)
        
        return SprintSummary(
            sprint_number=sprint_num,
            start_time=start_time,
            end_time=end_time,
            duration_minutes=duration,
            success=sprint_data.get('success', False),
            iterations_completed=sprint_data.get('iterations_completed', 0),
            total_iterations=sprint_data.get('total_iterations', 0),
            artifacts_created=sprint_data.get('artifacts_created', 0),
            files_modified=metrics.get('modified_files', 0),
            test_results=test_results,
            quality_results=quality_results,
            errors=sprint_data.get('errors', []),
            recommendations=recommendations
        )
    
    def _generate_recommendations(self, metrics: Dict) -> List[str]:
        """Generate recommendations based on metrics."""
        recommendations = []
        
        # Test coverage recommendations
        test_coverage = metrics.get('test_coverage', 0.0)
        if test_coverage < 80:
            recommendations.append(f"Increase test coverage from {test_coverage:.1f}% to at least 80%")
        elif test_coverage < 90:
            recommendations.append(f"Consider increasing test coverage from {test_coverage:.1f}% to 90%+")
        
        # Quality recommendations
        total_issues = metrics.get('total_issues', 0)
        if total_issues > 0:
            recommendations.append(f"Address {total_issues} code quality issues")
        
        # Build recommendations
        if not metrics.get('build_success', False):
            recommendations.append("Fix build issues to ensure successful compilation")
        
        # Performance recommendations
        if metrics.get('overall_score', 0) < 80:
            recommendations.append("Focus on improving overall code quality score")
        
        if not recommendations:
            recommendations.append("Excellent work! Maintain current quality standards")
        
        return recommendations
    
    def save_sprint_summary(self, summary: SprintSummary) -> Path:
        """Save sprint summary to file."""
        sprint_file = self.artifacts_dir / "sprints" / f"sprint_{summary.sprint_number}.md"
        
        content = self._generate_sprint_markdown(summary)
        
        with open(sprint_file, 'w') as f:
            f.write(content)
        
        logger.info(f"Saved sprint summary to {sprint_file}")
        return sprint_file
    
    def _generate_sprint_markdown(self, summary: SprintSummary) -> str:
        """Generate markdown content for sprint summary."""
        lines = []
        
        # Header
        lines.append(f"# Sprint {summary.sprint_number} Results")
        lines.append("")
        
        # Overview
        lines.append("## Overview")
        status = "✅ SUCCESS" if summary.success else "❌ FAILED"
        lines.append(f"- **Status**: {status}")
        lines.append(f"- **Duration**: {summary.duration_minutes:.1f} minutes")
        lines.append(f"- **Iterations**: {summary.iterations_completed}/{summary.total_iterations}")
        lines.append(f"- **Files Modified**: {summary.files_modified}")
        lines.append(f"- **Artifacts Created**: {summary.artifacts_created}")
        lines.append("")
        
        # Test Results
        lines.append("## Test Results")
        if summary.test_results:
            test_pass_rate = summary.test_results.get('test_pass_rate', 0.0)
            test_coverage = summary.test_results.get('test_coverage', 0.0)
            lines.append(f"- **Pass Rate**: {test_pass_rate:.1f}%")
            lines.append(f"- **Coverage**: {test_coverage:.1f}%")
            lines.append(f"- **Total Tests**: {summary.test_results.get('total_tests', 0)}")
            lines.append(f"- **Passed**: {summary.test_results.get('passed_tests', 0)}")
            lines.append(f"- **Failed**: {summary.test_results.get('failed_tests', 0)}")
        else:
            lines.append("- No test results available")
        lines.append("")
        
        # Quality Results
        lines.append("## Code Quality")
        if summary.quality_results:
            for qr in summary.quality_results:
                tool = qr.get('tool', 'Unknown')
                success = qr.get('success', False)
                issues = qr.get('issues', 0)
                status = "✅ PASSED" if success else "❌ FAILED"
                lines.append(f"- **{tool}**: {status} ({issues} issues)")
        else:
            lines.append("- No quality results available")
        lines.append("")
        
        # Errors
        if summary.errors:
            lines.append("## Errors")
            for error in summary.errors:
                lines.append(f"- {error}")
            lines.append("")
        
        # Recommendations
        lines.append("## Recommendations")
        for rec in summary.recommendations:
            lines.append(f"- {rec}")
        lines.append("")
        
        # Timestamps
        lines.append("## Timestamps")
        lines.append(f"- **Started**: {summary.start_time}")
        lines.append(f"- **Completed**: {summary.end_time}")
        lines.append("")
        
        return "\n".join(lines)
    
    def generate_project_report(self, all_sprints: List[SprintSummary]) -> Path:
        """Generate comprehensive project report."""
        report_file = self.artifacts_dir / "reports" / "project_report.md"
        
        content = self._generate_project_report_markdown(all_sprints)
        
        with open(report_file, 'w') as f:
            f.write(content)
        
        logger.info(f"Generated project report: {report_file}")
        return report_file
    
    def _generate_project_report_markdown(self, sprints: List[SprintSummary]) -> str:
        """Generate comprehensive project report markdown."""
        lines = []
        
        # Header
        lines.append("# AutoGen TS Engine Project Report")
        lines.append("")
        lines.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # Executive Summary
        lines.append("## Executive Summary")
        total_sprints = len(sprints)
        successful_sprints = sum(1 for s in sprints if s.success)
        total_duration = sum(s.duration_minutes for s in sprints)
        total_files_modified = sum(s.files_modified for s in sprints)
        
        lines.append(f"- **Total Sprints**: {total_sprints}")
        lines.append(f"- **Successful Sprints**: {successful_sprints}")
        if total_sprints > 0:
            success_rate = (successful_sprints / total_sprints) * 100
            lines.append(f"- **Success Rate**: {success_rate:.1f}%")
        else:
            lines.append("- **Success Rate**: N/A")
        lines.append(f"- **Total Duration**: {total_duration:.1f} minutes")
        lines.append(f"- **Files Modified**: {total_files_modified}")
        lines.append("")
        
        # Sprint Details
        lines.append("## Sprint Details")
        for sprint in sprints:
            status = "✅" if sprint.success else "❌"
            lines.append(f"### {status} Sprint {sprint.sprint_number}")
            lines.append(f"- **Duration**: {sprint.duration_minutes:.1f} minutes")
            lines.append(f"- **Iterations**: {sprint.iterations_completed}/{sprint.total_iterations}")
            lines.append(f"- **Files Modified**: {sprint.files_modified}")
            
            # Test coverage
            if sprint.test_results:
                coverage = sprint.test_results.get('test_coverage', 0.0)
                lines.append(f"- **Test Coverage**: {coverage:.1f}%")
            
            lines.append("")
        
        # Quality Trends
        lines.append("## Quality Trends")
        if sprints:
            # Calculate average metrics
            sprints_with_tests = [s for s in sprints if s.test_results]
            if sprints_with_tests:
                avg_coverage = sum(
                    s.test_results.get('test_coverage', 0.0) for s in sprints_with_tests
                ) / len(sprints_with_tests)
            else:
                avg_coverage = 0.0
            
            total_issues = sum(
                sum(qr.get('issues', 0) for qr in s.quality_results) 
                for s in sprints
            )
            
            lines.append(f"- **Average Test Coverage**: {avg_coverage:.1f}%")
            lines.append(f"- **Total Quality Issues**: {total_issues}")
            lines.append("")
        
        # Recommendations
        lines.append("## Overall Recommendations")
        if sprints:
            # Generate overall recommendations
            if successful_sprints < total_sprints:
                lines.append("- Focus on improving sprint success rate")
            
            if avg_coverage < 80:
                lines.append("- Prioritize increasing test coverage")
            
            if total_issues > 0:
                lines.append("- Address code quality issues systematically")
            
            lines.append("- Continue iterative development approach")
        else:
            lines.append("- No sprint data available for recommendations")
        
        lines.append("")
        
        return "\n".join(lines)
    
    def save_metrics_json(self, sprint_num: int, metrics: Dict) -> Path:
        """Save metrics as JSON for analysis."""
        metrics_file = self.artifacts_dir / "metrics" / f"sprint_{sprint_num}_metrics.json"
        
        metrics_data = {
            "sprint_number": sprint_num,
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics
        }
        
        with open(metrics_file, 'w') as f:
            json.dump(metrics_data, f, indent=2)
        
        logger.info(f"Saved metrics to {metrics_file}")
        return metrics_file
    
    def generate_burndown_chart_data(self, sprints: List[SprintSummary]) -> Path:
        """Generate data for burndown chart."""
        chart_file = self.artifacts_dir / "reports" / "burndown_data.json"
        
        chart_data = {
            "sprints": [],
            "cumulative_metrics": []
        }
        
        cumulative_files = 0
        cumulative_issues = 0
        
        for sprint in sprints:
            cumulative_files += sprint.files_modified
            cumulative_issues += sum(qr.get('issues', 0) for qr in sprint.quality_results)
            
            chart_data["sprints"].append({
                "sprint": sprint.sprint_number,
                "files_modified": sprint.files_modified,
                "cumulative_files": cumulative_files,
                "quality_issues": sum(qr.get('issues', 0) for qr in sprint.quality_results),
                "cumulative_issues": cumulative_issues,
                "test_coverage": sprint.test_results.get('test_coverage', 0.0) if sprint.test_results else 0.0,
                "success": sprint.success
            })
        
        with open(chart_file, 'w') as f:
            json.dump(chart_data, f, indent=2)
        
        logger.info(f"Generated burndown chart data: {chart_file}")
        return chart_file
    
    def create_sprint_artifact(self, sprint_num: int, artifact_type: str, 
                              content: str, metadata: Dict = None) -> SprintArtifact:
        """Create a sprint artifact."""
        artifact = SprintArtifact(
            sprint_number=sprint_num,
            timestamp=datetime.now().isoformat(),
            artifact_type=artifact_type,
            content=content,
            metadata=metadata or {}
        )
        
        # Save artifact
        artifact_file = self.artifacts_dir / "sprints" / f"sprint_{sprint_num}_{artifact_type}.json"
        with open(artifact_file, 'w') as f:
            json.dump(asdict(artifact), f, indent=2)
        
        logger.info(f"Created artifact: {artifact_file}")
        return artifact
    
    def get_sprint_artifacts(self, sprint_num: int) -> List[SprintArtifact]:
        """Get all artifacts for a specific sprint."""
        artifacts = []
        sprint_dir = self.artifacts_dir / "sprints"
        
        for file_path in sprint_dir.glob(f"sprint_{sprint_num}_*.json"):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    artifacts.append(SprintArtifact(**data))
            except Exception as e:
                logger.error(f"Error loading artifact {file_path}: {e}")
        
        return artifacts
    
    def cleanup_old_artifacts(self, keep_days: int = 30) -> int:
        """Clean up old artifacts, keeping only recent ones."""
        cutoff_date = datetime.now() - timedelta(days=keep_days)
        cleaned_count = 0
        
        for file_path in self.artifacts_dir.rglob("*.json"):
            try:
                file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_time < cutoff_date:
                    file_path.unlink()
                    cleaned_count += 1
            except Exception as e:
                logger.error(f"Error cleaning up {file_path}: {e}")
        
        logger.info(f"Cleaned up {cleaned_count} old artifacts")
        return cleaned_count
