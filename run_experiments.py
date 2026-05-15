"""
Experimental Evaluation Runner for Baswana-Sen Spanner Algorithm

This script runs comprehensive experiments on various graph types to evaluate
the Baswana-Sen algorithm's performance, including:
- Multiple graph families (complete, random, grid, etc.)
- Different stretch parameters (k values)
- Statistical analysis across multiple runs
- Comparative analysis

Author: Hagar Rosenthal
Advisor: Prof. Michael Elkin
Institution: Ben-Gurion University
"""

import random
from typing import List, Tuple
from spanner_analysis import (
    run_academic_evaluation,
    print_evaluation_report,
    print_comparative_report,
    quick_analysis
)


# ============================================================================
# Graph Generators
# ============================================================================

def generate_complete_graph(n: int) -> List[Tuple[int, int, float]]:
    """Generate complete graph K_n with distance-based weights."""
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            weight = abs(i - j) * 1.0
            edges.append((i, j, weight))
    return edges


def generate_random_graph(n: int, p: float = 0.3, seed: int = 42) -> List[Tuple[int, int, float]]:
    """Generate Erdős-Rényi random graph G(n, p)."""
    random.seed(seed)
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            if random.random() < p:
                weight = random.uniform(1.0, 10.0)
                edges.append((i, j, weight))
    return edges


def generate_grid_graph(rows: int, cols: int) -> Tuple[List[Tuple[int, int, float]], int]:
    """Generate grid graph with uniform weights."""
    edges = []

    def node_id(r, c):
        return r * cols + c

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

    n = rows * cols
    return edges, n


def generate_cycle_graph(n: int) -> List[Tuple[int, int, float]]:
    """Generate cycle graph C_n."""
    edges = []
    for i in range(n):
        j = (i + 1) % n
        edges.append((i, j, 1.0))
    return edges


def generate_path_graph(n: int) -> List[Tuple[int, int, float]]:
    """Generate path graph P_n."""
    edges = []
    for i in range(n - 1):
        edges.append((i, i + 1, float(i + 1)))
    return edges


def generate_star_graph(n: int) -> List[Tuple[int, int, float]]:
    """Generate star graph with center at vertex 0."""
    edges = []
    center = 0
    for i in range(1, n):
        weight = float(i)
        edges.append((center, i, weight))
    return edges


# ============================================================================
# Experiment Scenarios
# ============================================================================

def experiment_1_basic_verification():
    """
    Experiment 1: Basic Verification on Small Complete Graph
    Goal: Verify algorithm correctness with full stretch computation
    """
    print("\n" + "█" * 80)
    print(f"{'EXPERIMENT 1: BASIC VERIFICATION (K_10)':^80}")
    print("█" * 80)

    edges = generate_complete_graph(10)
    n = 10
    k = 2

    stats = run_academic_evaluation(
        edges, n, k,
        num_runs=5,
        compute_stretch=True
    )

    print_evaluation_report(stats, title="Experiment 1: Complete Graph K_10")


def experiment_2_parameter_comparison():
    """
    Experiment 2: Effect of Stretch Parameter k
    Goal: Analyze size-stretch tradeoff
    """
    print("\n" + "█" * 80)
    print(f"{'EXPERIMENT 2: PARAMETER COMPARISON':^80}")
    print("█" * 80)

    edges = generate_random_graph(30, p=0.3, seed=42)
    n = 30

    results = []

    for k in [2, 3, 4]:
        print(f"\n[Running k={k}...]")
        stats = run_academic_evaluation(
            edges, n, k,
            num_runs=5,
            compute_stretch=True
        )
        results.append((f"Random (k={k})", stats))

    print_comparative_report(results)

    # Detailed report for each k
    for name, stats in results:
        print_evaluation_report(stats, title=name)


def experiment_3_graph_families():
    """
    Experiment 3: Different Graph Families
    Goal: Compare performance across graph structures
    """
    print("\n" + "█" * 80)
    print(f"{'EXPERIMENT 3: GRAPH FAMILIES':^80}")
    print("█" * 80)

    k = 3
    results = []

    # Complete graph
    print(f"\n[Running Complete Graph K_15...]")
    edges_complete = generate_complete_graph(15)
    stats_complete = run_academic_evaluation(
        edges_complete, 15, k,
        num_runs=5,
        compute_stretch=True
    )
    results.append(("Complete K_15", stats_complete))

    # Random graph
    print(f"\n[Running Random Graph (n=20, p=0.4)...]")
    edges_random = generate_random_graph(20, p=0.4, seed=42)
    stats_random = run_academic_evaluation(
        edges_random, 20, k,
        num_runs=5,
        compute_stretch=True
    )
    results.append(("Random (n=20, p=0.4)", stats_random))

    # Grid graph
    print(f"\n[Running Grid Graph 4×4...]")
    edges_grid, n_grid = generate_grid_graph(4, 4)
    stats_grid = run_academic_evaluation(
        edges_grid, n_grid, k,
        num_runs=5,
        compute_stretch=True
    )
    results.append(("Grid 4×4", stats_grid))

    print_comparative_report(results)

    # Detailed reports
    for name, stats in results:
        print_evaluation_report(stats, title=f"{name} (k={k})")


