# run_owner_final.py - Official Owner: YuNg Alhaji
import os, json, hashlib
import app as app_module
from app import app
from flask import session, redirect, request

OWNER = {
    "name": "YuNg Alhaji",
    "username": "realyungalhaji",
    "email": "realyungalhaji.mv@gmail.com",
    "role": "owner",
    "title": "Founder, Owner, Admin, Editor, Creator",
    "verified": True,
    "bio": "Founder & Owner of VibMagick 👑 | YuNg Alhaji",
    "badge": "👑 Founder"
}

SAVE_FILE = "all_data.json"

# Load existing data
data = {}
if os.path.exists(SAVE_FILE):
    try: data = json.load(open(SAVE_FILE))
    except: data = {}
    for k,v in data.items():
        if hasattr(app_module, k):
            setattr(app_module, k, v)

# Ensure owner exists in users dict (whatever format your app uses)
try:
    users = getattr(app_module, "users", {})
    if isinstance(users, dict):
        # Create / update owner user - keeps existing password if any
        existing = users.get(OWNER["username"], {})
        if isinstance(existing, dict):
            existing.update({"name": OWNER["name"], "email": OWNER["email"], "username": OWNER["username"], "role": "owner", "is_owner": True, "is_admin": True, "is_founder": True, "bio": OWNER["bio"], "verified": True})
            users[OWNER["username"]] = existing
        else:
            users[OWNER["username"]] = {"name": OWNER["name"], "email": OWNER["email"], "username": OWNER["username"], "role": "owner", "bio": OWNER["bio"], "verified": True}
        setattr(app_module, "users", users)
        print(f"OWNER ACCOUNT READY: {OWNER['username']} | {OWNER['email']}")
except Exception as e:
    print("Owner create:", e)

def is_owner():
    u = (session.get("username") or session.get("user") or "").lower()
    return u == "realyungalhaji" or session.get("role") == "owner"

@app.before_request
def _set_owner():
    if (session.get("username") or "").lower() == "realyungalhaji":
        session["role"] = "owner"
        session["is_owner"] = True
        session["is_admin"] = True
        session["is_founder"] = True
        session["name"] = "YuNg Alhaji"
        session["email"] = "realyungalhaji.mv@gmail.com"

@app.after_request
def _save_and_badge(response):
    try:
        out={}
        for k,v in vars(app_module).items():
            if isinstance(v,(dict,list,str,int)) and not k.startswith("_"):
                try: json.dumps(v); out[k]=v
                except: pass
        json.dump(out, open(SAVE_FILE,"w"))
    except: pass
    try:
        if response.content_type and "text/html" in response.content_type:
            html = response.get_data(as_text=True)
            if is_owner() and "OWNER_BADGE" not in html:
                badge = """<div id="OWNER_BADGE" style="position:fixed;top:10px;right:10px;z-index:9999;background:gold;color:black;padding:8px 12px;border-radius:20px;font-weight:bold">👑 YuNg Alhaji | Founder & Owner | <a href='/admin' style='color:black'>Admin</a></div>"""
                html = html.replace("</body>", badge+"</body>") if "</body>" in html else badge+html
                response.set_data(html)
    except: pass
    return response

@app.route("/admin")
def admin():
    if not is_owner():
        return "<h2>⛔ Admin Only - Owner: YuNg Alhaji (realyungalhaji)</h2><a href='/'>Back</a>"
    return f"""
    <h1>👑 YuNg Alhaji - Owner Panel</h1>
    <p><b>Name:</b> YuNg Alhaji<br><b>Username:</b> @realyungalhaji<br><b>Email:</b> realyungalhaji.mv@gmail.com<br><b>Roles:</b> Founder | Owner | Admin | Editor | Creator<br><b>Status:</b> ✅ Verified Owner</p>
    <hr><a href='/'>Home</a> | <a href='/api/whoami'>Who Am I</a>
    """

@app.route("/api/whoami")
def whoami():
    return {"name": "YuNg Alhaji" if is_owner() else session.get("username"), "username": session.get("username"), "email": "realyungalhaji.mv@gmail.com" if is_owner() else None, "role": "owner" if is_owner() else "user", "is_owner": is_owner(), "is_founder": is_owner(), "is_admin": is_owner(), "title": "Founder, Owner, Admin, Editor, Creator" if is_owner() else None}

if __name__ == "__main__":
    print("OWNER: YuNg Alhaji | @realyungalhaji | realyungalhaji.mv@gmail.com")
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)
