from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel
import firebase_admin
from firebase_admin import credentials, messaging
import redis
from fastapi.middleware.cors import CORSMiddleware
import random

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

# CORS cho frontend có thể truy cập từ mọi nơi
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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
            return JSONResponse(content={"valid": False}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis error: {str(e)}")
    
# Mock esp32 webserver
@app.get("/scan-wifi/")
async def scan_wifi():
    # Mô phỏng danh sách wifi
    wifi_list = [f"SlockNet_{i}" for i in range(1, 6)]
    return JSONResponse(content=wifi_list)

@app.get("/mac/")
async def get_mac():
    # Giả lập MAC address
    mac = "AA:BB:CC:{:02X}:{:02X}:{:02X}".format(
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255)
    )
    return PlainTextResponse(mac)

@app.post("/connect-wifi/")
async def connect_wifi(
    ssid: str = Form(...),
    password: str = Form(...),
    uuid: str = Form(...)
):
    # Mô phỏng quá trình kết nối
    print(f"Connecting to SSID: {ssid}, UUID: {uuid}")
    if ssid == "fail":
        return PlainTextResponse("Connection failed", status_code=500)
    return PlainTextResponse("Connected")

@app.get("/shutdown-ap/")
async def shutdown_ap():
    # Giả lập shutdown AP
    print("Shutting down AP...")
    return PlainTextResponse("SoftAP turned off")