import shutil, re
shutil.copy2("app.py", "app.py.bak10")
t = open("app.py").read()
new_func = '''
@app.route('/profile/<username>')
def view_creator_profile(username):
    import sqlite3, glob, json, os
    username = username.strip().lstrip('@')
    try:
        db = sqlite3.connect("app.db", check_same_thread=False, isolation_level=None)
        db.row_factory = sqlite3.Row
        user = None
        try: user = db.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        except: pass
        if not user:
            try: user = db.execute("SELECT * FROM users WHERE username LIKE ?", ('%'+username+'%',)).fetchone()
            except: pass
        ud = dict(user) if user else {}
        uname = ud.get('username', username)
        bio = ud.get('bio','') or ''
        uid = ud.get('id')
        # --- PIC 1: profile.json (where YOUR pic really lives) ---
        pic = ""
        for f in sorted(glob.glob("profile.json") + glob.glob("data/profile.json") + glob.glob("BACKUP_ALL/*profile.json"), reverse=True):
            try:
                d = json.load(open(f))
                if isinstance(d, dict) and d.get('username','').lower().strip() == uname.lower().strip():
                    pic = d.get('avatar') or d.get('profile_pic') or d.get('image') or d.get('pic') or ""
                    if pic: break
                if isinstance(d, dict) and not pic and d.get('avatar'):
                    # single-user app: only one profile.json, use it
                    pic = d.get('avatar')
                    if uname.lower() in username.lower() or username.lower() in uname.lower(): break
            except: pass
        # --- PIC 2: any image column in DB ---
        if not pic:
            for k,v in ud.items():
                if v and isinstance(v,str) and any(x in v.lower() for x in ['.jpg','.jpeg','.png','.webp','.gif','/static/','/uploads/','imgur','http']):
                    pic = v; break
        # --- PIC 3: file named after user ---
        if not pic:
            for pat in [f"static/**/*{uname}*", f"uploads/**/*{uname}*"]:
                try:
                    m = glob.glob(pat, recursive=True)
                    if m: pic = m[0]; break
                except: pass
        if pic and not pic.startswith('http') and not pic.startswith('/'):
            pic = '/' + pic.lstrip('/')
        if pic:
            avatar_html = f"<img src='{pic}' style='width:90px;height:90px;border-radius:50%;object-fit:cover;border:2px solid #1877F2'>"
        else:
            initial = (uname[:1] or '?').upper()
            avatar_html = f"<div style='width:90px;height:90px;border-radius:50%;background:#1877F2;color:#fff;display:flex;align-items:center;justify-content:center;font-size:42px;font-weight:bold'>{initial}</div>"
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
pat = re.compile(r"@app\.route\('/profile/<username>'\)\ndef view_creator_profile.*?return f\".*?\"\)\n", re.DOTALL)
if pat.search(t):
    t = pat.sub(new_func.strip() + "\n", t, count=1)
    print("View Creator now reads profile.json avatar")
else:
    t = t.replace('if __name__', new_func + '\nif __name__', 1) if 'if __name__' in t else t + new_func
    print("Appended new profile function")
open("app.py","w").write(t)
print("Done - backup app.py.bak10")
