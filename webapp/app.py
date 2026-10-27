import os
from dotenv import load_dotenv

load_dotenv()

import re
import sqlite3
from pathlib import Path

from flask import (
    Flask, render_template, request,
    jsonify, redirect, url_for, flash
)
from flask_login import (
    LoginManager, UserMixin, login_user,
    logout_user, login_required, current_user
)
from werkzeug.security import (
    generate_password_hash, check_password_hash
)

app = Flask(__name__)

# Local development key. Public deployment se pehle environment variable set karna.
app.config["SECRET_KEY"] = os.environ.get("MINDVAULT_SECRET_KEY")

if not app.config["SECRET_KEY"]:
    raise RuntimeError("MINDVAULT_SECRET_KEY is missing. Check your .env file.")

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "mindvault.db"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"





def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


class User(UserMixin):
    def __init__(self, user_id, username, password_hash):
        self.id = str(user_id)
        self.username = username
        self.password_hash = password_hash


@login_manager.user_loader
def load_user(user_id):
    with get_db() as conn:
        user = conn.execute(
            "SELECT * FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()

    if user is None:
        return None

    return User(user["id"], user["username"], user["password_hash"])


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT NOT NULL DEFAULT 'Study',
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Existing database ko delete kiye bina ownership column add karo.
        columns = {
            row["name"]
            for row in conn.execute("PRAGMA table_info(notes)").fetchall()
        }

        if "owner_id" not in columns:
            conn.execute(
                "ALTER TABLE notes ADD COLUMN owner_id INTEGER REFERENCES users(id)"
            )


@login_manager.unauthorized_handler
def unauthorized():
    if request.path.startswith("/api/"):
        return jsonify({"error": "Please log in to continue."}), 401

    return redirect(url_for("login"))


@app.route("/")
@login_required
def home():
    return render_template("index.html", username=current_user.username)


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not re.fullmatch(r"[A-Za-z0-9_]{3,30}", username):
            flash(
                "Username 3–30 characters ka hona chahiye. "
                "Letters, numbers aur underscore use karo.",
                "error"
            )
            return render_template("auth.html", mode="register")

        if len(password) < 8:
            flash("Password kam se kam 8 characters ka hona chahiye.", "error")
            return render_template("auth.html", mode="register")

        try:
            with get_db() as conn:
                cursor = conn.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (username, generate_password_hash(password))
                )
                new_user_id = cursor.lastrowid

                # Pehle se maujood notes ko first account se associate karo.
                # Yeh initial migration local development ke liye hai.
                user_count = conn.execute(
                    "SELECT COUNT(*) FROM users"
                ).fetchone()[0]

                if user_count == 1:
                    conn.execute(
                        "UPDATE notes SET owner_id = ? WHERE owner_id IS NULL",
                        (new_user_id,)
                    )

            user = User(new_user_id, username, "")
            login_user(user)
            return redirect(url_for("home"))

        except sqlite3.IntegrityError:
            flash("Yeh username pehle se registered hai.", "error")

    return render_template("auth.html", mode="register")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        with get_db() as conn:
            user = conn.execute(
                "SELECT * FROM users WHERE username = ?",
                (username,)
            ).fetchone()

        if user and check_password_hash(user["password_hash"], password):
            login_user(
                User(user["id"], user["username"], user["password_hash"])
            )
            return redirect(url_for("home"))

        flash("Username ya password galat hai.", "error")

    return render_template("auth.html", mode="login")


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/api/notes", methods=["GET"])
@login_required
def get_notes():
    with get_db() as conn:
        notes = conn.execute(
            """
            SELECT id, title, category, content, created_at
            FROM notes
            WHERE owner_id = ?
            ORDER BY id DESC
            """,
            (int(current_user.id),)
        ).fetchall()

    return jsonify([dict(note) for note in notes])


@app.route("/api/notes", methods=["POST"])
@login_required
def add_note():
    data = request.get_json(silent=True) or {}

    title = str(data.get("title", "")).strip()
    category = str(data.get("category", "Study")).strip() or "Study"
    content = str(data.get("content", "")).strip()

    if not title or not content:
        return jsonify({"error": "Title and content are required"}), 400

    with get_db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO notes (title, category, content, owner_id)
            VALUES (?, ?, ?, ?)
            """,
            (title, category, content, int(current_user.id))
        )

        note = conn.execute(
            """
            SELECT id, title, category, content, created_at
            FROM notes
            WHERE id = ? AND owner_id = ?
            """,
            (cursor.lastrowid, int(current_user.id))
        ).fetchone()

    return jsonify(dict(note)), 201


@app.route("/api/notes/<int:note_id>", methods=["PUT"])
@login_required
def update_note(note_id):
    data = request.get_json(silent=True) or {}

    title = str(data.get("title", "")).strip()
    category = str(data.get("category", "Study")).strip() or "Study"
    content = str(data.get("content", "")).strip()

    if not title or not content:
        return jsonify({"error": "Title and content are required"}), 400

    with get_db() as conn:
        cursor = conn.execute(
            """
            UPDATE notes
            SET title = ?, category = ?, content = ?
            WHERE id = ? AND owner_id = ?
            """,
            (title, category, content, note_id, int(current_user.id))
        )

        if cursor.rowcount == 0:
            return jsonify({"error": "Note not found"}), 404

        note = conn.execute(
            """
            SELECT id, title, category, content, created_at
            FROM notes
            WHERE id = ? AND owner_id = ?
            """,
            (note_id, int(current_user.id))
        ).fetchone()

    return jsonify(dict(note))


@app.route("/api/notes/<int:note_id>", methods=["DELETE"])
@login_required
def delete_note(note_id):
    with get_db() as conn:
        cursor = conn.execute(
            "DELETE FROM notes WHERE id = ? AND owner_id = ?",
            (note_id, int(current_user.id))
        )

        if cursor.rowcount == 0:
            return jsonify({"error": "Note not found"}), 404

    return jsonify({"success": True})


init_db()

if __name__ == "__main__":
    app.run(debug=True)