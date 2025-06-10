import firebase_admin
from firebase_admin import credentials, firestore
import json, os, time, requests
import datetime
import uuid

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