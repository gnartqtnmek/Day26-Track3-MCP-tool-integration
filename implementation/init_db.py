# implementation/init_db.py
import sqlite3
import os

"""SQLite database initialisation and seed data for the MCP lab."""

DB_PATH = os.path.join(os.path.dirname(__file__), "lab.db")

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS students (
    id     INTEGER PRIMARY KEY AUTOINCREMENT,
    name   TEXT    NOT NULL,
    email  TEXT    UNIQUE NOT NULL,
    cohort TEXT    NOT NULL,
    score  REAL    NOT NULL
);

CREATE TABLE IF NOT EXISTS courses (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    title      TEXT    NOT NULL,
    instructor TEXT    NOT NULL,
    credits    INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS enrollments (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id  INTEGER NOT NULL REFERENCES students(id),
    course_id   INTEGER NOT NULL REFERENCES courses(id),
    grade       TEXT    NOT NULL,
    enrolled_at TEXT    NOT NULL,
    UNIQUE(student_id, course_id)
);
"""

SEED_SQL = """
INSERT INTO students (name, email, cohort, score) VALUES
    ('Alice Chen',  'alice@lab.com',  'A1', 92),
    ('Bob Kim',     'bob@lab.com',    'A1', 85),
    ('Carol Wu',    'carol@lab.com',  'A1', 78),
    ('David Lee',   'david@lab.com',  'A1', 88),
    ('Eve Zhang',   'eve@lab.com',    'A1', 71),
    ('Frank Ho',    'frank@lab.com',  'A1', 95),
    ('Grace Liu',   'grace@lab.com',  'A2', 82),
    ('Henry Tan',   'henry@lab.com',  'A2', 67),
    ('Iris Wong',   'iris@lab.com',   'A2', 90),
    ('Jack Ma',     'jack@lab.com',   'A2', 75),
    ('Kara Ng',     'kara@lab.com',   'A2', 65),
    ('Leo Chen',    'leo@lab.com',    'A2', 88),
    ('Mia Park',    'mia@lab.com',    'B1', 80),
    ('Nate Liu',    'nate@lab.com',   'B1', 60),
    ('Olivia Wu',   'olivia@lab.com', 'B1', 75),
    ('Paul Kim',    'paul@lab.com',   'B1', 85),
    ('Quinn Lee',   'quinn@lab.com',  'B1', 70),
    ('Rose Ho',     'rose@lab.com',   'B1', 63);

INSERT INTO courses (title, instructor, credits) VALUES
    ('Python Basics',   'Dr. Smith',  3),
    ('Data Analysis',   'Dr. Jones',  3),
    ('Web Dev',         'Dr. Brown',  2),
    ('ML Fundamentals', 'Dr. Taylor', 4),
    ('SQL Mastery',     'Dr. Wilson', 2);

INSERT INTO enrollments (student_id, course_id, grade, enrolled_at) VALUES
    (1,  1, 'A', '2024-01-15'), (1,  2, 'A', '2024-01-15'),
    (2,  1, 'B', '2024-01-15'), (2,  3, 'B', '2024-01-16'),
    (3,  2, 'B', '2024-01-15'), (3,  4, 'C', '2024-01-17'),
    (4,  1, 'A', '2024-01-15'), (4,  5, 'A', '2024-01-18'),
    (5,  3, 'C', '2024-01-16'),
    (6,  1, 'A', '2024-01-15'),
    (7,  2, 'B', '2024-01-15'), (7,  5, 'B', '2024-01-18'),
    (8,  3, 'C', '2024-01-16'),
    (9,  4, 'A', '2024-01-17'), (9,  2, 'A', '2024-01-15'),
    (10, 1, 'B', '2024-01-15'), (10, 5, 'C', '2024-01-18'),
    (11, 3, 'D', '2024-01-16'), (11, 4, 'C', '2024-01-17'),
    (12, 2, 'A', '2024-01-15'), (12, 1, 'B', '2024-01-15'),
    (13, 1, 'B', '2024-01-15'), (13, 3, 'C', '2024-01-16'),
    (14, 4, 'D', '2024-01-17'),
    (15, 5, 'B', '2024-01-18'), (15, 2, 'B', '2024-01-15'),
    (16, 1, 'A', '2024-01-15'), (16, 4, 'B', '2024-01-17'),
    (17, 3, 'C', '2024-01-16'),
    (18, 5, 'D', '2024-01-18');
"""


def create_database(db_path: str = DB_PATH) -> str:
    """Create (or reset) the lab database with schema and seed data.

    WARNING: If db_path already exists, it is deleted and recreated from scratch.
    This is intentional for lab/demo resets. Do not call during tests — use
    a tmp_path fixture instead.
    """
    if os.path.exists(db_path):
        os.remove(db_path)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA_SQL)
    conn.executescript(SEED_SQL)
    conn.close()
    print(f"Database created: {db_path}")
    return db_path


if __name__ == "__main__":
    create_database()
