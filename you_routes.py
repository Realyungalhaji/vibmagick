
import os, json
from flask import request, session, jsonify, redirect

PROFILE_FILE="data/profile.json"
def load_profile():
    if os.path.exists(PROFILE_FILE):
        try: return json.load(open(PROFILE_FILE))
        except: pass
    return {"name":"YuNg Alhaji","username":"@YuNg Alhaji","bio":"CEO & Admin - Artist","avatar":"https://i.imgur.com/8Km9tLL.jpg","following":1,"followers":0,"likes":0,"videos":[]}

def save_profile(p):
    json.dump(p, open(PROFILE_FILE,"w"))

def register_you(app, BASE=None):
    @app.route("/you")
    @app.route("/profile")
    def you_new():
        p = load_profile()
        # videos grid
        vids = ""
        for v in p.get("videos",[]):
            vids += f'<div class="vid"><img src="{v}"><span>▶ 0</span></div>'
        if not vids:
            vids = '<div style="grid-column:1/-1;text-align:center;color:#777;padding:30px">No videos yet<br><small>Tap + to upload your first video</small></div>'
        return f"""<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>
        *{{margin:0;padding:0;box-sizing:border-box;font-family:Arial}} body{{background:#000;color:#fff;padding-bottom:70px}}
        .top{{padding:15px 15px 5px}} .row{{display:flex;justify-content:space-between;align-items:flex-start}}
        h2{{font-size:22px}} .blue{{color:#20d5ec}} small{{color:#aaa;font-size:13px}}
        .avatar{{width:85px;height:85px;border-radius:50%;object-fit:cover;border:2px solid #333}}
        .stats{{display:flex;gap:20px;margin:14px 0 6px}} .stats b{{display:block;font-size:17px}} .stats span{{color:#aaa;font-size:12px}}
        .bio{{font-size:14px;margin:4px 0 12px;color:#ddd}}
        .edit{{background:#fff;color:#000;text-align:center;padding:11px;border-radius:6px;font-weight:bold;cursor:pointer}}
        .logout{{text-align:center;color:#ff4d4d;font-size:13px;margin-top:10px;cursor:pointer}}
        .tabs{{display:flex;justify-content:space-around;border-top:1px solid #222;border-bottom:1px solid #222;padding:12px 0;color:#aaa;margin-top:12px}}
        .tabs b{{color:#fff}} .grid{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:2px}}
        .vid{{position:relative;aspect-ratio:9/13;background:#222;overflow:hidden}} .vid img{{width:100%;height:100%;object-fit:cover}} .vid span{{position:absolute;left:6px;bottom:6px;font-size:12px}}
        .nav{{position:fixed;bottom:0;left:0;right:0;background:#000;border-top:1px solid #222;display:flex;justify-content:space-around;padding:10px 0;font-size:11px;text-align:center}}
        .nav a{{color:#aaa;text-decoration:none}} .nav a.active{{color:#fff}} .plus{{background:#fff;color:#000;padding:2px 12px;border-radius:6px;font-size:18px;font-weight:bold}}
        #modal{{display:none;position:fixed;inset:0;background:rgba(0,0,0,.8);align-items:center;justify-content:center}} .box{{background:#111;padding:20px;border-radius:12px;width:90%}} input,textarea{{width:100%;padding:10px;margin:8px 0;background:#222;border:none;color:#fff;border-radius:6px}} button{{width:100%;padding:12px;background:#fe2c55;border:none;color:#fff;border-radius:6px;font-weight:bold;margin-top:8px}}
        </style></head><body>
        <div class="top"><div class="row"><div><h2>{p['name']} <span class="blue">✔</span></h2><small>{p['username']} • {p['bio']}</small>
        <div class="stats"><div><b id="f1">{p['following']}</b><span>Following</span></div><div><b id="f2">{p['followers']}</b><span>Followers</span></div><div><b>{p['likes']}</b><span>Likes</span></div></div></div>
        <img class="avatar" src="{p['avatar']}" onclick="document.getElementById('fileAvatar').click()"><input type="file" id="fileAvatar" hidden accept="image/*" onchange="uploadAvatar(this)"></div>
        <p class="bio" id="bioText">{p['bio']}</p>
        <div class="edit" onclick="openEdit()">Edit Profile</div><div class="logout" onclick="location.href='/logout'">Logout</div>
        <div class="tabs"><b>▦ Videos</b><span>♡ Liked</span><span>🔖 Saved</span></div></div>
        <div class="grid">{vids}</div>
        <div class="nav"><a href="/">🏠<br>Home</a><a href="/friends">👥<br>Friends</a><a href="/upload"><span class="plus">+</span></a><a href="/inbox">💬<br>Inbox</a><a class="active" href="/you">👤<br>You</a></div>
        <div id="modal"><div class="box"><h3>Edit Profile</h3><input id="eName" value="{p['name']}" placeholder="Name"><input id="eUser" value="{p['username']}" placeholder="Username"><textarea id="eBio">{p['bio']}</textarea><input id="eAvatar" value="{p['avatar']}" placeholder="Avatar image URL"><button onclick="saveEdit()">Save Changes</button><button style="background:#333" onclick="closeEdit()">Cancel</button></div></div>
        <script>
        function openEdit(){{document.getElementById('modal').style.display='flex'}}
        function closeEdit(){{document.getElementById('modal').style.display='none'}}
        async function saveEdit(){{let d={{name:document.getElementById('eName').value,username:document.getElementById('eUser').value,bio:document.getElementById('eBio').value,avatar:document.getElementById('eAvatar').value}};let r=await fetch('/api/profile/update',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify(d)}});if(r.ok) location.reload(); else alert('Failed to save')}}
        async function uploadAvatar(el){{let f=el.files[0];let fd=new FormData();fd.append('file',f);let r=await fetch('/api/avatar',{{method:'POST',body:fd}});if(r.ok) location.reload(); else alert('Use image URL in Edit Profile for now')}}
        </script></body></html>"""
    @app.route("/api/videos")
    def list_videos():
        p = load_profile()
        return jsonify(p.get("videos",[]))
    @app.route("/api/videos/add", methods=["POST"])
    def add_video():
        p = load_profile()
        d = request.get_json(force=True, silent=True) or {}
        if d.get("url"):
            p.setdefault("videos",[]).append(d["url"])
            save_profile(p)
        return jsonify({"ok":True, "videos":p.get("videos",[])})
    @app.route("/api/profile/update", methods=["POST"])
    def update_profile():
        p = load_profile(); d = request.get_json(force=True, silent=True) or {}
        for k in ["name","username","bio","avatar"]:
            if d.get(k): p[k]=d[k]
        import datetime
        old = load_profile()
        save_profile(p)
        hist = json.load(open("data/history.json"))
        for k in ["name","username","bio","avatar"]:
            if old.get(k) != p.get(k):
                hist.append({"time":str(datetime.datetime.now()),"type":k,"old":old.get(k),"new":p.get(k)})
        json.dump(hist, open("data/history.json","w"), indent=2)
        return jsonify({"ok":True,"profile":p})
    @app.route("/api/avatar", methods=["POST"])
    def save_avatar():
        import datetime
        f = request.files.get("file")
        if not f:
            return jsonify({"ok":False}), 400
        path = "static/uploads/avatar.jpg"
        f.save(path)
        p = load_profile()
        old = dict(p)
        p["avatar"] = "/" + path + "?t=" + str(int(datetime.datetime.now().timestamp()))
        save_profile(p)
        hist = json.load(open("data/history.json"))
        hist.append({"time":str(datetime.datetime.now()),"type":"avatar","old":old.get("avatar"),"new":p["avatar"]})
        json.dump(hist, open("data/history.json","w"), indent=2)
        return jsonify({"ok":True,"avatar":p["avatar"]})
    @app.route("/api/avatar_OLD", methods=["POST"])
    def upload_avatar():
        # if your app already has upload handling, this will fallback to URL method
        return jsonify({"ok":False}), 400
