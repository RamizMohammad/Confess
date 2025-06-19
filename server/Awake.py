import requests, time

def keep_alive():
    while True:
        try:
            requests.get("https://confess-ysj8.onrender.com/jagte-raho")
        except Exception as e:
            print("KeepAlive Error:", e)
        time.sleep(100)