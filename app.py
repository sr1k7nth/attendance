from flask import Flask, render_template, request, session, redirect, url_for
from scrapper import scrape_attendance
import requests

APP_VERSION = "1.1.2"
GITHUB_API = "https://api.github.com/repos/sr1k7nth/attendance/releases/latest"

def version_tuple(v):
    return tuple(map(int, v.split(".")))

def check_for_update():
    try:
        response = requests.get(GITHUB_API, timeout=5)
        data = response.json()

        latest_version = data["tag_name"].lstrip("v")

        if version_tuple(latest_version) > version_tuple(APP_VERSION):
            return {
                "update_available": True,
                "latest_version": latest_version,
                "url": data["html_url"]
            }

        return {"update_available": False}

    except:
        return {"update_available": False}


app = Flask(__name__)
app.secret_key = "1234"

@app.get("/")
def home():
    return render_template("index.html")

@app.post("/login")
def login():
    uid = request.form["uid"]
    password = request.form["pass"]
    result = scrape_attendance(uid, password)

    session["attendance_result"] = result

    return redirect(url_for("summary"))

@app.get("/summary")
def summary():
    result = session.get("attendance_result")
    update_info = check_for_update()

    if not result:
        return render_template("wrong.html")

    return render_template("summary.html", result=result, update=update_info)



if __name__ == "__main__":
    import webbrowser
    webbrowser.open("http://127.0.0.1:5000")

    from waitress import serve
    serve(app, host="127.0.0.1", port=5000)