"""Heap-based priority scheduling with FIFO tie-breaking."""
from __future__ import annotations
import heapq
from .models import ShuttleRequest

class ShuttleScheduler:
    def __init__(self) -> None:
        self._heap: list[tuple[int, int, str]] = []
        self.requests: dict[str, ShuttleRequest] = {}
        self._sequence = 0

    def add_request(self, passenger: str, origin: str, destination: str, category: str) -> ShuttleRequest:
        self._sequence += 1
        request = ShuttleRequest(
            request_id=f"REQ-{self._sequence:03d}", passenger=passenger.strip() or "Guest",
            origin=origin, destination=destination, category=category, sequence=self._sequence
        )
        self.requests[request.request_id] = request
        heapq.heappush(self._heap, (request.priority, request.sequence, request.request_id))
        return request

    def _discard_stale(self) -> None:
        while self._heap and self.requests[self._heap[0][2]].status != "Pending":
            heapq.heappop(self._heap)

    def next_request(self) -> ShuttleRequest | None:
        self._discard_stale()
        return self.requests[self._heap[0][2]] if self._heap else None

    def process_next(self) -> ShuttleRequest | None:
        request = self.next_request()
        if request:
            heapq.heappop(self._heap)
            request.status = "Assigned"
        return request

    def pending_requests(self) -> list[ShuttleRequest]:
        return sorted((r for r in self.requests.values() if r.status == "Pending"),
                      key=lambda r: (r.priority, r.sequence))

    def counts(self) -> dict[str, int]:
        return {status: sum(r.status == status for r in self.requests.values())
                for status in ("Pending", "Assigned", "Completed", "Cancelled")}
