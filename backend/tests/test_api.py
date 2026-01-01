"""
Integration tests for the Flask API
"""
import pytest
import json
from app.main import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_health_endpoint(client):
    response = client.get('/api/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'


def test_validate_yaml_valid(client):
    yaml_content = """
stages:
  - build
build:
  stage: build
  script:
    - echo "test"
"""
    response = client.post('/api/validate',
        json={'yaml_content': yaml_content},
        content_type='application/json'
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['valid'] == True


def test_validate_yaml_invalid(client):
    yaml_content = "invalid: yaml: content:"
    response = client.post('/api/validate',
        json={'yaml_content': yaml_content},
        content_type='application/json'
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['valid'] == False


def test_analyze_endpoint(client):
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
    response = client.post('/api/analyze',
        json={'yaml_content': yaml_content},
        content_type='application/json'
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    assert 'graph' in data
    assert 'metrics' in data


def test_convert_endpoint(client):
    yaml_content = """
stages:
  - build

build:
  stage: build
  image: python:3.11
  script:
    - pip install -r requirements.txt
"""
    response = client.post('/api/convert',
        json={'yaml_content': yaml_content},
        content_type='application/json'
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    assert 'github_workflow' in data


def test_missing_yaml_content(client):
    response = client.post('/api/convert',
        json={},
        content_type='application/json'
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
