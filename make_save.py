import pathlib
p = pathlib.Path("app.py")
t = p.read_text()
if "def save_all_real" not in t:
    code = '''
# --- SAVE BACK TO DB ---
def save_all_real():
    try:
        c = real_db()
        # users: dict username -> dict
        if "users" in globals():
            for uname, u in list(globals()["users"].items()):
                if isinstance(u, dict):
                    c.execute("INSERT OR REPLACE INTO users (username,password,bio,pic,verified,created) VALUES (?,?,?,?,?,?)",
                        (uname, u.get("password",""), u.get("bio",""), u.get("pic",""), int(bool(u.get("verified",0))), u.get("created","")))
        # posts: list of dicts
        if "posts" in globals():
            for po in list(globals()["posts"]):
                if isinstance(po, dict) and "id" in po:
                    c.execute("INSERT OR REPLACE INTO posts (id,username,caption,file,time) VALUES (?,?,?,?,?)",
                        (po.get("id"), po.get("username",""), po.get("caption",""), po.get("file",""), po.get("time","")))
        # messages: list of dicts
        if "messages" in globals():
            for m in list(globals()["messages"]):
                if isinstance(m, dict) and "id" in m:
                    c.execute("INSERT OR REPLACE INTO messages (id,sender,receiver,text,time,seen) VALUES (?,?,?,?,?,?)",
                        (m.get("id"), m.get("sender",""), m.get("receiver",""), m.get("text",""), m.get("time",""), int(bool(m.get("seen",0)))))
        c.commit(); c.close()
    except Exception as e:
        print("save_all_real skipped:", e)

@app.after_request
def _auto_save_all(response):
    try:
        save_all_real()
    except: pass
    return response
'''
    first = t.find("@app.route")
    t = t[:first] + code + "\n" + t[first:]
    p.write_text(t)
    print("SAVE ADDED")
else:
    print("Already has save")
import py_compile
py_compile.compile("app.py", doraise=True)
print("SYNTAX OK")
