/**
 * UI Controller
 * Manages user interface and interactions
 */

class UIController {
    constructor() {
        this.currentData = null;
        this.setupEventListeners();
    }

    setupEventListeners() {
        // File input
        document.getElementById('fileInput').addEventListener('change', (e) => this.handleFileSelect(e));
        
        // Upload label click
        document.querySelector('.upload-label').addEventListener('dragover', (e) => this.handleDragOver(e));
        document.querySelector('.upload-label').addEventListener('dragleave', (e) => this.handleDragLeave(e));
        document.querySelector('.upload-label').addEventListener('drop', (e) => this.handleDrop(e));

        // Change file button
        document.getElementById('changeFileBtn')?.addEventListener('click', () => {
            this.resetFileInput();
        });

        // Buttons
        document.getElementById('analyzeBtn').addEventListener('click', () => this.analyzeYAML());
        document.getElementById('clearBtn').addEventListener('click', () => this.clearEditor());
        document.getElementById('copyBtn').addEventListener('click', () => this.copyToClipboard());
        document.getElementById('downloadBtn').addEventListener('click', () => this.downloadWorkflow());

        // View toggle
        document.querySelectorAll('.toggle-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.toggleView(e.target.dataset.view));
        });

        // Metadata tabs
        document.querySelectorAll('.metadata-tab').forEach(tab => {
            tab.addEventListener('click', (e) => this.switchMetadataTab(e.target.dataset.tab));
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                this.analyzeYAML();
            }
        });
    }

    /**
     * Handle file selection
     */
    async handleFileSelect(event) {
        const file = event.target.files[0];
        if (!file) return;

        this.showLoading(true);

        try {
            // Read file content
            const content = await this.readFileContent(file);
            
            // Populate editor with file content
            document.getElementById('yamlEditor').value = content;
            this.showEditorSection();
            
            // Show file info
            this.displayFileInfo(file.name);
            
            // Show success message
            this.showMessage(`✓ File loaded: ${file.name}`, 'success');
            
            // Auto-analyze the file
            await this.analyzeYAML();
        } catch (error) {
            this.showMessage(`File read failed: ${error.message}`, 'error');
        } finally {
            this.showLoading(false);
        }
    }

    /**
     * Display file information
     */
    displayFileInfo(fileName) {
        document.getElementById('fileInfo').style.display = 'block';
        document.getElementById('fileName').textContent = fileName;
    }

    /**
     * Reset file input and UI
     */
    resetFileInput() {
        document.getElementById('fileInput').value = '';
        document.getElementById('fileInfo').style.display = 'none';
        document.getElementById('yamlEditor').value = '';
        document.getElementById('editorSection').style.display = 'none';
        this.clearResults();
    }

    /**
     * Read file content as text
     */
    readFileContent(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => {
                try {
                    const content = e.target.result;
                    resolve(content);
                } catch (err) {
                    reject(err);
                }
            };
            reader.onerror = (e) => {
                reject(new Error('Failed to read file'));
            };
            reader.readAsText(file);
        });
    }

    /**
     * Handle drag over
     */
    handleDragOver(event) {
        event.preventDefault();
        event.stopPropagation();
        document.querySelector('.upload-label').style.borderColor = 'var(--primary-color)';
        document.querySelector('.upload-label').style.backgroundColor = 'rgba(3, 102, 214, 0.3)';
    }

    /**
     * Handle drag leave
     */
    handleDragLeave(event) {
        event.preventDefault();
        event.stopPropagation();
        document.querySelector('.upload-label').style.borderColor = '';
        document.querySelector('.upload-label').style.backgroundColor = '';
    }

    /**
     * Handle drop
     */
    handleDrop(event) {
        event.preventDefault();
        event.stopPropagation();
        
        const files = event.dataTransfer.files;
        if (files.length > 0) {
            document.getElementById('fileInput').files = files;
            this.handleFileSelect({ target: { files } });
        }
    }

    /**
     * Show editor section
     */
    showEditorSection() {
        document.getElementById('editorSection').style.display = 'flex';
    }

    /**
     * Analyze YAML content
     */
    async analyzeYAML() {
        const yamlContent = document.getElementById('yamlEditor').value.trim();
        
        if (!yamlContent) {
            this.showMessage('Please enter or upload YAML content', 'warning');
            return;
        }

        this.showLoading(true);

        try {
            // First validate
            const validation = await apiClient.validateYAML(yamlContent);
            
            if (!validation.valid) {
                this.showMessage(`YAML validation failed: ${validation.error}`, 'error');
                this.showLoading(false);
                return;
            }

            // Then analyze
            const result = await apiClient.analyze(yamlContent);
            this.displayResults(result);
            
            // Also convert to GitHub Actions
            const conversion = await apiClient.convert(yamlContent);
            this.displayGitHubWorkflow(conversion.github_workflow);
            
            this.showMessage('Analysis completed successfully', 'success');
        } catch (error) {
            this.showMessage(`Analysis failed: ${error.message}`, 'error');
        } finally {
            this.showLoading(false);
        }
    }

    /**
     * Display analysis results
     */
    displayResults(data) {
        this.currentData = data;

        // Update header stats
        const stats = data.graph ? {
            jobs: data.graph.nodes.length,
            variables: Object.keys(data.graph.variables).length,
            secrets: data.graph.secrets.length
        } : (data.gitlab_config ? {
            jobs: data.gitlab_config.jobs_count,
            variables: data.gitlab_config.variables_count,
            secrets: data.gitlab_config.secrets_count
        } : {});

        document.getElementById('headerStats').style.display = 'flex';
        document.getElementById('jobCount').textContent = stats.jobs;
        document.getElementById('varCount').textContent = stats.variables;
        document.getElementById('secretCount').textContent = stats.secrets;

        // Show metadata panel
        document.getElementById('metadataPanel').style.display = 'flex';

        // Render graph
        if (data.graph) {
            graphRenderer.render(data.graph);
        }

        // Display variables
        this.displayVariables(data.variables);

        // Display secrets
        this.displaySecrets(data.secrets);

        // Display metrics
        if (data.metrics) {
            this.displayMetrics(data.metrics);
        }

        // Display job references
        if (data.job_references) {
            this.displayReferences(data.job_references);
        }
    }

    /**
     * Display GitHub workflow
     */
    displayGitHubWorkflow(workflowYaml) {
        const container = document.getElementById('outputContainer');
        
        const html = `
            <div class="yaml-output">
                <pre><code class="language-yaml">${this.escapeHtml(workflowYaml)}</code></pre>
            </div>
        `;

        container.innerHTML = html;
        document.getElementById('copyBtn').style.display = 'inline-block';
        document.getElementById('downloadBtn').style.display = 'inline-block';

        // Highlight syntax
        document.querySelectorAll('code').forEach(block => {
            hljs.highlightElement(block);
        });
    }

    /**
     * Display variables
     */
    displayVariables(variables) {
        const pane = document.getElementById('variablesPane');
        
        if (!variables || Object.keys(variables).length === 0) {
            pane.innerHTML = '<p style="color: var(--text-secondary);">No variables found</p>';
            return;
        }

        let html = '';
        for (const [name, data] of Object.entries(variables)) {
            html += `
                <div class="metadata-item">
                    <div class="metadata-item-name">${this.escapeHtml(name)}</div>
                    <div class="metadata-item-value">
                        Value: ${this.escapeHtml(String(data.value || '').substring(0, 100))}
                        ${data.scope ? `<span class="metadata-item-badge">${data.scope}</span>` : ''}
                        ${data.protected ? '<span class="metadata-item-badge protected">Protected</span>' : ''}
                        ${data.masked ? '<span class="metadata-item-badge masked">Masked</span>' : ''}
                    </div>
                </div>
            `;
        }

        pane.innerHTML = html;
    }

    /**
     * Display secrets
     */
    displaySecrets(secrets) {
        const pane = document.getElementById('secretsPane');
        
        if (!secrets || secrets.length === 0) {
            pane.innerHTML = '<p style="color: var(--text-secondary);">No secrets found</p>';
            return;
        }

        let html = '';
        secrets.forEach(secret => {
            html += `
                <div class="metadata-item">
                    <div class="metadata-item-name">${this.escapeHtml(secret.name)}</div>
                    <div class="metadata-item-value">
                        Type: ${this.escapeHtml(secret.type)}<br/>
                        ${secret.description ? `Description: ${this.escapeHtml(secret.description)}` : ''}
                    </div>
                </div>
            `;
        });

        pane.innerHTML = html;
    }

    /**
     * Display job references
     */
    displayReferences(references) {
        const pane = document.getElementById('referencesPane');
        
        let html = '';
        for (const [job, deps] of Object.entries(references)) {
            if (deps.length > 0) {
                html += `
                    <div class="metadata-item">
                        <div class="metadata-item-name">${this.escapeHtml(job)}</div>
                        <div class="metadata-item-value">
                            Depends on: ${deps.map(d => this.escapeHtml(d)).join(', ')}
                        </div>
                    </div>
                `;
            }
        }

        if (!html) {
            html = '<p style="color: var(--text-secondary);">No job references found</p>';
        }

        pane.innerHTML = html;
    }

    /**
     * Display metrics
     */
    displayMetrics(metrics) {
        const pane = document.getElementById('metricsPane');
        
        const html = `
            <div class="metadata-item">
                <div class="metadata-item-name">Pipeline Metrics</div>
                <div class="metadata-item-value">
                    Total Jobs: ${metrics.total_nodes}<br/>
                    Total Dependencies: ${metrics.total_edges}<br/>
                    Stages: ${metrics.total_stages}<br/>
                    Variables: ${metrics.total_variables}<br/>
                    Secrets: ${metrics.total_secrets}<br/>
                    ${metrics.cycles ? `Circular Dependencies: ${metrics.cycles}` : ''}<br/>
                    ${metrics.critical_path_length ? `Critical Path Length: ${metrics.critical_path_length}` : ''}<br/>
                    Avg Dependencies: ${(metrics.avg_job_dependencies || 0).toFixed(2)}
                </div>
            </div>
        `;

        pane.innerHTML = html;
    }

    /**
     * Toggle view between graph and details
     */
    toggleView(view) {
        document.querySelectorAll('.toggle-btn').forEach(btn => {
            btn.classList.remove('active');
        });

        document.querySelector(`[data-view="${view}"]`).classList.add('active');

        const graphContainer = document.getElementById('graphContainer');
        const detailsContainer = document.getElementById('detailsContainer');

        if (view === 'graph') {
            graphContainer.style.display = 'block';
            detailsContainer.style.display = 'none';
        } else {
            graphContainer.style.display = 'none';
            detailsContainer.style.display = 'block';
            this.displayDetails();
        }
    }

    /**
     * Display detailed job information
     */
    displayDetails() {
        if (!this.currentData || !this.currentData.graph) return;

        const detailsContent = document.querySelector('.details-content');
        let html = '';

        this.currentData.graph.nodes.forEach(node => {
            const deps = this.currentData.job_references[node.label] || [];
            html += `
                <div class="job-detail">
                    <div class="job-detail-title">${this.escapeHtml(node.label)}</div>
                    <div class="job-detail-item">
                        <span class="label">Stage:</span>
                        <span class="value">${this.escapeHtml(node.stage)}</span>
                    </div>
                    <div class="job-detail-item">
                        <span class="label">Type:</span>
                        <span class="value">${this.escapeHtml(node.type)}</span>
                    </div>
                    ${node.allowFailure ? `
                    <div class="job-detail-item">
                        <span class="label">Allow Failure:</span>
                        <span class="value">Yes</span>
                    </div>
                    ` : ''}
                    ${deps.length > 0 ? `
                    <div class="job-detail-item">
                        <span class="label">Dependencies:</span>
                        <span class="value">${deps.map(d => this.escapeHtml(d)).join(', ')}</span>
                    </div>
                    ` : ''}
                </div>
            `;
        });

        detailsContent.innerHTML = html;
    }

    /**
     * Switch metadata tab
     */
    switchMetadataTab(tab) {
        document.querySelectorAll('.metadata-tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.metadata-pane').forEach(p => p.classList.remove('active'));

        document.querySelector(`[data-tab="${tab}"]`).classList.add('active');
        document.getElementById(`${tab}Pane`).classList.add('active');
    }

    /**
     * Show loading indicator
     */
    showLoading(show) {
        document.getElementById('loadingIndicator').style.display = show ? 'flex' : 'none';
    }

    /**
     * Show message
     */
    showMessage(message, type = 'info') {
        const container = document.getElementById('validationMessages');
        
        const div = document.createElement('div');
        div.className = `validation-message ${type}`;
        div.innerHTML = `
            <span>${type === 'error' ? '❌' : type === 'success' ? '✅' : type === 'warning' ? '⚠️' : 'ℹ️'}</span>
            <span>${this.escapeHtml(message)}</span>
        `;

        container.appendChild(div);

        // Auto remove after 5 seconds for non-error messages
        if (type !== 'error') {
            setTimeout(() => div.remove(), 5000);
        }
    }

    /**
     * Clear editor
     */
    clearEditor() {
        document.getElementById('yamlEditor').value = '';
        document.getElementById('outputContainer').innerHTML = `
            <div class="empty-state">
                <p>Analyzed data will appear here</p>
            </div>
        `;
        document.getElementById('validationMessages').innerHTML = '';
        document.getElementById('headerStats').style.display = 'none';
        document.getElementById('metadataPanel').style.display = 'none';
    }

    /**
     * Clear analysis results
     */
    clearResults() {
        document.getElementById('outputContainer').innerHTML = `
            <div class="empty-state">
                <p>Analyzed data will appear here</p>
            </div>
        `;
        document.getElementById('validationMessages').innerHTML = '';
        document.getElementById('headerStats').style.display = 'none';
        document.getElementById('metadataPanel').style.display = 'none';
        document.getElementById('graphContainer').innerHTML = '';
    }

    /**
     * Copy to clipboard
     */
    copyToClipboard() {
        const yaml = document.querySelector('code')?.textContent;
        if (!yaml) return;

        navigator.clipboard.writeText(yaml).then(() => {
            this.showMessage('Workflow copied to clipboard', 'success');
        });
    }

    /**
     * Download workflow
     */
    downloadWorkflow() {
        const yaml = document.querySelector('code')?.textContent;
        if (!yaml) return;

        const blob = new Blob([yaml], { type: 'text/yaml' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'main.yml';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        this.showMessage('Workflow downloaded', 'success');
    }

    /**
     * Escape HTML
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize UI Controller
const uiController = new UIController();
