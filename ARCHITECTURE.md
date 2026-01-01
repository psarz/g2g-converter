# Architecture and Design

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Frontend (Static HTML/CSS/JS)                │
│                   Hosted on GitHub Pages                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ • YAML Editor/Upload                                     │  │
│  │ • D3.js Dependency Graph Visualization                   │  │
│  │ • Variables/Secrets/Metrics Display                      │  │
│  │ • GitHub Workflow Viewer                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                            ↓ (HTTP)
┌─────────────────────────────────────────────────────────────────┐
│                Backend API (Flask + Python)                      │
│              Deployed on Heroku/AWS/DigitalOcean                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ REST Endpoints:                                          │  │
│  │ • POST /api/validate - Validate YAML                    │  │
│  │ • POST /api/analyze - Generate dependency graph         │  │
│  │ • POST /api/convert - Convert to GitHub Actions         │  │
│  │ • POST /api/upload - File upload + analysis             │  │
│  │ • GET /api/health - Health check                        │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Processing Modules                            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Parsers:                                                │   │
│  │ • GitLabParser - YAML parsing, variable extraction     │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Converters:                                             │   │
│  │ • GitLabToGitHubConverter - Configuration translation  │   │
│  │ • DependencyGraphBuilder - Graph generation            │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Models:                                                 │   │
│  │ • GitLabConfig - Parsed CI configuration               │   │
│  │ • GitHubWorkflow - Target workflow structure           │   │
│  │ • DependencyGraph - Visualization data                 │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Component Architecture

### Frontend Components

```
index.html
├── Header (Title, Stats)
├── Left Panel
│   ├── File Upload Section
│   ├── YAML Editor
│   └── Validation Messages
├── Center Panel
│   ├── D3.js Graph Visualization
│   └── Job Details View
├── Right Panel
│   └── GitHub Workflow Output
└── Metadata Panel
    ├── Variables Tab
    ├── Secrets Tab
    ├── References Tab
    └── Metrics Tab
```

**Key JavaScript Files:**

- `api-client.js` - HTTP communication with backend
- `graph-renderer.js` - D3.js visualization logic
- `ui-controller.js` - UI state and event handling
- `app.js` - Application initialization

### Backend Components

```
Backend
├── Parsers
│   └── GitLabParser
│       ├── Parse stages
│       ├── Extract variables/secrets
│       ├── Parse jobs and dependencies
│       └── Handle GitLab-specific features
├── Converters
│   ├── GitLabToGitHubConverter
│   │   ├── Convert triggers (on conditions)
│   │   ├── Convert jobs to GitHub jobs
│   │   ├── Generate steps from scripts
│   │   └── Output YAML
│   └── DependencyGraphBuilder
│       ├── Build nodes from jobs
│       ├── Create edges from dependencies
│       ├── Detect cycles
│       └── Calculate metrics
├── Models
│   ├── GitLabConfig
│   ├── GitHubWorkflow
│   └── DependencyGraph
└── Flask API
    ├── Routes
    ├── Request validation
    └── Response formatting
```

## Data Flow

### Conversion Flow

```
1. User Input (YAML)
   ↓
2. Validation (YAML syntax check)
   ↓
3. Parsing (GitLabParser)
   ├── Extract stages, jobs, variables, secrets
   ├── Parse dependencies and conditions
   └── Build GitLabConfig object
   ↓
4. Conversion (GitLabToGitHubConverter)
   ├── Determine runners from tags/image
   ├── Convert triggers and conditions
   ├── Generate steps from scripts
   └── Build GitHub workflow YAML
   ↓
5. Output
   ├── Display in editor
   ├── Enable download/copy
   └── Return to frontend
```

### Analysis Flow

