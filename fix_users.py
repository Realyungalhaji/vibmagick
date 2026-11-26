import pathlib
p = pathlib.Path("app.py")
t = p.read_text()
if "users = {}" not in t:
    fix = '''
# --- FIX: load real data into the names your old code expects ---
try:
    _c = real_db()
    users = {r["username"]: dict(r) for r in _c.execute("SELECT * FROM users").fetchall()}
    posts = [dict(r) for r in _c.execute("SELECT * FROM posts ORDER BY id DESC").fetchall()]
    messages = [dict(r) for r in _c.execute("SELECT * FROM messages ORDER BY id").fetchall()]
    saved_posts = {}
    for r in _c.execute("SELECT * FROM saved_posts").fetchall():
        saved_posts.setdefault(r["username"], []).append(r["post_id"])
    _c.close()
    print(f"LOADED REAL: {len(users)} users, {len(posts)} posts, {len(messages)} messages")
except Exception as e:
    users = {}
    posts = []
    messages = []
    saved_posts = {}
    print("load fallback:", e)
'''
    # insert right after REAL_MODE block, before first route
    t = t.replace("# --- REAL MODE ---", "# --- REAL MODE ---", 1)
    # put it after real_db() definition - find "REAL DB READY"
    marker = 'print("REAL DB READY'
    idx = t.find(marker)
    # find end of that try block - insert after the except block of real_db init
    # simpler: insert just before first @app.route
    first_route = t.find("@app.route")
    t = t[:first_route] + fix + "\n" + t[first_route:]
    p.write_text(t)
    print("FIXED users/posts/messages")
else:
    print("Already fixed")
import py_compile
py_compile.compile("app.py", doraise=True)
print("SYNTAX OK")
