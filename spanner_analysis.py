"""
Academic Analysis Module for Baswana-Sen Spanner Algorithm

This module provides comprehensive evaluation tools for analyzing the
Baswana-Sen (2k-1)-spanner algorithm.

Key Features:
- Graph characteristics analysis (n, m, density)
- Running time measurement
- Sparsity and size analysis vs theoretical bounds
- Empirical stretch verification via APSP (Dijkstra)
- Statistical analysis across multiple randomized runs

"""

import time
import heapq
from typing import Any, List, Tuple, Dict, Optional
from collections import defaultdict
from statistics import mean, stdev
from spanner_algorithm import compute_spanner


# ============================================================================
# Shortest Path Computation (for Stretch Verification)
# ============================================================================

def dijkstra(adj: Dict[int, List[Tuple[int, float]]], source: int, n: int) -> Dict[int, float]:
    """
    Compute single-source shortest paths using Dijkstra's algorithm.

    Args:
        adj: Adjacency list {vertex: [(neighbor, weight), ...]}
        source: Source vertex
        n: Number of vertices

    Returns:
        Dictionary mapping vertex -> shortest distance from source
    """
    dist = {i: float('inf') for i in range(n)}
    dist[source] = 0.0

    pq = [(0.0, source)]
    visited = set()

    while pq:
        d, u = heapq.heappop(pq)

        if u in visited:
            continue
        visited.add(u)

        if u not in adj:
            continue

        for v, weight in adj[u]:
            if dist[u] + weight < dist[v]:
                dist[v] = dist[u] + weight
                heapq.heappush(pq, (dist[v], v))

    return dist


def build_adjacency_list(edges: List[Tuple[int, int, float]]) -> Dict[int, List[Tuple[int, float]]]:
    """Build adjacency list from edge list."""
    adj = defaultdict[Any, list](list)
    for u, v, weight in edges:
        adj[u].append((v, weight))
        adj[v].append((u, weight))
    return dict(adj)


# ============================================================================
# Graph Characteristics
# ============================================================================

def compute_graph_characteristics(edges: List[Tuple[int, int, float]], n: int) -> Dict:
    """
    Compute basic graph characteristics.

    Returns:
        Dictionary with keys: n, m, density
    """
    m = len(edges)
    max_edges = n * (n - 1) / 2
    density = m / max_edges if max_edges > 0 else 0.0

    return {
        'n': n,
        'm': m,
        'density': density
    }


# ============================================================================
# Single Run Analysis
# ============================================================================

def analyze_single_run(
    edges: List[Tuple[int, int, float]],
    n: int,
    k: int,
    seed: int,
    compute_stretch: bool = True
) -> Dict:
    """
    Analyze a single run of the spanner algorithm.

    Returns:
        Dictionary with keys:
        - spanner_size: Number of edges in spanner
        - running_time: Time in seconds
        - max_stretch: Maximum observed stretch 
        - avg_stretch: Average stretch 
    """
    # Measure running time
    start_time = time.time()
    spanner = compute_spanner(edges, n, k, seed)
    running_time = time.time() - start_time

    result = {
        'spanner_size': len(spanner),
        'running_time': running_time,
        'spanner_edges': spanner
    }

    # Compute empirical stretch if requested
    if compute_stretch:
        adj_original = build_adjacency_list(edges)
        adj_spanner = build_adjacency_list(spanner)

        stretches = []

        for u in range(n):
            dist_orig = dijkstra(adj_original, u, n)
            dist_span = dijkstra(adj_spanner, u, n)

            for v in range(u + 1, n):
                if dist_orig[v] != float('inf') and dist_orig[v] > 0:
                    if dist_span[v] == float('inf'):
                        # Disconnected in spanner - violation
                        stretches.append(float('inf'))
                    else:
                        stretch = dist_span[v] / dist_orig[v]
                        stretches.append(stretch)

        # Filter out inf values for statistics
        finite_stretches = [s for s in stretches if s != float('inf')]

        result['max_stretch'] = max(finite_stretches) if finite_stretches else float('inf')
        result['avg_stretch'] = mean(finite_stretches) if finite_stretches else float('inf')
        result['num_violations'] = sum(1 for s in stretches if s == float('inf'))

    return result


# ============================================================================
# Multi-Run Statistical Analysis
# ============================================================================

