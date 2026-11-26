# run_persistent.py - SAVES EVERYTHING forever
import os, json, sqlite3, shutil, datetime
import app as app_module
from app import app

os.makedirs("uploads", exist_ok=True)
os.makedirs("backups", exist_ok=True)
SAVE_FILE = "all_data.json"
DB_FILE = "all_data.db"

# --- 1. CREATE REAL DATABASE FOR ALL DATA ---
def db():
    c = sqlite3.connect(DB_FILE)
    c.row_factory = sqlite3.Row
    c.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, data TEXT, updated TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS posts (id TEXT PRIMARY KEY, data TEXT, updated TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, receiver TEXT, text TEXT, time TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS comments (id INTEGER PRIMARY KEY AUTOINCREMENT, post_id TEXT, username TEXT, text TEXT, time TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS followers (follower TEXT, following TEXT, UNIQUE(follower,following))")
    c.execute("CREATE TABLE IF NOT EXISTS saved_posts (username TEXT, post_id TEXT, UNIQUE(username,post_id))")
    c.execute("CREATE TABLE IF NOT EXISTS likes (username TEXT, post_id TEXT, UNIQUE(username,post_id))")
    c.execute("CREATE TABLE IF NOT EXISTS app_state (key TEXT PRIMARY KEY, value TEXT)")
    c.commit()
    try:
     c.execute("ALTER TABLE users ADD COLUMN pic TEXT")
     c.commit()
    except:
     pass
    return c

db().close()

# --- 2. LOAD ON STARTUP ---
if os.path.exists(SAVE_FILE):
    try:
        data = json.load(open(SAVE_FILE))
        for k,v in data.items():
            if hasattr(app_module, k):
                setattr(app_module, k, v)
                print(f"RESTORED {k}: {len(v) if hasattr(v,'__len__') else 'ok'}")
        print("✅ ALL DATA RESTORED")
    except Exception as e:
        print("Restore:", e)

# --- 3. SAVE AFTER EVERY ACTION ---
def save_all():
    try:
        out = {}
        for k, v in vars(app_module).items():
            if k.startswith("_"): continue
            if isinstance(v, (dict, list, str, int, float, bool)) and k not in ["app","__name__"]:
                try:
                    json.dumps(v)
                    out[k] = v
                except: pass
        # JSON backup (fast restore)
        json.dump(out, open(SAVE_FILE, "w"), indent=2)
        # SQLite backup (real database, survives JSON corruption)
        c = db()
        c.execute("INSERT OR REPLACE INTO app_state (key,value) VALUES (?,?)", ("all", json.dumps(out)))
        c.commit(); c.close()
        # Daily backup copy
        shutil.copy(SAVE_FILE, f"backups/all_data_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')}.json")
    except Exception as e:
        print("Save error:", e)

@app.after_request
def _save_and_mobile(response):
    save_all()
    # Mobile + Desktop fix
    try:
        if response.content_type and "text/html" in response.content_type:
            html = response.get_data(as_text=True)
            if 'name="viewport"' not in html:
                html = html.replace("<head>", '<head><meta name="viewport" content="width=device-width, initial-scale=1">', 1) if "<head>" in html else '<meta name="viewport" content="width=device-width, initial-scale=1">' + html
                response.set_data(html)
    except: pass
    return response

@app.route("/api/save-status")
def status():
    c = db()
    row = c.execute("SELECT COUNT(*) as n FROM app_state").fetchone()
    c.close()
    d = json.load(open(SAVE_FILE)) if os.path.exists(SAVE_FILE) else {}
    return {"saved": True, "file": SAVE_FILE, "db": DB_FILE, "keys": list(d.keys()), "counts": {k: len(v) if hasattr(v,'__len__') else v for k,v in d.items()}, "backups": len(os.listdir("backups"))}
db().close()
if __name__ == "__main__":
    print("PERSISTENT MODE: All data saves on every click | 0.0.0.0:5000")
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)), debug=True, threaded=True)