```
1. Parsed GitLabConfig
   ↓
2. Graph Building (DependencyGraphBuilder)
   ├── Create nodes from jobs
   ├── Create edges from dependencies
   ├── Extract variables and secrets
   └── Build DependencyGraph
   ↓
3. Analysis
   ├── Detect cycles (DFS)
   ├── Calculate critical path
   ├── Compute metrics
   └── Extract job references
   ↓
4. Visualization Data
   ├── Nodes with properties
   ├── Edges with types
   ├── Variables metadata
   └── Pipeline metrics
```

## Key Algorithms

### Circular Dependency Detection

```python
def detect_circular_dependencies():
    visited = set()
    rec_stack = set()
    
    def dfs(node):
        visited.add(node)
        rec_stack.add(node)
        
        for neighbor in graph.neighbors(node):
            if neighbor not in visited:
                dfs(neighbor)
            elif neighbor in rec_stack:
                return cycle_found()
        
        rec_stack.remove(node)
    
    for node in graph.nodes:
        if node not in visited:
            dfs(node)
```

### Critical Path Calculation

```python
def get_critical_path():
    # Find longest dependency chain
    paths = []
    
    for leaf in leaf_nodes:
        path = find_longest_path_to_root(leaf)
        paths.append(path)
    
    return max(paths, key=len)
```

### D3.js Force-Directed Layout

```javascript
simulation = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(edges)
        .id(d => d.id)
        .distance(100))
    .force('charge', d3.forceManyBody().strength(-300))
    .force('center', d3.forceCenter(width/2, height/2))
    .force('collision', d3.forceCollide().radius(40))
```

## Conversion Mapping

### GitLab CI → GitHub Actions

| GitLab Feature | GitHub Actions Equivalent |
|---|---|
| `stages` | Sequential job execution |
| `needs` | `needs` keyword |
| `dependencies` | `needs` with artifacts |
| `variables` | `env` or secrets |
| `before_script` | First step |
| `script` | Main steps |
| `after_script` | Final step |
| `artifacts` | `actions/upload-artifact` |
| `cache` | `actions/cache` |
| `image` | `container.image` |
| `only/except` | `if` condition |
| `when: manual` | Manual workflow dispatch |
| Tags | `runs-on` mapping |

## Security Considerations

1. **Secret Handling**
   - Masked variables → GitHub Actions secrets
   - Protected variables → Protected environments
   - No secrets logged in output

2. **Input Validation**
   - YAML parsing with error handling
   - File size limits (16MB)
   - Script injection prevention

3. **CORS Configuration**
   - Production: Restrict origins
   - Development: Allow localhost

4. **Sensitive Data**
   - Don't store uploaded files
   - Process in-memory only
   - Clear caches after processing

## Performance Optimization

1. **Frontend**
   - D3.js rendering optimized for 100+ nodes
   - Incremental graph updates
   - Debounced event handlers

2. **Backend**
   - Streaming YAML parsing
   - In-memory processing
   - Minimal database queries

3. **Deployment**
   - Frontend: CDN with caching
   - API: Auto-scaling containers
   - Database: Redis caching (optional)

## Error Handling

```
User Error → Validation → Clear Message
       ↓
Parser Error → Try/Catch → Detailed Error
       ↓
Conversion Error → Fallback → Partial Output
       ↓
API Error → HTTP Status Code → Error Response
```

## Testing Strategy

1. **Unit Tests**
   - Parser tests with various YAML formats
   - Converter mapping tests
   - Graph builder algorithm tests

2. **Integration Tests**
   - API endpoint tests
   - End-to-end flow tests

3. **E2E Tests**
   - Frontend interaction tests
   - File upload scenarios
   - Graph visualization tests

## Scalability Considerations

### Horizontal Scaling
- Stateless API servers
- Load balancer for multiple instances
- Separate frontend CDN

### Vertical Scaling
- Caching layer (Redis)
- Database (optional)
- Worker queue for async processing

### Limits
- Current: Single-threaded processing
- Bottleneck: YAML parsing for very large files
- Solution: Stream processing for 100MB+ files
