import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from flask import Flask,request,jsonify
import json, os, threading, time, requests

app = Flask(__name__)

class serverClass:
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

    def createUser(self,data):
        try:
            self.db.collection("Confession-UserData").add(data)
            self.status = True
        except:
            self.status = True

    def checkUser(self,email):
        findTheMail = self.db.collection("Confession-UserData")
        query = findTheMail.where("email", "==", email).limit(1).stream()

        for mail in query:
            return True
        
        return False

server = serverClass()

@app.route('/jagte-raho')
def jagteRaho():
    return "Abhi hum jinda hai"

@app.route('/')
def establishConnection():
    return jsonify({
        "message": server.status
    }),200

@app.route('/add-user', methods=['POST'])
def saveData():
    res = request.get_json()
    server.createUser(res)
    return jsonify({
        "message": server.status
    })

@app.route('/check-user',methods=['POST'])
def checkUser():
    res = request.get_json()
    email = res.get('email')

    if server.checkUser(email):
        return jsonify({
            "message" : True,
        })
    else:
        return jsonify({
            "message" : False,
        })


def keepAlive():
    while True:
        time.sleep(300)
        requests.get("https://confess-ysj8.onrender.com/jagte-raho")

threading.Thread(target=keepAlive, daemon=True).start()