# Smart Campus Shuttle Router

A local academic demonstration of shortest-path routing, priority-based shuttle requests, fleet dispatch simulation, analytics, and software testing.

## Requirements
- Windows 10/11
- Python 3.10 or newer
- Internet access for the first dependency installation only

No API keys, database server, login, or paid services are required. The map is a fictional schematic and does not use external map tiles.

## Run
1. Extract the ZIP archive.
2. Double-click `run.bat`, or open the folder in VS Code and run:
   ```bat
   run.bat
   ```
3. The script creates `.venv`, installs dependencies once, and starts Streamlit. If the browser does not open automatically, visit the local URL printed in the terminal (usually `http://localhost:8501`).

## Run tests
After the first setup, double-click `test.bat`, or run:
```bat
.venv\Scripts\python -m pytest -q
```

## Features
- Schematic interactive campus map with ten labelled buildings and road links.
- Dijkstra shortest route, route distance, estimated travel time, segment count, and a feasible alternative route when available.
- Heap-based shuttle request queue: Emergency (0), Faculty (1), Student (2); insertion sequence provides FIFO ordering within a category.
- Three-shuttle fleet simulation with dispatch and completion actions.
- Request/fleet metrics, Plotly charts, and small generated-graph benchmarks.
- Automated tests for route correctness, edge cases, scheduling order, validation, and trip completion.

## Architecture and component-to-file mapping
- `app.py`: Streamlit UI, map rendering, form handling, charts, and session state.
- `src/campus_data.py`: fixed building coordinates and positive road distances.
- `src/router.py`: graph creation, Dijkstra routing, alternative routes, distance/time helpers.
- `src/models.py`: typed dataclasses for requests and shuttles.
- `src/scheduler.py`: priority heap, FIFO sequence tie-breaking, request state.
- `src/analytics.py`: pure request summaries and bounded concurrent benchmark workloads.
- `tests/`: deterministic unit tests.
- `run.bat` / `test.bat`: Windows setup, launch, and test scripts.

## Algorithm and complexity notes
Dijkstra's algorithm finds a minimum-distance path for non-negative edge weights. With a binary heap, a common complexity bound is `O((V + E) log V)` time and `O(V + E)` storage for graph representation. The scheduling heap prioritises smaller numeric values; sequence numbers make equal-priority requests FIFO. Alternative routes are found by temporarily removing each edge in the shortest route, checking the resulting route, and restoring the edge.

The benchmark uses `ThreadPoolExecutor` to run independent, bounded graph scenarios. Since the work is CPU-light and Python's GIL and thread overhead can dominate, concurrency is included as an example of a deliberate design choice, not a promise of speedup. Benchmark timings are machine-specific.

## Manual demonstration checklist
- [ ] Select Main Gate → Hospital and show the optimal red route.
- [ ] Change the origin and destination and confirm the computed route changes.
- [ ] Add an Emergency request and verify it is scheduled before Faculty and Student requests.
- [ ] Dispatch a request and show the shuttle route and status.
- [ ] Complete the trip and confirm the shuttle becomes available.
- [ ] Inspect the charts and run the performance benchmark.
- [ ] Run `test.bat` and show the actual output.

## AI-assisted software engineering
AI assistance was used to draft the specification-aligned structure and implementation. Review generated code critically, run automated tests, and manually inspect behaviour before presenting it. Tests are evidence for the tested cases, not a guarantee that all defects have been found. No independent audit is claimed.

## Scope and limitations
This is a deterministic simulation, not a live vehicle tracking system. The campus is fictional, route distances are sample values, travel time assumes an illustrative average speed of 12 km/h, and all app state is held in Streamlit's session. A map click-to-select workflow is not required for dependable use; the origin and destination selectors are the reliable selection controls.
