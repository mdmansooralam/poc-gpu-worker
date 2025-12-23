import base64
import json
import os
from fastapi import FastAPI, Request, HTTPException
from starlette.concurrency import run_in_threadpool

app = FastAPI()

# -------- Worker identity (FAIL FAST) --------
REQUIRED_ENV = ["WORKER_ID", "WORKER_TYPE", "GPU"]
missing = [k for k in REQUIRED_ENV if not os.getenv(k)]
if missing:
    raise RuntimeError(f"Missing env vars: {missing}")

WORKER_ID = os.getenv("WORKER_ID")
WORKER_TYPE = os.getenv("WORKER_TYPE")

# -------- Health check --------
@app.get("/health")
def health():
    return {
        "status": "ok",
        "worker_id": WORKER_ID,
        "worker_type": WORKER_TYPE
    }

# -------- Pub/Sub receiver --------
@app.post("/")
async def receive_pubsub(request: Request):
    try:
        body = await request.json()

        if "message" not in body or "data" not in body["message"]:
            # 400 = no retry
            raise HTTPException(status_code=400, detail="Invalid Pub/Sub message")

        payload = json.loads(
            base64.b64decode(body["message"]["data"]).decode("utf-8")
        )

        job_id = payload["job_id"]
        prompt = payload["prompt"]
        resolution = payload["resolution"]
        photorealistic = payload["photorealistic"]

        # 🔥 SAFE imports (no startup GPU load)
        from db.session import SessionLocal
        from utils.generate import generate_and_store_image

        db = SessionLocal()
        try:
            # 🔥 GPU work in thread (DO NOT block event loop)
            await run_in_threadpool(
                generate_and_store_image,
                job_id,
                prompt,
                resolution,
                photorealistic,
                db
            )
        finally:
            db.close()

        # 200 = Pub/Sub ACK
        return {"status": "ok"}

    except HTTPException:
        # Explicit HTTP errors should not be retried
        raise

    except Exception as e:
        print("Worker failed:", e)
        # 500 = Pub/Sub retry
        raise HTTPException(status_code=500, detail="Worker execution failed")