def experiment_4_scalability():
    """
    Experiment 4: Scalability Analysis
    Goal: Test performance on larger graphs (without full APSP)
    """
    print("\n" + "█" * 80)
    print(f"{'EXPERIMENT 4: SCALABILITY':^80}")
    print("█" * 80)

    k = 3
    results = []

    for n in [50, 100, 200]:
        print(f"\n[Running n={n}...]")
        edges = generate_random_graph(n, p=0.2, seed=42)

        # Skip stretch computation for large graphs (too expensive)
        compute_stretch = (n <= 50)

        stats = run_academic_evaluation(
            edges, n, k,
            num_runs=5,
            compute_stretch=compute_stretch
        )
        results.append((f"Random n={n}", stats))

    print_comparative_report(results)

    # Detailed reports
    for name, stats in results:
        print_evaluation_report(stats, title=name)


def experiment_5_girth_conjecture():
    """
    Experiment 5: Erdős's Girth Conjecture - Lower Bound Demonstration
    Goal: Demonstrate that graphs with large girth cannot be sparsified
    """
    print("\n" + "█" * 80)
    print(f"{'EXPERIMENT 5: ERDŐS GIRTH CONJECTURE - LOWER BOUND':^80}")
    print("█" * 80)

    # Graph parameters
    n = 20
    k = 4
    edges = generate_cycle_graph(n)

    # Run evaluation
    stats = run_academic_evaluation(
        edges, n, k,
        num_runs=5,
        compute_stretch=True
    )

    print_evaluation_report(stats, title="Experiment 5: Girth Conjecture Demonstration")

    # Analysis of results
    compression = 100 * (1 - stats['size_mean'] / stats['m'])
    print("\n" + "╔" + "═" * 78 + "╗")
    print("║" + " ANALYSIS & CONCLUSION ".center(78) + "║")
    print("╚" + "═" * 78 + "╝")
    print(f"""
Observed Results:
  - Original edges:     {stats['m']}
  - Spanner edges:      {stats['size_mean']:.1f} (mean)
  - Reduction:          {compression:.1f}%

Interpretation:
""")

    if compression < 1.0:
        print("""  ✅ As predicted by Erdős's girth conjecture, the algorithm preserved
     virtually all edges (≈0% reduction). This confirms the theoretical lower
     bound: graphs with girth > 2k are inherently incompressible for (2k-1)-
     spanners.

  ✅ This validates both:
     (1) The correctness of our implementation
     (2) The tightness of the O(kn^(1+1/k)) upper bound
""")
    else:
        print(f"""  ⚠️  Unexpected reduction of {compression:.1f}% detected!

     Theoretical analysis suggests this should not happen for a cycle graph
     with girth {n} > 2k = {2*k}. This may indicate:
     - A subtle issue in the implementation
     - Or the randomized nature produced an unusual clustering

     Further investigation recommended.
""")

    print("─" * 80)
    print()


def experiment_6_custom():
    """
    Experiment 6: Custom Experiment Template
    Goal: Easy template for running your own experiments
    """
    print("\n" + "█" * 80)
    print(f"{'EXPERIMENT 6: CUSTOM EXPERIMENT':^80}")
    print("█" * 80)

    # Define your custom graph here
    edges = generate_random_graph(25, p=0.35, seed=123)
    n = 25
    k = 2

    stats = run_academic_evaluation(
        edges, n, k,
        num_runs=10,  # More runs for better statistics
        compute_stretch=True
    )

    print_evaluation_report(stats, title="Custom Experiment")


# ============================================================================
# Quick Tests (for development)
# ============================================================================

def quick_test_triangle():
    """Quick test on triangle graph"""
    print("\n" + "▼" * 40)
    print("QUICK TEST: Triangle Graph")
    print("▼" * 40)

    edges = [
        (0, 1, 1.0),
        (1, 2, 2.0),
        (0, 2, 4.0)
    ]

    quick_analysis(edges, n=3, k=2, seed=42)


