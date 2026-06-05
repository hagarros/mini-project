# Baswana–Sen Sparse Spanner — Implementation & Empirical Study

Python implementation and experimental evaluation of the linear-time randomized
algorithm from:

> Surender Baswana and Sandeep Sen.
> *A Simple and Linear Time Randomized Algorithm for Computing Sparse Spanners
> in Weighted Graphs.* ICALP 2003 / Random Structures & Algorithms 2007.

**Student:** Hagar Rosenthal · **Advisor:** Prof. Michael Elkin · Ben-Gurion University

---

## What is a (2k−1)-spanner?

Given a weighted undirected graph G = (V, E), a *t-spanner* is a subgraph
H = (V, E_S) with E_S ⊆ E such that for every pair u, v ∈ V:

```
dist_H(u, v) ≤ t · dist_G(u, v)
```

For an integer parameter k > 1, the Baswana–Sen algorithm produces a
**(2k − 1)-spanner** with the following guarantees:

| Quantity         | Bound                        |
|------------------|------------------------------|
| Stretch          | 2k − 1                       |
| Expected size    | O(k · n^(1+1/k))             |
| Expected runtime | O(k · m)                     |

The size matches the lower bound implied by Erdős' girth conjecture up to a
factor of k.

---

## Repository layout

```
mini-project/
├── spanner_algorithm.py   Core algorithm: Edge, AugmentedGraph, BaswanaSenSpanner, compute_spanner()
├── test_spanner.py        Two experiments: correctness invariants + large-scale benchmark
└── README.md              This file
```

No external dependencies — pure Python 3.9+ (`heapq`, `csv`, `random`, `collections`).

---

## Quick start

```bash
python3 test_spanner.py
# → writes results_correctness.csv and results_benchmark.csv
```

### Programmatic API

```python
from spanner_algorithm import compute_spanner

edges = [(0, 1, 2.5), (1, 2, 3.0), (2, 3, 1.5), (0, 3, 8.0), (1, 3, 4.0)]
spanner = compute_spanner(edges, n=4, k=2, seed=42)
# spanner is a list of (u, v, weight) tuples; len(spanner) ≤ k · n^(1+1/k)
```

For incremental graph construction:

```python
from spanner_algorithm import BaswanaSenSpanner

algo = BaswanaSenSpanner(n=100, k=3, seed=42)
for u, v, w in my_edges:
    algo.add_edge(u, v, w)
spanner = algo.compute_spanner()
```

---

## Algorithm at a glance

The algorithm is purely *local* — it never computes BFS levels or shortest-path
trees. Two phases:

**Phase 1 — Forming clusters** (k − 1 iterations). Each iteration:
1. Sample each current cluster independently with probability n^(−1/k).
2. For every unsampled vertex v, find the cheapest edge to *any* sampled cluster.
3. Add carefully chosen edges to the spanner (cases (a) and (b) of §4.2 in the paper).
4. Discard intra-cluster edges of the new clustering.

The clustering radius grows by at most one per iteration (Theorem 4.1).

**Phase 2 — Vertex–cluster joining**. For every remaining vertex v and every
neighboring cluster c, add the lightest edge between v and c.

Theorem 4.2 + the Phase-2 argument together yield the (2k − 1) stretch.

### Implementation notes

- **Augmented adjacency lists with twin pointers**
  ([spanner_algorithm.py:12-31](spanner_algorithm.py#L12-L31)) — every undirected
  edge is stored twice and the two `Edge` objects point at each other, giving
  O(1) symmetric deletion.
- **Tie-breaking** — distinct weights are guaranteed by adding `idx · 1e-12`
  to each input weight ([spanner_algorithm.py:344-348](spanner_algorithm.py#L344-L348)).
- **O(1) duplicate detection** — `BaswanaSenSpanner` keeps a parallel
  `spanner_set` so `_add_to_spanner` is O(1) instead of the original
  O(|E_S|) list comprehension. This was the bottleneck above n ≈ 1000.

---

## Empirical evaluation

`test_spanner.py` runs two experiments end-to-end and writes per-row CSVs:

| Experiment | What it does | Output |
|---|---|---|
| `correctness_experiment` | Sweeps (n, p, k, trial) over small/medium random graphs. On every graph verifies three invariants: size ≤ k·n^(1+1/k), connectivity preserved, max stretch ≤ 2k−1 (full APSP Dijkstra). | `results_correctness.csv` |
| `large_scale_benchmark` | Random graphs at n = 1k…10k. Records runtime and size ratio; estimates stretch from 400 random (s, t) pairs (full APSP at n=10k would be ~n³ log n). | `results_benchmark.csv` |

Both experiments reuse one Dijkstra per source by grouping sampled targets per
source — measurable cost stays at ≤400 shortest-path computations regardless of
graph size.

### Stretch verification — exact vs. sampled

| Mode        | Cost                                              | Used by               |
|-------------|---------------------------------------------------|-----------------------|
| Full APSP   | n × Dijkstra (~n² log n total)                    | `correctness_experiment` (small n) |
| Sampled (~400 pairs) | ≤400 Dijkstras (one per distinct source) | `large_scale_benchmark` (n ≥ 1000) |

The sampled variant draws uniform (u, v) pairs via `random.Random(seed).randrange`
and reports the number of pairs actually evaluated, so the source of every
stretch number stays explicit in the CSV.

---

## Reproducing results

Every randomized component takes a `seed` argument. The same seed → identical
spanner (modulo Python's hash randomization, which the algorithm does not depend
on). The benchmark and correctness CSVs include the seed implicitly via the
trial index and base seed declared in their respective driver functions.

---

## Theoretical context

**Lower bound.** Erdős' girth conjecture states that for every k there exist
graphs with Ω(n^(1+1/k)) edges and girth > 2k. Such a graph admits no proper
spanner with stretch < 2k+1, so Ω(n^(1+1/k)) edges are necessary for any
(2k−1)-spanner in the worst case.

**Prior algorithms** (running times for the (2k−1)-spanner with size O(k·n^(1+1/k))):
- Althöfer et al. (1993): O(m · n^(1+1/k))
- Cohen (1998): O(m · n^(1/k)) with stretch (2k+ε)
- Thorup–Zwick (2005): O(k · m · n^(1/k))
- **Baswana–Sen (2003):** O(k · m) — linear in the input.

---

## Citation

```bibtex
@article{baswana2007simple,
  title   = {A simple and linear time randomized algorithm for computing
             sparse spanners in weighted graphs},
  author  = {Baswana, Surender and Sen, Sandeep},
  journal = {Random Structures \& Algorithms},
  volume  = {30},
  number  = {4},
  pages   = {532--563},
  year    = {2007}
}
```
