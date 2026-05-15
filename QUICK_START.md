# Quick Start Guide

## Installation

No dependencies needed! Just Python 3.7+

```bash
cd "/Users/hagar.rosenthal/Projects/mini project"
```

## Run Tests

```bash
python test_spanner.py
```

## Run Examples

```bash
python example_usage.py
```

## Basic Usage

```python
from spanner_algorithm import compute_spanner

# Define graph: list of (u, v, weight) tuples
edges = [
    (0, 1, 2.5),
    (1, 2, 3.0),
    (2, 3, 1.5),
    (0, 3, 8.0)
]

# Compute (2k-1)-spanner
n = 4  # number of vertices (0 to n-1)
k = 2  # stretch parameter (gives 3-spanner)

spanner = compute_spanner(edges, n=n, k=k, seed=42)

print(f"Spanner has {len(spanner)} edges")
for u, v, w in spanner:
    print(f"  {u} -- {v}: {w}")
```

## Key Parameters

- **n**: Number of vertices (labeled 0 to n-1)
- **k**: Stretch parameter
  - k=2 → 3-spanner
  - k=3 → 5-spanner
  - k=4 → 7-spanner
- **seed**: Random seed for reproducibility (optional)

## Expected Performance

- **Time**: O(km) where m = number of edges
- **Spanner size**: O(kn^(1+1/k)) edges
- **Stretch**: 2k-1

## Trade-offs

Higher k:
- ✅ Smaller spanner (fewer edges)
- ❌ Worse approximation (higher stretch)

Lower k:
- ✅ Better approximation (lower stretch)
- ❌ Larger spanner (more edges)

## Common Use Cases

### 1. Graph Compression
```python
# Reduce large graph to sparse representation
spanner = compute_spanner(large_graph, n, k=3)
compression_ratio = len(spanner) / len(large_graph)
```

### 2. Approximate Distance Oracle
```python
# Preprocess for fast distance queries
spanner = compute_spanner(graph, n, k=2)
# Query distances using only spanner edges
# Approximation: at most 3x true distance
```

### 3. Network Design
```python
# Find sparse network with bounded routing cost
cost_edges = [(u, v, cost) for u, v, cost in connections]
spanner = compute_spanner(cost_edges, n, k=2)
total_cost = sum(w for _, _, w in spanner)
```

## Files

- `spanner_algorithm.py` - Main implementation
- `test_spanner.py` - Test suite  
- `example_usage.py` - 6 detailed examples
- `visualize_spanner.py` - Analysis and stretch verification
- `example_stretch_verification.py` - Empirical verification examples
- `README.md` - Full documentation
- `STRETCH_VERIFICATION.md` - Stretch verification guide

## Algorithm Details

The algorithm works in two phases:

**Phase 1** (k-1 iterations):
- Sample clusters with probability n^(-1/k)
- Assign vertices to nearest sampled cluster
- Add strategic edges to preserve distances

**Phase 2**:
- For each vertex-cluster pair
- Add lightest connecting edge

Key innovation: **No distance computation needed!**

## Troubleshooting

### Issue: KeyError on vertices
**Solution**: Make sure all vertices are numbered 0 to n-1

### Issue: Too many edges in spanner
**Solution**: Try higher k value (but increases stretch)

### Issue: Different results each run
**Solution**: Set `seed` parameter for reproducibility

### Issue: Slow performance
**Expectation**: O(km) time is already optimal
**Tip**: For very large graphs (>100k edges), consider distributed implementation

## For Your Project

### Working with Prof. Elkin on Graph Embeddings

This spanner algorithm is useful for:

1. **Sparse graph representation**
   - Reduce storage from O(m) to O(kn^(1+1/k))
   - Preserve approximate distances

2. **Embedding preprocessing**
   - Compute spanner first
   - Run embedding on smaller graph
   - Bounded distortion guarantee

3. **Distance approximation**
   - Use spanner for (2k-1)-approximate distances
   - Much faster than exact computation

### Integration Example

```python
from spanner_algorithm import compute_spanner

# Your graph data
edges = load_graph_data()  # (u, v, weight) tuples
n = get_num_vertices()

# Compute sparse representation
k = 3  # 5x stretch
spanner = compute_spanner(edges, n, k, seed=42)

# Use spanner for embedding
embedding = your_embedding_algorithm(spanner)

# Verify quality
distortion = compute_distortion(original=edges, 
                                embedded=embedding,
                                spanner=spanner)
```

## Next Steps

1. Read full [README.md](README.md) for theory
2. Study [example_usage.py](example_usage.py) for patterns
3. Check [test_spanner.py](test_spanner.py) for edge cases
4. Experiment with your own graphs!

## Need Help?

- Check examples in `example_usage.py`
- Read algorithm details in comments
- Refer to original paper (Baswana-Sen, ICALP 2003)
- Consult with Prof. Elkin

---

**Good luck with your research! 🚀**
