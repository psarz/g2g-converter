"""
Converter from GitLab CI to GitHub Actions workflows.
"""
import re
from typing import Dict, List, Any, Optional
from app.models.gitlab_config import GitLabConfig, Job
from app.models.github_workflow import (
    GitHubWorkflow, GitHubJob, GitHubStep
)
from jinja2 import Template


class GitLabToGitHubConverter:
    """Converts GitLab CI configuration to GitHub Actions workflows."""
    
    # Mapping of GitLab runners to GitHub runners
    RUNNER_MAPPING = {
        'linux': 'ubuntu-latest',
        'linux-docker': 'ubuntu-latest',
        'windows': 'windows-latest',
        'macos': 'macos-latest',
        'docker': 'ubuntu-latest',
    }
    
    # Mapping of GitLab images to GitHub actions/setup
    IMAGE_SETUP_MAPPING = {
        'python': ('setup-python', {'python-version': '3.11'}),
        'node': ('setup-node', {'node-version': '18'}),
        'ruby': ('setup-ruby', {'ruby-version': '3.2'}),
        'go': ('setup-go', {'go-version': '1.21'}),
        'java': ('setup-java', {'java-version': '17'}),
    }
    
    def __init__(self):
        """Initialize converter."""
        self.gitlab_config: Optional[GitLabConfig] = None
        self.github_workflow: Optional[GitHubWorkflow] = None
    
    def convert(self, gitlab_config: GitLabConfig) -> GitHubWorkflow:
        """
        Convert GitLab CI config to GitHub Actions workflow.
        
        Args:
            gitlab_config: Parsed GitLab CI configuration
            
        Returns:
            GitHub Actions workflow configuration
        """
        self.gitlab_config = gitlab_config
        
        workflow_name = self._extract_workflow_name()
        self.github_workflow = GitHubWorkflow(
            name=workflow_name,
            on=self._convert_triggers(),
            env=self._convert_global_variables()
        )
        
        # Convert jobs
        for job in gitlab_config.jobs:
            github_job = self._convert_job(job)
            if github_job:
                job_id = self._sanitize_job_id(job.name)
                self.github_workflow.add_job(job_id, github_job)
        
        return self.github_workflow
    
    def _extract_workflow_name(self) -> str:
        """Extract workflow name from GitLab config."""
        if self.gitlab_config.workflow:
            return self.gitlab_config.workflow.get('name', 'CI/CD Pipeline')
        return 'CI/CD Pipeline'
    
    def _convert_triggers(self) -> Dict[str, Any]:
        """Convert GitLab CI triggers to GitHub Actions triggers."""
        triggers = {}
        
        workflow = self.gitlab_config.workflow or {}
        rules = workflow.get('rules', [])
        
        # Default to push and pull request
        if not rules:
            triggers['push'] = {'branches': ['main', 'develop', '**']}
            triggers['pull_request'] = {'branches': ['main', 'develop']}
        else:
            # Parse workflow rules
            for rule in rules:
                if isinstance(rule, dict):
                    if rule.get('if') == '$CI_PIPELINE_SOURCE == "push"':
                        triggers['push'] = {'branches': ['main', '**']}
                    elif rule.get('if') == '$CI_PIPELINE_SOURCE == "pull_request"':
                        triggers['pull_request'] = {'branches': ['main']}
                    elif rule.get('if') == '$CI_PIPELINE_SOURCE == "schedule"':
                        triggers['schedule'] = [{'cron': '0 0 * * *'}]
        
        return triggers or {'push': {'branches': ['main']}, 'pull_request': {}}
    
    def _convert_global_variables(self) -> Dict[str, str]:
        """Convert global variables to GitHub Actions format."""
        env_vars = {}
        for var in self.gitlab_config.variables:
            if not var.masked and not var.protected:
                env_vars[var.name] = var.value
        return env_vars
    
    def _convert_job(self, gitlab_job: Job) -> Optional[GitHubJob]:
        """Convert individual GitLab job to GitHub job."""
        try:
            # Determine runner
            runner = self._determine_runner(gitlab_job)
            
            # Create GitHub job
            github_job = GitHubJob(
                name=gitlab_job.name,
                runs_on=runner,
                needs=gitlab_job.needs or gitlab_job.dependencies,
                env=gitlab_job.variables or {},
                timeout_minutes=self._parse_timeout(gitlab_job.timeout) if gitlab_job.timeout else None,
                if_=self._convert_job_rules(gitlab_job)
            )
            
            # Add steps
            github_job.steps = self._convert_steps(gitlab_job)
            
            # Handle container if image is specified
            if gitlab_job.image:
                github_job.container = {
                    'image': gitlab_job.image,
                    'options': '--cpus 1 --memory 2gb'
                }
            
            return github_job
        except Exception as e:
            print(f"Warning: Failed to convert job '{gitlab_job.name}': {e}")
            return None
    
    def _determine_runner(self, job: Job) -> str:
        """Determine GitHub runner from GitLab job configuration."""
        # Check tags
        for tag in job.tags:
            if tag.lower() in self.RUNNER_MAPPING:
                return self.RUNNER_MAPPING[tag.lower()]
        
        # Check image
        if job.image:
            for key, runner in self.RUNNER_MAPPING.items():
                if key in job.image.lower():
                    return runner
        
        # Default to ubuntu-latest
        return 'ubuntu-latest'
    
    def _convert_steps(self, job: Job) -> List[GitHubStep]:
        """Convert job script to GitHub Actions steps."""
        steps = []
        
        # Checkout step
        steps.append(GitHubStep(
            name='Checkout repository',
            uses='actions/checkout@v4'
        ))
        
        # Setup steps based on image
        setup_steps = self._generate_setup_steps(job.image)
        steps.extend(setup_steps)
        
        # Before script
        if job.before_script:
            steps.append(GitHubStep(
                name='Run before_script',
                run='\n'.join(job.before_script)
            ))
        
        # Main script
        if job.script:
            steps.append(GitHubStep(
                name=f'Run {job.name}',
                run='\n'.join(job.script),
                continue_on_error=job.allow_failure
            ))
        
        # After script
        if job.after_script:
            steps.append(GitHubStep(
                name='Run after_script',
                run='\n'.join(job.after_script),
                continue_on_error=True
            ))
        
        # Upload artifacts
        if job.artifacts:
            artifact_paths = job.artifacts.get('paths', [])
            if artifact_paths:
                steps.append(GitHubStep(
                    name='Upload artifacts',
                    uses='actions/upload-artifact@v3',
                    with_={
                        'name': f'{job.name}-artifacts',
                        'path': '\n'.join(artifact_paths),
                        'retention-days': job.artifacts.get('expire_in', '30')
                    }
                ))
        
        return steps
    
    def _generate_setup_steps(self, image: Optional[str]) -> List[GitHubStep]:
        """Generate setup action steps based on image."""
        steps = []
        
        if not image:
            return steps
        
        image_lower = image.lower()
        
        # Match image to setup actions
        for lang_key, (action, defaults) in self.IMAGE_SETUP_MAPPING.items():
            if lang_key in image_lower:
                with_params = self._extract_version_from_image(image, lang_key, defaults)
                steps.append(GitHubStep(
                    name=f'Setup {lang_key.capitalize()}',
                    uses=f'actions/{action}@v4',
                    with_=with_params
                ))
                break
        
        return steps
    
    def _extract_version_from_image(self, image: str, language: str, defaults: Dict) -> Dict[str, str]:
        """Extract version from image string."""
        # Try to extract version numbers
        pattern = r'(\d+\.\d+(?:\.\d+)?)'
        matches = re.findall(pattern, image)
        
        result = defaults.copy()
        if matches:
            version_key = list(defaults.keys())[0]
            result[version_key] = matches[-1]  # Use last matched version
        
        return result
    
    def _convert_job_rules(self, job: Job) -> Optional[str]:
        """Convert GitLab job rules to GitHub job conditions."""
        if job.rules:
            # Convert first applicable rule
            for rule in job.rules:
                if isinstance(rule, dict):
                    if_condition = rule.get('if')
                    if if_condition:
                        return self._convert_gitlab_condition(if_condition)
        
        # Handle only/except
        if job.only:
            return self._convert_only_except(job.only, include=True)
        elif job.except_on:
            return self._convert_only_except(job.except_on, include=False)
        
        if job.when == 'manual':
            return 'false'  # Manual jobs not directly supported
        elif job.when == 'delayed':
            return None  # Requires workflow dispatch
        
        return None
    
    def _convert_gitlab_condition(self, condition: str) -> str:
        """Convert GitLab CI condition to GitHub Actions condition."""
        # Common GitLab CI variable replacements
        replacements = {
            '$CI_COMMIT_BRANCH': 'github.ref_name',
            '$CI_COMMIT_REF_NAME': 'github.ref_name',
            '$CI_PIPELINE_SOURCE': 'github.event_name',
            '$CI_MERGE_REQUEST_IID': 'github.event.number',
            'push': 'push',
            'merge_request': 'pull_request',
            'main': "'main'",
            'master': "'master'",
        }
        
        result = condition
        for gitlab_var, github_var in replacements.items():
            result = result.replace(gitlab_var, github_var)
        
        return result
    
    def _convert_only_except(self, config: Dict, include: bool = True) -> Optional[str]:
        """Convert only/except to GitHub condition."""
        if isinstance(config, dict):
            branches = config.get('branches', [])
            if branches:
                branch_condition = ' || '.join([f"github.ref_name == '{b}'" for b in branches])
                return branch_condition if include else f'!({branch_condition})'
        return None
    
    @staticmethod
    def _parse_timeout(timeout_str: str) -> int:
        """Parse timeout string to minutes."""
        if not timeout_str:
            return 360
        
        # Handle formats like "1h", "30m", "3600s"
        timeout_str = timeout_str.lower().strip()
        
        if timeout_str.endswith('h'):
            return int(timeout_str[:-1]) * 60
        elif timeout_str.endswith('m'):
            return int(timeout_str[:-1])
        elif timeout_str.endswith('s'):
            return int(timeout_str[:-1]) // 60
        else:
            try:
                return int(timeout_str)
            except ValueError:
                return 360
    
    @staticmethod
    def _sanitize_job_id(job_name: str) -> str:
        """Sanitize job name to valid GitHub job ID."""
        # Replace invalid characters with underscores
        sanitized = re.sub(r'[^a-zA-Z0-9_-]', '_', job_name)
        return sanitized[:250]  # GitHub job ID max length
    
    def to_yaml(self) -> str:
        """Convert workflow to GitHub Actions YAML format."""
        if not self.github_workflow:
            raise ValueError("Workflow not converted yet")
        
        import yaml
        
        workflow_dict = {
            'name': self.github_workflow.name,
            'on': self.github_workflow.on,
        }
        
        if self.github_workflow.env:
            workflow_dict['env'] = self.github_workflow.env
        
        jobs = {}
        for job_id, job in self.github_workflow.jobs.items():
            job_dict = {
                'name': job.name,
                'runs-on': job.runs_on,
                'steps': []
            }
            
            if job.needs:
                job_dict['needs'] = job.needs
            
            if job.env:
                job_dict['env'] = job.env
            
            if job.timeout_minutes:
                job_dict['timeout-minutes'] = job.timeout_minutes
            
            if job.if_:
                job_dict['if'] = job.if_
            
            if job.container:
                job_dict['container'] = job.container
            
            # Convert steps
            for step in job.steps:
                step_dict = {}
                if step.name:
                    step_dict['name'] = step.name
                
                if step.uses:
                    step_dict['uses'] = step.uses
                    if step.with_:
                        step_dict['with'] = step.with_
                elif step.run:
                    step_dict['run'] = step.run
                
                if step.env:
                    step_dict['env'] = step.env
                
                if step.if_:
                    step_dict['if'] = step.if_
                
                if step.continue_on_error:
                    step_dict['continue-on-error'] = step.continue_on_error
                
                job_dict['steps'].append(step_dict)
            
            jobs[job_id] = job_dict
        
        workflow_dict['jobs'] = jobs
        
        return yaml.dump(workflow_dict, default_flow_style=False, sort_keys=False)
