import pytest
from src.router import CampusRouter, route_distance

def test_known_shortest_path():
    router = CampusRouter()
    path, distance, elapsed = router.shortest_path("Main Gate", "Library")
    assert path == ["Main Gate", "Library"]
    assert distance == pytest.approx(0.8)
    assert elapsed >= 0

def test_route_distance():
    router = CampusRouter()
    assert route_distance(router.graph, ["Main Gate", "Library", "CSE Block"]) == pytest.approx(1.5)

def test_same_source_destination():
    router = CampusRouter()
    path, distance, _ = router.shortest_path("Library", "Library")
    assert path == ["Library"]
    assert distance == 0

def test_invalid_or_unreachable_location():
    router = CampusRouter()
    with pytest.raises(ValueError):
        router.shortest_path("Unknown Building", "Library")
    router.graph.add_node("Isolated")
    with pytest.raises(ValueError, match="No route"):
        router.shortest_path("Main Gate", "Isolated")

def test_alternative_route_is_not_shortest_route():
    router = CampusRouter()
    path, distance, _ = router.shortest_path("Main Gate", "Hospital")
    alt = router.alternative_path("Main Gate", "Hospital", path)
    assert alt is None or (alt[0] != path and alt[1] >= distance)
