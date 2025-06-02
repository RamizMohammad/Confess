from fastapi import FastAPI, Request, BackgroundTasks
from pydantic import BaseModel, model_validator
from fastapi.responses import JSONResponse
import firebase_admin
from firebase_admin import credentials,firestore
import json, os, time, requests
from typing import Optional

app = FastAPI()

#!----------------------------------
#! Server Class
#!----------------------------------

class ConfessServer():
    def __init__(self):

        self.botToken = os.environ["BOT_TOKEN"]
        self.chatId = os.environ["CHAT_ID"]

        try:
            if not firebase_admin._apps:
                cred_json = json.loads(os.environ["FIREBASE_CREDENTIALS"])
                cred = credentials.Certificate(cred_json)
                firebase_admin.initialize_app(cred)
            self.db = firestore.client()
            self.status = True
        except Exception as e:
            self.send_telegram_log(f"FireStroe Connection failed:\n{e}")
            self.status = False

    def createUser(self, data: dict):
        try:
            self.db.collection("Confession-UserData").add(data)
            self.send_telegram_log(f"We found a new user:\n{data}")
            return True
        except Exception as e:
            self.send_telegram_log(f"CreateUser Error:\n{e}")
            return False
        
    def checkUser(self, email: str) -> bool:
        try:
            user = self.db.collection("Confession-UserData").where("email", "==", email).limit(1).stream()
            for _ in user:
                return True
        except Exception as e:
            self.send_telegram_log(f"CheckUser Error:\n{e}")
            return False
        
    def deleteExistingUser(self, email: str) -> bool:
        try:
            users = self.db.collection("Confession-UserData").where("email", "==", email).limit(1).stream()
            userErased = False
            for user in users:
                self.db.collection("Confession-UserData").document(user.id).delete()
                userErased = True
            return userErased
        except Exception as e:
            self.send_telegram_log(f"Caught an error while deleting user:\n{e}")
            return userErased
        
    def send_telegram_log(self, message: str):
        try:
            if self.botToken and self.chatId:
                url = f"https://api.telegram.org/bot{self.botToken}/sendMessage"
                payload = {
                    "chat_id": self.chatId,
                    "text": f"[ConfessBot Error]\n{message}"
                }
                requests.post(url, data=payload)
        except Exception as e:
            print("Telegram Logging Failed:", e)

        
#*----------------------
#* Server Class Start
#* ---------------------
        
server = ConfessServer()

#!----------------------------------
#! Pydantic Class
#!----------------------------------

class addUserData(BaseModel):
    token: str
    email: str
    alaisName: str
    date: str
    isPassword: bool
    password: Optional[str] = None

    @model_validator(mode='after')
    def passwordValidator(cls, values):
        isPassword = values.get('isPassword')
        password = values.get('password')

        if isPassword and not password:
            server.send_telegram_log("There is error in setting the password")
            raise ValueError("Password must be provided if isPassword is True")
        return values

class checkUserEmail(BaseModel):
    email: str

class telegramMessages(BaseModel):
    message: str

class deleteExistingUser(BaseModel):
    email: str

#!----------------------------------
#! Routes
#!----------------------------------

@app.get('/jagte-raho')
async def serverInvoker():
    return "Abhi Hum Jinda Hai"

@app.get('/')
async def homeRoute():
    return {
        "message": server.status
    }

@app.post('/add-user')
async def addUser(data: addUserData):
    result = server.createUser(data.dict(exclude=True))
    return{
        "message": result
    }

@app.post('/check-user')
async def checkExistingUser(data: checkUserEmail):
    result = server.checkUser(data.email)
    return{
        "message": result
    }

@app.post('/delete-user')
async def deleteTheUser(data: deleteExistingUser):
    result = server.deleteExistingUser(data.email)
    return{
        "message": result
    }

#! -------------------------------
#! Background Keep-Alive Task
#! -------------------------------

def keep_alive():
    while True:
        try:
            requests.get("https://confess-ysj8.onrender.com/jagte-raho")
        except Exception as e:
            print("KeepAlive Error:", e)
        time.sleep(100)

@app.on_event("startup")
def start_keep_alive():
    import threading
    threading.Thread(target=keep_alive, daemon=True).start()