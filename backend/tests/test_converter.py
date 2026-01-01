"""
Unit tests for GitLab CI Parser
"""
import pytest
from app.parsers.gitlab_parser import GitLabParser
from app.models.gitlab_config import GitLabConfig


class TestGitLabParser:
    
    def test_parse_basic_config(self):
        yaml_content = """
stages:
  - build
  - test

variables:
  APP_NAME: myapp

build_job:
  stage: build
  image: python:3.11
  script:
    - make build
"""
        parser = GitLabParser()
        config = parser.parse(yaml_content)
        
        assert isinstance(config, GitLabConfig)
        assert config.stages == ['build', 'test']
        assert len(config.jobs) == 1
        assert config.jobs[0].name == 'build_job'
        assert config.jobs[0].stage == 'build'
    
    def test_parse_variables(self):
        yaml_content = """
variables:
  GLOBAL_VAR: value1
  SECRET_VAR:
    value: secret_value
    protected: true
    masked: true
"""
        parser = GitLabParser()
        config = parser.parse(yaml_content)
        
        assert len(config.variables) == 2
        assert config.variables[0].name == 'GLOBAL_VAR'
        assert config.variables[1].protected == True
        assert config.variables[1].masked == True
    
    def test_parse_dependencies(self):
        yaml_content = """
stages:
  - build
  - test

build:
  stage: build
  script:
    - make build

test:
  stage: test
  dependencies:
    - build
  script:
    - make test
"""
        parser = GitLabParser()
        config = parser.parse(yaml_content)
        
        test_job = config.get_job_by_name('test')
        assert 'build' in test_job.dependencies
    
    def test_parse_invalid_yaml(self):
        yaml_content = "invalid: yaml: content:"
        parser = GitLabParser()
        
        with pytest.raises(ValueError):
            parser.parse(yaml_content)


class TestGraphBuilder:
    
    def test_graph_building(self):
        from app.converters.graph_builder import DependencyGraphBuilder
        
        yaml_content = """
stages:
  - build
  - test

build:
  stage: build
  script:
    - make build

test:
  stage: test
  needs:
    - build
  script:
    - make test
"""
        parser = GitLabParser()
        config = parser.parse(yaml_content)
        
        builder = DependencyGraphBuilder(config)
        graph = builder.build()
        
        assert len(graph.nodes) == 2
        assert len(graph.edges) > 0


class TestGitHubConverter:
    
    def test_convert_basic_job(self):
        from app.converters.gitlab_to_github import GitLabToGitHubConverter
        
        yaml_content = """
stages:
  - build

build:
  stage: build
  image: python:3.11
  script:
    - pip install -r requirements.txt
    - python setup.py build
"""
        parser = GitLabParser()
        gitlab_config = parser.parse(yaml_content)
        
        converter = GitLabToGitHubConverter()
        github_workflow = converter.convert(gitlab_config)
        
        assert github_workflow.name
        assert len(github_workflow.jobs) > 0
        
        yaml_output = converter.to_yaml()
        assert 'jobs:' in yaml_output
        assert 'steps:' in yaml_output
