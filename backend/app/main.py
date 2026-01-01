"""
Flask REST API for GitLab CI to GitHub Actions converter.
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import yaml
import os
import logging
from typing import Dict, Any

from app.parsers.gitlab_parser import GitLabParser
from app.converters.gitlab_to_github import GitLabToGitHubConverter
from app.converters.graph_builder import DependencyGraphBuilder

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = '/tmp'
ALLOWED_EXTENSIONS = {'yml', 'yaml'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB


def allowed_file(filename: str) -> bool:
    """Check if file is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'version': '1.0.0'}), 200


@app.route('/api/convert', methods=['POST'])
def convert_gitlab_to_github():
    """
    Convert GitLab CI YAML to GitHub Actions workflow.
    
    Expected JSON:
    {
        "yaml_content": "...",  # GitLab CI YAML content
        "workflow_name": "..."  # Optional workflow name
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'yaml_content' not in data:
            return jsonify({'error': 'Missing yaml_content'}), 400
        
        yaml_content = data['yaml_content']
        
        # Parse GitLab CI
        parser = GitLabParser()
        gitlab_config = parser.parse(yaml_content)
        
        # Convert to GitHub Actions
        converter = GitLabToGitHubConverter()
        github_workflow = converter.convert(gitlab_config)
        
        # Generate YAML
        github_yaml = converter.to_yaml()
        
        return jsonify({
            'success': True,
            'github_workflow': github_yaml,
            'gitlab_config': {
                'stages': gitlab_config.stages,
                'jobs': [
                    {
                        'name': job.name,
                        'stage': job.stage,
                        'image': job.image,
                        'allow_failure': job.allow_failure,
                        'when': job.when,
                        'dependencies': job.dependencies,
                        'needs': job.needs
                    }
                    for job in gitlab_config.jobs
                ],
                'variables': [
                    {'name': var.name, 'value': var.value, 'protected': var.protected, 'masked': var.masked}
                    for var in gitlab_config.variables
                ],
                'secrets': [
                    {'name': sec.name, 'type': sec.type, 'description': sec.description}
                    for sec in gitlab_config.secrets
                ]
            }
        }), 200
    
    except ValueError as e:
        return jsonify({'error': f'Validation error: {str(e)}'}), 400
    except Exception as e:
        logger.error(f"Conversion error: {str(e)}")
        return jsonify({'error': f'Conversion failed: {str(e)}'}), 500


@app.route('/api/analyze', methods=['POST'])
def analyze_gitlab_ci():
    """
    Analyze GitLab CI configuration and generate dependency graph.
    
    Expected JSON:
    {
        "yaml_content": "..."  # GitLab CI YAML content
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'yaml_content' not in data:
            return jsonify({'error': 'Missing yaml_content'}), 400
        
        yaml_content = data['yaml_content']
        
        # Parse GitLab CI
        parser = GitLabParser()
        gitlab_config = parser.parse(yaml_content)
        
        # Build dependency graph
        graph_builder = DependencyGraphBuilder(gitlab_config)
        dependency_graph = graph_builder.build()
        
        # Detect circular dependencies
        cycles = graph_builder.detect_circular_dependencies()
        
        # Get critical path
        critical_path = graph_builder.get_critical_path()
        
        # Get metrics
        metrics = graph_builder.get_graph_metrics()
        
        # Extract references
        job_references = parser.get_job_references()
        
        return jsonify({
            'success': True,
            'graph': dependency_graph.to_dict(),
            'metrics': metrics,
            'cycles': cycles,
            'critical_path': critical_path,
            'job_references': job_references,
            'variables': parser.extract_variables(),
            'secrets': parser.extract_secrets()
        }), 200
    
    except ValueError as e:
        return jsonify({'error': f'Analysis error: {str(e)}'}), 400
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload and analyze GitLab CI YAML file."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Only .yml and .yaml files allowed'}), 400
        
        # Read file content
        yaml_content = file.read().decode('utf-8')
        
        # Perform analysis and conversion
        parser = GitLabParser()
        gitlab_config = parser.parse(yaml_content)
        
        converter = GitLabToGitHubConverter()
        github_workflow = converter.convert(gitlab_config)
        
        graph_builder = DependencyGraphBuilder(gitlab_config)
        dependency_graph = graph_builder.build()
        
        return jsonify({
            'success': True,
            'filename': secure_filename(file.filename),
            'gitlab_config': {
                'stages': gitlab_config.stages,
                'jobs_count': len(gitlab_config.jobs),
                'variables_count': len(gitlab_config.variables),
                'secrets_count': len(gitlab_config.secrets)
            },
            'graph': dependency_graph.to_dict(),
            'github_workflow': converter.to_yaml(),
            'metrics': graph_builder.get_graph_metrics()
        }), 200
    
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500


@app.route('/api/validate', methods=['POST'])
def validate_yaml():
    """Validate GitLab CI YAML syntax."""
    try:
        data = request.get_json()
        
        if not data or 'yaml_content' not in data:
            return jsonify({'error': 'Missing yaml_content'}), 400
        
        yaml_content = data['yaml_content']
        
        try:
            parsed = yaml.safe_load(yaml_content)
            return jsonify({
                'success': True,
                'valid': True,
                'message': 'YAML is valid'
            }), 200
        except yaml.YAMLError as e:
            return jsonify({
                'success': True,
                'valid': False,
                'error': str(e)
            }), 200
    
    except Exception as e:
        return jsonify({'error': f'Validation failed: {str(e)}'}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
