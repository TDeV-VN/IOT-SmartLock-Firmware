from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import firebase_admin
from firebase_admin import credentials, messaging

# pip freeze > requirements.txt

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
