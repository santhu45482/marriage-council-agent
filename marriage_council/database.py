import sqlite3
import random
import os
from datetime import datetime
from .config import conf

def setup_database():
    """Idempotent Database Initialization."""
    db_exists = os.path.exists(conf.db_name)
    conn = sqlite3.connect(conf.db_name)
    cursor = conn.cursor()
    
    # Schema
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS profiles (
        id TEXT PRIMARY KEY, name TEXT, gender TEXT, age INTEGER,
        location TEXT, job TEXT, salary TEXT, family_type TEXT,
        horoscope_sign TEXT, risk_factor TEXT
    );""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS agent_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT,
        agent_name TEXT, action TEXT, details TEXT
    );""")
    
    # Seed Data
    cursor.execute("SELECT count(*) FROM profiles")
    if cursor.fetchone()[0] == 0:
        print("⚡ Seeding Database...")
        locations = ["Bangalore", "Mumbai", "Delhi", "Chennai"]
        jobs = ["Engineer", "Doctor", "Banker", "Artist"]
        risks = ["Clean"] * 8 + ["High Debt", "Fake Job"]
        signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio"]
        
        data = []
        for i in range(1, 11):
            data.append((f"G-{i}", f"Groom_{i}", "Male", 29, random.choice(locations), random.choice(jobs), "30 LPA", "Joint", random.choice(signs), random.choice(risks)))
            data.append((f"B-{i}", f"Bride_{i}", "Female", 27, random.choice(locations), random.choice(jobs), "25 LPA", "Nuclear", random.choice(signs), random.choice(risks)))
        cursor.executemany("INSERT INTO profiles VALUES (?,?,?,?,?,?,?,?,?,?)", data)
        conn.commit()
    conn.close()

def log_event(agent, action, details):
    try:
        conn = sqlite3.connect(conf.db_name)
        conn.execute("INSERT INTO agent_logs (timestamp, agent_name, action, details) VALUES (?,?,?,?)",
                     (datetime.now().isoformat(), agent, action, details))
        conn.commit()
        conn.close()
    except: pass

setup_database()
