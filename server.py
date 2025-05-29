import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from flask import Flask,request,jsonify
import json
import os

app = Flask(__name__)

class serverClass:
    def __init__(self):
        try:
            if not firebase_admin._apps:
                cred_json = json.loads(os.environ["FIREBASE_CREDENTIALS"])
                cred = credentials.Certificate(cred_json)
                firebase_admin.initialize_app(cred)
            self.db = firestore.client()
            self.status = "Firestore Connected"
        except:
            self.status = "Firebase Not Connected"

    def addData(self,data):
        try:
            self.db.collection("Confession-UserData").add(data)
            self.status = "Data Saved Successfully"
        except:
            self.status = "Error in data saving"

server = serverClass()

@app.route('/jagte-raho')
def jagteRaho():
    return "JaagRaha hun"

@app.route('/')
def establishConnection():
    return server.status

@app.route('/add-data', methods=['POST'])
def saveData():
    res = request.get_json()
    server.addData(res)
    return server.status
