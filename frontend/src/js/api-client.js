/**
 * API Client for GitLab to GitHub Converter
 * Handles all backend API communication
 */

class APIClient {
    constructor(baseURL = 'http://localhost:5000/api') {
        this.baseURL = baseURL;
    }

    /**
     * Make API request
     */
    async request(endpoint, method = 'GET', data = null) {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
            }
        };

        if (data) {
            options.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, options);
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || `API error: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            throw new Error(`Request failed: ${error.message}`);
        }
    }

    /**
     * Check API health
     */
    async health() {
        return this.request('/health');
    }

    /**
     * Convert GitLab CI to GitHub Actions
     */
    async convert(yamlContent) {
        return this.request('/convert', 'POST', {
            yaml_content: yamlContent
        });
    }

    /**
     * Analyze GitLab CI and generate dependency graph
     */
    async analyze(yamlContent) {
        return this.request('/analyze', 'POST', {
            yaml_content: yamlContent
        });
    }

    /**
     * Upload and process GitLab CI file
     */
    async uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(`${this.baseURL}/upload`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || `Upload failed: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            throw new Error(`Upload failed: ${error.message}`);
        }
    }

    /**
     * Validate YAML syntax
     */
    async validateYAML(yamlContent) {
        return this.request('/validate', 'POST', {
            yaml_content: yamlContent
        });
    }
}

// Export for use in other modules
const apiClient = new APIClient();
