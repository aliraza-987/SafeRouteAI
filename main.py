import os
import json
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify, render_template, g
from flask_cors import CORS
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

app = Flask(__name__)
CORS(app)

DB_PATH = "saferoute.db"
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

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
            upvotes     INTEGER DEFAULT 0
        )
    """)
    db.commit()
    db.close()

# ── ROUTES ────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/incidents", methods=["GET"])
def get_incidents():
    city = request.args.get("city")
    db = get_db()
    if city:
        rows = db.execute(
            "SELECT * FROM incidents WHERE city=? ORDER BY created_at DESC LIMIT 200",
            (city,)
        ).fetchall()
    else:
        rows = db.execute(
            "SELECT * FROM incidents ORDER BY created_at DESC LIMIT 500"
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
           (lat, lng, type, description, time_of_day, area_name, city, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            data["lat"], data["lng"], data["type"],
            data.get("description", ""),
            data["time_of_day"], data["area_name"],
            data["city"], datetime.utcnow().isoformat()
        )
    )
    db.commit()
    row = db.execute(
        "SELECT * FROM incidents WHERE id=?", (cur.lastrowid,)
    ).fetchone()
    return jsonify(dict(row)), 201


@app.route("/api/incidents/<int:incident_id>/upvote", methods=["POST"])
def upvote(incident_id):
    db = get_db()
    db.execute(
        "UPDATE incidents SET upvotes=upvotes+1 WHERE id=?", (incident_id,)
    )
    db.commit()
    row = db.execute(
        "SELECT * FROM incidents WHERE id=?", (incident_id,)
    ).fetchone()
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
           WHERE city = ?
           AND ABS(lat - ?) < 0.03
           AND ABS(lng - ?) < 0.03
           ORDER BY created_at DESC""",
        (city, lat, lng)
    ).fetchall()
    incidents = [dict(r) for r in rows]

    # No incidents nearby — return unknown
    if not incidents:
        return jsonify({
            "area_name":        area,
            "safety_level":     "unknown",
            "safety_score":     75,
            "summary":          "No incidents have been reported in this area yet. This could mean it is relatively safe, or that incidents simply haven't been reported here. Always stay alert.",
            "incident_count":   0,
            "most_common_type": "none",
            "safest_time":      "Morning",
            "tip":              "Share your live location with a trusted contact when travelling alone at night."
        })

    # Build incident summary for AI
    lines = "\n".join([
        f"- {i['type'].replace('_',' ')} at {i['area_name']} "
        f"during {i['time_of_day'].replace('_',' ')}: "
        f"{i['description'] or 'no details'}"
        for i in incidents[:15]
    ])

    # Find most common type and safest time
    type_counts = {}
    for i in incidents:
        type_counts[i["type"]] = type_counts.get(i["type"], 0) + 1
    most_common = max(type_counts, key=type_counts.get)

    time_counts = {}
    for i in incidents:
        time_counts[i["time_of_day"]] = time_counts.get(i["time_of_day"], 0) + 1
    all_times = ["morning", "afternoon", "evening", "night", "late_night"]
    safest_time = next(
        (t.title() for t in all_times if t not in time_counts), "Morning"
    )

    prompt = f"""You are a women's safety assistant for {city}, India.

Here are {len(incidents)} recent community-reported safety incidents near {area}:
{lines}

Give a JSON safety assessment with these exact keys:
- safety_score: integer 0-100 (100 = perfectly safe, 0 = extremely dangerous)
- safety_level: "safe" if score>=70, "caution" if 40-69, "danger" if below 40
- summary: 2 sentences max. Be direct and practical. Mention the main risk.
- tip: one specific safety tip based on the incidents. Under 20 words.

Respond ONLY with valid JSON. No extra text."""

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.3,
        )
        raw = response.choices[0].message.content.strip()
        # Strip markdown code fences if present
        raw = raw.replace("```json", "").replace("```", "").strip()
        ai = json.loads(raw)
    except Exception as e:
        print(f"Groq error: {e}")
        n = len(incidents)
        score = max(10, 85 - n * 7)
        level = "safe" if score >= 70 else "caution" if score >= 40 else "danger"
        ai = {
            "safety_score": score,
            "safety_level": level,
            "summary": f"{n} incidents reported nearby, mostly {most_common.replace('_',' ')}. Be especially careful at night.",
            "tip": "Avoid this area alone after dark. Use main roads and stay in lit areas."
        }

    return jsonify({
        "area_name":        area,
        "safety_level":     ai.get("safety_level", "caution"),
        "safety_score":     ai.get("safety_score", 50),
        "summary":          ai.get("summary", ""),
        "incident_count":   len(incidents),
        "most_common_type": most_common,
        "safest_time":      safest_time,
        "tip":              ai.get("tip", "Stay alert and trust your instincts.")
    })


@app.route("/api/stats", methods=["GET"])
def stats():
    city = request.args.get("city", "Mumbai")
    db = get_db()
    total = db.execute(
        "SELECT COUNT(*) FROM incidents WHERE city=?", (city,)
    ).fetchone()[0]
    by_type = db.execute(
        """SELECT type, COUNT(*) as count FROM incidents
           WHERE city=? GROUP BY type ORDER BY count DESC""",
        (city,)
    ).fetchall()
    by_time = db.execute(
        """SELECT time_of_day, COUNT(*) as count FROM incidents
           WHERE city=? GROUP BY time_of_day ORDER BY count DESC""",
        (city,)
    ).fetchall()
    hot_areas = db.execute(
        """SELECT area_name, COUNT(*) as count FROM incidents
           WHERE city=? GROUP BY area_name ORDER BY count DESC LIMIT 5""",
        (city,)
    ).fetchall()
    return jsonify({
        "total":     total,
        "by_type":   [dict(r) for r in by_type],
        "by_time":   [dict(r) for r in by_time],
        "hot_areas": [dict(r) for r in hot_areas],
    })

import threading
import requests
import time

def keep_alive():
    time.sleep(30)
    while True:
        try:
            requests.get('https://saferouteai-zbf0.onrender.com')
            print('keep-alive ping sent')
        except:
            pass
        time.sleep(840)

threading.Thread(target=keep_alive, daemon=True).start()


# ── START ─────────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    # Run seed data if DB is empty
    from seed_data import seed
    seed()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
