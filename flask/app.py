import PyPDF2
from flask import Flask, render_template, redirect, request, session, url_for, send_file, make_response, g
import os
# from init_db import get_db
from flask import send_from_directory
from werkzeug.utils import secure_filename
#from pdf2image import convert_from_path


from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

#from operator import methodcaller
from os import urandom
import sqlite3

from needlogin import login_required

app = Flask(__name__)
app.secret_key = urandom(24)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

DATABASE = 'princeton.db'
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DATABASE'] = DATABASE


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/suggestions")
def suggestions():
    return render_template("suggestions.html")

@app.route('/logout', methods=['POST'])
def logout():
    # Clear the user session
    session.pop('user_id', None)
    return redirect(url_for('index')) 

@app.route('/dashboard')
def dashboard():
    user_id = session['user_id']
    db = get_db()
    cursor = db.cursor()

    # Retrieve user information from the database based on user_id
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()

    # Retrieve all previous submissions for the user
    cursor.execute("SELECT * FROM resumeResult WHERE user_id = ?", (user_id,))
    submissions = cursor.fetchall()

    return render_template('dashboard.html', user=user, submissions=submissions)

    

@app.route('/mainpage', methods=['GET', 'POST'])
def mainpage():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    

    if 'user_id' in session:
        user_id = session['user_id']
        db = get_db()
        cursor = db.cursor()

        # Retrieve user information from the database based on user_id
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()


    matPercent = None
    pdf_images = None

    if request.method == 'POST':
        job_listing = request.form.get('job_listing')
        if job_listing:
            matPercent = checkKeyWordMatch(job_listing)

            # Access feature names from the session
            feature_names = session.get('feature_names', [])

            # Convert the PDF to images
            pdf_path = session.get('current_filename')
            #pdf_images = convert_pdf_to_images(pdf_path)

            # Render the match_result.html template with the match percentage, feature names, and PDF images
            return render_template('match_result.html', matPercent=matPercent, feature_names=feature_names)

    pdf_path = session.get('current_filename')
    filename = os.path.basename(pdf_path) if pdf_path else None

    return render_template('mainpage.html', user=user, matPercent=matPercent, pdf_path=pdf_path, filename=filename, pdf_images=pdf_images)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    session['current_filename'] = filename
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

#def convert_pdf_to_images(pdf_path):
    #images = convert_from_path(pdf_path)
   # return images


@app.route('/upload', methods=['POST'])
def upload():
    if 'pdf_file' not in request.files or not request.files['pdf_file'].filename:
        return render_template('mainpage.html', error='No file part', pdf_path=None)

    file = request.files['pdf_file']

    if file.filename == '':
        return render_template('mainpage.html', error='No selected file', filename=None, pdf_path=None)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        session['current_filename'] = filename  # Save the current filename in the session

        return redirect(url_for('process_form', job_listing=request.form.get('job_listing')), code=307)
       # return redirect(url_for('mainpage'))
    error = 'Invalid file type' if file else 'No selected file'
    return render_template('mainpage.html', error=error, filename=None, pdf_path=None)

def extract_text_from_pdf(pdf_path, page_number=0):
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = pdf_reader.pages[page_number].extract_text()
    return text

@app.route('/process_form', methods=['POST'])
def process_form():
    
    if 'user_id' in session:
        user_id = session['user_id']
        db = get_db()
        cursor = db.cursor()

        # Retrieve user information from the database based on user_id
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()

    job_listing = request.form.get('job_listing')

    pdf_path = session.get('current_filename')
    filename = os.path.basename(pdf_path) if pdf_path else None

    if job_listing and pdf_path:
        matPercent, matching_words = checkKeyWordMatch(job_listing)        
        cursor.execute(
            "INSERT INTO resumeResult (user_id, pdf_filename, job_listing, match_percentage) VALUES (?, ?, ?, ?)",
            (user_id, filename, job_listing, matPercent)
        )
        db.commit()
        return render_template('mainpage.html', user=user, matPercent=matPercent, pdf_path=pdf_path, filename=filename)
    else:
        error_message = 'No file uploaded' if not pdf_path else 'Job listing is empty'
        return render_template('mainpage.html', error=error_message, pdf_path=pdf_path, filename=filename)


def checkKeyWordMatch(job_listing):
    filename = session.get('current_filename')

    if filename is None:
        return "Error: No filename in session."

    pdf_path = os.path.join('uploads', filename)

    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)

        # Assuming you want to extract text from the first page (zero-indexed)
        page_number = 0
        text = extract_text_from_pdf(pdf_path, page_number)

        if job_listing:
            compare = [text, job_listing]

        cVect = CountVectorizer()
        cMatrix = cVect.fit_transform(compare)
        matPercent = cosine_similarity(cMatrix)[0][1] * 100
        matPercent = round(matPercent, 2)  # round to two decimal

        feature_names = cVect.get_feature_names_out().tolist()

        # Filter out non-matching words
        matching_words = [word for word, value in zip(feature_names, cMatrix.toarray()[0]) if value > 0]

        session['feature_names'] = feature_names

        return str(matPercent), matching_words

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(
            app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        db.row_factory = sqlite3.Row
    return db

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql') as f:
            db.executescript(f.read().decode('utf-8'))



@app.teardown_appcontext
def close_db(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

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
        first_name = first_name[0].upper() + first_name[1:]
        last_name = request.form.get("last_name")
        last_name = last_name[0].upper() + last_name[1:]


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


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        passw = request.form.get("passw")  # Rename to "password" for clarity
        print(email)
        print(passw)
        db = get_db()
        cursor = db.cursor()

        # Retrieve the user's record from the database based on email
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()

        if not user:
            return render_template("error.html")

        # Compare the provided password with the password stored in the database
        if user["passw"] == passw:  # Assuming both are plain text
            # Store user information in the session
            session["user_id"] = user["id"]
            return redirect(url_for("mainpage"))
        else:
            return render_template("error.html")

    return render_template("login.html")


init_db()
if __name__ == "__main__":
    app.run(debug=True)
