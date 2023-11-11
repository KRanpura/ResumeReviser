from flask import Flask, render_template, redirect, url_for
#from datetime import datetime
app = Flask(__name__)

@app.route("/")
def index():
    return redirect(url_for('login'))

@app.route("/login")
def login():
    return render_template ("login.html" )

# @app.route("/hello/<name>")
# def hello(name = None):
#     return render_template (
#         "hello.html",
#         name = name,
#         date = datetime.now()
#     )