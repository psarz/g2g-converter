"""
Data models for GitHub Actions workflow generation.
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class GitHubStep:
    """Represents a GitHub Actions step."""
    name: str
    uses: Optional[str] = None
    run: Optional[str] = None
    env: Dict[str, str] = field(default_factory=dict)
    with_: Dict[str, Any] = field(default_factory=dict)
    if_: Optional[str] = None
    continue_on_error: bool = False


@dataclass
class GitHubJob:
    """Represents a GitHub Actions job."""
    name: str
    runs_on: str
    steps: List[GitHubStep] = field(default_factory=list)
    needs: List[str] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)
    strategy: Optional[Dict[str, Any]] = None
    container: Optional[Dict[str, Any]] = None
    services: Optional[Dict[str, Any]] = None
    timeout_minutes: Optional[int] = None
    if_: Optional[str] = None


@dataclass
class GitHubWorkflow:
    """Complete GitHub Actions workflow."""
    name: str
    on: Dict[str, Any] = field(default_factory=dict)
    env: Dict[str, str] = field(default_factory=dict)
    concurrency: Optional[Dict[str, Any]] = None
    jobs: Dict[str, GitHubJob] = field(default_factory=dict)
    
    def add_job(self, job_id: str, job: GitHubJob) -> None:
        """Add a job to the workflow."""
        self.jobs[job_id] = job
