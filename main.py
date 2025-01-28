from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
from dbinit import get_db_connection

# Initialize Flask app
app = Flask(__name__)

db = get_db_connection()

# Helper function to format note data
def format_note(note):
    return {
        "id": str(note.get("_id")),
        "title": note.get("title"),
        "content": note.get("content"),
        "tags": note.get("tags", []),
        "input_type": note.get("input_type"),
        "timestamp": note.get("timestamp"),
        "updated_at": note.get("updated_at"),
        "priority": note.get("priority"),
        "archived": note.get("archived", False),
        "pinned": note.get("pinned", False),
        "favorite": note.get("favorite", False),
        "related_notes": note.get("related_notes", []),
        "color_label": note.get("color_label"),
    }


# 1. Create a new note
@app.route("/notes", methods=["POST"])
def create_note():
    data = request.json
    note = {
        "title": data.get("title"),
        "content": data.get("content"),
        "tags": data.get("tags", []),
        "input_type": data.get("input_type"),
        "timestamp": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "priority": data.get("priority", "low"),
        "archived": False,
        "pinned": False,
        "favorite": False,
        "related_notes": data.get("related_notes", []),
        "color_label": data.get("color_label"),
    }
    note_id = db.insert_one(note).inserted_id
    return jsonify({"message": "Note created", "id": str(note_id)}), 201


# 2. Retrieve all notes
@app.route("/notes", methods=["GET"])
def get_notes():
    notes = db.find()
    return jsonify([format_note(note) for note in notes]), 200


# 3. Retrieve a single note by ID
@app.route("/notes/<note_id>", methods=["GET"])
def get_note(note_id):
    note = db.find_one({"_id": ObjectId(note_id)})
    if not note:
        return jsonify({"error": "Note not found"}), 404
    return jsonify(format_note(note)), 200


# 4. Update a note
@app.route("/notes/<note_id>", methods=["PUT"])
def update_note(note_id):
    data = request.json
    update_data = {
        "title": data.get("title"),
        "content": data.get("content"),
        "tags": data.get("tags"),
        "input_type": data.get("input_type"),
        "updated_at": datetime.utcnow(),
        "priority": data.get("priority"),
        "archived": data.get("archived"),
        "pinned": data.get("pinned"),
        "favorite": data.get("favorite"),
        "related_notes": data.get("related_notes"),
        "color_label": data.get("color_label"),
    }
    update_data = {
        k: v for k, v in update_data.items() if v is not None
    }  # Remove None values
    result = db.update_one({"_id": ObjectId(note_id)}, {"$set": update_data})
    if result.matched_count == 0:
        return jsonify({"error": "Note not found"}), 404
    return jsonify({"message": "Note updated"}), 200


# 5. Delete a note
@app.route("/notes/<note_id>", methods=["DELETE"])
def delete_note(note_id):
    result = db.delete_one({"_id": ObjectId(note_id)})
    if result.deleted_count == 0:
        return jsonify({"error": "Note not found"}), 404
    return jsonify({"message": "Note deleted"}), 200


# 6. Search notes by tag or input type
@app.route("/notes/search", methods=["GET"])
def search_notes():
    tag = request.args.get("tag")
    input_type = request.args.get("input_type")
    query = {}
    if tag:
        query["tags"] = tag
    if input_type:
        query["input_type"] = input_type
    notes = db.find(query)
    return jsonify([format_note(note) for note in notes]), 200


# 7. Archive/Unarchive a note
@app.route("/notes/<note_id>/archive", methods=["PATCH"])
def archive_note(note_id):
    data = request.json
    archived = data.get("archived", True)
    result = db.update_one({"_id": ObjectId(note_id)}, {"$set": {"archived": archived}})
    if result.matched_count == 0:
        return jsonify({"error": "Note not found"}), 404
    status = "archived" if archived else "unarchived"
    return jsonify({"message": f"Note {status}"}), 200


if __name__ == "__main__":
    app.run(debug=True)
