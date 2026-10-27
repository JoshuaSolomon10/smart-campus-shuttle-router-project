from src.models import Shuttle
from src.router import CampusRouter
from src.scheduler import ShuttleScheduler

def test_shuttle_assignment_and_completion():
    router = CampusRouter()
    scheduler = ShuttleScheduler()
    request = scheduler.add_request("Emergency", "Main Gate", "Hospital", "Emergency")
    shuttle = Shuttle("SH-01")
    assigned = scheduler.process_next()
    route, distance, _ = router.shortest_path(assigned.origin, assigned.destination)
    shuttle.status = "In Transit"
    shuttle.assigned_route = route
    shuttle.current_request_id = assigned.request_id
    assert distance > 0
    assert shuttle.status == "In Transit"
    assigned.status = "Completed"
    shuttle.status = "Available"
    shuttle.completed_trips += 1
    shuttle.assigned_route = []
    shuttle.current_request_id = None
    assert assigned.status == "Completed"
    assert shuttle.status == "Available"
    assert shuttle.completed_trips == 1
