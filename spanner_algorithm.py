"""
Baswana-Sen Algorithm for Computing (2k-1)-Spanners in Weighted Graphs (Part 4 in the artice)
Expected time complexity: O(km)
Expected spanner size: O(kn^(1+1/k)) 
"""

import random
from typing import List, Tuple, Dict, Set, Optional
from collections import defaultdict


class Edge:
    """
    Each edge (u,v) appears twice: once in u's adjacency list, once in v's.
    Twin pointers allow constant-time bidirectional deletion (O(1)).
    """
    __slots__ = ['u', 'v', 'weight', 'twin', 'deleted', 'id']

    def __init__(self, u: int, v: int, weight: float, edge_id: int):
        self.u = u
        self.v = v
        self.weight = weight
        self.twin: Optional['Edge'] = None
        self.deleted = False
        self.id = edge_id  # For tie-breaking

    def __lt__(self, other: 'Edge') -> bool:
        """Compare by weight, then by ID for deterministic tie-breaking"""
        if abs(self.weight - other.weight) < 1e-10:
            return self.id < other.id
        return self.weight < other.weight


class AugmentedGraph:
    """
    Augmented adjacency list representation.
    Supports O(1) edge deletion via twin pointers.
    """

    def __init__(self, n: int):
        self.n = n
        self.adj: Dict[int, List[Edge]] = defaultdict(list)
        self.vertices: Set[int] = set()
        self.edge_count = 0

    def add_edge(self, u: int, v: int, weight: float) -> None:
        """Add undirected edge with augmented representation"""
        edge_uv = Edge(u, v, weight, self.edge_count)
        edge_vu = Edge(v, u, weight, self.edge_count)
        self.edge_count += 1

        # Create twin pointers for O(1) deletion
        edge_uv.twin = edge_vu
        edge_vu.twin = edge_uv

        self.adj[u].append(edge_uv)
        self.adj[v].append(edge_vu)
        self.vertices.add(u)
        self.vertices.add(v)

    def delete_edge(self, edge: Edge) -> None:
        """Delete edge in O(1) using twin pointer"""
        if not edge.deleted:
            edge.deleted = True
            if edge.twin:
                edge.twin.deleted = True

    def get_active_edges(self, v: int) -> List[Edge]:
        """Return non-deleted edges incident to vertex v"""
        return [e for e in self.adj[v] if not e.deleted]

    def get_all_active_edges(self) -> Set[Tuple[int, int, float]]:
        """Return all active edges (avoiding duplicates)"""
        edges = set()
        for v in self.vertices:
            for edge in self.get_active_edges(v):
                if edge.u < edge.v:  # Avoid duplicates
                    edges.add((edge.u, edge.v, edge.weight))
        return edges