def run_academic_evaluation(
    edges: List[Tuple[int, int, float]],
    n: int,
    k: int,
    num_runs: int = 5,
    compute_stretch: bool = True,
    base_seed: int = 42
) -> Dict:
    """
    Comprehensive academic evaluation of the Baswana-Sen spanner algorithm.

    This function performs rigorous analysis suitable for research publication:
    1. Graph characteristics (n, m, density)
    2. Multiple randomized runs to analyze variance
    3. Sparsity analysis vs theoretical bounds
    4. Empirical stretch verification via APSP
    5. Statistical analysis (mean, std, min, max)

    Args:
        edges: Original graph edge list [(u, v, weight), ...]
        n: Number of vertices
        k: Stretch parameter (produces (2k-1)-spanner)
        num_runs: Number of independent runs (for statistical analysis)
        compute_stretch: Whether to compute empirical stretch (expensive for large graphs)
        base_seed: Base random seed for reproducibility

    Returns:
        Comprehensive dictionary with all metrics and statistics
    """
    theoretical_stretch = 2 * k - 1

    # ========================================================================
    # Phase 1: Graph Characteristics
    # ========================================================================
    graph_chars = compute_graph_characteristics(edges, n)

    # ========================================================================
    # Phase 2: Multiple Runs for Statistical Analysis
    # ========================================================================
    run_results = []

    for run_idx in range(num_runs):
        seed = base_seed + run_idx
        result = analyze_single_run(edges, n, k, seed, compute_stretch)
        run_results.append(result)

    # ========================================================================
    # Phase 3: Aggregate Statistics
    # ========================================================================
    spanner_sizes = [r['spanner_size'] for r in run_results]
    running_times = [r['running_time'] for r in run_results]

    # Theoretical bound
    theoretical_size = k * (n ** (1 + 1/k))

    stats = {
        # Graph characteristics
        'n': n,
        'm': graph_chars['m'],
        'density': graph_chars['density'],
        'k': k,
        'theoretical_stretch': theoretical_stretch,
        'theoretical_size': theoretical_size,

        # Spanner size statistics
        'size_mean': mean(spanner_sizes),
        'size_std': stdev(spanner_sizes) if len(spanner_sizes) > 1 else 0.0,
        'size_min': min(spanner_sizes),
        'size_max': max(spanner_sizes),

        # Running time statistics
        'time_mean': mean(running_times),
        'time_std': stdev(running_times) if len(running_times) > 1 else 0.0,
        'time_min': min(running_times),
        'time_max': max(running_times),

        # Number of runs
        'num_runs': num_runs,

        # Raw data
        'all_sizes': spanner_sizes,
        'all_times': running_times
    }

    # Add stretch statistics if computed
    if compute_stretch:
        max_stretches = [r['max_stretch'] for r in run_results]
        avg_stretches = [r['avg_stretch'] for r in run_results]
        violations = [r['num_violations'] for r in run_results]

        # Filter finite values
        finite_max_stretches = [s for s in max_stretches if s != float('inf')]
        finite_avg_stretches = [s for s in avg_stretches if s != float('inf')]

        stats['stretch_max_mean'] = mean(finite_max_stretches) if finite_max_stretches else float('inf')
        stats['stretch_max_std'] = stdev(finite_max_stretches) if len(finite_max_stretches) > 1 else 0.0
        stats['stretch_max_min'] = min(finite_max_stretches) if finite_max_stretches else float('inf')
        stats['stretch_max_max'] = max(finite_max_stretches) if finite_max_stretches else float('inf')

        stats['stretch_avg_mean'] = mean(finite_avg_stretches) if finite_avg_stretches else float('inf')
        stats['stretch_avg_std'] = stdev(finite_avg_stretches) if len(finite_avg_stretches) > 1 else 0.0

        stats['total_violations'] = sum(violations)
        stats['satisfies_guarantee'] = stats['total_violations'] == 0 and stats['stretch_max_max'] <= theoretical_stretch + 0.01

        stats['all_max_stretches'] = max_stretches
        stats['all_avg_stretches'] = avg_stretches

    return stats


# ============================================================================
# Professional Output Formatting
# ============================================================================