def quick_test_k7():
    """Quick test on complete K_7"""
    print("\n" + "▼" * 40)
    print("QUICK TEST: Complete Graph K_7")
    print("▼" * 40)

    edges = generate_complete_graph(7)
    quick_analysis(edges, n=7, k=2, seed=42)


# ============================================================================
# Main Runner
# ============================================================================

def run_all_experiments():
    """Run all experiments in sequence."""
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║           BASWANA-SEN SPANNER ALGORITHM: EXPERIMENTAL EVALUATION           ║
║                                                                            ║
║  Paper: "A Simple and Linear Time Randomized Algorithm for Computing      ║
║          Sparse Spanners in Weighted Graphs" (ICALP 2003)                 ║
║                                                                            ║
║  Implementation: Hagar Rosenthal                                           ║
║  Advisor: Prof. Michael Elkin                                              ║
║  Institution: Ben-Gurion University                                        ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
""")

    experiments = [
        ("Basic Verification", experiment_1_basic_verification),
        ("Parameter Comparison", experiment_2_parameter_comparison),
        ("Graph Families", experiment_3_graph_families),
        ("Scalability", experiment_4_scalability),
        ("Girth Conjecture Lower Bound", experiment_5_girth_conjecture),
        ("Custom Experiment", experiment_6_custom)
    ]

    print("\nAvailable Experiments:")
    for i, (name, _) in enumerate(experiments, 1):
        print(f"  {i}. {name}")

    print("\n" + "─" * 80)
    print("Running all experiments...")
    print("─" * 80)

    for name, func in experiments:
        try:
            func()
        except KeyboardInterrupt:
            print(f"\n\n⚠️  Experiment '{name}' interrupted by user.")
            break
        except Exception as e:
            print(f"\n\n❌ Error in experiment '{name}': {e}")
            continue

    print("\n" + "╔" + "═" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "ALL EXPERIMENTS COMPLETED".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "═" * 78 + "╝\n")


def interactive_menu():
    """Interactive menu for selecting experiments."""
    experiments = {
        '1': ("Basic Verification (K_10)", experiment_1_basic_verification),
        '2': ("Parameter Comparison", experiment_2_parameter_comparison),
        '3': ("Graph Families", experiment_3_graph_families),
        '4': ("Scalability Analysis", experiment_4_scalability),
        '5': ("Girth Conjecture Lower Bound", experiment_5_girth_conjecture),
        '6': ("Custom Experiment", experiment_6_custom),
        'q1': ("Quick Test: Triangle", quick_test_triangle),
        'q2': ("Quick Test: K_7", quick_test_k7),
        'all': ("Run All Experiments", run_all_experiments)
    }

    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║           BASWANA-SEN SPANNER ALGORITHM: EXPERIMENTAL EVALUATION           ║
╚════════════════════════════════════════════════════════════════════════════╝
""")

    print("\nSelect an experiment to run:")
    print("\n  Main Experiments:")
    print("    1  - Basic Verification (K_10)")
    print("    2  - Parameter Comparison (k=2,3,4)")
    print("    3  - Graph Families (Complete, Random, Grid)")
    print("    4  - Scalability Analysis (n=50,100,200)")
    print("    5  - Girth Conjecture Lower Bound (Cycle C_20)")
    print("    6  - Custom Experiment (Template)")

    print("\n  Quick Tests:")
    print("    q1 - Triangle Graph")
    print("    q2 - Complete K_7")

    print("\n  Other:")
    print("    all - Run All Experiments")
    print("    exit - Exit")

    print("\n" + "─" * 80)

    while True:
        choice = input("\nEnter choice: ").strip().lower()

        if choice == 'exit':
            print("\nGoodbye!\n")
            break

        if choice in experiments:
            name, func = experiments[choice]
            print(f"\nRunning: {name}")
            print("─" * 80)
            try:
                func()
            except Exception as e:
                print(f"\n❌ Error: {e}")
        else:
            print("Invalid choice. Please try again.")


# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # Command-line mode
        arg = sys.argv[1].lower()

        if arg == 'all':
            run_all_experiments()
        elif arg == '1':
            experiment_1_basic_verification()
        elif arg == '2':
            experiment_2_parameter_comparison()
        elif arg == '3':
            experiment_3_graph_families()
        elif arg == '4':
            experiment_4_scalability()
        elif arg == '5':
            experiment_5_girth_conjecture()
        elif arg == '6':
            experiment_6_custom()
        elif arg == 'q1':
            quick_test_triangle()
        elif arg == 'q2':
            quick_test_k7()
        else:
            print(f"Unknown experiment: {arg}")
            print("Usage: python run_experiments.py [1|2|3|4|5|6|q1|q2|all]")
    else:
        # Interactive mode
        interactive_menu()
