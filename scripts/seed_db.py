"""Manual seed script to populate MongoDB with initial activities.

Usage:
    python scripts/seed_db.py
"""
from src.db import activities_collection


def run():
    col = activities_collection()
    if col.count_documents({}) > 0:
        print("Collection already has documents; aborting.")
        return

    seed = [
        {"name": "Chess Club", "description": "Learn strategies and compete in chess tournaments", "schedule": "Fridays, 3:30 PM - 5:00 PM", "max_participants": 12, "participants": ["michael@mergington.edu", "daniel@mergington.edu"]},
        {"name": "Programming Class", "description": "Learn programming fundamentals and build software projects", "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM", "max_participants": 20, "participants": ["emma@mergington.edu", "sophia@mergington.edu"]},
        {"name": "Gym Class", "description": "Physical education and sports activities", "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM", "max_participants": 30, "participants": ["john@mergington.edu", "olivia@mergington.edu"]},
    ]

    col.insert_many(seed)
    print("Seeded activities collection.")


if __name__ == "__main__":
    run()