def print_evaluation_report(stats: Dict, title: str = "Spanner Algorithm Evaluation") -> None:
    """
    Print a professional, publication-quality evaluation report.

    Args:
        stats: Dictionary returned by run_academic_evaluation()
        title: Report title
    """
    k = stats['k']
    theoretical_stretch = stats['theoretical_stretch']

    # Header
    print("\n" + "=" * 80)
    print(f"{title:^80}")
    print("=" * 80)

    # Section 1: Problem Instance
    print(f"\n{'PROBLEM INSTANCE':^80}")
    print("─" * 80)
    print(f"  Algorithm:             Baswana-Sen (ICALP 2003)")
    print(f"  Stretch Parameter:     k = {k}  →  (2k-1) = {theoretical_stretch}-spanner")
    print(f"  Input Graph:           n = {stats['n']}, m = {stats['m']}")
    print(f"  Edge Density:          ρ = {stats['density']:.4f}")

    # Section 2: Sparsity Analysis
    print(f"\n{'SPARSITY ANALYSIS':^80}")
    print("─" * 80)
    print(f"  Original Size:         m = {stats['m']} edges")
    print(f"  Theoretical Bound:     O(kn^(1+1/k)) ≈ {stats['theoretical_size']:.1f} edges")
    print(f"\n  Spanner Size (|E_S|):")
    print(f"    Mean:                {stats['size_mean']:.2f}")
    print(f"    Std Dev:             {stats['size_std']:.2f}")
    print(f"    Min:                 {stats['size_min']}")
    print(f"    Max:                 {stats['size_max']}")
    print(f"\n  Compression Ratio:     {100 * (1 - stats['size_mean']/stats['m']):.1f}% reduction")
    print(f"  Theoretical Ratio:     {stats['size_mean'] / stats['theoretical_size']:.3f}x bound")

    # Section 3: Running Time
    print(f"\n{'RUNNING TIME ANALYSIS':^80}")
    print("─" * 80)
    print(f"  Theoretical:           O(km) = O({k * stats['m']})")
    print(f"\n  Measured Time:")
    print(f"    Mean:                {stats['time_mean']*1000:.2f} ms")
    print(f"    Std Dev:             {stats['time_std']*1000:.2f} ms")
    print(f"    Min:                 {stats['time_min']*1000:.2f} ms")
    print(f"    Max:                 {stats['time_max']*1000:.2f} ms")

    # Section 4: Empirical Stretch (if available)
    if 'stretch_max_mean' in stats:
        print(f"\n{'EMPIRICAL STRETCH VERIFICATION (APSP)':^80}")
        print("─" * 80)
        print(f"  Theoretical Guarantee: dist_H(u,v) ≤ {theoretical_stretch} · dist_G(u,v)  ∀u,v ∈ V")
        print(f"\n  Maximum Stretch:")
        print(f"    Mean:                {stats['stretch_max_mean']:.4f}")
        print(f"    Std Dev:             {stats['stretch_max_std']:.4f}")
        print(f"    Min:                 {stats['stretch_max_min']:.4f}")
        print(f"    Max:                 {stats['stretch_max_max']:.4f}")
        print(f"\n  Average Stretch:")
        print(f"    Mean:                {stats['stretch_avg_mean']:.4f}")
        print(f"    Std Dev:             {stats['stretch_avg_std']:.4f}")

        print(f"\n  Violations:            {stats['total_violations']}")

        # Verdict
        if stats['satisfies_guarantee']:
            print(f"\n  ✅ VERDICT: Algorithm satisfies P_{{{theoretical_stretch}}} property")
            print(f"              Max stretch {stats['stretch_max_max']:.4f} ≤ {theoretical_stretch}")
        else:
            print(f"\n  ❌ VERDICT: Algorithm violates P_{{{theoretical_stretch}}} property")
            print(f"              Max stretch {stats['stretch_max_max']:.4f} > {theoretical_stretch}")

    # Section 5: Number of Runs
    print("─" * 80)
    print(f"  Number of Runs:        {stats['num_runs']}")

    # Footer
    print("\n" + "=" * 80)
    print()


def print_comparative_report(results_list: List[Tuple[str, Dict]]) -> None:
    """
    Print comparative analysis across multiple experiments.

    Args:
        results_list: List of (experiment_name, stats_dict) tuples
    """
    print("\n" + "=" * 80)
    print(f"{'COMPARATIVE ANALYSIS':^80}")
    print("=" * 80)

    # Header
    print(f"\n{'Experiment':<30} {'n':<8} {'k':<5} {'|E_S|':<10} {'Max Stretch':<15} {'Time (ms)':<12}")
    print("─" * 80)

    # Each experiment
    for name, stats in results_list:
        size_str = f"{stats['size_mean']:.1f}±{stats['size_std']:.1f}"

        if 'stretch_max_mean' in stats:
            stretch_str = f"{stats['stretch_max_mean']:.3f}±{stats['stretch_max_std']:.3f}"
        else:
            stretch_str = "N/A"

        time_str = f"{stats['time_mean']*1000:.2f}"

        print(f"{name:<30} {stats['n']:<8} {stats['k']:<5} {size_str:<10} {stretch_str:<15} {time_str:<12}")

    print("=" * 80)
    print()


# ============================================================================
# Quick Analysis Function (for small experiments)
# ============================================================================

def quick_analysis(edges: List[Tuple[int, int, float]], n: int, k: int, seed: int = 42) -> None:
    """
    Quick single-run analysis for rapid prototyping.

    Args:
        edges: Graph edges
        n: Number of vertices
        k: Stretch parameter
        seed: Random seed
    """
    print(f"\nQuick Analysis: n={n}, k={k}")
    print("─" * 40)

    result = analyze_single_run(edges, n, k, seed, compute_stretch=True)

    print(f"Spanner size:   {result['spanner_size']} edges")
    print(f"Running time:   {result['running_time']*1000:.2f} ms")
    print(f"Max stretch:    {result['max_stretch']:.4f}")
    print(f"Avg stretch:    {result['avg_stretch']:.4f}")

    theoretical_stretch = 2 * k - 1
    if result['max_stretch'] <= theoretical_stretch + 0.01:
        print(f"✅ Satisfies {theoretical_stretch}-spanner property")
    else:
        print(f"❌ Violates {theoretical_stretch}-spanner property")

    print()
