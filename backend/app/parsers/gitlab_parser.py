"""
GitLab CI YAML parser.
Analyzes .gitlab-ci.yaml files and extracts configuration.
"""
import yaml
import re
from typing import Dict, List, Any, Optional
from app.models.gitlab_config import (
    GitLabConfig, Job, Variable, Secret, Stage
)


class GitLabParser:
    """Parser for GitLab CI configuration files."""
    
    RESERVED_KEYS = {
        'stages', 'variables', 'before_script', 'after_script',
        'cache', 'retry', 'timeout', 'image', 'default', 'include',
        'workflow'
    }
    
    def __init__(self):
        """Initialize the parser."""
        self.raw_config: Dict[str, Any] = {}
        self.config: GitLabConfig = GitLabConfig()
    
    def parse(self, yaml_content: str) -> GitLabConfig:
        """
        Parse GitLab CI YAML content.
        
        Args:
            yaml_content: String content of .gitlab-ci.yaml file
            
        Returns:
            GitLabConfig object with parsed configuration
        """
        try:
            self.raw_config = yaml.safe_load(yaml_content) or {}
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML format: {e}")
        
        self.config = GitLabConfig()
        
        # Parse stages
        self._parse_stages()
        
        # Parse global variables
        self._parse_variables()
        
        # Parse secrets (masked/protected variables)
        self._parse_secrets()
        
        # Parse default configuration
        self._parse_default()
        
        # Parse jobs
        self._parse_jobs()
        
        # Parse include and workflow
        self._parse_includes()
        self._parse_workflow()
        
        return self.config
    
    def _parse_stages(self) -> None:
        """Parse stages from configuration."""
        stages = self.raw_config.get('stages', [])
        self.config.stages = stages if isinstance(stages, list) else []
    
    def _parse_variables(self) -> None:
        """Parse global variables."""
        variables = self.raw_config.get('variables', {})
        if isinstance(variables, dict):
            for name, value in variables.items():
                if isinstance(value, dict):
                    var = Variable(
                        name=name,
                        value=str(value.get('value', '')),
                        protected=value.get('protected', False),
                        masked=value.get('masked', False),
                        expand=value.get('expand', True)
                    )
                else:
                    var = Variable(name=name, value=str(value))
                self.config.variables.append(var)
    
    def _parse_secrets(self) -> None:
        """Parse secrets (masked/protected variables)."""
        variables = self.raw_config.get('variables', {})
        if isinstance(variables, dict):
            for name, value in variables.items():
                if isinstance(value, dict):
                    if value.get('masked', False) or value.get('protected', False):
                        secret = Secret(
                            name=name,
                            type='env',
                            description=f"{'Masked' if value.get('masked') else 'Protected'} variable"
                        )
                        self.config.secrets.append(secret)
    
    def _parse_default(self) -> None:
        """Parse default job configuration."""
        default = self.raw_config.get('default', {})
        if isinstance(default, dict):
            self.config.before_script = default.get('before_script', [])
            self.config.after_script = default.get('after_script', [])
            self.config.cache = default.get('cache')
            self.config.retry = default.get('retry')
            self.config.timeout = default.get('timeout')
            self.config.image = default.get('image') or self.raw_config.get('image')
    
    def _parse_jobs(self) -> None:
        """Parse jobs from configuration."""
        for job_name, job_config in self.raw_config.items():
            if job_name in self.RESERVED_KEYS or job_name.startswith('.'):
                continue
            
            if isinstance(job_config, dict):
                job = self._parse_job(job_name, job_config)
                if job:
                    self.config.jobs.append(job)
    
    def _parse_job(self, name: str, config: Dict[str, Any]) -> Optional[Job]:
        """Parse individual job configuration."""
        try:
            job = Job(
                name=name,
                stage=config.get('stage', 'test'),
                image=config.get('image'),
                script=self._normalize_list(config.get('script', [])),
                before_script=self._normalize_list(config.get('before_script', [])),
                after_script=self._normalize_list(config.get('after_script', [])),
                dependencies=self._normalize_list(config.get('dependencies', [])),
                needs=self._parse_needs(config.get('needs', [])),
                variables=config.get('variables', {}),
                artifacts=config.get('artifacts'),
                cache=config.get('cache'),
                retry=config.get('retry'),
                timeout=config.get('timeout'),
                only=config.get('only'),
                except_on=config.get('except'),
                tags=self._normalize_list(config.get('tags', [])),
                allow_failure=config.get('allow_failure', False),
                when=config.get('when', 'on_success'),
                environment=config.get('environment'),
                rules=config.get('rules', [])
            )
            return job
        except Exception as e:
            print(f"Warning: Failed to parse job '{name}': {e}")
            return None
    
    def _parse_needs(self, needs: Any) -> List[str]:
        """Parse needs configuration (can be list or dict)."""
        if isinstance(needs, list):
            result = []
            for item in needs:
                if isinstance(item, str):
                    result.append(item)
                elif isinstance(item, dict):
                    result.append(item.get('job', ''))
            return result
        return []
    
    def _parse_includes(self) -> None:
        """Parse include directives."""
        includes = self.raw_config.get('include', [])
        if isinstance(includes, list):
            for inc in includes:
                if isinstance(inc, str):
                    self.config.include.append(inc)
                elif isinstance(inc, dict):
                    self.config.include.append(inc.get('local', ''))
        elif isinstance(includes, str):
            self.config.include.append(includes)
    
    def _parse_workflow(self) -> None:
        """Parse workflow configuration."""
        self.config.workflow = self.raw_config.get('workflow')
    
    @staticmethod
    def _normalize_list(value: Any) -> List[str]:
        """Normalize value to list of strings."""
        if isinstance(value, list):
            return [str(item) for item in value]
        elif isinstance(value, str):
            return [value]
        return []
    
    def get_job_references(self) -> Dict[str, List[str]]:
        """
        Get job dependencies and references.
        
        Returns:
            Dictionary mapping job names to their dependencies
        """
        references = {}
        for job in self.config.jobs:
            deps = set(job.dependencies + job.needs)
            references[job.name] = list(deps)
        return references
    
    def extract_variables(self) -> Dict[str, Any]:
        """Extract all variables including job-specific ones."""
        all_vars = {}
        
        # Global variables
        for var in self.config.variables:
            all_vars[var.name] = {
                'value': var.value,
                'protected': var.protected,
                'masked': var.masked,
                'scope': 'global'
            }
        
        # Job-specific variables
        for job in self.config.jobs:
            for name, value in job.variables.items():
                if name not in all_vars:
                    all_vars[name] = {
                        'value': value,
                        'protected': False,
                        'masked': False,
                        'scope': 'job'
                    }
        
        return all_vars
    
    def extract_secrets(self) -> List[Dict[str, Any]]:
        """Extract secrets and sensitive variables."""
        secrets = []
        for secret in self.config.secrets:
            secrets.append({
                'name': secret.name,
                'type': secret.type,
                'description': secret.description
            })
        return secrets
