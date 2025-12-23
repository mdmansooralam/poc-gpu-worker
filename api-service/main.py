from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from db.session import get_db
from google.cloud import pubsub_v1
import json
from models.jobs import Job
import uuid
from pydantic import BaseModel

# pydantic model
class GenerateRequest(BaseModel):
    prompt: str
    resolution: str
    photorealistic: bool = False
    
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'], 
    allow_methods=["*"],
    allow_headers=["*"],  
)

PROJECT_ID = "indixpert-poc"
TOPIC_ID = "image-jobs"

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)

@app.post("/generate")
async def submit_job(data: GenerateRequest, db : Session = Depends(get_db)):
    
    try:
        # 1️⃣ Create job
        job_id = str(uuid.uuid4())
        new_job = Job(job_id=job_id)
        db.add(new_job)
        db.commit()
        db.refresh(new_job)

        # 2️⃣ Attach job_id to payload
        payload = {
            "job_id": job_id,
            "prompt": data.prompt,
            "resolution": data.resolution,
            "photorealistic": data.photorealistic
        }

        # 3️⃣ Publish to Pub/Sub (IMPORTANT: attributes)
        future = publisher.publish(
            topic_path,
            json.dumps(payload).encode("utf-8"),
            load="low"   # 👈 MUST match subscription filter
        )
        future.result()  # ensure publish success

        return new_job
    
    except Exception as e:
        db.rollback()
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/status/{job_id}')
async def get_status(job_id, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="job not found with given job_id")
    
    return job
    