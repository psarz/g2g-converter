/**
 * Graph Renderer using D3.js
 * Visualizes CI/CD pipeline dependencies
 */

class GraphRenderer {
    constructor(containerSelector) {
        this.container = document.querySelector(containerSelector);
        this.svg = null;
        this.simulation = null;
        this.data = null;
    }

    /**
     * Render dependency graph
     */
    render(graphData) {
        this.data = graphData;
        
        // Clear previous rendering
        this.container.innerHTML = '';

        const width = this.container.clientWidth;
        const height = this.container.clientHeight;

        // Create SVG
        this.svg = d3.select(this.container)
            .append('svg')
            .attr('width', width)
            .attr('height', height);

        // Create arrow marker
        this.svg.append('defs').append('marker')
            .attr('id', 'arrowhead')
            .attr('markerWidth', 10)
            .attr('markerHeight', 10)
            .attr('refX', 9)
            .attr('refY', 3)
            .attr('orient', 'auto')
            .append('polygon')
            .attr('points', '0 0, 10 3, 0 6')
            .attr('fill', 'var(--primary-color)');

        // Create zoom behavior
        const zoom = d3.zoom()
            .on('zoom', (event) => {
                g.attr('transform', event.transform);
            });

        this.svg.call(zoom);

        const g = this.svg.append('g');

        // Create force simulation
        this.simulation = d3.forceSimulation(graphData.nodes)
            .force('link', d3.forceLink(graphData.edges)
                .id(d => d.id)
                .distance(100))
            .force('charge', d3.forceManyBody().strength(-300))
            .force('center', d3.forceCenter(width / 2, height / 2))
            .force('collision', d3.forceCollide().radius(40));

        // Create links
        const link = g.append('g')
            .selectAll('line')
            .data(graphData.edges)
            .enter()
            .append('line')
            .attr('class', d => `link ${d.type}`)
            .attr('stroke-width', 2);

        // Create nodes
        const node = g.append('g')
            .selectAll('circle')
            .data(graphData.nodes)
            .enter()
            .append('circle')
            .attr('class', d => `node node-${d.type}`)
            .attr('r', 30)
            .attr('fill', d => this._getNodeColor(d))
            .call(this._createDragBehavior(this.simulation))
            .on('click', (event, d) => this._onNodeClick(event, d))
            .on('mouseover', (event, d) => this._onNodeHover(event, d))
            .on('mouseout', () => this._onNodeOut());

        // Create labels
        const labels = g.append('g')
            .selectAll('text')
            .data(graphData.nodes)
            .enter()
            .append('text')
            .attr('class', 'node-label')
            .attr('text-anchor', 'middle')
            .attr('dy', '.3em')
            .text(d => d.label.length > 15 ? d.label.substring(0, 12) + '...' : d.label);

        // Update positions on simulation tick
        this.simulation.on('tick', () => {
            link
                .attr('x1', d => d.source.x)
                .attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x)
                .attr('y2', d => d.target.y);

            node
                .attr('cx', d => d.x)
                .attr('cy', d => d.y);

            labels
                .attr('x', d => d.x)
                .attr('y', d => d.y);
        });

        // Add legend
        this._addLegend();

        // Store references for later use
        this.node = node;
        this.link = link;
        this.labels = labels;
        this.g = g;
    }

    /**
     * Get node color based on type and stage
     */
    _getNodeColor(d) {
        if (d.allowFailure) {
            return '#ffc107';
        }

        const stageIndex = this.data.stages.indexOf(d.stage);
        const colors = [
            '#0366d6',  // blue
            '#28a745',  // green
            '#6f42c1',  // purple
            '#fd7e14',  // orange
            '#dc3545'   // red
        ];

        return colors[stageIndex % colors.length];
    }

    /**
     * Create drag behavior for nodes
     */
    _createDragBehavior(simulation) {
        return d3.drag()
            .on('start', (event, d) => {
                if (!event.active) simulation.alphaTarget(0.3).restart();
                d.fx = d.x;
                d.fy = d.y;
            })
            .on('drag', (event, d) => {
                d.fx = event.x;
                d.fy = event.y;
            })
            .on('end', (event, d) => {
                if (!event.active) simulation.alphaTarget(0);
                d.fx = null;
                d.fy = null;
            });
    }

    /**
     * Handle node click
     */
    _onNodeClick(event, d) {
        event.stopPropagation();
        
        const event_data = new CustomEvent('nodeSelected', {
            detail: { node: d }
        });
        document.dispatchEvent(event_data);
    }

    /**
     * Handle node hover
     */
    _onNodeHover(event, d) {
        const tooltip = document.getElementById('tooltip');
        tooltip.innerHTML = `
            <strong>${d.label}</strong><br/>
            Stage: ${d.stage}<br/>
            Type: ${d.type}<br/>
            Allow Failure: ${d.allowFailure ? 'Yes' : 'No'}
        `;
        tooltip.style.display = 'block';
        tooltip.style.left = (event.pageX + 10) + 'px';
        tooltip.style.top = (event.pageY + 10) + 'px';

        // Highlight connected nodes
        if (this.link) {
            this.link.style('opacity', link => 
                link.source.id === d.id || link.target.id === d.id ? 1 : 0.3
            );
        }

        if (this.node) {
            this.node.style('opacity', node =>
                node.id === d.id || 
                this.data.edges.some(e => (e.source.id === d.id && e.target.id === node.id) || 
                                           (e.target.id === d.id && e.source.id === node.id)) ? 1 : 0.3
            );
        }
    }

    /**
     * Handle node mouse out
     */
    _onNodeOut() {
        document.getElementById('tooltip').style.display = 'none';

        if (this.link) this.link.style('opacity', 1);
        if (this.node) this.node.style('opacity', 1);
    }

    /**
     * Add legend to graph
     */
    _addLegend() {
        const legend = this.svg.append('g')
            .attr('class', 'legend')
            .attr('transform', 'translate(20, 20)');

        const items = [
            { color: '#0366d6', label: 'Stage 1' },
            { color: '#28a745', label: 'Stage 2' },
            { color: '#ffc107', label: 'Allow Failure' }
        ];

        items.forEach((item, i) => {
            const g = legend.append('g')
                .attr('transform', `translate(0, ${i * 25})`);

            g.append('circle')
                .attr('r', 5)
                .attr('fill', item.color);

            g.append('text')
                .attr('x', 15)
                .attr('dy', '.3em')
                .attr('font-size', '12px')
                .attr('fill', 'var(--text-primary)')
                .text(item.label);
        });
    }

    /**
     * Highlight job and dependencies
     */
    highlightJob(jobName) {
        if (!this.node) return;

        this.node.style('opacity', d => {
            if (d.id === jobName) return 1;
            
            // Check if connected
            const isConnected = this.data.edges.some(e =>
                (e.source.id === jobName && e.target.id === d.id) ||
                (e.target.id === jobName && e.source.id === d.id)
            );
            
            return isConnected ? 0.8 : 0.2;
        });

        if (this.link) {
            this.link.style('opacity', d => {
                return (d.source.id === jobName || d.target.id === jobName) ? 1 : 0.2;
            });
        }
    }

    /**
     * Clear highlights
     */
    clearHighlights() {
        if (this.node) this.node.style('opacity', 1);
        if (this.link) this.link.style('opacity', 1);
    }
}

// Export for use
const graphRenderer = new GraphRenderer('#graphContainer');
