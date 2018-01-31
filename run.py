from app import app


import threading, webbrowser


url = "http://localhost:5000"
#threading.Timer(1.25, lambda: webbrowser.open(url,new = 2) ).start()


app.run(debug = True,threaded=True)

