import sqlite3
import json
import random
from .config import conf
from .database import log_event

def get_random_profile_id(gender: str) -> str:
    conn = sqlite3.connect(conf.db_name)
    cursor = conn.cursor()
    g_map = {"groom": "Male", "bride": "Female"}
    search = g_map.get(gender.lower(), gender)
    cursor.execute("SELECT id FROM profiles WHERE gender = ?", (search,))
    rows = cursor.fetchall()
    conn.close()
    return random.choice(rows)[0] if rows else "None"

def get_profile_details(profile_id: str) -> str:
    conn = sqlite3.connect(conf.db_name)
    row = conn.execute("SELECT * FROM profiles WHERE id = ?", (profile_id,)).fetchone()
    conn.close()
    if not row: return json.dumps({"error": "Not Found"})
    return json.dumps({
        "id": row[0], "name": row[1], "age": row[3], "location": row[4],
        "job": row[5], "horoscope": row[8]
    })

def perform_background_check(profile_id: str) -> str:
    conn = sqlite3.connect(conf.db_name)
    row = conn.execute("SELECT name, risk_factor FROM profiles WHERE id = ?", (profile_id,)).fetchone()
    conn.close()
    if not row: return "Error"
    log_event("Detective", "Background Check", f"Checked {row[0]}: {row[1]}")
    return "RISK_FOUND" if row[1] in ["High Debt", "Fake Job"] else "CLEAN"

def check_horoscope_compatibility(sign1: str, sign2: str) -> str:
    score = random.randint(10, 36)
    return "BAD_MATCH" if score < 18 else "GOOD_MATCH"

def calculate_utility_score(groom_loc: str, bride_loc: str, proposal_loc: str, bride_career: str) -> str:
    score = 100
    if proposal_loc != groom_loc: score -= 30
    if proposal_loc != bride_loc: score -= 20
    if bride_career == "Quit Job": score -= 50 
    return json.dumps({"total_score": score, "viability": "High" if score > 60 else "Low"})
