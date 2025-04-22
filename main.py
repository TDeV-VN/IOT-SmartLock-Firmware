from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import firebase_admin
from firebase_admin import credentials, messaging
import redis

# pip freeze > requirements.txt

# Kết nối đến Redis Cloud
r = redis.Redis(
    host='redis-14643.c334.asia-southeast2-1.gce.redns.redis-cloud.com',
    port=14643,
    decode_responses=True,
    username="default",
    password="Trvg6z0wpXovzI13dNl3TDwHIwNt5O70",
)



# Khởi tạo Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.Certificate("firebaseKey.json")
    firebase_admin.initialize_app(cred)

app = FastAPI()

# Định nghĩa schema cho gửi FCM theo topic
class FCMTopicMessage(BaseModel):
    topic: str
    title: str
    body: str
    data: dict = None  # Optional

@app.post("/send-topic")
async def send_to_topic(message: FCMTopicMessage):
    try:
        msg = messaging.Message(
            notification=messaging.Notification(
                title=message.title,
                body=message.body
            ),
            topic=message.topic,
            data=message.data or {}
        )

        response = messaging.send(msg)
        return {"message_id": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/set-secret-code")
def set_secret_code(code: str):
    try:
        r.set("secret-code", code, ex=900)
        return JSONResponse(content={"message": "Secret code set successfully"}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis error: {str(e)}")

@app.post("/validate-secret-code")
def validate_secret_code(code: str):
    try:
        stored_code = r.get("secret-code")
        if stored_code is None:
            raise HTTPException(status_code=404, detail="No code found or it has expired")
        if stored_code == code:
            return JSONResponse(content={"valid": True}, status_code=200)
        else:
            return JSONResponse(content={"valid": False}, status_code=400)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis error: {str(e)}")