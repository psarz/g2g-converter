# GitLab to GitHub CI/CD Converter - Setup and Usage Guide

## Quick Start

### 1. Local Development Setup

```bash
# Clone repository
git clone https://github.com/yourusername/g2g-converter.git
cd g2g-converter

# Setup backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py

# In another terminal, setup frontend
cd frontend
python -m http.server 8000
```

Then open http://localhost:8000 in your browser.

### 2. Docker Setup

```bash
docker-compose up
```

Access:
- Frontend: http://localhost:8000
- API: http://localhost:5000

### 3. GitHub Pages Deployment

1. Push code to GitHub
2. Enable GitHub Pages in Settings → Pages
3. Select `main` branch and `/root` folder
4. Site will be published to: `https://yourusername.github.io/g2g-converter`

## API Usage Examples

### Convert GitLab CI to GitHub Actions

```python
import requests
import json

yaml_content = """
stages:
  - build
  - test

build:
  stage: build
  image: python:3.11
  script:
    - pip install -r requirements.txt
    - python setup.py build

test:
  stage: test
  needs:
    - build
  script:
    - pytest
"""

response = requests.post(
    'http://localhost:5000/api/convert',
    json={'yaml_content': yaml_content}
)

result = response.json()
print("GitHub Actions Workflow:")
print(result['github_workflow'])
```

### Analyze Pipeline Dependencies

```python
response = requests.post(
    'http://localhost:5000/api/analyze',
    json={'yaml_content': yaml_content}
)

result = response.json()
print("Jobs:", [node['label'] for node in result['graph']['nodes']])
print("Metrics:", result['metrics'])
print("Cycles:", result['cycles'])
```

## Workflow Examples

### Simple Node.js Pipeline

```yaml
# .gitlab-ci.yaml
stages:
  - build
  - test

variables:
  NODE_VERSION: "18"

build:
  stage: build
  image: node:${NODE_VERSION}
  script:
    - npm ci
    - npm run build
  artifacts:
    paths:
      - dist/

test:
  stage: test
  image: node:${NODE_VERSION}
  needs:
    - build
  script:
    - npm test
```

**Converts to:**

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "18"
      - run: npm ci && npm run build
      - uses: actions/upload-artifact@v3
        with:
          name: dist
          path: dist/

  test:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "18"
      - run: npm test
```

### Python Project with Multiple Stages

```yaml
# .gitlab-ci.yaml
stages:
  - lint
  - test
  - build
  - deploy

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

cache:
  paths:
    - .cache/pip
    - venv/

lint:
  stage: lint
  image: python:3.11
  script:
    - pip install flake8 black
    - black --check .
    - flake8 src/

test:
  stage: test
  image: python:3.11
  script:
    - pip install -r requirements-test.txt
    - pytest --cov=src
  coverage: '/TOTAL.*\s+(\d+%)$/'

build:
  stage: build
  needs:
    - lint
    - test
  image: python:3.11
  script:
    - pip install build
    - python -m build
  artifacts:
    paths:
      - dist/

deploy:
  stage: deploy
  image: python:3.11
  environment:
    name: production
  script:
    - pip install twine
    - twine upload dist/*
  only:
    - tags
```

## Troubleshooting

### API Connection Issues

If you get "API not available" warning:

1. Ensure backend is running: `python backend/run.py`
2. Check port 5000 is not in use
3. Update API URL in `frontend/src/js/api-client.js` if using different port

### File Upload Not Working

1. Check browser console for errors (F12)
2. Ensure file is valid YAML
3. File size < 16MB

### Graph Not Rendering

1. Check if jobs are properly formatted
2. Ensure stages are defined
3. Look for circular dependencies in Metrics tab

## Performance Tips

1. **Large Pipelines**: Files with 100+ jobs may take a few seconds
2. **Browser**: Use Chrome/Firefox for best performance
3. **API**: Run on same machine for local development

## Advanced Configuration

### Custom API URL

Edit `frontend/src/js/api-client.js`:

```javascript
const apiClient = new APIClient('https://your-api-domain.com/api');
```

### Environment Variables

Create `backend/.env`:

```env
FLASK_ENV=production
CORS_ORIGINS=https://your-domain.com
MAX_FILE_SIZE=33554432
```

### HTTPS for Deployment

```nginx
# nginx.conf
server {
    listen 443 ssl;
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location /api {
        proxy_pass http://backend:5000;
    }
    
    location / {
        root /usr/share/nginx/html;
        index index.html;
    }
}
```

## CI/CD Pipeline for This Project

The project itself uses GitHub Actions:

- **Tests**: Runs on push to main/develop
- **Deploy Pages**: Automatically deploys frontend on push to main
- **Deploy API**: Builds Docker image (requires manual setup)

## Contributing

```bash
# Create feature branch
git checkout -b feature/your-feature

# Make changes and test
cd backend && pytest tests/

# Commit and push
git commit -m "Add feature"
git push origin feature/your-feature
```

## Support Resources

- Check [README.md](../README.md) for detailed documentation
- See [examples/](../frontend/examples/) for sample pipelines
- Review [test files](../backend/tests/) for API usage patterns

## Next Steps

1. Try converting your own `.gitlab-ci.yaml`
2. Explore the dependency graph visualization
3. Download generated GitHub workflow
4. Adjust and use in your GitHub repositories
4. Consider contributing improvements back!
