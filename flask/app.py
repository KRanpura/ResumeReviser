from flask import Flask, render_template, redirect, request, session, url_for
from init_db import get_db
app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template ("login.html" )

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # Ensure required fields are filled
        if (
            not request.form.get("email")
            or not request.form.get("passw")
            or not request.form.get("first_name")
            or not request.form.get("last_name")
        ):
            return render_template("error.html")

        email = request.form.get("email")
        passw = request.form.get("passw")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")

        db = get_db()
        cursor = db.cursor()

        # Check if email already exists in the database
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            return render_template("error.html")

        # Insert the new user into the database
        cursor.execute(
            "INSERT INTO users (first_name, last_name, email, passw) VALUES (?, ?, ?, ?)",
            (first_name, last_name, email, passw),
        )
        db.commit()

        # Store user information in the session
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        session["user_id"] = user["id"]

        return redirect(url_for("mainpage"))

    return render_template("signup.html")
