import os
import json
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify, render_template, g, session, redirect
from flask_cors import CORS
from dotenv import load_dotenv
from groq import Groq
import threading
import requests
import time

load_dotenv()

app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv("SECRET_KEY", "saferoute-secret-2025")

DB_PATH = "saferoute.db"
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

ADMIN_USER = os.getenv("ADMIN_USER", "aliraza987")
ADMIN_PASS = os.getenv("ADMIN_PASS", "aliraza987")

# ── DATABASE ──────────────────────────────────────────────

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop("db", None)
    if db:
        db.close()

def init_db():
    db = sqlite3.connect(DB_PATH)
    db.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            lat         REAL NOT NULL,
            lng         REAL NOT NULL,
            type        TEXT NOT NULL,
            description TEXT,
            time_of_day TEXT NOT NULL,
            area_name   TEXT NOT NULL,
            city        TEXT NOT NULL,
            created_at  TEXT NOT NULL,
            upvotes     INTEGER DEFAULT 0,
            reported_by TEXT DEFAULT NULL,
            status      TEXT DEFAULT 'approved'
        )
    """)
    # Add columns if they don't exist (for existing DBs)
    try:
        db.execute("ALTER TABLE incidents ADD COLUMN reported_by TEXT DEFAULT NULL")
    except:
        pass
    try:
        db.execute("ALTER TABLE incidents ADD COLUMN status TEXT DEFAULT 'approved'")
    except:
        pass
    db.commit()
    db.close()

# ── PUBLIC ROUTES ─────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/incidents", methods=["GET"])
def get_incidents():
    city = request.args.get("city")
    db = get_db()
    if city:
        rows = db.execute(
            "SELECT * FROM incidents WHERE city=? AND status='approved' ORDER BY created_at DESC LIMIT 200",
            (city,)
        ).fetchall()
    else:
        rows = db.execute(
            "SELECT * FROM incidents WHERE status='approved' ORDER BY created_at DESC LIMIT 500"
        ).fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/api/incidents", methods=["POST"])
def post_incident():
    data = request.get_json()
    required = ["lat", "lng", "type", "time_of_day", "area_name", "city"]
    if not all(k in data for k in required):
        return jsonify({"error": "Missing fields"}), 400

    db = get_db()
    cur = db.execute(
        """INSERT INTO incidents
           (lat, lng, type, description, time_of_day, area_name, city, created_at, reported_by, status)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending')""",
        (
            data["lat"], data["lng"], data["type"],
            data.get("description", ""),
            data["time_of_day"], data["area_name"],
            data["city"], datetime.utcnow().isoformat(),
            data.get("reported_by", None)
        )
    )
    db.commit()
    row = db.execute("SELECT * FROM incidents WHERE id=?", (cur.lastrowid,)).fetchone()
    return jsonify(dict(row)), 201


@app.route("/api/incidents/<int:incident_id>/upvote", methods=["POST"])
def upvote(incident_id):
    db = get_db()
    db.execute("UPDATE incidents SET upvotes=upvotes+1 WHERE id=?", (incident_id,))
    db.commit()
    row = db.execute("SELECT * FROM incidents WHERE id=?", (incident_id,)).fetchone()
    return jsonify(dict(row))


@app.route("/api/assess", methods=["GET"])
def assess():
    lat  = float(request.args.get("lat", 0))
    lng  = float(request.args.get("lng", 0))
    city = request.args.get("city", "Mumbai")
    area = request.args.get("area", "this area")

    db = get_db()
    rows = db.execute(
        """SELECT * FROM incidents
           WHERE city=? AND status='approved'
           AND ABS(lat-?)< 0.03 AND ABS(lng-?)<0.03
           ORDER BY created_at DESC""",
        (city, lat, lng)
    ).fetchall()
    incidents = [dict(r) for r in rows]

    if not incidents:
        return jsonify({
            "area_name": area, "safety_level": "unknown", "safety_score": 75,
            "summary": "No incidents have been reported in this area yet. Always stay alert.",
            "incident_count": 0, "most_common_type": "none",
            "safest_time": "Morning",
            "tip": "Share your live location with a trusted contact when travelling alone at night."
        })

    lines = "\n".join([
        f"- {i['type'].replace('_',' ')} at {i['area_name']} during {i['time_of_day'].replace('_',' ')}: {i['description'] or 'no details'}"
        for i in incidents[:15]
    ])

    type_counts = {}
    for i in incidents:
        type_counts[i["type"]] = type_counts.get(i["type"], 0) + 1
    most_common = max(type_counts, key=type_counts.get)

    time_counts = {}
    for i in incidents:
        time_counts[i["time_of_day"]] = time_counts.get(i["time_of_day"], 0) + 1
    all_times = ["morning", "afternoon", "evening", "night", "late_night"]
    safest_time = next((t.title() for t in all_times if t not in time_counts), "Morning")

    prompt = f"""You are a women's safety assistant for {city}, India.
Here are {len(incidents)} recent community-reported safety incidents near {area}:
{lines}
Give a JSON safety assessment with these exact keys:
- safety_score: integer 0-100
- safety_level: "safe" if score>=70, "caution" if 40-69, "danger" if below 40
- summary: 2 sentences max.
- tip: one specific safety tip. Under 20 words.
Respond ONLY with valid JSON."""

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200, temperature=0.3,
        )
        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        ai = json.loads(raw)
    except Exception as e:
        n = len(incidents)
        score = max(10, 85 - n * 7)
        level = "safe" if score >= 70 else "caution" if score >= 40 else "danger"
        ai = {
            "safety_score": score, "safety_level": level,
            "summary": f"{n} incidents reported nearby. Be especially careful at night.",
            "tip": "Avoid this area alone after dark."
        }

    return jsonify({
        "area_name": area,
        "safety_level": ai.get("safety_level", "caution"),
        "safety_score": ai.get("safety_score", 50),
        "summary": ai.get("summary", ""),
        "incident_count": len(incidents),
        "most_common_type": most_common,
        "safest_time": safest_time,
        "tip": ai.get("tip", "Stay alert and trust your instincts.")
    })


