import shutil, re
shutil.copy2("app.py", "app.py.bak7")
t = open("app.py").read()

# 1. Fix click: handle @@username, use real /profile/ route
# Remove old broken handler if present
t = t.replace("let m=p?p.innerText.match(/@(\\w+)/):null", "let m=p?p.innerText.match(/@+(\\w+)/):null")
t = t.replace("let m=p?p.innerText.match(/@(\\w+)/):null", "let m=p?p.innerText.match(/@+(\\w+)/):null")
# If no vc-btn handler at all, add one before comment-btn handler
if "vc-btn" in t and "view-creator-real" not in t:
    old = "if e.target.classList.contains('comment-btn')"
    new = "if(e.target.classList.contains('vc-btn')){let p=e.target.closest('div');let m=p?p.innerText.match(/@+(\\w+)/):null;if(m){window.location.href='/profile/'+m[1];}return;} /*view-creator-real*/ if e.target.classList.contains('comment-btn')"
    if old in t:
        t = t.replace(old, new, 1)

# 2. Add real /profile/<username> route if it does not exist
if "/profile/<" not in t and 'profile/<username>' not in t:
    route = '''
@app.route('/profile/<username>')
def view_creator_profile(username):
    import sqlite3
    username = username.strip().lstrip('@')
    try:
        db = sqlite3.connect("app.db", check_same_thread=False, isolation_level=None)
        db.row_factory = sqlite3.Row
        user = None
        try:
            user = db.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        except: pass
        if not user:
            try: user = db.execute("SELECT * FROM users WHERE username LIKE ?", ('%'+username+'%',)).fetchone()
            except: pass
        posts = []
        try: posts = db.execute("SELECT * FROM posts WHERE username=? ORDER BY id DESC", (username,)).fetchall()
        except:
            try: posts = db.execute("SELECT * FROM posts WHERE user=? ORDER BY id DESC", (username,)).fetchall()
            except: pass
        db.close()
    except Exception as e:
        user=None; posts=[]
    uname = dict(user)['username'] if user else username
    bio = ""
    try: bio = dict(user).get('bio','') or ''
    except: pass
    plist = "".join([f"<div style='background:#111;padding:12px;border-radius:12px;margin:10px 0'>{dict(p).get('content','') or dict(p).get('caption','') or 'Post'}</div>" for p in posts])
    return f"<html><head><meta name='viewport' content='width=device-width,initial-scale=1'><title>@{uname}</title></head><body style='background:#000;color:#fff;font-family:sans-serif;padding:20px;max-width:600px;margin:auto'><a href='/' style='color:#1877F2'>&larr; Back</a><h2>@{uname}</h2><p style='color:#aaa'>{bio}</p><p>{len(posts)} posts</p><hr style='border-color:#222'><h3>Posts by @{uname}</h3>{plist if plist else '<p>No posts yet</p>'}</body></html>"
'''
    # Insert before if __name__ or app.run, else append
    if 'if __name__' in t:
        t = t.replace('if __name__', route + '\nif __name__', 1)
    else:
        t += route
    print("Added real /profile/<username> route")
else:
    print("Profile route already exists - only click fixed")

open("app.py","w").write(t)
print("View Creator REAL fix done - backup app.py.bak7")
