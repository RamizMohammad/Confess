import hashlib
import secrets
from .Databaseconfig import ConfessServer
import os

class ApiValidator:
    def __init__(self):
        self.apiKey = os.environ["API_KEY"]
        self.valiServer = ConfessServer()

    def validate(self, client_key: str) -> bool:
        if not client_key:
            self.valiServer.send_telegram_log(message="Api key not found in request")
            return False
        
        match_key = hashlib.sha256(client_key.encode()).hexdigest()
        if match_key != self.apiKey:
            self.valiServer.send_telegram_log(message="API_KEY not matched")
            return False
        return True