# Baswana–Sen Sparse Spanner: Implementation and Empirical Evaluation

**Course:** Mini-Project in Algorithms  
**Students:** Hagar Rosenthal, Eden Zeira  
**Advisor:** Prof. Michael Elkin  
**Institution:** Ben-Gurion University of the Negev

---

## Overview

This project implements and empirically evaluates the randomized graph spanner algorithm introduced by Baswana and Sen:

> Surender Baswana and Sandeep Sen.  
> *A Simple and Linear Time Randomized Algorithm for Computing Sparse Spanners in Weighted Graphs.*  
> ICALP 2003 / Random Structures & Algorithms, 30(4):532–563, 2007.

Given a weighted undirected graph G = (V, E) and an integer parameter k ≥ 2, the algorithm produces a **(2k − 1)-spanner**: a subgraph H = (V, E_S) satisfying

```
dist_H(u, v) ≤ (2k − 1) · dist_G(u, v)   for all u, v ∈ V
```

with expected edge count O(k · n^(1+1/k)) and expected running time O(k · m). This is optimal up to constant factors, matching the lower bound implied by Erdős' girth conjecture.

The algorithm works through a **randomized clustering process** that runs in k − 1 phases, followed by a vertex-cluster joining phase. Crucially, it never computes any shortest paths or BFS trees — all decisions are purely local, based on edge weights between adjacent clusters.

---

## Repository Structure

```
mini_project/
├── spanner_algorithm.py     Core algorithm implementation
├── test_spanner.py          Experimental driver: three evaluation experiments
├── csv_results/             Output directory for experimental results
│   ├── results_correctness.csv   Experiment 1 output
│   ├── results_benchmark.csv     Experiment 2 output
│   └── results_worst_case.csv    Experiment 3 output
└── README.md                This file
```

### Key files

**`spanner_algorithm.py`**  
Contains three classes and one convenience function:

- `Edge` - represents one directed half edge in an augmented adjacency list. Each undirected edge is stored as two `Edge` objects that point at each other via twin pointers, enabling O(1) symmetric deletion.
- `AugmentedGraph` - adjacency-list graph supporting O(1) edge deletion.
- `BaswanaSenSpanner` - the full algorithm. `compute_spanner()` runs Phase 1 (k − 1 cluster-forming iterations) followed by Phase 2 (vertex-cluster joining) and returns the spanner as a list of `(u, v, weight)` tuples.
- `compute_spanner(edges, n, k, seed)` - a stateless convenience wrapper that handles weight tie breaking and returns the spanner directly.

**`test_spanner.py`**  
Defines three self contained experiments along with shared Dijkstra and BFS helpers. Running this file executes all three experiments in sequence and writes results to CSV.

**`csv_results/`**  
Pre generated example output included for reference, so the results can be reviewed without running the experiments. When you run `test_spanner.py`, new CSV files are written to the directory the script is executed from, not here.

---

## Prerequisites and Installation

The project has **no external dependencies**. It uses only the Python standard library (`heapq`, `csv`, `random`, `collections`, `time`).

**Requirements:**
- Python 3.9 or newer

**Verify your Python version:**
```bash
python --version
# or, on systems where both Python 2 and 3 are installed:
python3 --version
```

**Clone the repository:**
```bash
git clone <repository-url>
cd mini_project
```

No package installation step is needed. The project is ready to run immediately after cloning.

---

## How to Run

### Run all three experiments

```bash
python test_spanner.py
```

This executes the three experiments sequentially and writes three CSV files (`results_correctness.csv`, `results_benchmark.csv`, `results_worst_case.csv`) to the directory you run the script from. Typical total runtime on a modern laptop is under two minutes.

### Use the algorithm in your own code

**Simple interface** — pass a list of edges and get back the spanner:

```python
from spanner_algorithm import compute_spanner

# Each edge is a (u, v, weight) tuple; vertices are 0-indexed integers
edges = [
    (0, 1, 2.5),
    (1, 2, 3.0),
    (2, 3, 1.5),
    (0, 3, 8.0),
    (1, 3, 4.0),
]
spanner = compute_spanner(edges, n=4, k=2, seed=42)
# Returns a list of (u, v, weight) tuples
# Stretch guarantee: ≤ 2k−1 = 3
# Expected size: ≤ k · n^(1+1/k) ≈ 2 · 4^1.5 ≈ 16 edges
```

**Incremental interface** — build the graph edge by edge, then compute:

```python
from spanner_algorithm import BaswanaSenSpanner

algo = BaswanaSenSpanner(n=100, k=3, seed=42)
for u, v, w in my_edges:
    algo.add_edge(u, v, w)

spanner = algo.compute_spanner()  # Returns List[Tuple[int, int, float]]
```

The `seed` parameter makes the output fully reproducible. Omitting it uses Python's default random state.

---

## Experiments and Evaluation

The test suite contains three experiments, each targeting a different aspect of the algorithm's behavior.

### Experiment 1 - Correctness Verification

**Purpose:** Confirm that the spanner satisfies all three formal guarantees on small and medium sized graphs where exact verification is affordable.


**Parameter grid:**

| Parameter | Values tested |
|-----------|--------------|
| n (vertices) | 20, 40, 60 |
| p (edge probability) | 0.15, 0.30, 0.50 |
| k (stretch parameter) | 2, 3, 4 |
| Trials per configuration | 3 |

**What is checked for each graph:**
1. **Size bound** - is `|E_S| ≤ k · n^(1+1/k)`?
2. **Connectivity** - does H preserve the connected component structure of G? Every pair of vertices connected in G must also be connected in H.
3. **Stretch compliance** - is `dist_H(u, v) / dist_G(u, v) ≤ 2k − 1` for every reachable pair?

