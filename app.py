from flask import Flask, render_template, request, session, redirect, url_for
from scrapper import scrape_attendance

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

    if result is None:
        return render_template("wrong.html")
    
    return render_template("summary.html", result=result)


if __name__ == "__main__":
    import webbrowser
    webbrowser.open("http://127.0.0.1:5000")

    from waitress import serve
    serve(app, host="127.0.0.1", port=5000)