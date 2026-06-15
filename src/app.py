"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pathlib import Path
from typing import Dict

from .db import activities_collection

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=current_dir / "static"), name="static")

# Seed data (kept here to bootstrap DB on first run)
SEED_ACTIVITIES = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"],
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"],
    },
}


def _doc_to_activity_doc(doc: Dict) -> Dict:
    # Convert Mongo document to API-friendly dict
    return {
        "description": doc.get("description", ""),
        "schedule": doc.get("schedule", ""),
        "max_participants": int(doc.get("max_participants", 0)),
        "participants": doc.get("participants", []),
    }


@app.on_event("startup")
def startup_seed_db():
    col = activities_collection()
    # If empty, seed with initial activities
    if col.count_documents({}) == 0:
        seed_docs = []
        for name, values in SEED_ACTIVITIES.items():
            doc = {"name": name, **values}
            seed_docs.append(doc)
        if seed_docs:
            col.insert_many(seed_docs)


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    col = activities_collection()
    docs = list(col.find({}))
    # Return same shape as before: mapping by activity name
    result = {}
    for d in docs:
        name = d.get("name")
        if name:
            result[name] = _doc_to_activity_doc(d)
    return result


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    col = activities_collection()
    doc = col.find_one({"name": activity_name})
    if not doc:
        raise HTTPException(status_code=404, detail="Activity not found")

    participants = doc.get("participants", [])
    if email in participants:
        raise HTTPException(status_code=400, detail="Student is already signed up")

    maxp = int(doc.get("max_participants", 0))
    if maxp and len(participants) >= maxp:
        raise HTTPException(status_code=400, detail="Activity is full")

    participants.append(email)
    col.update_one({"_id": doc["_id"]}, {"$set": {"participants": participants}})
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    col = activities_collection()
    doc = col.find_one({"name": activity_name})
    if not doc:
        raise HTTPException(status_code=404, detail="Activity not found")

    participants = doc.get("participants", [])
    if email not in participants:
        raise HTTPException(status_code=400, detail="Student is not signed up for this activity")

    participants.remove(email)
    col.update_one({"_id": doc["_id"]}, {"$set": {"participants": participants}})
    return {"message": f"Unregistered {email} from {activity_name}"}
