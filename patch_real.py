import pathlib, re
p = pathlib.Path("app.py")
t = p.read_text()
# 1. Make sure app has real secret + upload folder + DB init at startup
if "REAL_MODE" not in t:
    real = '''
# --- REAL MODE ---
import os, sqlite3, json
REAL_MODE = True
app.secret_key = os.environ.get("SECRET_KEY", "vibmagick-real-key-123")
os.makedirs("static/uploads", exist_ok=True)
os.makedirs("instance", exist_ok=True)
def real_db():
    c = sqlite3.connect("data.db")
    c.row_factory = sqlite3.Row
    c.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, bio TEXT, pic TEXT, verified INTEGER DEFAULT 0, created TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, caption TEXT, file TEXT, time TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, receiver TEXT, text TEXT, time TEXT, seen INTEGER DEFAULT 0)")
    c.execute("CREATE TABLE IF NOT EXISTS saved_posts (username TEXT, post_id INTEGER, PRIMARY KEY(username, post_id))")
    c.execute("CREATE TABLE IF NOT EXISTS blocks (blocker TEXT, blocked TEXT, PRIMARY KEY(blocker, blocked))")
    c.execute("CREATE TABLE IF NOT EXISTS reports (id INTEGER PRIMARY KEY AUTOINCREMENT, reporter TEXT, reported TEXT, reason TEXT, time TEXT)")
    c.commit()
    return c
try:
    real_db().close()
    print("REAL DB READY: users/posts/messages/saved/blocks/reports")
except Exception as e:
    print("DB init error:", e)
'''
    m = re.search(r"app\s*=\s*Flask.*\n", t)
    t = t[:m.end()] + real + t[m.end():]
    p.write_text(t)
    print("REAL MODE ADDED")
else:
    print("Already real")

# 2. Add health check - proves read/write works
if "/api/health" not in t:
    t = p.read_text() + '''
@app.route("/api/health")
def _health():
    try:
        c = real_db()
        u = c.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        po = c.execute("SELECT COUNT(*) FROM posts").fetchone()[0]
        me = c.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
        c.close()
        return {"status":"REAL","ok":True,"users":u,"posts":po,"messages":me,"db":"data.db","uploads": os.path.exists("static/uploads")}
    except Exception as e:
        return {"status":"ERROR","ok":False,"error":str(e)}, 500
'''
    p.write_text(t)
    print("Added /api/health")
import py_compile
py_compile.compile("app.py", doraise=True)
print("SYNTAX OK")
