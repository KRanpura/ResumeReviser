DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS resumeResult;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    passw TEXT NOT NULL
);

CREATE TABLE resumeResult (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    pdf_filename TEXT NOT NULL,
    job_listing TEXT NOT NULL,
    match_percentage REAL NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);