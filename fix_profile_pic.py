import shutil, re
shutil.copy2("app.py", "app.py.bak8")
t = open("app.py").read()

# Replace ONLY view_creator_profile function with picture version
new_func = '''
@app.route('/profile/<username>')
def view_creator_profile(username):
    import sqlite3
    username = username.strip().lstrip('@')
    try:
        db = sqlite3.connect("app.db", check_same_thread=False, isolation_level=None)
        db.row_factory = sqlite3.Row
        user = None
        uid = None
        try: user = db.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        except: pass
        if not user:
            try: user = db.execute("SELECT * FROM users WHERE username LIKE ?", ('%'+username+'%',)).fetchone()
            except: pass
        ud = dict(user) if user else {}
        uname = ud.get('username', username)
        bio = ud.get('bio','') or ''
        try: uid = ud.get('id')
        except: pass
        # --- PICTURE: try every common column name ---
        pic = ""
        for k in ['profile_pic','profile_image','avatar','pic','image','photo','profile_photo','picture']:
            if ud.get(k):
                pic = str(ud.get(k)); break
        if pic and not pic.startswith('http') and not pic.startswith('/'):
            pic = '/' + pic.lstrip('/')
        if pic and pic.startswith('/static') or pic.startswith('http'):
            avatar_html = f"<img src='{pic}' style='width:90px;height:90px;border-radius:50%;object-fit:cover;border:2px solid #1877F2'>"
        elif pic:
            avatar_html = f"<img src='{pic}' style='width:90px;height:90px;border-radius:50%;object-fit:cover;border:2px solid #1877F2'>"
        else:
            # No pic saved -> big initial circle
            initial = (uname[:1] or '?').upper()
            avatar_html = f"<div style='width:90px;height:90px;border-radius:50%;background:#1877F2;color:#fff;display:flex;align-items:center;justify-content:center;font-size:42px;font-weight:bold'>{initial}</div>"
        # --- POSTS: try username, then user_id ---
        posts = []
        for q, arg in [("SELECT * FROM posts WHERE username=? ORDER BY id DESC", uname), ("SELECT * FROM posts WHERE user=? ORDER BY id DESC", uname)]:
            try:
                posts = db.execute(q, (arg,)).fetchall()
                if posts: break
            except: pass
        if not posts and uid is not None:
            for col in ['user_id','author_id','creator_id','owner_id']:
                try:
                    posts = db.execute(f"SELECT * FROM posts WHERE {col}=? ORDER BY id DESC", (uid,)).fetchall()
                    if posts: break
                except: pass
        db.close()
    except Exception as e:
        uname=username; bio=''; avatar_html=f"<div style='width:90px;height:90px;border-radius:50%;background:#1877F2;color:#fff;display:flex;align-items:center;justify-content:center;font-size:42px;font-weight:bold'>{username[:1].upper()}</div>"; posts=[]
    plist = "".join([f"<div style='background:#111;padding:12px;border-radius:12px;margin:10px 0'>{dict(p).get('content','') or dict(p).get('caption','') or dict(p).get('text','') or 'Post'}</div>" for p in posts])
    return f"<html><head><meta name='viewport' content='width=device-width,initial-scale=1'><title>@{uname}</title></head><body style='background:#000;color:#fff;font-family:sans-serif;padding:20px;max-width:600px;margin:auto'><a href='/' style='color:#1877F2'>&larr; Back</a><div style='display:flex;gap:16px;align-items:center;margin-top:16px'>{avatar_html}<div><h2 style='margin:0'>@{uname}</h2><p style='color:#aaa;margin:4px 0'>{bio}</p><p style='margin:0'>{len(posts)} posts</p></div></div><hr style='border-color:#222'><h3>Posts by @{uname}</h3>{plist if plist else '<p>No posts yet</p>'}</body></html>"
'''

# Replace old function (from def view_creator_profile to next @app.route or if __name__)
pat = re.compile(r"@app\.route\('/profile/<username>'\)\ndef view_creator_profile.*?return f\".*?\"\)\n", re.DOTALL)
if pat.search(t):
    t = pat.sub(new_func.strip() + "\n", t, count=1)
    print("Profile picture added")
else:
    print("Old profile function not found - appending new one")
    if 'if __name__' in t:
        t = t.replace('if __name__', new_func + '\nif __name__', 1)
    else:
        t += new_func

open("app.py","w").write(t)
print("Done - backup app.py.bak8")
