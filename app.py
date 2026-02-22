import json
import os
import shutil
from pathlib import Path
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

load_dotenv()

app = Flask(__name__)

CANVAS_BASE_URL = os.getenv("CANVAS_BASE_URL", "").rstrip("/")
CANVAS_TOKEN = os.getenv("CANVAS_TOKEN", "")
PORT = int(os.getenv("PORT", "5000"))
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"

CRITERIA_CONFIG_PATH = Path("config/criteria.json")
GROUPING_MODELS_PATH = Path("Criteria Grouping Models")


class CanvasError(Exception):
    pass


DEMO_COURSES = [
    {"id": 101, "name": "Demo Course: Foundations"},
    {"id": 102, "name": "Demo Course: Project Studio"},
]

DEMO_ASSIGNMENTS = {
    101: [
        {"id": 5001, "name": "Essay Draft", "points_possible": 100},
        {"id": 5002, "name": "Presentation", "points_possible": 100},
    ],
    102: [
        {"id": 6001, "name": "Prototype Plan", "points_possible": 100},
    ],
}

DEMO_STUDENTS = {
    (101, 5001): [
        {"id": 9001, "name": "Alex Smith", "current_grade": None},
        {"id": 9002, "name": "Jordan Lee", "current_grade": None},
    ],
    (101, 5002): [
        {"id": 9001, "name": "Alex Smith", "current_grade": None},
    ],
    (102, 6001): [
        {"id": 9003, "name": "Taylor Rivera", "current_grade": None},
    ],
}


def canvas_headers() -> Dict[str, str]:
    if not CANVAS_TOKEN:
        raise CanvasError("CANVAS_TOKEN is not set. Add it to your .env file.")
    return {"Authorization": f"Bearer {CANVAS_TOKEN}"}


def canvas_get(path: str, params: Dict[str, Any] = None) -> Any:
    if not CANVAS_BASE_URL:
        raise CanvasError("CANVAS_BASE_URL is not set. Add it to your .env file.")
    response = requests.get(
        f"{CANVAS_BASE_URL}{path}", headers=canvas_headers(), params=params or {}, timeout=20
    )
    if response.status_code >= 400:
        raise CanvasError(f"Canvas GET failed ({response.status_code}): {response.text}")
    return response.json()


def canvas_put(path: str, payload: Dict[str, Any]) -> Any:
    if not CANVAS_BASE_URL:
        raise CanvasError("CANVAS_BASE_URL is not set. Add it to your .env file.")
    response = requests.put(
        f"{CANVAS_BASE_URL}{path}", headers=canvas_headers(), data=payload, timeout=20
    )
    if response.status_code >= 400:
        raise CanvasError(f"Canvas PUT failed ({response.status_code}): {response.text}")
    return response.json()


def load_criteria() -> List[Dict[str, Any]]:
    if not CRITERIA_CONFIG_PATH.exists():
        return []

    with CRITERIA_CONFIG_PATH.open("r", encoding="utf-8") as file:
        payload = json.load(file)

    criteria = payload.get("criteria", [])
    valid = []
    for item in criteria:
        title = item.get("title", "").strip()
        domain = item.get("domain", "").strip()
        max_score = float(item.get("max_score", 5))
        if not title or not domain:
            continue
        valid.append(
            {
                "id": item.get("id", title.lower().replace(" ", "_")),
                "title": title,
                "domain": domain,
                "description": item.get("description", ""),
                "max_score": max_score,
                "weight": float(item.get("weight", 1)),
            }
        )
    return valid


