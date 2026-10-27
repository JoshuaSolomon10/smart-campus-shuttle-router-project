"""Weighted campus graph and shortest-path routing."""
from __future__ import annotations
import heapq
import time
from typing import Iterable
import networkx as nx
from .campus_data import BUILDINGS, ROADS

class CampusRouter:
    def __init__(self) -> None:
        self.graph = nx.Graph()
        for name, (x, y) in BUILDINGS.items():
            self.graph.add_node(name, x=x, y=y)
        for a, b, distance in ROADS:
            self.graph.add_edge(a, b, weight=float(distance))

    def shortest_path(self, origin: str, destination: str) -> tuple[list[str], float, float]:
        """Return path, km, and elapsed milliseconds using Dijkstra."""
        if origin not in self.graph or destination not in self.graph:
            raise ValueError("Please choose valid campus buildings.")
        started = time.perf_counter()
        try:
            path = nx.dijkstra_path(self.graph, origin, destination, weight="weight")
            distance = nx.dijkstra_path_length(self.graph, origin, destination, weight="weight")
        except nx.NetworkXNoPath as exc:
            raise ValueError(f"No route connects {origin} and {destination}.") from exc
        elapsed_ms = (time.perf_counter() - started) * 1000
        return path, float(distance), elapsed_ms

    def alternative_path(self, origin: str, destination: str, shortest: list[str]) -> tuple[list[str], float] | None:
        """Find a deterministic alternative by excluding each shortest-path edge in turn."""
        candidates: list[tuple[float, tuple[str, ...]]] = []
        for a, b in zip(shortest, shortest[1:]):
            self.graph.remove_edge(a, b)
            try:
                path = nx.dijkstra_path(self.graph, origin, destination, weight="weight")
                distance = float(nx.dijkstra_path_length(self.graph, origin, destination, weight="weight"))
                if path != shortest:
                    candidates.append((distance, tuple(path)))
            except nx.NetworkXNoPath:
                pass
            finally:
                self.graph.add_edge(a, b, weight=float(next(w for x, y, w in ROADS if {x, y} == {a, b})))
        if not candidates:
            return None
        distance, path = min(candidates, key=lambda item: (item[0], item[1]))
        return list(path), distance

    @property
    def node_count(self) -> int:
        return self.graph.number_of_nodes()

    @property
    def edge_count(self) -> int:
        return self.graph.number_of_edges()

def route_distance(graph: nx.Graph, route: Iterable[str]) -> float:
    """Pure calculation of total route distance in kilometres."""
    nodes = list(route)
    return round(sum(float(graph[a][b]["weight"]) for a, b in zip(nodes, nodes[1:])), 3)

def estimated_minutes(distance_km: float, speed_kmh: float = 12.0) -> int:
    if speed_kmh <= 0:
        raise ValueError("Speed must be positive.")
    return round(distance_km / speed_kmh * 60)