Stretch is verified using **full all-pairs shortest paths** (one Dijkstra per source vertex), which is feasible because n ≤ 60.

---

### Experiment 2 - Large-Scale Performance Benchmark

**Purpose:** Measure how the algorithm's running time and the spanner's size scale with graph size, and verify that the stretch guarantee holds in practice.


**Parameter grid:**

| Parameter | Values tested |
|-----------|--------------|
| n (vertices) | 1,000 · 2,000 · 4,000 · 7,000 · 10,000 |
| p (edge probability) | 0.005, 0.02 |
| k (stretch parameter) | 2, 3 |

**Stretch estimation:** Full APSP is not practical at n = 10,000. Instead, stretch is estimated from **400 randomly sampled (s, t) pairs**. Pairs are grouped by source so that each Dijkstra computation is reused across all targets sharing that source, keeping verification cost bounded regardless of n.

---

### Experiment 3 - Worst-Case Diluted Clique

**Purpose:** Stress test the algorithm on graphs designed to be adversarial inputs that already have close to the minimum number of edges any (2k−1)-spanner must contain.


**Parameter grid:**

| Parameter | Values tested |
|-----------|--------------|
| n (vertices) | 1,000 · 2,000 · 4,000 · 7,000 · 10,000 |
| k (stretch parameter) | 2, 3, 4 |

**Graph construction:** Each graph starts as a complete graph on n vertices and then each of the n(n − 1)/2 candidate edges is kept independently with probability p = n^(1/k) / n. All retained edges are assigned weight 1 (unweighted). This survival probability is chosen so that the expected edge count is roughly ½ · n^(1 + 1/k) - exactly the theoretical lower bound on spanner size, making these graphs a natural stress test: the input is already near optimal in density, so there is little room for the algorithm to compress it further.

Stretch is estimated from 400 sampled pairs.

---

## Output Format

Running `test_spanner.py` produces three CSV files in the directory the script is executed from. The `csv_results/` folder in this repository contains pre generated example output with the same format.

### `results_correctness.csv`

One row per (n, p, k, trial) combination.

| Column | Description |
|--------|-------------|
| `n` | Number of vertices |
| `p` | Edge probability used to generate the graph |
| `k` | Stretch parameter |
| `trial` | Trial index within this configuration (0-based) |
| `m` | Actual number of edges in the generated graph |
| `spanner_size` | Number of edges in the computed spanner |
| `size_bound` | Theoretical size bound: k · n^(1+1/k) |
| `size_ok` | `True` if `spanner_size ≤ size_bound` |
| `connectivity_ok` | `True` if H preserves all connected components of G |
| `stretch_ok` | `True` if no pair exceeds the (2k−1) stretch limit |
| `max_stretch` | Largest observed `dist_H(u,v) / dist_G(u,v)` across all reachable pairs |
| `stretch_limit` | The stretch limit for this k, equal to 2k−1 |
| `time_s` | Wall-clock time in seconds to compute the spanner |
| `passed` | `True` if all three invariants hold |

---

### `results_benchmark.csv`

One row per (n, p, k) combination.

| Column | Description |
|--------|-------------|
| `n` | Number of vertices |
| `p` | Edge probability |
| `k` | Stretch parameter |
| `m` | Actual number of edges in the graph |
| `spanner_size` | Number of edges in the computed spanner |
| `size_ratio` | `spanner_size / m` — fraction of original edges retained |
| `size_bound` | Theoretical size bound: k · n^(1+1/k) |
| `time_s` | Wall-clock time in seconds to compute the spanner |
| `pairs_sampled` | Number of (s, t) pairs drawn for stretch estimation |
| `pairs_evaluated` | Pairs where both endpoints were reachable (finite distance in G) |
| `disconnected_pairs` | Pairs connected in G but disconnected in H (should be 0) |
| `max_stretch` | Largest observed stretch ratio among evaluated pairs |
| `avg_stretch` | Mean stretch ratio among evaluated pairs |
| `violations` | Number of pairs whose stretch exceeded 2k−1 (should be 0) |
| `stretch_limit` | The stretch limit for this k, equal to 2k−1 |

---

### `results_worst_case.csv`

One row per (n, k) combination.

| Column | Description |
|--------|-------------|
| `n` | Number of vertices |
| `k` | Stretch parameter |
| `p` | Edge survival probability used: n^(1/k) / n |
| `m` | Actual number of edges in the diluted clique |
| `spanner_size` | Number of edges in the computed spanner |
| `sparsification_ratio` | `spanner_size / m` — how much the spanner reduces edge count |
| `size_bound` | Theoretical size bound: k · n^(1+1/k) |
| `time_s` | Wall-clock time in seconds to compute the spanner |
| `pairs_sampled` | Number of (s, t) pairs drawn for stretch estimation |
| `pairs_evaluated` | Pairs with finite distance in G |
| `disconnected_pairs` | Pairs connected in G but disconnected in H (should be 0) |
| `max_stretch` | Largest observed stretch ratio among evaluated pairs |
| `avg_stretch` | Mean stretch ratio among evaluated pairs |
| `violations` | Number of pairs whose stretch exceeded 2k−1 (should be 0) |
| `stretch_limit` | The stretch limit for this k, equal to 2k−1 |

A `sparsification_ratio` close to 1 in Experiment 3 indicates that the input graph was already near optimal in density and the algorithm could not reduce it further  confirming that the lower bound is essentially tight.

