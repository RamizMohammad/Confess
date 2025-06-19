import requests
import time
import os

def keep_alive():
    while True:
        try:
            headers = {
                "x-api-key": os.environ["CLIENT_KEY"]
            }
            response = requests.post("https://confess-ysj8.onrender.com/jagte-raho", headers=headers)
            print("KeepAlive Ping:", response.status_code, response.text)
        except Exception as e:
            print("KeepAlive Error:", e)
        time.sleep(100) 
