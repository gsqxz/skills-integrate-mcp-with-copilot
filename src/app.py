"""
High School Management System API

A FastAPI application that now uses MongoDB for persistence.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pathlib import Path
import os

from db import get_activities_collection, seed_if_empty

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent, "static")), name="static")

# Initialize DB / seed on startup
@app.on_event("startup")
async def startup_event():
    seed_if_empty()


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    """Return all activities from MongoDB as a dict keyed by activity name"""
    coll = get_activities_collection()
    items = coll.find({})

    activities = {}
    for doc in items:
        name = doc.get("name")
        activities[name] = {
            "description": doc.get("description"),
            "schedule": doc.get("schedule"),
            "max_participants": doc.get("max_participants"),
            "participants": doc.get("participants", []),
        }

    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity (stored in MongoDB)"""
    coll = get_activities_collection()
    activity = coll.find_one({"name": activity_name})

    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    participants = activity.get("participants", [])

    if email in participants:
        raise HTTPException(status_code=400, detail="Student is already signed up")

    if len(participants) >= activity.get("max_participants", 0):
        raise HTTPException(status_code=400, detail="No spots available")

    coll.update_one({"name": activity_name}, {"$push": {"participants": email}})
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    coll = get_activities_collection()
    activity = coll.find_one({"name": activity_name})

    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    participants = activity.get("participants", [])

    if email not in participants:
        raise HTTPException(status_code=400, detail="Student is not signed up for this activity")

    coll.update_one({"name": activity_name}, {"$pull": {"participants": email}})
    return {"message": f"Unregistered {email} from {activity_name}"}
