"""
Data models for GitLab CI configuration parsing.
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class JobStatus(Enum):
    """Possible job statuses."""
    SUCCESS = "success"
    FAILURE = "failure"
    ALWAYS = "always"
    MANUAL = "manual"
    DELAYED = "delayed"


@dataclass
class Variable:
    """Represents a CI/CD variable."""
    name: str
    value: str
    protected: bool = False
    masked: bool = False
    expand: bool = True


@dataclass
class Secret:
    """Represents a secret or sensitive variable."""
    name: str
    type: str = "env"  # env, file, docker
    description: str = ""


@dataclass
class Dependency:
    """Represents a job dependency."""
    name: str
    artifacts: bool = True
    optional: bool = False


@dataclass
class JobScript:
    """Represents job script commands."""
    before_script: List[str] = field(default_factory=list)
    script: List[str] = field(default_factory=list)
    after_script: List[str] = field(default_factory=list)


@dataclass
class Job:
    """Represents a GitLab CI job."""
    name: str
    stage: str
    image: Optional[str] = None
    script: List[str] = field(default_factory=list)
    before_script: List[str] = field(default_factory=list)
    after_script: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    needs: List[str] = field(default_factory=list)
    variables: Dict[str, str] = field(default_factory=dict)
    artifacts: Optional[Dict[str, Any]] = None
    cache: Optional[Dict[str, Any]] = None
    retry: Optional[Dict[str, Any]] = None
    timeout: Optional[str] = None
    only: Optional[Dict[str, Any]] = None
    except_on: Optional[Dict[str, Any]] = None
    tags: List[str] = field(default_factory=list)
    allow_failure: bool = False
    when: str = "on_success"
    environment: Optional[str] = None
    rules: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class Stage:
    """Represents a CI stage."""
    name: str
    jobs: List[Job] = field(default_factory=list)


@dataclass
class GitLabConfig:
    """Complete GitLab CI configuration."""
    stages: List[str] = field(default_factory=list)
    variables: List[Variable] = field(default_factory=list)
    secrets: List[Secret] = field(default_factory=list)
    jobs: List[Job] = field(default_factory=list)
    image: Optional[str] = None
    before_script: List[str] = field(default_factory=list)
    after_script: List[str] = field(default_factory=list)
    cache: Optional[Dict[str, Any]] = None
    retry: Optional[Dict[str, Any]] = None
    timeout: Optional[str] = None
    workflow: Optional[Dict[str, Any]] = None
    include: List[str] = field(default_factory=list)
    default: Optional[Dict[str, Any]] = None
    
    def get_job_by_name(self, name: str) -> Optional[Job]:
        """Get a job by name."""
        for job in self.jobs:
            if job.name == name:
                return job
        return None
    
    def get_jobs_by_stage(self, stage: str) -> List[Job]:
        """Get all jobs in a specific stage."""
        return [job for job in self.jobs if job.stage == stage]
