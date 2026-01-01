# 🚀 GitLab CI to GitHub Actions Converter

> **Convert your GitLab CI/CD pipelines to GitHub Actions workflows with interactive visualization and dependency analysis**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)](https://flask.palletsprojects.com/)

## ✨ Features

- 📊 **Interactive Dependency Graphs** - Visualize job dependencies with D3.js
- 🔄 **Automatic Conversion** - Convert GitLab CI to GitHub Actions workflows
- 🔐 **Security Analysis** - Identify and categorize variables and secrets
- 📈 **Pipeline Analytics** - Calculate critical paths and detect circular dependencies
- 🎨 **Modern UI** - Clean, responsive interface with drag-drop file upload
- 💾 **Export Ready** - Download or copy converted workflows instantly
- 🐳 **Docker Support** - Easy deployment with Docker and Docker Compose
- ☁️ **Cloud Ready** - Deploy to GitHub Pages, Heroku, AWS, or any cloud platform

## 🎯 Quick Start

### Local Development (5 minutes)

```bash
# Clone repository
git clone https://github.com/yourusername/g2g-converter.git
cd g2g-converter

# Automatic setup (Linux/Mac)
bash setup.sh

# Or manual setup
cd backend && python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run.py

# In another terminal
cd frontend && python -m http.server 8000
```

Then open **http://localhost:8000** in your browser!

### Docker Setup

```bash
docker-compose up
```

Visit http://localhost:8000 and http://localhost:5000/api/health

### GitHub Pages Deployment

1. Push to GitHub
2. Enable Pages in Settings → Pages
3. Auto-deploys to `https://yourusername.github.io/g2g-converter`

## 📖 Documentation

| Document | Purpose |
|----------|---------|
| [README.md](README.md) | Main documentation and feature overview |
| [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) | Executive summary and deliverables |
| [SETUP.md](SETUP.md) | Detailed setup and usage guide |
| [API.md](API.md) | Complete API reference |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Technical architecture and design |
| [FILE_INDEX.md](FILE_INDEX.md) | Complete file structure reference |
| [AI_PROMPT.md](AI_PROMPT.md) | System prompt for AI-assisted development |

## 🏗️ Project Structure

```
g2g-converter/
├── backend/                    # Python Flask API
│   ├── app/
│   │   ├── models/            # Data models
│   │   ├── parsers/           # YAML parsing
│   │   ├── converters/        # Conversion engines
│   │   └── main.py            # Flask API
│   ├── tests/                 # Test suite
│   ├── run.py                 # Entry point
│   └── requirements.txt       # Dependencies
│
├── frontend/                   # Web UI
│   ├── index.html            # Main page
│   ├── src/
│   │   ├── js/               # JavaScript modules
│   │   └── css/              # Styling
│   └── examples/             # Example YAML files
│
├── .github/workflows/        # CI/CD pipelines
├── docker-compose.yml        # Local development
└── [Documentation files]     # Setup, API, Architecture guides
```

## 🔧 Technology Stack

**Backend:**
- Python 3.9+ with Flask
- PyYAML for parsing
- NetworkX for graph algorithms
- Pydantic for validation

**Frontend:**
- HTML5, CSS3, Vanilla JavaScript
- D3.js v7 for visualization
- Highlight.js for syntax highlighting

**Deployment:**
- Docker & Docker Compose
- GitHub Actions for CI/CD
- GitHub Pages for frontend hosting

## 🎨 User Interface

### Left Panel
- Drag-drop file upload
- YAML text editor
- Real-time validation

### Center Panel
- Interactive D3.js dependency graph
- Zoom, pan, and node highlighting
- Color-coded by stage
- Edge types: needs, artifacts, dependencies

### Right Panel
- Syntax-highlighted workflow YAML
- Copy to clipboard
- Download as file
- Real-time updates

### Bottom Panel
- Variables with metadata
- Secrets listing
- Job references
- Pipeline metrics

## 📊 Supported Features

### ✅ Fully Supported
- Stages and sequential job execution
- Job dependencies (needs, dependencies)
- Variables (global and job-level)
- Secrets (masked, protected)
- Docker images and language setup
- Artifacts and caching
- Before/after scripts
- Conditions and when clauses
- Timeout and retry policies

### ⚠️ Partial Support
- Complex GitLab rules → basic if statements
- Manual jobs → conditional execution
- Scheduled pipelines → workflow_dispatch

### ❌ Not Yet Supported
- GitLab-specific runners
- Advanced CI/CD variables
- Template inheritance

## 🔐 Security

- ✅ YAML syntax validation
- ✅ Identifies masked/protected variables
- ✅ No sensitive data stored
- ✅ In-memory processing only
- ✅ CORS configurable for production
- ✅ Sanitized job IDs for GitHub compatibility

## 📈 Pipeline Analytics

Automatically generates:
- Total job/stage count
- Variable and secret inventory
- Dependency depth analysis
- Critical path calculation
- Circular dependency detection
- Pipeline complexity metrics

## 🧪 Testing

```bash
cd backend
pip install pytest pytest-cov
pytest tests/ --cov=app
```

## 🚀 Deployment

### GitHub Pages (Frontend)
```bash
git push origin main
# Auto-deploys to GitHub Pages
```

### Backend Deployment Options

**Option 1: Heroku**
```bash
heroku login
heroku create your-app-name
git push heroku main
```

**Option 2: Docker**
```bash
docker build -t g2g-converter-api .
docker run -p 5000:5000 g2g-converter-api
```

**Option 3: AWS/GCP/Azure**
- Use Dockerfile for containerization
- Deploy to Cloud Run, App Engine, or ECS

## 📚 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/health` | GET | Health check |
| `/api/validate` | POST | Validate YAML |
| `/api/analyze` | POST | Generate dependency graph |
| `/api/convert` | POST | Convert to GitHub Actions |
| `/api/upload` | POST | Upload and analyze file |

See [API.md](API.md) for complete documentation with examples.

## 🎓 Learning Path

1. Read [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) for overview
2. Follow [SETUP.md](SETUP.md) for installation
3. Review example files in `frontend/examples/`
4. Explore [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
5. Check [API.md](API.md) for endpoint documentation

## 💡 Example Usage

### Convert Simple Pipeline
```yaml
# Input: .gitlab-ci.yaml
stages:
  - build
  - test

build:
  stage: build
  image: python:3.11
  script:
    - pip install -r requirements.txt

test:
  stage: test
  needs:
    - build
  script:
    - pytest
```

### Output: GitHub Actions Workflow
```yaml
name: CI/CD Pipeline
on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt

  test:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - run: pytest
```

## 🤝 Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add/update tests
5. Submit a pull request

## 📝 License

MIT License - See LICENSE file for details

## 🎉 What's Included

✅ **Complete Source Code**
- Python backend with Flask API
- Responsive HTML/CSS/JS frontend
- Modular, well-documented code

✅ **Comprehensive Documentation**
- Setup guide with Docker support
- API reference with examples
- Architecture and design patterns
- Project structure overview

✅ **Production Ready**
- Unit and integration tests
- GitHub Actions CI/CD workflows
- Docker containerization
- Error handling and validation

✅ **Deployment Ready**
- GitHub Pages configuration
- Docker Compose for development
- Cloud deployment templates
- Environment variable support

✅ **Examples & Templates**
- Simple and complex pipeline examples
- Setup scripts for Linux/Mac/Windows
- Configuration templates

## 🚀 Get Started Now!

```bash
git clone https://github.com/yourusername/g2g-converter.git
cd g2g-converter
bash setup.sh
# or: docker-compose up
```

Open http://localhost:8000 and start converting!

---

**Built with ❤️ for CI/CD engineers and DevOps professionals**

For support, questions, or feedback:
- 📖 Check the documentation
- 🐛 Open an issue
- 💬 Share your feedback

---

### Quick Links
- [🏠 Home](.)
- [📚 Full Documentation](README.md)
- [🚀 Setup Guide](SETUP.md)
- [📖 API Reference](API.md)
- [🏗️ Architecture](ARCHITECTURE.md)
- [📂 File Index](FILE_INDEX.md)
- [🤖 AI Prompt](AI_PROMPT.md)
