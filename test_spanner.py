"""
Three experiments:
  1. Correctness — verify three invariants (size bound, connectivity,
     stretch compliance) on small/medium random graphs using full APSP.
  2. Large-scale benchmark — N = 1,000 .. 10,000 random graphs, with
     sampled-pair stretch estimation so the experiment finishes in
     reasonable wall-clock time.
  3. Worst-case (diluted clique) — N = 1,000 .. 10,000 unweighted graphs
     where each clique edge is kept independently with probability
     p = n^(1/k) / n. 

"""

import csv
import heapq
import random
import time
from collections import defaultdict, deque
from typing import Dict, List, Optional, Tuple

from spanner_algorithm import compute_spanner


def generate_random_graph(n: int, p: float = 0.3, seed: int = 42) -> List[Tuple[int, int, float]]:
    rng = random.Random(seed)
    edges: List[Tuple[int, int, float]] = []
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < p:
                edges.append((i, j, rng.uniform(1.0, 10.0)))
    return edges


# ============================================================================
# Shared helpers
# ============================================================================

def _build_adj(edges: List[Tuple[int, int, float]]) -> Dict[int, List[Tuple[int, float]]]:
    adj: Dict[int, List[Tuple[int, float]]] = defaultdict(list)
    for u, v, w in edges:
        adj[u].append((v, w))
        adj[v].append((u, w))
    return adj


