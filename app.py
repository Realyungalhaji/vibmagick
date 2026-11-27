from flask import Flask, request, redirect, session, send_from_directory
import sqlite3, os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "vibmagick123"
os.makedirs("static/uploads", exist_ok=True)

STYLE = "body{background:#000;color:#fff;font-family:sans-serif;margin:0;padding-bottom:80px} .wrap{max-width:480px;margin:0 auto;padding:15px} input,textarea{width:100%;padding:12px;margin:8px 0;border-radius:10px;border:1px solid #333;background:#111;color:#fff;box-sizing:border-box} button{padding:10px 18px;background:#fff;color:#000;border:none;border-radius:20px;font-weight:bold;cursor:pointer} a{color:#fff;text-decoration:none} .post{background:#111;border:1px solid #222;border-radius:12px;padding:12px;margin:12px 0} .nav{position:fixed;bottom:0;left:0;right:0;background:#000;border-top:1px solid #222;display:flex;justify-content:space-around;padding:10px 0;z-index:99} .nav a{text-align:center;font-size:12px} .nav span{font-size:22px;display:block} .card{background:#111;border-radius:12px;padding:12px;margin:10px 0;display:flex;align-items:center;gap:10px} .ava{width:44px;height:44px;border-radius:50%;background:#FE2C55;display:flex;align-items:center;justify-content:center;font-size:20px;font-weight:bold;flex-shrink:0}"

def NAV():
    return "<div class='nav'><a href='/feed'><span>🏠</span>Home</a><a href='/friends'><span>👥</span>Friends</a><a href='/upload'><span style='background:#fff;color:#000;border-radius:12px;padding:2px 14px;font-size:24px'>+</span></a><a href='/inbox'><span>💬</span>Inbox</a><a href='/profile'><span>👤</span>You</a></div>"

def page(title, body):
    return f"""<html><head><meta name='viewport' content='width=device-width,initial-scale=1'><meta name='theme-color' content='#000000'><title>{title} - VibMagick</title><style>{STYLE}</style></head><body><div class='wrap'>{body}</div>{NAV()}</body></html>"""

def db():
    c = sqlite3.connect("vib.db")
    c.execute("CREATE TABLE IF NOT EXISTS users(name TEXT, username TEXT PRIMARY KEY, email TEXT, password TEXT, bio TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS posts(id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, caption TEXT, file TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS follows(follower TEXT, following TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS msgs(id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, receiver TEXT, text TEXT)")
    c.commit()
    return c

def me():
    return session.get("user", "")

@app.route("/")
def home():
    c = db()
    users = c.execute("SELECT name, username FROM users").fetchall()
    c.close()
    h = ""
    for u in users:
        first = u[1][0].upper() if u[1] else "?"
        h += f"<div class='card'><div class='ava'>{first}</div><b>@{u[1]}</b><a href='/login/{u[1]}' style='margin-left:auto'><button>Log in</button></a></div>"
    body = f"<h1 style='text-align:center'>VibMagick</h1><h3 style='text-align:center'>Welcome back</h3>{h}<p style='text-align:center'><a href='/create'>+ Log into another account</a></p>"
    return page("Home", body)

@app.route("/login/<u>")
def login(u):
    session["user"] = u
    return redirect("/feed")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        c = db()
        try:
            c.execute("INSERT INTO users VALUES(?,?,?,?,?)", (request.form.get("name",""), username, request.form.get("email",""), request.form.get("password",""), "Hey! I'm on VibMagick"))
            c.commit()
        except:
            pass
        c.close()
        session["user"] = username
        return redirect("/feed")
    body = "<h2 style='text-align:center'>Create account</h2><form method='post'><input name='name' placeholder='Full Name' required><input name='username' placeholder='Username' required><input name='email' placeholder='Email' type='email' required><input name='password' placeholder='Password' type='password' required><button style='width:100%'>Sign up</button></form>"
    return page("Create account", body)

@app.route("/feed")
def feed():
    u = me()
    if not u:
        return redirect("/")
    c = db()
    posts = c.execute("SELECT username, caption, file FROM posts ORDER BY id DESC").fetchall()
    c.close()
    p = ""
    for x in posts:
        media = ""
        if x[2]:
            if x[2].lower().endswith(('.jpg','.png','.jpeg','.gif','.webp')):
                media = f"<img src='/static/uploads/{x[2]}' style='width:100%;border-radius:10px;margin-top:8px'>"
            elif x[2].lower().endswith(('.mp4','.mov','.webm')):
                media = f"<video src='/static/uploads/{x[2]}' controls style='width:100%;border-radius:10px'></video>"
        p += f"<div class='post'><b>@{x[0]}</b><p>{x[1]}</p>{media}<div><a href='/profile/{x[0]}'>View Creator</a> | <a href='/chat/{x[0]}'>Message</a></div></div>"
    if not p:
        p = "<p style='text-align:center;color:#888'>No posts yet. Tap + to post!</p>"
    body = f"<h1 style='text-align:center'>VibMagick</h1><p style='text-align:center'>Welcome @{u}</p>{p}"
    return page("Feed", body)

@app.route("/friends")
def friends():
    u = me()
    if not u:
        return redirect("/")
    q = request.args.get("q", "")
    c = db()
    users = c.execute("SELECT name, username, email, password, bio FROM users WHERE username LIKE ? AND username!=?", (f"%{q}%", u)).fetchall()
    out = ""
    for x in users:
        isf = c.execute("SELECT * FROM follows WHERE follower=? AND following=?", (u, x[1])).fetchone()
        isback = c.execute("SELECT * FROM follows WHERE follower=? AND following=?", (x[1], u)).fetchone()
        label = "Unfollow" if isf else ("Follow Back" if isback else "Follow")
        tag = " - Friends" if (isf and isback) else ""
        first = x[1][0].upper() if x[1] else "?"
        out += f"<div class='card'><div class='ava'>{first}</div><div><b>@{x[1]}</b><br><small>{x[4] or ''}{tag}</small></div><a href='/follow/{x[1]}' style='margin-left:auto'><button>{label}</button></a></div>"
    c.close()
    body = f"<h2>Friends</h2><form><input name='q' value='{q}' placeholder='Search users...'><button>Search</button></form><p>Follow back = Friends</p>{out or '<p>No users found</p>'}"
    return page("Friends", body)

@app.route("/follow/<t>")
def follow(t):
    u = me()
    c = db()
    if c.execute("SELECT * FROM follows WHERE follower=? AND following=?", (u, t)).
