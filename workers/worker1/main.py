import base64
import json
from fastapi import FastAPI, Request, HTTPException

app = FastAPI()


@app.post("/")
async def receive_pubsub(request: Request):
    try:
        body = await request.json()

        if "message" not in body or "data" not in body["message"]:
            raise HTTPException(status_code=400, detail="Invalid Pub/Sub message")

        payload = json.loads(
            base64.b64decode(body["message"]["data"]).decode("utf-8")
        )

        job_id = payload["job_id"]
        prompt = payload["prompt"]
        resolution = payload["resolution"]
        photorealistic = payload["photorealistic"]
        
        print('app is running fine')

        # 🔥 IMPORTS MOVED HERE (SAFE)
        from db.session import SessionLocal
        print('after session import')
        from utils.generate import generate_and_store_image
        print('after generate and store image import')

        db = SessionLocal()
        print('after session called')
        print('command go to the generate and store image ')
        generate_and_store_image(
            job_id=job_id,
            prompt=prompt,
            resolution=resolution,
            photorealistic=photorealistic,
            db=db
        )
        print('after generate and store image called')

        db.close()

        return {"status": "ok"}

    except Exception as e:
        print("Pub/Sub worker error:", e)
        raise HTTPException(status_code=500, detail="Worker failed")
