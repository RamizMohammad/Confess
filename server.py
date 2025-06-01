from fastapi import FastAPI, Request, BackgroundTasks
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import firebase_admin
from firebase_admin import credentials,firestore
import json, os, time, requests

app = FastAPI()

#!----------------------------------
#! Server Class
#!----------------------------------

class ConfessServer():
    def __init__(self):
        try:
            if not firebase_admin._apps:
                cred_json = json.loads(os.environ["FIREBASE_CREDENTIALS"])
                cred = credentials.Certificate(cred_json)
                firebase_admin.initialize_app(cred)
            self.db = firestore.client()
            self.status = True
        except:
            self.status = False

    def createUser(self, data: dict):
        try:
            self.db.collection("Confession-UserData").add(data)
            return True
        except Exception as e:
            return False
        
    def checkUser(self, email: str) -> bool:
        try:
            user = self.db.collection("Confession-UserData").where("email", "==", email).limit(1).stream()
            for _ in user:
                return True
        except Exception as e:
            return False
        
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

class checkUserEmail(BaseModel):
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
    result = server.createUser(data.dict())
    return{
        "message": result
    }

@app.post('/check-user')
async def checkExistingUser(data: checkUserEmail):
    result = server.checkUser(data.email)
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