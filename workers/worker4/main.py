from fastapi import FastAPI, Request
import base64, json

app = FastAPI()

@app.post("/")
async def handler(request: Request):
    body = await request.json()
    message = body["message"]["data"]
    decoded = base64.b64decode(message).decode()
    job = json.loads(decoded)

    print("Job received:", job)

    # TODO: process job here

    return {"status": "done"}
