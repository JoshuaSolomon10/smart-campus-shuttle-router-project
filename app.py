from __future__ import annotations
import html
import pandas as pd
import plotly.express as px
import streamlit as st
import folium
from streamlit_folium import st_folium
from src.campus_data import BUILDINGS, ROADS
from src.models import Shuttle
from src.router import CampusRouter, estimated_minutes
from src.scheduler import ShuttleScheduler
from src.analytics import run_benchmarks, summarize_requests

px.defaults.template = "plotly_dark"

st.set_page_config(page_title="Smart Campus Shuttle Router", page_icon="🚌", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
:root { color-scheme: dark; }
.stApp { background: radial-gradient(ellipse at 15% 0%, #172b47 0%, #0b1220 48%, #080d17 100%); color: #e8eef8; }
.block-container { padding-top: 1.6rem; padding-bottom: 2.5rem; max-width: 1700px; }
[data-testid="stHeader"] { background: rgba(8,13,23,.88); }
[data-testid="stToolbar"] { right: 1rem; }
[data-testid="stSidebar"] { background: linear-gradient(180deg,#101a2b 0%,#0c1422 100%); border-right: 1px solid #26354b; }
[data-testid="stSidebar"] * { color: #e5edf9 !important; }
[data-testid="stSidebar"] [data-testid="stRadio"] label { padding: .55rem .65rem; margin: .12rem 0; border: 1px solid transparent; border-radius: 10px; }
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover { background: #1a2940; border-color: #30445f; }
.stMarkdown, .stText, p, li, label, [data-testid="stCaptionContainer"] { color: #d1dced; }
h1,h2,h3,h4,h5 { color: #f4f7ff !important; letter-spacing: -.02em; }
.hero { padding: 1.8rem 2rem; border: 1px solid #31516d; border-radius: 22px; color: #f8fbff !important; background: linear-gradient(115deg,#13243d 0%,#17465c 58%,#176b70 100%); margin-bottom: 1.5rem; box-shadow: 0 18px 45px rgba(0,0,0,.28); }
.hero h1 { color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; margin: 0; font-size: clamp(1.65rem,2.8vw,2.45rem); line-height: 1.25; font-weight: 850; letter-spacing: -.035em; }
.hero p { color: #d7f4ff !important; margin: .7rem 0 0; font-size: 1.02rem; }
[data-testid="stMetric"] { background: linear-gradient(145deg,#17263b,#111d30); padding: 1rem 1.05rem; border-radius: 16px; border: 1px solid #2b405b; box-shadow: 0 8px 22px rgba(0,0,0,.16); min-width: 0; }
[data-testid="stMetricLabel"], [data-testid="stMetricLabel"] p { color: #aebfd6 !important; font-size: .9rem !important; font-weight: 650; white-space: normal !important; overflow: visible !important; }
[data-testid="stMetricValue"], [data-testid="stMetricValue"] div { color: #f5f8ff !important; font-weight: 800 !important; font-size: clamp(1.15rem,1.7vw,1.8rem) !important; white-space: normal !important; overflow: visible !important; text-overflow: clip !important; overflow-wrap: anywhere; line-height: 1.25; }
.metric-grid { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap: .8rem; margin: .8rem 0 1rem; }
.metric-card { min-width:0; background:linear-gradient(145deg,#17263b,#111d30); border:1px solid #2b405b; border-radius:16px; padding:1rem 1.05rem; box-shadow:0 8px 22px rgba(0,0,0,.16); }
.metric-label { color:#aebfd6; font-size:.88rem; font-weight:650; margin-bottom:.55rem; }
.metric-value { color:#f5f8ff; font-size:clamp(1.25rem,2vw,1.85rem); line-height:1.25; font-weight:850; overflow-wrap:anywhere; font-variant-numeric:tabular-nums; }
.metric-note { color:#8fa5c1; font-size:.76rem; margin-top:.35rem; }
.stButton > button, [data-testid="stFormSubmitButton"] button { border-radius: 11px; min-height: 2.65rem; font-weight: 700; border: 1px solid #344b68; background: #1a2a40; color: #edf5ff; transition: all .15s ease; }
.stButton > button[kind="primary"], [data-testid="stFormSubmitButton"] button { background: linear-gradient(110deg,#e14b65,#ef7957); color: #fff; border: 0; }
.stButton > button:hover { border-color: #5a83ad; transform: translateY(-1px); box-shadow: 0 7px 18px rgba(0,0,0,.2); }
[data-baseweb="select"] > div, [data-baseweb="input"] > div, [data-baseweb="textarea"] { background: #111d2e !important; border-color: #344963 !important; border-radius: 10px; color: #eef4ff !important; }
[data-baseweb="select"] *, [data-baseweb="input"] input, [data-baseweb="textarea"] textarea { color: #eef4ff !important; }
[data-baseweb="popover"] [role="listbox"], [data-baseweb="menu"] { background: #152338 !important; }
[role="option"] { color: #edf4ff !important; }
[data-testid="stDataFrame"], [data-testid="stTable"] { background: #111d2e; border-radius: 14px; overflow: hidden; border: 1px solid #2b405b; }
[data-testid="stAlert"] { border-radius: 12px; }
hr { border-color: #293c55; }
.map-caption { background:#111d2e; border:1px solid #2b405b; border-radius:12px; padding:10px 14px; color:#cbd8eb; }
[data-testid="stExpander"] { background: rgba(18,31,49,.72); border:1px solid #293d57; border-radius:14px; }
[data-testid="stForm"] { border-color:#293d57 !important; }
.js-plotly-plot .plotly .main-svg { background: transparent !important; }
@media (max-width: 800px) { .block-container {padding-left:1rem;padding-right:1rem;} .hero {padding:1.25rem;} .metric-grid {grid-template-columns:1fr;} }
</style>
<div class="hero"><h1>🚌 Smart Campus Shuttle Router</h1><p>Intelligent campus routing&nbsp; · &nbsp;Priority-based dispatch&nbsp; · &nbsp;Fleet simulation</p></div>
""", unsafe_allow_html=True)

def render_metric_cards(items):
    cards = []
    for label, value, note in items:
        cards.append(f'<div class="metric-card"><div class="metric-label">{html.escape(str(label))}</div><div class="metric-value">{html.escape(str(value))}</div><div class="metric-note">{html.escape(str(note))}</div></div>')
    st.markdown('<div class="metric-grid">' + ''.join(cards) + '</div>', unsafe_allow_html=True)

@st.cache_resource
def get_router():
    return CampusRouter()
router = get_router()

if "scheduler" not in st.session_state:
    scheduler = ShuttleScheduler()
    scheduler.add_request("Student A", "Main Gate", "Library", "Student")
    scheduler.add_request("Faculty B", "Hostel", "AI & Data Science Lab", "Faculty")
    scheduler.add_request("Emergency Demo", "Canteen", "Hospital", "Emergency")
    scheduler.add_request("Student C", "CSE Block", "Auditorium", "Student")
    st.session_state.scheduler = scheduler
if "shuttles" not in st.session_state:
    st.session_state.shuttles = [Shuttle(f"SH-{i:02d}") for i in range(1, 4)]
if "origin" not in st.session_state: st.session_state.origin = "Main Gate"
if "destination" not in st.session_state: st.session_state.destination = "Hospital"
if "last_route_ms" not in st.session_state: st.session_state.last_route_ms = 0.0
if "map_click_seen" not in st.session_state: st.session_state.map_click_seen = None

scheduler: ShuttleScheduler = st.session_state.scheduler
shuttles: list[Shuttle] = st.session_state.shuttles
locations = list(BUILDINGS.keys())

# Apply a marker selection on the next rerun, before the selectbox widgets are created.
pending_building = st.session_state.pop("pending_map_building", None)
if pending_building in BUILDINGS:
    target = st.session_state.get("map_click_target", "Destination")
    if target == "Origin":
        st.session_state.origin = pending_building
        st.session_state["origin_select"] = pending_building
    else:
        st.session_state.destination = pending_building
        st.session_state["destination_select"] = pending_building

with st.sidebar:
    st.title("Navigation")
    st.caption("Choose a workspace below.")
    page = st.radio("Workspace", ["Campus Route Planner", "Shuttle Requests", "Fleet Dashboard", "Performance & About"])
    st.divider()
    st.markdown("**Campus network**")
    st.write(f"{router.node_count} buildings · {router.edge_count} road links")
    st.caption("Fictional schematic coordinates; not GPS data.")

if page == "Campus Route Planner":
    left, right = st.columns([1, 1.7], gap="large")
    with left:
        st.subheader("Plan a journey")
        st.radio("When clicking a map marker, set:", ["Origin", "Destination"],
                 horizontal=True, key="map_click_target")
        origin = st.selectbox("Starting building", locations, index=locations.index(st.session_state.origin), key="origin_select")
        destination = st.selectbox("Destination building", locations, index=locations.index(st.session_state.destination), key="destination_select")
        st.session_state.origin, st.session_state.destination = origin, destination
        if st.button("Reset Route", use_container_width=True):
            st.session_state.origin, st.session_state.destination = "Main Gate", "Hospital"
            st.rerun()
        try:
            path, distance, elapsed = router.shortest_path(origin, destination)
            st.session_state.last_route_ms = elapsed
            alt = router.alternative_path(origin, destination, path)
            render_metric_cards([
                ("TOTAL DISTANCE", f"{distance:.2f} km", "Shortest route"),
                ("ROAD SEGMENTS", f"{max(0, len(path)-1)}", "Connections used"),
                ("ESTIMATED TRAVEL", f"{estimated_minutes(distance)} min", "At campus shuttle speed"),
            ])
            st.markdown("**Optimal route**")
            st.write(" → ".join(path))
            st.caption(f"Dijkstra computation: {elapsed:.4f} ms")
            if alt:
                st.markdown("**Alternative route**")
                st.write(" → ".join(alt[0]))
                st.write(f"{alt[1]:.2f} km · {alt[1]-distance:+.2f} km compared with optimal")
            else:
                st.info("No alternative route was found.")
        except ValueError as exc:
            path, distance, alt = [], 0.0, None
            st.error(str(exc))
    with right:
        st.subheader("Interactive schematic campus")
        map_obj = folium.Map(location=[2.1, 2.7], zoom_start=0, tiles=None, crs="Simple",
                             min_zoom=-2, max_zoom=4, control_scale=False,
                             zoom_control=True, prefer_canvas=True)
        folium.Rectangle(bounds=[[-0.8,-0.8],[5.5,6.5]], color="#cbd8e6", fill=True,
                         fill_color="#f8fbff", fill_opacity=1, weight=1).add_to(map_obj)
        map_obj.fit_bounds([[-0.8, -0.8], [5.5, 6.5]], padding=(24, 24))
        # Base road network in schematic coordinate space.
        for a, b, km in ROADS:
            ax, ay = BUILDINGS[a]; bx, by = BUILDINGS[b]
            folium.PolyLine([[ay, ax], [by, bx]], color="#b9c8d5", weight=4,
                            tooltip=f"{a} ↔ {b}: {km:.1f} km").add_to(map_obj)
        if path:
            coords = [[BUILDINGS[n][1], BUILDINGS[n][0]] for n in path]
            folium.PolyLine(coords, color="#e11d48", weight=8, opacity=.95,
                            tooltip=f"Optimal route · {distance:.2f} km").add_to(map_obj)
        if alt:
            coords_alt = [[BUILDINGS[n][1], BUILDINGS[n][0]] for n in alt[0]]
            folium.PolyLine(coords_alt, color="#2563eb", weight=4, opacity=.75,
                            dash_array="8, 10", tooltip=f"Alternative · {alt[1]:.2f} km").add_to(map_obj)
        for name, (x, y) in BUILDINGS.items():
            if name == origin:
                color, label = "green", "START"
            elif name == destination:
                color, label = "red", "DESTINATION"
            else:
                color, label = "cadetblue", "BUILDING"
            folium.Marker([y, x], tooltip=name, popup=name,
                          icon=folium.Icon(color=color, icon="info-sign")).add_to(map_obj)
        map_result = st_folium(
            map_obj, height=520, use_container_width=True,
            returned_objects=["last_object_clicked_tooltip"]
        )
        clicked_building = (map_result or {}).get("last_object_clicked_tooltip")
        if clicked_building in BUILDINGS and clicked_building != st.session_state.get("map_click_seen"):
            st.session_state.map_click_seen = clicked_building
            st.session_state.pending_map_building = clicked_building
            st.rerun()
        st.markdown("<div class='map-caption'>🟢 Start &nbsp;&nbsp; 🔴 Destination &nbsp;&nbsp; 🔵 Alternative route &nbsp;&nbsp; 🟥 <b>Optimal route</b></div>", unsafe_allow_html=True)
        st.caption("Click a building marker to set the selected Origin or Destination (choose the target above), or use the selectors. The schematic map requires no map API or map tiles.")

elif page == "Shuttle Requests":
    st.subheader("Shuttle request queue")
    with st.expander("＋ Add a shuttle request", expanded=True):
        with st.form("request_form", clear_on_submit=True):
            passenger = st.text_input("Passenger name / identifier", placeholder="e.g. Student D")
            c1, c2 = st.columns(2)
            req_origin = c1.selectbox("Origin", locations, index=0)
            req_dest = c2.selectbox("Destination", locations, index=1)
            category = st.selectbox("Passenger category", ["Student", "Faculty", "Emergency"])
            submitted = st.form_submit_button("Add request", use_container_width=True)
            if submitted:
                if req_origin == req_dest:
                    st.error("Origin and destination must be different.")
                else:
                    request = scheduler.add_request(passenger, req_origin, req_dest, category)
                    st.success(f"{request.request_id} added with {category} priority.")
                    st.rerun()
    next_req = scheduler.next_request()
    if next_req:
        st.info(f"**Next in queue:** {next_req.request_id} · {next_req.category} · {next_req.origin} → {next_req.destination}")
    else:
        st.info("No pending requests.")
    c1, c2 = st.columns(2)
    available = next((s for s in shuttles if s.status == "Available"), None)
    if c1.button("Dispatch next request", use_container_width=True, disabled=available is None or next_req is None):
        req = scheduler.process_next()
        if req and available:
            try:
                route, distance, _ = router.shortest_path(req.origin, req.destination)
                available.status = "In Transit"
                available.assigned_route = route
                available.current_request_id = req.request_id
                st.session_state.last_dispatch = f"{available.shuttle_id}: {' → '.join(route)} ({distance:.2f} km)"
                st.rerun()
            except ValueError as exc:
                req.status = "Pending"
                st.error(str(exc))
    if c2.button("Complete selected trip", use_container_width=True,
                 disabled=not any(s.status == "In Transit" for s in shuttles)):
        active = next(s for s in shuttles if s.status == "In Transit")
        req = scheduler.requests[active.current_request_id]
        req.status = "Completed"
        active.status = "Available"
        active.completed_trips += 1
        active.assigned_route = []
        active.current_request_id = None
        st.success(f"{active.shuttle_id} trip completed.")
        st.rerun()
    if st.session_state.get("last_dispatch"):
        st.success(f"Last dispatch: {st.session_state.last_dispatch}")
    requests = list(scheduler.requests.values())
    df = pd.DataFrame([{"ID":r.request_id, "Passenger":r.passenger, "Origin":r.origin,
                        "Destination":r.destination, "Category":r.category,
                        "Priority (lower = sooner)":r.priority, "Status":r.status,
                        "Sequence":r.sequence} for r in sorted(requests, key=lambda r:(r.priority,r.sequence))])
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.caption("Priority values: Emergency = 0, Faculty = 1, Student = 2. heapq returns the smallest priority first; sequence number preserves FIFO order for ties.")

elif page == "Fleet Dashboard":
    st.subheader("Fleet overview")
    requests = list(scheduler.requests.values())
    counts = scheduler.counts()
    a,b,c,d = st.columns(4)
    a.metric("Total requests", len(requests))
    b.metric("Pending", counts["Pending"])
    c.metric("Completed trips", counts["Completed"])
    d.metric("Available shuttles", sum(s.status == "Available" for s in shuttles))
    fleet_rows = []
    for shuttle in shuttles:
        fleet_rows.append({"Shuttle": shuttle.shuttle_id, "Status": shuttle.status,
                           "Current request": shuttle.current_request_id or "—",
                           "Assigned route": " → ".join(shuttle.assigned_route) if shuttle.assigned_route else "—",
                           "Completed trips": shuttle.completed_trips})
    st.dataframe(pd.DataFrame(fleet_rows), use_container_width=True, hide_index=True)
    st.subheader("Request status counts")
    status_df = pd.DataFrame([{"Status": status, "Count": sum(r.status == status for r in requests)}
                              for status in ("Pending","Assigned","Completed","Cancelled")])
    st.plotly_chart(px.bar(status_df, x="Status", y="Count", color="Status",
                           title="Requests by status", text_auto=True), use_container_width=True)
    stats = summarize_requests(requests)
    st.subheader("Requests by passenger category")
    category_df = pd.DataFrame([{"Category": cat, "Count": stats[cat]} for cat in ("Emergency","Faculty","Student")])
    st.plotly_chart(px.pie(category_df, names="Category", values="Count", hole=.45,
                           title="Category mix"), use_container_width=True)

else:
    st.subheader("Performance & About")
    requests = list(scheduler.requests.values())
    counts = scheduler.counts()
    a,b,c,d = st.columns(4)
    a.metric("Buildings / nodes", router.node_count)
    b.metric("Road links / edges", router.edge_count)
    c.metric("Requests", len(requests))
    d.metric("Last route time", f"{st.session_state.last_route_ms:.4f} ms")
    st.markdown("### Algorithm notes")
    st.markdown("""
    - **Dijkstra:** finds a minimum-distance route in a graph with non-negative edge weights. This campus graph uses positive kilometre weights.
    - **Complexity:** with a binary heap, the usual bound is `O((V + E) log V)` time and `O(V + E)` graph storage.
    - **Priority queue:** `heapq` is a min-heap. Smaller priority numbers are served first; sequence numbers make equal-priority requests FIFO.
    - **OOP:** router, request, shuttle, and scheduler classes keep related data and behaviour together.
    - **Functional style:** route-distance and request-summary helpers return results without mutating their inputs.
    - **Concurrency:** independent graph benchmarks run in a bounded `ThreadPoolExecutor`. These tiny CPU-bound tasks may not become faster because of overhead and Python's GIL; concurrency is demonstrated as a measured design choice, not a speed guarantee.
    """)
    if st.button("Run benchmark scenarios", type="primary"):
        with st.spinner("Benchmarking small generated graphs..."):
            results = run_benchmarks()
        st.session_state.benchmark_results = results
    if "benchmark_results" in st.session_state:
        bench_df = pd.DataFrame(st.session_state.benchmark_results)
        st.dataframe(bench_df, use_container_width=True, hide_index=True)
        st.plotly_chart(px.line(bench_df, x="Nodes", y="Time (ms)", markers=True,
                                title="Illustrative Dijkstra benchmark"), use_container_width=True)
        st.caption("Times are local measurements from this run and machine; they are illustrative, not universal performance guarantees.")
    st.markdown("### Architecture")
    st.write("- `app.py`: Streamlit interface, map, forms, charts, session state.")
    st.write("- `src/campus_data.py`: deterministic campus coordinates and road distances.")
    st.write("- `src/router.py`: weighted graph, shortest path, alternative path, distance helpers.")
    st.write("- `src/models.py`: request and shuttle dataclasses.")
    st.write("- `src/scheduler.py`: heap-based request scheduling.")
    st.write("- `src/analytics.py`: summaries and concurrent benchmarks.")
    st.write("- `tests/`: deterministic unit tests.")
    st.markdown("### AI-assisted development and manual validation")
    st.write("AI-assisted generation was guided by a written specification. Review the implementation critically; tests and manual demonstrations provide evidence, but do not guarantee defect-free software.")
    st.markdown("""
    **Demonstration checklist**
    1. Plan Main Gate → Hospital and inspect the red optimal route.
    2. Change the origin and destination and confirm the route updates.
    3. Add an Emergency request and confirm it moves ahead of Faculty and Student requests.
    4. Dispatch a request, inspect its shuttle assignment, then complete the trip.
    5. Review fleet and analytics metrics; run the benchmark.
    6. Run `test.bat` and show the actual test output.
    """)
