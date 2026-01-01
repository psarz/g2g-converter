"""
Build dependency graphs from parsed GitLab CI configuration.
"""
from typing import Dict, List, Set
from app.models.gitlab_config import GitLabConfig
from app.models.dependency_graph import DependencyGraph, Node, Edge


class DependencyGraphBuilder:
    """Build visualization-ready dependency graphs."""
    
    def __init__(self, gitlab_config: GitLabConfig):
        """Initialize graph builder."""
        self.config = gitlab_config
        self.graph = DependencyGraph()
    
    def build(self) -> DependencyGraph:
        """
        Build complete dependency graph.
        
        Returns:
            DependencyGraph ready for visualization
        """
        self.graph = DependencyGraph()
        self.graph.stages = self.config.stages
        
        # Add nodes
        self._add_nodes()
        
        # Add edges
        self._add_edges()
        
        # Extract variables and secrets
        self._extract_variables_and_secrets()
        
        return self.graph
    
    def _add_nodes(self) -> None:
        """Add job nodes to graph."""
        for job in self.config.jobs:
            job_type = self._determine_job_type(job)
            node = Node(
                id=job.name,
                label=job.name,
                stage=job.stage,
                job_type=job_type,
                allow_failure=job.allow_failure
            )
            self.graph.add_node(node)
    
    def _add_edges(self) -> None:
        """Add dependency edges to graph."""
        for job in self.config.jobs:
            # Add edges for 'needs' (direct dependencies)
            for need in job.needs:
                edge = Edge(
                    source=need,
                    target=job.name,
                    type='needs'
                )
                self.graph.add_edge(edge)
            
            # Add edges for 'dependencies' (artifact dependencies)
            for dep in job.dependencies:
                edge = Edge(
                    source=dep,
                    target=job.name,
                    type='artifact'
                )
                self.graph.add_edge(edge)
            
            # Add implicit stage dependencies
            if not job.needs and not job.dependencies:
                stage_idx = self._get_stage_index(job.stage)
                if stage_idx > 0:
                    prev_stage = self.config.stages[stage_idx - 1]
                    prev_jobs = self.config.get_jobs_by_stage(prev_stage)
                    for prev_job in prev_jobs:
                        edge = Edge(
                            source=prev_job.name,
                            target=job.name,
                            type='depends_on'
                        )
                        self.graph.add_edge(edge)
    
    def _extract_variables_and_secrets(self) -> None:
        """Extract variables and secrets for graph metadata."""
        # Global variables
        for var in self.config.variables:
            self.graph.variables[var.name] = var.value
        
        # Job-level variables
        for job in self.config.jobs:
            for name, value in job.variables.items():
                if name not in self.graph.variables:
                    self.graph.variables[name] = str(value)
        
        # Secrets
        for secret in self.config.secrets:
            self.graph.secrets.append(secret.name)
    
    def _determine_job_type(self, job) -> str:
        """Determine job type (regular, manual, delayed)."""
        if job.when == 'manual':
            return 'manual'
        elif job.when == 'delayed':
            return 'delayed'
        return 'regular'
    
    def _get_stage_index(self, stage: str) -> int:
        """Get stage index in stages list."""
        try:
            return self.config.stages.index(stage)
        except ValueError:
            return -1
    
    def get_job_dependencies(self, job_name: str) -> Dict[str, List[str]]:
        """
        Get all dependencies for a specific job.
        
        Returns:
            Dictionary with 'direct' and 'transitive' dependencies
        """
        direct_deps = []
        transitive_deps = []
        
        # Find direct dependencies
        for edge in self.graph.edges:
            if edge.target == job_name:
                direct_deps.append(edge.source)
        
        # Find transitive dependencies
        visited = set()
        
        def find_transitive(job_id):
            for edge in self.graph.edges:
                if edge.target == job_id and edge.source not in visited:
                    visited.add(edge.source)
                    transitive_deps.append(edge.source)
                    find_transitive(edge.source)
        
        find_transitive(job_name)
        
        return {
            'direct': direct_deps,
            'transitive': transitive_deps
        }
    
    def detect_circular_dependencies(self) -> List[List[str]]:
        """
        Detect circular dependencies in the graph.
        
        Returns:
            List of cycles found
        """
        cycles = []
        visited = set()
        rec_stack = set()
        path = []
        
        def dfs(node):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for edge in self.graph.edges:
                if edge.source == node:
                    if edge.target not in visited:
                        dfs(edge.target)
                    elif edge.target in rec_stack:
                        # Found cycle
                        cycle_start = path.index(edge.target)
                        cycle = path[cycle_start:] + [edge.target]
                        cycles.append(cycle)
            
            path.pop()
            rec_stack.remove(node)
        
        for node in self.graph.nodes:
            if node.id not in visited:
                dfs(node.id)
        
        return cycles
    
    def get_critical_path(self) -> List[str]:
        """
        Get the critical path (longest dependency chain).
        
        Returns:
            List of job names in critical path
        """
        # Find all leaf nodes (jobs with no dependents)
        leaf_nodes = []
        job_ids = {node.id for node in self.graph.nodes}
        targets = {edge.target for edge in self.graph.edges}
        
        for job_id in job_ids:
            if job_id not in targets:
                leaf_nodes.append(job_id)
        
        if not leaf_nodes:
            return []
        
        # Find longest path from root to leaf
        longest_path = []
        
        def find_longest_path(node, current_path):
            nonlocal longest_path
            current_path = current_path + [node]
            
            # Check if this is a leaf
            has_dependents = any(edge.source == node for edge in self.graph.edges)
            if not has_dependents:
                if len(current_path) > len(longest_path):
                    longest_path = current_path[:]
            else:
                # Continue to dependents
                for edge in self.graph.edges:
                    if edge.source == node:
                        find_longest_path(edge.target, current_path)
        
        # Find nodes with no dependencies
        all_sources = {edge.source for edge in self.graph.edges}
        root_nodes = [node for node in self.graph.nodes if node.id not in all_sources]
        
        for root in root_nodes:
            find_longest_path(root.id, [])
        
        return longest_path
    
    def get_graph_metrics(self) -> Dict:
        """
        Calculate graph metrics.
        
        Returns:
            Dictionary with various metrics
        """
        metrics = self.graph.get_graph_metrics()
        
        # Add additional metrics
        cycles = self.detect_circular_dependencies()
        critical_path = self.get_critical_path()
        
        metrics['cycles'] = len(cycles)
        metrics['critical_path_length'] = len(critical_path)
        metrics['avg_job_dependencies'] = (
            sum(len(self.get_job_dependencies(node.id)['direct']) 
                for node in self.graph.nodes) 
            / len(self.graph.nodes) 
            if self.graph.nodes else 0
        )
        
        return metrics
