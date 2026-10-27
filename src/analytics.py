"""Pure summaries and bounded benchmark scenarios."""
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor
import time
import networkx as nx
from .router import CampusRouter

def summarize_requests(requests) -> dict[str, int]:
    return {
        "Emergency": sum(r.category == "Emergency" for r in requests),
        "Faculty": sum(r.category == "Faculty" for r in requests),
        "Student": sum(r.category == "Student" for r in requests),
        "Pending": sum(r.status == "Pending" for r in requests),
        "Assigned": sum(r.status == "Assigned" for r in requests),
        "Completed": sum(r.status == "Completed" for r in requests),
    }

def benchmark_graph(node_count: int) -> dict[str, float | int]:
    """Generate a deterministic connected graph and time one shortest-path query."""
    graph = nx.path_graph(node_count)
    for node in range(node_count - 1):
        graph[node][node + 1]["weight"] = 1.0 + (node % 5) * 0.1
    for node in range(node_count - 2):
        graph.add_edge(node, node + 2, weight=2.0 + (node % 3) * 0.1)
    start = time.perf_counter()
    nx.dijkstra_path(graph, 0, node_count - 1, weight="weight")
    elapsed = (time.perf_counter() - start) * 1000
    return {"Nodes": node_count, "Edges": graph.number_of_edges(), "Time (ms)": round(elapsed, 4)}

def run_benchmarks() -> list[dict[str, float | int]]:
    sizes = (10, 100, 500, 1000)
    with ThreadPoolExecutor(max_workers=4) as executor:
        return list(executor.map(benchmark_graph, sizes))
