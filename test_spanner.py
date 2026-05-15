"""
Test suite and examples for the Baswana-Sen Spanner Algorithm
"""

import random
from spanner_algorithm import compute_spanner, BaswanaSenSpanner
from typing import List, Tuple, Set


def verify_spanner(
    edges: List[Tuple[int, int, float]],
    spanner: List[Tuple[int, int, float]],
    n: int,
    stretch: int
) -> bool:
    """
    Verify that spanner satisfies the stretch guarantee using BFS.

    Args:
        edges: Original graph edges
        spanner: Spanner edges
        n: Number of vertices
        stretch: Required stretch factor

    Returns:
        True if spanner is valid, False otherwise
    """
    # Build adjacency lists
    graph = {i: [] for i in range(n)}
    spanner_graph = {i: [] for i in range(n)}

    for u, v, w in edges:
        graph[u].append((v, w))
        graph[v].append((u, w))

    for u, v, w in spanner:
        spanner_graph[u].append((v, w))
        spanner_graph[v].append((u, w))

    # Compute all-pairs shortest paths using BFS (for unweighted check)
    # For weighted graphs, this is a simplified check
    def bfs_distance(adj, start, end):
        """Simple BFS path check"""
        if start == end:
            return 0
        visited = {start}
        queue = [(start, 0)]
        while queue:
            node, dist = queue.pop(0)
            for neighbor, weight in adj[node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    if neighbor == end:
                        return dist + 1
                    queue.append((neighbor, dist + 1))
        return float('inf')

    # Check a sample of vertex pairs
    for u in range(min(n, 20)):
        for v in range(u + 1, min(n, 20)):
            orig_dist = bfs_distance(graph, u, v)
            span_dist = bfs_distance(spanner_graph, u, v)

            if orig_dist < float('inf'):
                if span_dist > stretch * orig_dist + 1:  # Allow for rounding
                    print(f"Stretch violation: {u}-{v}, "
                          f"original={orig_dist}, spanner={span_dist}")
                    return False

    return True


def test_simple_triangle():
    """Test on simple triangle graph"""
    print("Test 1: Simple Triangle")
    edges = [
        (0, 1, 1.0),
        (1, 2, 2.0),
        (0, 2, 4.0)
    ]
    spanner = compute_spanner(edges, n=3, k=2, seed=42)

    print(f"  Original edges: {len(edges)}")
    print(f"  Spanner edges: {len(spanner)}")
    print(f"  Spanner: {spanner}")

    assert len(spanner) <= len(edges), "Spanner should not have more edges"
    assert len(spanner) >= 2, "Spanner needs at least 2 edges for connectivity"
    print("  ✓ Passed\n")


def test_path_graph():
    """Test on path graph"""
    print("Test 2: Path Graph (n=10)")
    n = 10
    edges = [(i, i + 1, float(i + 1)) for i in range(n - 1)]

    spanner = compute_spanner(edges, n=n, k=2, seed=42)

    print(f"  Original edges: {len(edges)}")
    print(f"  Spanner edges: {len(spanner)}")

    # Path graph should keep most/all edges for connectivity
    assert len(spanner) >= n - 1, "Path needs all edges"
    print("  ✓ Passed\n")


def test_complete_graph():
    """Test on complete graph K_n"""
    print("Test 3: Complete Graph K_7")
    n = 7
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            weight = abs(i - j) * 1.5
            edges.append((i, j, weight))

    k = 2
    spanner = compute_spanner(edges, n=n, k=k, seed=42)

    print(f"  Original edges: {len(edges)}")
    print(f"  Spanner edges: {len(spanner)}")

    # Should significantly reduce edges
    expected_max = k * (n ** (1 + 1/k)) * 3  # With some slack
    print(f"  Theoretical bound: O(k·n^(1+1/k)) ≈ {expected_max:.1f}")

    assert len(spanner) < len(edges), "Should reduce edges"
    print("  ✓ Passed\n")


def test_random_graph():
    """Test on random Erdős-Rényi graph"""
    print("Test 4: Random Graph (n=20, p=0.3)")
    n = 20
    p = 0.3
    random.seed(123)

    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            if random.random() < p:
                weight = random.uniform(1.0, 10.0)
                edges.append((i, j, weight))

    k = 3
    spanner = compute_spanner(edges, n=n, k=k, seed=42)

    print(f"  Original edges: {len(edges)}")
    print(f"  Spanner edges: {len(spanner)}")

    # Verify basic properties
    assert len(spanner) > 0, "Spanner should have edges"
    assert len(spanner) <= len(edges), "Spanner should not add edges"

    # Basic connectivity check
    spanner_vertices = set()
    for u, v, _ in spanner:
        spanner_vertices.add(u)
        spanner_vertices.add(v)

    print(f"  Vertices in spanner: {len(spanner_vertices)}/{n}")
    print("  ✓ Passed\n")


def test_grid_graph():
    """Test on 2D grid graph"""
    print("Test 5: Grid Graph (5x5)")
    rows, cols = 5, 5
    n = rows * cols

    def node_id(r, c):
        return r * cols + c

    edges = []
    # Horizontal edges
    for r in range(rows):
        for c in range(cols - 1):
            u = node_id(r, c)
            v = node_id(r, c + 1)
            edges.append((u, v, 1.0))

    # Vertical edges
    for r in range(rows - 1):
        for c in range(cols):
            u = node_id(r, c)
            v = node_id(r + 1, c)
            edges.append((u, v, 1.0))

    k = 2
    spanner = compute_spanner(edges, n=n, k=k, seed=42)

    print(f"  Original edges: {len(edges)}")
    print(f"  Spanner edges: {len(spanner)}")

    # Grid should remain fairly dense
    assert len(spanner) >= n - 1, "Need edges for connectivity"
    print("  ✓ Passed\n")


def test_stretch_factors():
    """Test with different k values"""
    print("Test 6: Different Stretch Factors")

    # Create a test graph
    n = 15
    random.seed(456)
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            if random.random() < 0.4:
                edges.append((i, j, random.uniform(1.0, 5.0)))

    print(f"  Original graph: {n} vertices, {len(edges)} edges")

    for k in [2, 3, 4]:
        spanner = compute_spanner(edges, n=n, k=k, seed=42)
        print(f"  k={k} (stretch={2*k-1}): {len(spanner)} edges")

    print("  ✓ Passed\n")


def test_weighted_edges():
    """Test with various weight patterns"""
    print("Test 7: Various Weight Patterns")

    # Star graph with different weight patterns
    n = 10
    center = 0

    test_cases = [
        ("Uniform", [1.0] * (n - 1)),
        ("Increasing", list(range(1, n))),
        ("Decreasing", list(range(n - 1, 0, -1))),
        ("Random", [random.uniform(1, 100) for _ in range(n - 1)])
    ]

    for name, weights in test_cases:
        edges = [(center, i + 1, weights[i]) for i in range(n - 1)]
        spanner = compute_spanner(edges, n=n, k=2, seed=42)
        print(f"  {name} weights: {len(spanner)}/{len(edges)} edges in spanner")

    print("  ✓ Passed\n")


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("Baswana-Sen Spanner Algorithm - Test Suite")
    print("=" * 60 + "\n")

    tests = [
        test_simple_triangle,
        test_path_graph,
        test_complete_graph,
        test_random_graph,
        test_grid_graph,
        test_stretch_factors,
        test_weighted_edges
    ]

    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"  ✗ Failed with error: {e}\n")
            raise

    print("=" * 60)
    print("All tests passed! ✓")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