class BaswanaSenSpanner:
    """
    Baswana-Sen (2k-1)-Spanner Algorithm

    Computes sparse spanners using a novel clustering approach that avoids
    any distance computation, achieving linear time complexity.
    """

    def __init__(self, n: int, k: int, seed: Optional[int] = None):
        """
        Initialize spanner algorithm.

        Args:
            n: Number of vertices
            k: Stretch parameter (computes (2k-1)-spanner)
            seed: Random seed for reproducibility
        """
        self.n = n
        self.k = k
        self.graph = AugmentedGraph(n)
        self.spanner_edges: List[Tuple[int, int, float]] = []

        if seed is not None:
            random.seed(seed)

    def add_edge(self, u: int, v: int, weight: float) -> None:
        """Add edge to graph"""
        self.graph.add_edge(u, v, weight)

    def compute_spanner(self) -> List[Tuple[int, int, float]]:
        """
        Compute (2k-1)-spanner using Baswana-Sen algorithm.

        Returns:
            List of (u, v, weight) tuples representing spanner edges
        """
        # Initialize clustering: each vertex is its own cluster
        cluster_center = {v: v for v in self.graph.vertices}
        cluster_edges = defaultdict(list)  # Edges defining each cluster

        # Phase 1: Forming the clusters (k-1 iterations)
        for i in range(1, self.k):
            cluster_center, cluster_edges = self._phase1_iteration(
                i, cluster_center, cluster_edges
            )

        # Phase 2: Vertex-cluster joining
        self._phase2_vertex_cluster_joining(cluster_center)

        return self.spanner_edges

    def _phase1_iteration(
        self,
        iteration: int,
        cluster_center: Dict[int, int],
        cluster_edges: Dict[int, List[Tuple[int, int, float]]]
    ) -> Tuple[Dict[int, int], Dict[int, List[Tuple[int, int, float]]]]:
        """
        Execute iteration i of Phase 1: Forming clusters.

        Steps:
        1. Sample clusters with probability n^(-1/k)
        2. Find nearest sampled cluster for each vertex
        3. Add appropriate edges to spanner
        4. Update clustering
        5. Remove intra-cluster edges
        """
        # Step 1: Sample clusters with probability n^(-1/k)
        p = self.n ** (-1.0 / self.k)
        current_clusters = set(cluster_center.values())
        sampled_clusters = {c for c in current_clusters if random.random() < p}

        # Initialize new clustering
        new_cluster_center = {}
        new_cluster_edges = defaultdict(list)

        # Step 2: Find nearest sampled cluster for each vertex
        nearest_sampled_cluster = {}
        nearest_edge_weight = {}

        for v in self.graph.vertices:
            # If v is in a sampled cluster, it remains there
            if cluster_center.get(v, v) in sampled_clusters:
                new_cluster_center[v] = cluster_center.get(v, v)
                continue

            # Find nearest sampled cluster (lightest edge to sampled cluster)
            min_edge = None
            for edge in self.graph.get_active_edges(v):
                neighbor_cluster = cluster_center.get(edge.v, edge.v)
                if neighbor_cluster in sampled_clusters:
                    if min_edge is None or edge < min_edge:
                        min_edge = edge

            if min_edge:
                nearest_sampled_cluster[v] = cluster_center[min_edge.v]
                nearest_edge_weight[v] = min_edge.weight

        # Step 3: Add edges to spanner based on cases
        for v in self.graph.vertices:
            if cluster_center.get(v, v) in sampled_clusters:
                continue

            # Case (a): v not adjacent to any sampled cluster
            if v not in nearest_sampled_cluster:
                self._add_edges_case_a(v, cluster_center)

            # Case (b): v adjacent to sampled cluster(s)
            else:
                nearest_cluster = nearest_sampled_cluster[v]
                threshold_weight = nearest_edge_weight[v]

                self._add_edges_case_b(
                    v, cluster_center, nearest_cluster,
                    threshold_weight, new_cluster_edges
                )

                new_cluster_center[v] = nearest_cluster

        # Step 4: Remove intra-cluster edges
        self._remove_intra_cluster_edges(new_cluster_center)

        return new_cluster_center, new_cluster_edges

    def _add_edges_case_a(
        self,
        v: int,
        cluster_center: Dict[int, int]
    ) -> None:
        """
        Case (a): Vertex v not adjacent to any sampled cluster.
        Add lightest edge from v to each neighboring cluster.
        """
        # Group edges by target cluster
        cluster_edges_map = defaultdict(list)
        for edge in self.graph.get_active_edges(v):
            neighbor_cluster = cluster_center.get(edge.v, edge.v)
            cluster_edges_map[neighbor_cluster].append(edge)

        # Add lightest edge to each cluster
        for cluster, edges in cluster_edges_map.items():
            min_edge = min(edges)
            self._add_to_spanner(min_edge)
            self.graph.delete_edge(min_edge)

    def _add_edges_case_b(
        self,
        v: int,
        cluster_center: Dict[int, int],
        nearest_cluster: int,
        threshold_weight: float,
        new_cluster_edges: Dict[int, List[Tuple[int, int, float]]]
    ) -> None:
        """
        Case (b): Vertex v adjacent to sampled cluster(s).

        1. Add edge to nearest sampled cluster
        2. Add lightest edge to each cluster lighter than edge to nearest cluster
        """
        # Find and add edge to nearest cluster
        nearest_edge = None
        for edge in self.graph.get_active_edges(v):
            neighbor_cluster = cluster_center.get(edge.v, edge.v)
            if neighbor_cluster == nearest_cluster:
                if nearest_edge is None or edge < nearest_edge:
                    nearest_edge = edge

        if nearest_edge:
            self._add_to_spanner(nearest_edge)
            new_cluster_edges[nearest_cluster].append(
                (nearest_edge.u, nearest_edge.v, nearest_edge.weight)
            )

        # Add edges lighter than threshold to other clusters
        cluster_edges_map = defaultdict(list)
        for edge in self.graph.get_active_edges(v):
            if edge.weight < threshold_weight - 1e-10:  # Strict inequality
                neighbor_cluster = cluster_center.get(edge.v, edge.v)
                cluster_edges_map[neighbor_cluster].append(edge)

        for cluster, edges in cluster_edges_map.items():
            min_edge = min(edges)
            self._add_to_spanner(min_edge)
            self.graph.delete_edge(min_edge)

    def _remove_intra_cluster_edges(
        self,
        cluster_center: Dict[int, int]
    ) -> None:
        """Remove edges where both endpoints are in the same cluster"""
        edges_to_remove = []

        for v in self.graph.vertices:
            v_cluster = cluster_center.get(v)
            if v_cluster is None:
                continue

            for edge in self.graph.get_active_edges(v):
                u_cluster = cluster_center.get(edge.v)
                if u_cluster == v_cluster:
                    edges_to_remove.append(edge)

        for edge in edges_to_remove:
            self.graph.delete_edge(edge)

    def _phase2_vertex_cluster_joining(
        self,
        cluster_center: Dict[int, int]
    ) -> None:
        """
        Phase 2: For each vertex v and each neighboring cluster c,
        add lightest edge from v to c to the spanner.
        """
        for v in self.graph.vertices:
            # Group edges by target cluster
            cluster_edges_map = defaultdict(list)
            for edge in self.graph.get_active_edges(v):
                neighbor_cluster = cluster_center.get(edge.v)
                if neighbor_cluster is not None:
                    cluster_edges_map[neighbor_cluster].append(edge)

            # Add lightest edge to each cluster
            for cluster, edges in cluster_edges_map.items():
                min_edge = min(edges)
                self._add_to_spanner(min_edge)

    def _add_to_spanner(self, edge: Edge) -> None:
        """Add edge to spanner (avoiding duplicates)"""
        u, v = min(edge.u, edge.v), max(edge.u, edge.v)
        edge_tuple = (u, v, edge.weight)
        if edge_tuple not in [
            (min(e[0], e[1]), max(e[0], e[1]), e[2])
            for e in self.spanner_edges
        ]:
            self.spanner_edges.append((edge.u, edge.v, edge.weight))


