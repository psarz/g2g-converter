/**
 * Main Application Initialization
 */

document.addEventListener('DOMContentLoaded', async () => {
    console.log('GitLab to GitHub Converter initializing...');

    // Check API health
    try {
        const health = await apiClient.health();
        console.log('API is healthy:', health);
    } catch (error) {
        console.warn('API connection warning:', error.message);
        uiController.showMessage(
            'Backend API not available. Using demo mode. Connect to http://localhost:5000 to enable full functionality.',
            'warning'
        );
    }

    // Handle file upload and auto-process
    document.getElementById('fileInput').addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (file) {
            // File will be automatically read and analyzed by handleFileSelect
            console.log('File selected:', file.name);
        }
    });

    // Also show editor if user pastes or types content manually
    document.getElementById('yamlEditor').addEventListener('input', () => {
        const content = document.getElementById('yamlEditor').value.trim();
        document.getElementById('analyzeBtn').disabled = !content;
    });

    // Listen for node selection events
    document.addEventListener('nodeSelected', (event) => {
        const node = event.detail.node;
        graphRenderer.highlightJob(node.id);
        uiController.displayDetails();
    });

    // Check if a gitlab-ci.yaml file exists in the page context (for GitHub Pages deployment)
    checkAndLoadDefaultFile();

    console.log('Application ready');
});

/**
 * Check if a default gitlab-ci.yaml file exists and load it automatically
 */
async function checkAndLoadDefaultFile() {
    try {
        // Try to fetch a sample or default gitlab-ci.yaml from the examples folder
        const response = await fetch('examples/complete-pipeline.yml');
        if (response.ok) {
            console.log('Found default pipeline example');
        }
    } catch (error) {
        // Silent fail - this is optional
        console.debug('No default file found');
    }
}
