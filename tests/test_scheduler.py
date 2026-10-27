from src.scheduler import ShuttleScheduler

def test_emergency_precedes_faculty_and_student():
    scheduler = ShuttleScheduler()
    scheduler.add_request("Student", "Main Gate", "Library", "Student")
    scheduler.add_request("Faculty", "Main Gate", "Library", "Faculty")
    scheduler.add_request("Emergency", "Main Gate", "Hospital", "Emergency")
    assert scheduler.process_next().category == "Emergency"
    assert scheduler.process_next().category == "Faculty"
    assert scheduler.process_next().category == "Student"

def test_fifo_for_equal_priority():
    scheduler = ShuttleScheduler()
    first = scheduler.add_request("First", "Main Gate", "Library", "Student")
    second = scheduler.add_request("Second", "Library", "CSE Block", "Student")
    assert scheduler.process_next().request_id == first.request_id
    assert scheduler.process_next().request_id == second.request_id

def test_invalid_request():
    scheduler = ShuttleScheduler()
    try:
        scheduler.add_request("Invalid", "Library", "Library", "Student")
    except ValueError:
        pass
    else:
        raise AssertionError("Same-origin request should be rejected.")
