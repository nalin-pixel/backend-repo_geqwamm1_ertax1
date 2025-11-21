import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Post, Resource, Doctor, Message

app = FastAPI(title="Forest Fairy Blog API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Utility to convert Mongo documents

def serialize_doc(doc):
    if not doc:
        return doc
    d = dict(doc)
    _id = d.pop("_id", None)
    if _id is not None:
        d["id"] = str(_id)
    # convert datetime to iso
    for k, v in list(d.items()):
        try:
            import datetime
            if isinstance(v, (datetime.datetime, datetime.date)):
                d[k] = v.isoformat()
        except Exception:
            pass
    return d

@app.get("/")
def read_root():
    return {"message": "Forest Fairy Blog API is running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response

# ------------- Blog Posts -------------

@app.get("/api/posts")
def list_posts(limit: Optional[int] = 50):
    docs = get_documents("post", {}, limit)
    return [serialize_doc(d) for d in docs]

@app.post("/api/posts")
def create_post(post: Post):
    new_id = create_document("post", post)
    return {"id": new_id}

# ------------- Resources -------------

@app.get("/api/resources")
def list_resources(limit: Optional[int] = 100):
    docs = get_documents("resource", {}, limit)
    return [serialize_doc(d) for d in docs]

@app.post("/api/resources")
def create_resource(resource: Resource):
    new_id = create_document("resource", resource)
    return {"id": new_id}

# ------------- Doctors -------------

class DoctorCreate(Doctor):
    pass

class DoctorUpdate(BaseModel):
    # rating cannot be updated after creation; exclude it
    name: Optional[str] = None
    specialty: Optional[str] = None
    bio: Optional[str] = None
    photo_url: Optional[str] = None
    clinic: Optional[str] = None
    location: Optional[str] = None

@app.get("/api/doctors")
def list_doctors(limit: Optional[int] = 100):
    docs = get_documents("doctor", {}, limit)
    return [serialize_doc(d) for d in docs]

@app.post("/api/doctors")
def create_doctor(doctor: DoctorCreate):
    # Only allow rating on creation (Doctor model allows Optional[int])
    new_id = create_document("doctor", doctor)
    return {"id": new_id}

@app.put("/api/doctors/{doctor_id}")
def update_doctor(doctor_id: str, payload: DoctorUpdate):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    try:
        oid = ObjectId(doctor_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid doctor id")

    update_data = {k: v for k, v in payload.model_dump().items() if v is not None}
    if "rating" in update_data:
        update_data.pop("rating")  # enforce no rating updates
    update_data["updated_at"] = __import__("datetime").datetime.utcnow()

    result = db["doctor"].update_one({"_id": oid}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return {"updated": True}

# ------------- Contact Messages -------------

@app.post("/api/contact")
def create_message(msg: Message):
    new_id = create_document("message", msg)
    return {"id": new_id, "received": True}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