def compute_spanner(
    edges: List[Tuple[int, int, float]],
    n: int,
    k: int,
    seed: Optional[int] = None
) -> List[Tuple[int, int, float]]:
    """
    Compute (2k-1)-spanner for a weighted graph.

    Args:
        edges: List of (u, v, weight) tuples representing graph edges
        n: Number of vertices (labeled 0 to n-1)
        k: Stretch parameter (output is a (2k-1)-spanner)
        seed: Optional random seed for reproducibility

    Returns:
        List of (u, v, weight) tuples representing spanner edges

    Example:
        >>> edges = [(0, 1, 1.0), (1, 2, 2.0), (0, 2, 4.0)]
        >>> spanner = compute_spanner(edges, n=3, k=2)
        >>> len(spanner)  # Should be <= 3
        2
    """
    # Ensure distinct weights for deterministic behavior
    edges_adjusted = []
    for idx, (u, v, w) in enumerate(edges):
        # Add tiny epsilon based on edge ID for tie-breaking
        weight = w + idx * 1e-12
        edges_adjusted.append((u, v, weight))

    # Create algorithm instance
    algo = BaswanaSenSpanner(n, k, seed)

    # Add edges
    for u, v, weight in edges_adjusted:
        algo.add_edge(u, v, weight)

    # Compute spanner
    spanner = algo.compute_spanner()

    # Clean up weights (remove epsilon)
    return [(u, v, round(w, 10)) for u, v, w in spanner]
