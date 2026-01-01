"""
Dependency graph model for visualization.
"""
from typing import List, Dict, Set
from dataclasses import dataclass, field
import networkx as nx


@dataclass
class Node:
    """Represents a job node in the dependency graph."""
    id: str
    label: str
    stage: str
    job_type: str = "regular"  # regular, manual, delayed
    allow_failure: bool = False


@dataclass
class Edge:
    """Represents a dependency edge."""
    source: str
    target: str
    type: str = "depends_on"  # depends_on, needs, artifact


@dataclass
class DependencyGraph:
    """Complete dependency graph for visualization."""
    nodes: List[Node] = field(default_factory=list)
    edges: List[Edge] = field(default_factory=list)
    variables: Dict[str, str] = field(default_factory=dict)
    secrets: List[str] = field(default_factory=list)
    stages: List[str] = field(default_factory=list)
    
    def add_node(self, node: Node) -> None:
        """Add a node to the graph."""
        if not any(n.id == node.id for n in self.nodes):
            self.nodes.append(node)
    
    def add_edge(self, edge: Edge) -> None:
        """Add an edge to the graph."""
        if not any(e.source == edge.source and e.target == edge.target for e in self.edges):
            self.edges.append(edge)
    
    def to_dict(self) -> Dict:
        """Convert graph to dictionary format."""
        return {
            "nodes": [{"id": n.id, "label": n.label, "stage": n.stage, "type": n.job_type, "allowFailure": n.allow_failure} for n in self.nodes],
            "edges": [{"source": e.source, "target": e.target, "type": e.type} for e in self.edges],
            "variables": self.variables,
            "secrets": self.secrets,
            "stages": self.stages
        }
    
    def get_graph_metrics(self) -> Dict:
        """Calculate graph metrics."""
        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "total_stages": len(self.stages),
            "total_variables": len(self.variables),
            "total_secrets": len(self.secrets)
        }
