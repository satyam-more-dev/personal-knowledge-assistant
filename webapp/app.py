from flask import Flask, render_template, request, jsonify
import sqlite3
from pathlib import Path

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "mindvault.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT NOT NULL DEFAULT 'Study',
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/notes", methods=["GET"])
def get_notes():
    with get_db() as conn:
        notes = conn.execute(
            "SELECT * FROM notes ORDER BY id DESC"
        ).fetchall()
    return jsonify([dict(note) for note in notes])


@app.route("/api/notes", methods=["POST"])
def add_note():
    data = request.get_json(silent=True) or {}
    title = str(data.get("title", "")).strip()
    category = str(data.get("category", "Study")).strip() or "Study"
    content = str(data.get("content", "")).strip()

    if not title or not content:
        return jsonify({"error": "Title and content are required"}), 400

    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO notes (title, category, content) VALUES (?, ?, ?)",
            (title, category, content)
        )
        note = conn.execute(
            "SELECT * FROM notes WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()

    return jsonify(dict(note)), 201


@app.route("/api/notes/<int:note_id>", methods=["PUT"])
def update_note(note_id):
    data = request.get_json(silent=True) or {}
    title = str(data.get("title", "")).strip()
    category = str(data.get("category", "Study")).strip() or "Study"
    content = str(data.get("content", "")).strip()

    if not title or not content:
        return jsonify({"error": "Title and content are required"}), 400

    with get_db() as conn:
        cursor = conn.execute(
            "UPDATE notes SET title=?, category=?, content=? WHERE id=?",
            (title, category, content, note_id)
        )
        if cursor.rowcount == 0:
            return jsonify({"error": "Note not found"}), 404
        note = conn.execute(
            "SELECT * FROM notes WHERE id = ?", (note_id,)
        ).fetchone()

    return jsonify(dict(note))


@app.route("/api/notes/<int:note_id>", methods=["DELETE"])
def delete_note(note_id):
    with get_db() as conn:
        cursor = conn.execute(
            "DELETE FROM notes WHERE id = ?", (note_id,)
        )
        if cursor.rowcount == 0:
            return jsonify({"error": "Note not found"}), 404

    return jsonify({"success": True})


init_db()

if __name__ == "__main__":
    app.run(debug=True)