from fastapi import FastAPI, Request, BackgroundTasks
from pydantic import BaseModel, model_validator
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import firebase_admin
from firebase_admin import credentials, firestore
import json, os, time, requests
from typing import Optional
import datetime
import uuid

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

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

    def passwordReset(self, email: str):
        token = str(uuid.uuid4())
        now = datetime.datetime.utcnow().isoformat()
        data = {
            "email": email,
            "token": token,
            "createdAt": now,
            "used": False,
            "usedAt": None
        }

        try:
            self.db.collection("PasswordResetToken").document(token).set(data)
            return token
        except Exception as e:
            self.send_telegram_log(f"Error creating a link:\n{e}")
            return None

    def validateResetLink(self, token: str):
        try:
            doc = self.db.collection("PasswordResetToken").document(token).get()
            if not doc.exists:
                return False, "Invalid Token"

            data = doc.to_dict()
            now = datetime.datetime.utcnow()
            created = datetime.datetime.fromisoformat(data["createdAt"])

            if not data["used"]:
                if (now - created).total_seconds() > 600:
                    return False, "Token expired (10 mins)"
                return True, data["email"]
            else:
                usedAt = datetime.datetime.fromisoformat(data["usedAt"])
                if (now - usedAt).total_seconds() > 60:
                    return False, "Token expired after use"
                return True, data["email"]

        except Exception as e:
            self.send_telegram_log(f"Error in validating token:\n{e}")
            return False, "Validation Error"

    def markTokenUsed(self, token: str):
        try:
            self.db.collection("PasswordResetToken").document(token).update({
                "used": True,
                "usedAt": datetime.datetime.utcnow().isoformat()
            })
        except Exception as e:
            self.send_telegram_log(f"Error marking token:\n{e}")

    def updateUserPassword(self, email: str, new_password: str):
        try:
            users = self.db.collection("Confession-UserData").where("email", "==", email).limit(1).stream()
            for user in users:
                self.db.collection("Confession-UserData").document(user.id).update({
                    "password": new_password
                })
                return True
            return False
        except Exception as e:
            self.send_telegram_log(f"Error updating password:\n{e}")
            return False

server = ConfessServer()

class addUserData(BaseModel):
    token: str
    email: str
    alaisName: str
    date: str
    isPassword: bool
    password: Optional[str] = None

    @model_validator(mode='after')
    def passwordValidator(self) -> 'addUserData':
        if self.isPassword and not self.password:
            server.send_telegram_log("There is error in setting the password")
            raise ValueError("Password must be provided if isPassword is True")
        return self

class checkUserEmail(BaseModel):
    email: str

class deleteExistingUser(BaseModel):
    email: str

class requestResetModel(BaseModel):
    email: str

class passwordResetModel(BaseModel):
    token: str
    newPassword: str

@app.get('/reset-password/{token}', response_class=HTMLResponse)
async def show_reset_form(request: Request, token: str):
    return templates.TemplateResponse("reset_password.html", {"request": request})

@app.get('/jagte-raho')
async def serverInvoker():
    return "Abhi Hum Jinda Hai"

@app.get('/')
async def homeRoute():
    return {"message": server.status}

@app.post('/add-user')
async def addUser(data: addUserData):
    result = server.createUser(data.model_dump(exclude_none=True))
    return {"message": result}

@app.post('/check-user')
async def checkExistingUser(data: checkUserEmail):
    result = server.checkUser(data.email)
    return {"message": result}

@app.post('/delete-user')
async def deleteTheUser(data: deleteExistingUser):
    result = server.deleteExistingUser(data.email)
    return {"message": result}

@app.post('/request-reset')
async def requestUserPasswordReset(data: requestResetModel):
    if not server.checkUser(data.email):
        return JSONResponse(status_code=404, content={"success": False})
    
    token = server.passwordReset(data.email)
    if token:
        link = f"https://confess-ysj8.onrender.com/reset-password/{token}"
        server.send_telegram_log(f"[Password Reset Link Generated]\nEmail: {data.email}\nLink: {link}")
        return {"success": True}

    return JSONResponse(status_code=500, content={"success": False})

@app.post('/reset-password')
async def resetPassword(data: passwordResetModel):
    valid, result = server.validateResetLink(data.token)
    if not valid:
        return JSONResponse(status_code=400, content={"message": result})

    server.markTokenUsed(data.token)
    if server.updateUserPassword(result, data.newPassword):
        return {"message": "Password reset successful"}
    else:
        return JSONResponse(status_code=500, content={"message": "Failed to update password"})
    
@app.get('/validate-token/{token}')
async def validate_token(token: str):
    valid, msg = server.validateResetLink(token)
    return {"valid": valid, "message": msg if not valid else "Token is valid"}
    
@app.get('/reset-password/{token}', response_class=HTMLResponse)
async def show_reset_form(request: Request, token: str):
    valid, msg = server.validateResetLink(token)
    if not valid:
        return templates.TemplateResponse("invalid_token.html", {"request": request, "message": msg})
    return templates.TemplateResponse("reset_password.html", {"request": request, "token": token})


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