@app.route("/api/stats", methods=["GET"])
def stats():
    city = request.args.get("city", "Mumbai")
    db = get_db()
    total = db.execute("SELECT COUNT(*) FROM incidents WHERE city=? AND status='approved'", (city,)).fetchone()[0]
    by_type = db.execute(
        "SELECT type, COUNT(*) as count FROM incidents WHERE city=? AND status='approved' GROUP BY type ORDER BY count DESC", (city,)
    ).fetchall()
    by_time = db.execute(
        "SELECT time_of_day, COUNT(*) as count FROM incidents WHERE city=? AND status='approved' GROUP BY time_of_day ORDER BY count DESC", (city,)
    ).fetchall()
    hot_areas = db.execute(
        "SELECT area_name, COUNT(*) as count FROM incidents WHERE city=? AND status='approved' GROUP BY area_name ORDER BY count DESC LIMIT 5", (city,)
    ).fetchall()
    return jsonify({
        "total": total,
        "by_type": [dict(r) for r in by_type],
        "by_time": [dict(r) for r in by_time],
        "hot_areas": [dict(r) for r in hot_areas],
    })


# ── ADMIN ROUTES ──────────────────────────────────────────

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin"):
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated


@app.route("/sr-control-panel")
def admin_page():
    return render_template("admin.html")


@app.route("/api/admin/login", methods=["POST"])
def admin_login():
    data = request.get_json()
    if data.get("username") == ADMIN_USER and data.get("password") == ADMIN_PASS:
        session["admin"] = True
        return jsonify({"success": True})
    return jsonify({"error": "Invalid credentials"}), 401


@app.route("/api/admin/logout", methods=["POST"])
def admin_logout():
    session.pop("admin", None)
    return jsonify({"success": True})


@app.route("/api/admin/incidents", methods=["GET"])
@admin_required
def admin_get_incidents():
    status = request.args.get("status", "all")
    search = request.args.get("search", "").strip()
    db = get_db()

    query = "SELECT * FROM incidents WHERE 1=1"
    params = []

    if status != "all":
        query += " AND status=?"
        params.append(status)

    city_filter = request.args.get("city", "").strip()
    if city_filter:
        query += " AND city=?"
        params.append(city_filter)

    if search:
        query += " AND (area_name LIKE ? OR reported_by LIKE ? OR description LIKE ?)"
        params += [f"%{search}%", f"%{search}%", f"%{search}%"]

    query += " ORDER BY created_at DESC"
    rows = db.execute(query, params).fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/api/admin/incidents/<int:incident_id>/approve", methods=["POST"])
@admin_required
def admin_approve(incident_id):
    db = get_db()
    db.execute("UPDATE incidents SET status='approved' WHERE id=?", (incident_id,))
    db.commit()
    return jsonify({"success": True})


@app.route("/api/admin/incidents/<int:incident_id>/reject", methods=["POST"])
@admin_required
def admin_reject(incident_id):
    db = get_db()
    db.execute("UPDATE incidents SET status='rejected' WHERE id=?", (incident_id,))
    db.commit()
    return jsonify({"success": True})
@app.route("/api/admin/incidents/<int:incident_id>/setvotes", methods=["POST"])
@admin_required
def admin_set_votes(incident_id):
    data = request.get_json()
    upvotes = max(0, int(data.get("upvotes", 0)))
    db = get_db()
    db.execute("UPDATE incidents SET upvotes=? WHERE id=?", (upvotes, incident_id))
    db.commit()
    return jsonify({"success": True, "upvotes": upvotes})


@app.route("/api/admin/incidents/<int:incident_id>", methods=["DELETE"])
@admin_required
def admin_delete(incident_id):
    db = get_db()
    db.execute("DELETE FROM incidents WHERE id=?", (incident_id,))
    db.commit()
    return jsonify({"success": True})


@app.route("/api/admin/check", methods=["GET"])
def admin_check():
    return jsonify({"admin": bool(session.get("admin"))})


# ── KEEP ALIVE ────────────────────────────────────────────

def keep_alive():
    time.sleep(30)
    while True:
        try:
            requests.get('https://saferouteai-p2dw.onrender.com')
        except:
            pass
        time.sleep(840)

threading.Thread(target=keep_alive, daemon=True).start()

# ── START ─────────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    from seed_data import seed
    seed()
    from user_reports import add_user_reports
    add_user_reports()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