def _dijkstra(adj: Dict[int, List[Tuple[int, float]]], src: int, n: int) -> List[float]:
    dist = [float('inf')] * n
    dist[src] = 0.0
    pq = [(0.0, src)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v, w in adj.get(u, ()):
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                heapq.heappush(pq, (nd, v))
    return dist


def _components(adj: Dict[int, List[Tuple[int, float]]], n: int) -> List[int]:
    """Return component-id array (one int per vertex)."""
    comp = [-1] * n
    cid = 0
    for s in range(n):
        if comp[s] != -1:
            continue
        comp[s] = cid
        q = deque([s])
        while q:
            u = q.popleft()
            for v, _ in adj.get(u, ()):
                if comp[v] == -1:
                    comp[v] = cid
                    q.append(v)
        cid += 1
    return comp


def _size_bound(n: int, k: int) -> float:
    return k * (n ** (1 + 1.0 / k))


# ============================================================================
# Experiment 1 — Correctness (invariant verification)
# ============================================================================

def verify_invariants(
    edges: List[Tuple[int, int, float]],
    spanner: List[Tuple[int, int, float]],
    n: int,
    k: int,
) -> Dict[str, object]:
    """
    Check the three invariants with full APSP. Returns a dict describing
    each invariant's pass/fail and the worst observed stretch.
    """
    stretch_limit = 2 * k - 1
    bound = _size_bound(n, k)

    adj_g = _build_adj(edges)
    adj_h = _build_adj(spanner)

    # (a) Size bound
    size_ok = len(spanner) <= bound

    # (b) Connectivity: same component partition in G and H.
    comp_g = _components(adj_g, n)
    comp_h = _components(adj_h, n)
    connectivity_ok = True
    for u in range(n):
        for v in range(u + 1, n):
            if (comp_g[u] == comp_g[v]) and (comp_h[u] != comp_h[v]):
                connectivity_ok = False
                break
        if not connectivity_ok:
            break

    # (c) Stretch compliance via APSP Dijkstra.
    max_stretch = 0.0
    worst_pair: Optional[Tuple[int, int]] = None
    stretch_ok = True
    for u in range(n):
        dg = _dijkstra(adj_g, u, n)
        dh = _dijkstra(adj_h, u, n)
        for v in range(u + 1, n):
            if dg[v] == float('inf') or dg[v] == 0:
                continue
            if dh[v] == float('inf'):
                stretch_ok = False
                worst_pair = (u, v)
                max_stretch = float('inf')
                break
            ratio = dh[v] / dg[v]
            if ratio > max_stretch:
                max_stretch = ratio
                worst_pair = (u, v)
            # Tiny epsilon for float rounding (weights have 1e-12 tie-breaking).
            if ratio > stretch_limit + 1e-6:
                stretch_ok = False
        if not stretch_ok and max_stretch == float('inf'):
            break

    return {
        'size_ok': size_ok,
        'size': len(spanner),
        'size_bound': bound,
        'connectivity_ok': connectivity_ok,
        'stretch_ok': stretch_ok,
        'max_stretch': max_stretch,
        'stretch_limit': stretch_limit,
        'worst_pair': worst_pair,
    }


def correctness_experiment(
    *,
    sizes=(20, 40, 60),
    densities=(0.15, 0.3, 0.5),
    ks=(2, 3, 4),
    trials_per_config: int = 3,
    base_seed: int = 1000,
    csv_path: str = 'results_correctness.csv',
) -> List[Dict[str, object]]:
    """
    Run correctness verification across a grid of (n, p, k, trial). Each
    trial spawns one random graph + one spanner; we then check the three
    invariants. Results are logged to CSV.
    """
    print("\n" + "=" * 78)
    print("EXPERIMENT 1 — CORRECTNESS (size, connectivity, stretch)".center(78))
    print("=" * 78)

    rows: List[Dict[str, object]] = []
    fail_count = 0

    for n in sizes:
        for p in densities:
            for k in ks:
                for t in range(trials_per_config):
                    seed = base_seed + t
                    edges = generate_random_graph(n, p=p, seed=seed)
                    if not edges:
                        continue
                    t0 = time.perf_counter()
                    spanner = compute_spanner(edges, n, k, seed=seed)
                    elapsed = time.perf_counter() - t0

                    inv = verify_invariants(edges, spanner, n, k)
                    passed = inv['size_ok'] and inv['connectivity_ok'] and inv['stretch_ok']
                    if not passed:
                        fail_count += 1

                    row = {
                        'n': n,
                        'p': p,
                        'k': k,
                        'trial': t,
                        'm': len(edges),
                        'spanner_size': inv['size'],
                        'size_bound': round(inv['size_bound'], 2),
                        'size_ok': inv['size_ok'],
                        'connectivity_ok': inv['connectivity_ok'],
                        'stretch_ok': inv['stretch_ok'],
                        'max_stretch': (
                            round(inv['max_stretch'], 4)
                            if inv['max_stretch'] != float('inf') else 'inf'
                        ),
                        'stretch_limit': inv['stretch_limit'],
                        'time_s': round(elapsed, 4),
                        'passed': passed,
                    }
                    rows.append(row)

                    flag = '✓' if passed else '✗'
                    print(
                        f"  {flag} n={n:<4} p={p:<4} k={k} trial={t}  "
                        f"|E|={len(edges):<5} |E_S|={inv['size']:<5} "
                        f"max_stretch={row['max_stretch']}"
                    )

    _write_csv(csv_path, rows)
    print("-" * 78)
    print(f"Total configs: {len(rows)}   Failures: {fail_count}")
    print(f"CSV written to: {csv_path}")
    return rows


# ============================================================================
# Experiment 2 — Large-scale benchmark with sampled-pair stretch
# ============================================================================

def sampled_stretch(
    edges: List[Tuple[int, int, float]],
    spanner: List[Tuple[int, int, float]],
    n: int,
    k: int,
    *,
    num_pairs: int = 400,
    seed: int = 0,
) -> Dict[str, object]:
    """
    Estimate empirical stretch from `num_pairs` random source-destination
    pairs. Pairs are grouped by source so each Dijkstra is reused across
    every target sharing that source.
    """
    stretch_limit = 2 * k - 1
    rng = random.Random(seed)

    seen = set()
    by_source: Dict[int, List[int]] = defaultdict(list)
    attempts = 0
    while len(seen) < num_pairs and attempts < num_pairs * 10:
        attempts += 1
        u = rng.randrange(n)
        v = rng.randrange(n)
        if u == v:
            continue
        key = (u, v) if u < v else (v, u)
        if key in seen:
            continue
        seen.add(key)
        by_source[u].append(v)

    adj_g = _build_adj(edges)
    adj_h = _build_adj(spanner)

    finite_ratios: List[float] = []
    violations = 0
    disconnected = 0
    max_stretch = 0.0

    for src, targets in by_source.items():
        dg = _dijkstra(adj_g, src, n)
        dh = _dijkstra(adj_h, src, n)
        for tgt in targets:
            if dg[tgt] == float('inf') or dg[tgt] == 0:
                continue
            if dh[tgt] == float('inf'):
                disconnected += 1
                continue
            ratio = dh[tgt] / dg[tgt]
            finite_ratios.append(ratio)
            if ratio > max_stretch:
                max_stretch = ratio
            if ratio > stretch_limit + 1e-6:
                violations += 1

    avg = sum(finite_ratios) / len(finite_ratios) if finite_ratios else float('nan')
    return {
        'pairs_sampled': len(seen),
        'pairs_evaluated': len(finite_ratios),
        'disconnected_in_spanner': disconnected,
        'max_stretch': max_stretch,
        'avg_stretch': avg,
        'violations': violations,
        'stretch_limit': stretch_limit,
    }


def large_scale_benchmark(
    *,
    sizes=(1000, 2000, 4000, 7000, 10000),
    densities=(0.005, 0.02),
    ks=(2, 3),
    sample_pairs: int = 400,
    base_seed: int = 7000,
    csv_path: str = 'results_benchmark.csv',
) -> List[Dict[str, object]]:
    """
    Run the algorithm on large random graphs and record how runtime and
    spanner size scale with n. Stretch is estimated from `sample_pairs`
    random pairs to keep verification tractable at n=10,000.
    """
    print("\n" + "=" * 78)
    print(
        f"EXPERIMENT 2 — LARGE-SCALE BENCHMARK (n={sizes[0]}..{sizes[-1]})".center(78)
    )
    print("=" * 78)
    print(f"Stretch estimated from {sample_pairs} sampled (s,t) pairs per run.\n")

    rows: List[Dict[str, object]] = []

    print(
        f"  {'n':>6} {'p':>6} {'k':>3} {'m':>10} {'|E_S|':>10} "
        f"{'ratio':>7} {'time(s)':>9} {'max_str':>9} {'avg_str':>9}"
    )
    print("  " + "-" * 76)

    for n in sizes:
        for p in densities:
            edges = generate_random_graph(n, p=p, seed=base_seed)
            m = len(edges)
            if m == 0:
                continue
            for k in ks:
                t0 = time.perf_counter()
                spanner = compute_spanner(edges, n, k, seed=base_seed)
                elapsed = time.perf_counter() - t0
                size_ratio = len(spanner) / m if m else 0.0

                stretch_info = sampled_stretch(
                    edges, spanner, n, k,
                    num_pairs=sample_pairs, seed=base_seed,
                )

                row = {
                    'n': n,
                    'p': p,
                    'k': k,
                    'm': m,
                    'spanner_size': len(spanner),
                    'size_ratio': round(size_ratio, 4),
                    'size_bound': round(_size_bound(n, k), 2),
                    'time_s': round(elapsed, 4),
                    'pairs_sampled': stretch_info['pairs_sampled'],
                    'pairs_evaluated': stretch_info['pairs_evaluated'],
                    'disconnected_pairs': stretch_info['disconnected_in_spanner'],
                    'max_stretch': round(stretch_info['max_stretch'], 4),
                    'avg_stretch': round(stretch_info['avg_stretch'], 4),
                    'violations': stretch_info['violations'],
                    'stretch_limit': stretch_info['stretch_limit'],
                }
                rows.append(row)

                print(
                    f"  {n:>6} {p:>6} {k:>3} {m:>10} {len(spanner):>10} "
                    f"{size_ratio:>7.3f} {elapsed:>9.3f} "
                    f"{stretch_info['max_stretch']:>9.4f} "
                    f"{stretch_info['avg_stretch']:>9.4f}"
                )

    _write_csv(csv_path, rows)
    print("\n" + "-" * 78)
    print(f"CSV written to: {csv_path}")
    return rows


# ============================================================================
# Experiment 3 — Worst-case diluted clique (Prof. Elkin's feedback)
# ============================================================================

def generate_diluted_clique(n: int, k: int, seed: int = 42) -> List[Tuple[int, int, float]]:
    """
    Unweighted clique of size n, diluted by keeping each edge independently
    with probability p = n^(1/k) / n. All weights = 1.
    """
    rng = random.Random(seed)
    p = (n ** (1.0 / k)) / n
    edges: List[Tuple[int, int, float]] = []
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < p:
                edges.append((i, j, 1.0))
    return edges


def worst_case_experiment(
    *,
    sizes=(1000, 2000, 4000, 7000, 10000),
    ks=(2, 3, 4),
    sample_pairs: int = 400,
    base_seed: int = 9000,
    csv_path: str = 'results_worst_case.csv',
) -> List[Dict[str, object]]:
    """
    Diluted-clique benchmark. For each (n, k) we generate an unweighted
    graph where each of the n(n−1)/2 possible edges survives independently
    with probability n^(1/k)/n, run the spanner, and record the
    sparsification ratio |E_S|/|E|. Stretch is estimated from sampled
    pairs so n=10000 stays tractable.
    """
    print("\n" + "=" * 78)
    print(
        f"EXPERIMENT 3 — WORST-CASE DILUTED CLIQUE (n={sizes[0]}..{sizes[-1]})".center(78)
    )
    print("=" * 78)
    print(
        "p = n^(1/k) / n  →  expected |E| ≈ ½·n^(1+1/k); algorithm is already\n"
        "near the size lower bound, so sparsification ratio should stay close to 1.\n"
    )

    rows: List[Dict[str, object]] = []

    print(
        f"  {'n':>6} {'k':>3} {'p':>10} {'m':>10} {'|E_S|':>10} "
        f"{'sparsif':>9} {'time(s)':>9} {'max_str':>9} {'avg_str':>9}"
    )
    print("  " + "-" * 76)

    for n in sizes:
        for k in ks:
            p = (n ** (1.0 / k)) / n
            edges = generate_diluted_clique(n, k, seed=base_seed)
            m = len(edges)
            if m == 0:
                continue

            t0 = time.perf_counter()
            spanner = compute_spanner(edges, n, k, seed=base_seed)
            elapsed = time.perf_counter() - t0
            sparsif = len(spanner) / m

            stretch_info = sampled_stretch(
                edges, spanner, n, k,
                num_pairs=sample_pairs, seed=base_seed,
            )

            row = {
                'n': n,
                'k': k,
                'p': round(p, 6),
                'm': m,
                'spanner_size': len(spanner),
                'sparsification_ratio': round(sparsif, 4),
                'size_bound': round(_size_bound(n, k), 2),
                'time_s': round(elapsed, 4),
                'pairs_sampled': stretch_info['pairs_sampled'],
                'pairs_evaluated': stretch_info['pairs_evaluated'],
                'disconnected_pairs': stretch_info['disconnected_in_spanner'],
                'max_stretch': round(stretch_info['max_stretch'], 4),
                'avg_stretch': round(stretch_info['avg_stretch'], 4),
                'violations': stretch_info['violations'],
                'stretch_limit': stretch_info['stretch_limit'],
            }
            rows.append(row)

            print(
                f"  {n:>6} {k:>3} {p:>10.6f} {m:>10} {len(spanner):>10} "
                f"{sparsif:>9.3f} {elapsed:>9.3f} "
                f"{stretch_info['max_stretch']:>9.4f} "
                f"{stretch_info['avg_stretch']:>9.4f}"
            )

    _write_csv(csv_path, rows)
    print("\n" + "-" * 78)
    print(f"CSV written to: {csv_path}")
    return rows


# ============================================================================
# CSV utility
# ============================================================================

def _write_csv(path: str, rows: List[Dict[str, object]]) -> None:
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with open(path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


# ============================================================================
# Entry point
# ============================================================================

def main() -> None:
    correctness_experiment()
    large_scale_benchmark()
    worst_case_experiment()


if __name__ == '__main__':
    main()
