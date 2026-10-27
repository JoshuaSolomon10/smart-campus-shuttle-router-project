"""Deterministic fictional campus layout and road network."""
BUILDINGS = {
    "Main Gate": (0.0, 0.0),
    "Library": (1.2, 1.1),
    "CSE Block": (2.5, 1.8),
    "AI & Data Science Lab": (3.8, 2.5),
    "Administrative Block": (1.0, 3.0),
    "Hostel": (4.7, 0.4),
    "Canteen": (3.0, -0.2),
    "Hospital": (5.7, 2.4),
    "Sports Complex": (0.2, 4.5),
    "Auditorium": (3.2, 4.2),
}

# Positive distances in km; multiple alternative routes are intentionally available.
ROADS = [
    ("Main Gate", "Library", 0.8),
    ("Main Gate", "Administrative Block", 1.4),
    ("Main Gate", "Canteen", 1.8),
    ("Library", "CSE Block", 0.7),
    ("Library", "Administrative Block", 1.0),
    ("Library", "Canteen", 1.5),
    ("CSE Block", "AI & Data Science Lab", 0.9),
    ("CSE Block", "Canteen", 1.0),
    ("CSE Block", "Auditorium", 1.8),
    ("AI & Data Science Lab", "Hostel", 1.2),
    ("AI & Data Science Lab", "Hospital", 1.6),
    ("AI & Data Science Lab", "Auditorium", 1.7),
    ("Hostel", "Canteen", 0.9),
    ("Hostel", "Hospital", 1.5),
    ("Canteen", "Hospital", 2.2),
    ("Administrative Block", "Sports Complex", 1.3),
    ("Administrative Block", "Auditorium", 1.6),
    ("Sports Complex", "Auditorium", 2.0),
    ("Auditorium", "Hospital", 2.3),
]
