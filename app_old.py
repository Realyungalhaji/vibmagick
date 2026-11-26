from flask import Flask, request, redirect, session
import sqlite3
app = Flask(__name__)
app.secret_key = "vibmagick123"
DB = "vibmagick.db"
def db():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, username TEXT UNIQUE, email TEXT, password TEXT)")
    return c
STYLE = "body{margin:0;background:#000;color:#fff;font-family:sans-serif} .wrap{max-width:420px;margin:0 auto;padding:28px 24px 0} .top{display:flex;justify-content:space-between;font-size:22px} .title{font-size:42px;font-weight:900;text-align:center;margin:70px 0 60px} .row{display:flex;align-items:center;gap:16px;padding:20px 0;border-bottom:1px solid #222;text-decoration:none;color:#fff} .ava{width:68px;height:68px;border-radius:50%;background:#ccc;display:flex;align-items:center;justify-content:center} .plus{width:68px;height:68px;border-radius:50%;background:#1a1a1a;display:flex;align-items:center;justify-content:center;font-size:36px} .name{font-size:22px;font-weight:700} .email{color:#888;font-size:17px} .arrow{margin-left:auto;color:#666;font-size:24px} .manage{text-align:center;font-weight:700;font-size:20px;margin-top:340px} .bottom{position:fixed;bottom:0;left:0;right:0;background:#0a0a0a;text-align:center;padding:20px;font-size:19px} .bottom a{color:#ff2d55;text-decoration:none;font-weight:700} input{width:100%;padding:14px;border-radius:12px;border:1px solid #333;background:#111;color:#fff;margin:8px 0;box-sizing:border-box} button{width:100%;padding:14px;border-radius:30px;border:none;background:#fff;color:#000;font-weight:800;margin-top:16px} a{color:#ff2d55}"
AVATAR = "<svg viewBox='0 0 24 24'><path d='M12 12c2.7 0 5-2.3 5-5s-2.3-5-5-5-5 2.3-5 5 2.3 5 5 5zm0 2c-3.3 0-10 1.7-10 5v3h20v-3c0-3.3-6.7-5-10-5z'/></svg>"
@app.route("/")
def home():
    c = db()
    users = c.execute("SELECT * FROM users ORDER BY id DESC").fetchall()
    c.close()
    rows = ""
    for u in users:
        email = u["email"] or ""
        masked = email[:1] + "***" + email[email.find("@"):] if "@" in email else email
        rows += f"<a class='row' href='/quick/{u['id']}'><div class='ava'>{AVATAR}</div><div><div class='name'>{u['username']}</div><div class='email'>{masked}</div></div><div class='arrow'>&gt;</div></a>"
    return f"<html><head><meta name='viewport' content='width=device-width,initial-scale=1'><style>{STYLE}</style></head><body><div class='wrap'><div class='top'><span>?</span><span>X</span></div><div class='title'>Welcome back</div>{rows}<a class='row' style='border:none' href='/register'><div class='plus'>+</div><div class='name'>Add another account</div></a><div class='manage'>Manage accounts</div></div><div class='bottom'>Don't have an account? <a href='/register'>Sign up</a></div></body></html>"
@app.route("/quick/<int:uid>")
def quick(uid):
    c = db()
    u = c.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    c.close()
    if u:
        session["user"] = u["username"]
        return redirect("/feed")
    return redirect("/")
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        c = db()
        try:
            c.execute("INSERT INTO users (name,username,email,password) VALUES (?,?,?,?)", (request.form.get("name",""), request.form.get("username",""), request.form.get("email",""), request.form.get("password","")))
            c.commit()
        except: pass
        c.close()
        session["user"] = request.form.get("username","")
        return redirect("/feed")
    return f"<html><head><meta name='viewport' content='width=device-width,initial-scale=1'><style>{STYLE}</style></head><body><div class='wrap'><div class='title' style='font-size:32px'>Create account</div><form method='post'><input name='name' placeholder='Full Name' required><input name='username' placeholder='Username' required><input name='email' placeholder='Email' type='email' required><input name='password' placeholder='Password' type='password' required><button>Sign up</button></form><p style='text-align:center'><a href='/'>Back</a></p></div></body></html>"
@app.route("/feed")
def feed():
    user = session.get("user","Guest")
    return f"<html><head><meta name='viewport' content='width=device-width,initial-scale=1'><style>{STYLE}</style></head><body><div class='wrap'><h1 style='text-align:center'>VibMagick</h1><p style='text-align:center'>Welcome @{user}</p><p style='text-align:center;color:#888'>Your feed is ready!</p><p style='text-align:center'><a href='/'>Switch account</a></p></div></body></html>"
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