def grouped_criteria(criteria: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for item in criteria:
        domain = item["domain"]
        if domain not in grouped:
            grouped[domain] = []
        grouped[domain].append(item)
    return [{"domain": domain, "criteria": items} for domain, items in grouped.items()]


def available_models() -> List[Dict[str, str]]:
    models: List[Dict[str, str]] = []
    if GROUPING_MODELS_PATH.exists():
        for path in sorted(GROUPING_MODELS_PATH.glob("*.json")):
            models.append({"id": path.stem, "name": path.stem, "path": str(path)})
    return models


@app.route("/")
def index():
    criteria = load_criteria()
    return render_template(
        "index.html",
        criteria=criteria,
        grouped=grouped_criteria(criteria),
        demo_mode=DEMO_MODE,
    )


@app.route("/api/models")
def models():
    return jsonify(available_models())


@app.route("/api/models/<model_id>/activate", methods=["POST"])
def activate_model(model_id: str):
    source = GROUPING_MODELS_PATH / f"{model_id}.json"
    if not source.exists():
        return jsonify({"error": f"Model '{model_id}' not found."}), 404
    shutil.copyfile(source, CRITERIA_CONFIG_PATH)
    return jsonify({"ok": True, "message": f"Activated model: {model_id}"})


@app.route("/api/connection")
def connection():
    if DEMO_MODE:
        return jsonify(
            {
                "mode": "demo",
                "ok": True,
                "message": "Demo mode is active. Canvas is not required.",
            }
        )

    if not CANVAS_BASE_URL or not CANVAS_TOKEN:
        return jsonify(
            {
                "mode": "canvas",
                "ok": False,
                "message": "Canvas is not configured yet. Add CANVAS_BASE_URL and CANVAS_TOKEN in .env.",
            }
        )

    try:
        profile = canvas_get("/api/v1/users/self")
        return jsonify(
            {
                "mode": "canvas",
                "ok": True,
                "message": f"Connected to Canvas as {profile.get('name', 'Unknown User')}.",
            }
        )
    except CanvasError as error:
        return jsonify({"mode": "canvas", "ok": False, "message": str(error)}), 400


@app.route("/api/courses")
def courses():
    if DEMO_MODE:
        return jsonify(DEMO_COURSES)
    try:
        data = canvas_get("/api/v1/courses", {"per_page": 50, "enrollment_type": "teacher"})
        simplified = [{"id": c["id"], "name": c.get("name", f"Course {c['id']}")} for c in data]
        return jsonify(simplified)
    except CanvasError as error:
        return jsonify({"error": str(error)}), 400


@app.route("/api/courses/<int:course_id>/assignments")
def assignments(course_id: int):
    if DEMO_MODE:
        return jsonify(DEMO_ASSIGNMENTS.get(course_id, []))
    try:
        data = canvas_get(f"/api/v1/courses/{course_id}/assignments", {"per_page": 50})
        simplified = [
            {
                "id": a["id"],
                "name": a.get("name", f"Assignment {a['id']}"),
                "points_possible": a.get("points_possible", 100),
            }
            for a in data
        ]
        return jsonify(simplified)
    except CanvasError as error:
        return jsonify({"error": str(error)}), 400


@app.route("/api/courses/<int:course_id>/assignments/<int:assignment_id>/students")
def students(course_id: int, assignment_id: int):
    if DEMO_MODE:
        return jsonify(DEMO_STUDENTS.get((course_id, assignment_id), []))
    try:
        params = {
            "per_page": 50,
            "include[]": ["user"],
        }
        data = canvas_get(
            f"/api/v1/courses/{course_id}/assignments/{assignment_id}/submissions", params
        )
        simplified = []
        for submission in data:
            user = submission.get("user") or {}
            user_id = user.get("id")
            if not user_id:
                continue
            simplified.append(
                {
                    "id": user_id,
                    "name": user.get("name", f"Student {user_id}"),
                    "current_grade": submission.get("grade"),
                }
            )
        return jsonify(simplified)
    except CanvasError as error:
        return jsonify({"error": str(error)}), 400


@app.route("/api/publish-grade", methods=["POST"])
def publish_grade():
    payload = request.get_json(force=True)
    required = ["course_id", "assignment_id", "student_id", "grade"]
    if any(key not in payload for key in required):
        return jsonify({"error": "Missing required fields."}), 400

    grade = payload["grade"]
    comment = payload.get("comment", "")

    if DEMO_MODE:
        return jsonify(
            {
                "ok": True,
                "result": {
                    "demo": True,
                    "published_grade": grade,
                    "comment": comment,
                    "student_id": payload["student_id"],
                },
            }
        )

    try:
        result = canvas_put(
            f"/api/v1/courses/{payload['course_id']}/assignments/{payload['assignment_id']}/submissions/{payload['student_id']}",
            {
                "submission[posted_grade]": grade,
                "comment[text_comment]": comment,
            },
        )
        return jsonify({"ok": True, "result": result})
    except CanvasError as error:
        return jsonify({"error": str(error)}), 400


if __name__ == "__main__":
    app.run(debug=True, port=PORT)
