import firebase_admin
from firebase_admin import credentials, firestore, storage
import json, os, time, requests
import datetime
import uuid
from typing import Tuple
from fastapi import UploadFile
from .emailUtils import EmailManager

class ConfessServer():
    def __init__(self):
        #! Initialize Firebase and Telegram credentials
        self.botToken = os.environ["BOT_TOKEN"]
        self.chatId = os.environ["CHAT_ID"]
        self.BUCKET_NAME = os.environ["BUCKET_NAME"]
        self.emailServer = EmailManager()

        try:
            #! Initialize Firebase App only once
            if not firebase_admin._apps:
                cred_json = json.loads(os.environ["FIREBASE_CREDENTIALS"])
                cred = credentials.Certificate(cred_json)
                firebase_admin.initialize_app(
                    cred,
                    {'storageBucket': self.BUCKET_NAME}
                )
            self.db = firestore.client()
            self.bucket = storage.bucket()
            self.status = True
        except Exception as e:
            self.send_telegram_log(f"Firestore Connection failed:\n{e}")
            self.status = False

    #! ---------------------------------------------
    #! POST ALGORITHMS
    #! ---------------------------------------------

    def addPost(self, data: dict) -> bool:
        try:
            self.db.collection("Confession-Posts").add(data)
            return True
        except Exception as e:
            self.send_telegram_log(f"Error in post saving\n{e}")
            return False

    #! ──────────────────────────────────────────────
    #! 🧑‍💼 User Account Management
    #! ──────────────────────────────────────────────

    def createUser(self, data: dict) -> bool:
        try:
            self.db.collection("Confession-UserData").add(data)
            self.send_telegram_log(f"🎉 New user joined:\n{data}")
            name = data.get("name", "User")
            email = data.get("email")
            joined = data.get("date")

            if email:
                success = self.emailServer.send(
                    to=email,
                    subject="Welcome to Our Platform",
                    templateName="welcome.html",
                    context={
                        "name": name,
                        "email": email,
                        "date": joined
                    }
                )
                if success:
                    self.send_telegram_log(f"✅ Welcome email sent to {email}")
                else:
                    self.send_telegram_log(f"❌ Failed to send welcome email to {email}")
            return True
        except Exception as e:
            self.send_telegram_log(f"❌ CreateUser Error:\n{e}")
            return False

    def checkUser(self, email: str) -> bool:
        #! Check if a user exists in Firestore by email.
        try:
            user = self.db.collection("Confession-UserData").where("email", "==", email).limit(1).stream()
            for _ in user:
                return True
            return False
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

            if userErased:
                emailManager = EmailManager(log_func=self.send_telegram_log)
                emailSent = emailManager.send(
                    to=email,
                    subject="Your Confess Account Has Been Deleted",
                    templateName="delete.html",  # Ensure this file exists in /templates
                    context={
                        "name": email.split('@')[0].capitalize()
                    }
                )
                if not emailSent:
                    self.send_telegram_log(f"⚠️ User deleted but failed to send deletion email to {email}")
                return True
            return False

        except Exception as e:
            self.send_telegram_log(f"❌ Error deleting user {email}:\n{e}")
            return False

    def updateUserPassword(self, email: str, new_password: str):
        #! Update a user's password.
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
        
    def checkExistingAlaisName(self, alais: str) -> bool:
        try:
            alaisCheck = self.db.collection("Confession-UserData").where("aliasName", "==", alais).limit(1).stream()
            for  _ in alaisCheck:
                return True
            return False
        except Exception as e:
            self.send_telegram_log(f"We got an error:\n{e}")
    #! ──────────────────────────────────────────────
    #!🔐 Password Reset Workflow
    #! ──────────────────────────────────────────────

    def passwordReset(self, email: str):
        #! Generate and store a password reset token.
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
        #! Validate reset token and check expiry (10 mins) and usage.
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
                return False, "Token already used"

        except Exception as e:
            self.send_telegram_log(f"Error in validating token:\n{e}")
            return False, "Validation Error"

    def markTokenUsed(self, token: str):
        #! Mark a password reset token as used.
        try:
            self.db.collection("PasswordResetToken").document(token).update({
                "used": True,
                "usedAt": datetime.datetime.utcnow().isoformat()
            })
        except Exception as e:
            self.send_telegram_log(f"Error marking token:\n{e}")

    #! ---------------------------------------------
    #! Chech for password protection
    #! ---------------------------------------------

    def checkUserAndPassword(self, email: str) -> Tuple[bool, bool]:
        try:
            docs = self.db.collection("Confession-UserData").where("email", "==", email).limit(1).stream()
            for doc in docs:
                userData = doc.to_dict()
                return True, userData.get('isPassword', False)
            return False, False
        except Exception as e:
            self.send_telegram_log(f"Error in checking password:\n{e}")
            return False, False
        
    def checkForCorrectPassword(self, email:str, password: str) -> bool:
        
        if not self.checkUser(email):
            return False
        
        try:
            users = self.db.collection("Confession-UserData").where("email", "==", email).limit(1).stream()
            for user in users:
                data = user.to_dict()
                if(data.get("password") == password):
                    return True
            return False
        except Exception as e:
            self.send_telegram_log(f"Error in checking password:\n{e}")
            return False

    #!-----------------------------------------------
    #! Logs Saver
    #!-----------------------------------------------

    def saveTheServerLogs(self, logs:str):
        self.db.collection("Logs-Data").add({
            "log": logs,
            "timestamp": datetime.datetime.utcnow().isoformat()
        })
        
    #! ──────────────────────────────────────────────
    #! 📢 Telegram Bot Logging
    #! ──────────────────────────────────────────────

    def send_telegram_log(self, message: str):
        #! Send logs or errors to the configured Telegram bot.
        self.saveTheServerLogs(f"Confess Server Errors\n{message}")
        try:
            if self.botToken and self.chatId:
                url = f"https://api.telegram.org/bot{self.botToken}/sendMessage"
                payload = {
                    "chat_id": self.chatId,
                    "text": f"[ConfessBot Error Server]\n{message}"
                }
                requests.post(url, data=payload)
        except Exception as e:
            print("Telegram Logging Failed:", e)
