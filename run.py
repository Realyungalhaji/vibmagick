import pickle, os
import json, os, secrets, time
import app as m
from app import app
from flask import session, redirect, request, render_template_string
from datetime import timedelta
F="all_data.json"
KF="secret.key"
if os.path.exists(KF):
 app.secret_key=open(KF).read().strip()
else:
 k=secrets.token_hex(32); open(KF,"w").write(k); app.secret_key=k
app.config["PERMANENT_SESSION_LIFETIME"]=timedelta(days=30)
if not hasattr(m,"USERS"): m.USERS={}
if not hasattr(m,"POSTS"): m.POSTS=[]
if not hasattr(m,"MESSAGES"): m.MESSAGES=[]
if not hasattr(m,"COMMENTS"): m.COMMENTS=[]
if not hasattr(m,"STORIES"): m.STORIES=[]
if not hasattr(m,"NOTIFS"): m.NOTIFS=[]
if os.path.exists(F):
 try:
  d=json.load(open(F))
  for k,v in d.items():
   if hasattr(m,k): setattr(m,k,v)
 except: pass
def save_all():
 try:
  o={}
  for k,v in vars(m).items():
   if k.startswith("__"): continue
   try: json.dumps(v); o[k]=v
   except: pass
  json.dump(o, open(F,"w"))
 except: pass
def safe_add(path, endpoint, func, methods=["GET","POST"]):
 if endpoint in app.view_functions:
  app.view_functions[endpoint]=func; return
 if path not in [str(r) for r in app.url_map.iter_rules()]:
  app.add_url_rule(path, endpoint, func, methods=methods)
def real_logout():
 session.clear(); session.modified=True; return redirect("/")
safe_add("/logout","logout",real_logout,methods=["GET"])
def do_register():
 if request.method=="POST":
  u=request.form.get("username","").strip(); p=request.form.get("password","").strip()
  if u and p and u not in m.USERS:
   m.USERS[u]={"username":u,"password":p,"bio":request.form.get("bio",""),"pic":"","followers":[],"following":[]}
   session["username"]=u; session.permanent=True; save_all(); return redirect("/")
  return "Username taken! <a href='/register'>Try again</a>"
 return render_template_string('<h2 style="text-align:center">Create Account</h2><form method="POST" style="max-width:400px;margin:auto;display:flex;flex-direction:column;gap:10px"><input name="username" placeholder="Username" required style="padding:12px"><input name="password" type="password" placeholder="Password" required style="padding:12px"><input name="bio" placeholder="Bio" style="padding:12px"><button style="padding:12px;background:#1D9BF0;color:#fff;border:none">Create Account</button></form>')
safe_add("/register","register",do_register)
def do_edit():
 u=session.get("username")
 if not u: return redirect("/login")
 if request.method=="POST":
  if u in m.USERS:
   m.USERS[u]["bio"]=request.form.get("bio",""); m.USERS[u]["pic"]=request.form.get("pic",""); save_all()
  return redirect("/profile")
 cur=m.USERS.get(u,{})
 return render_template_string('<h2 style="text-align:center">Edit Profile</h2><form method="POST" style="max-width:400px;margin:auto;display:flex;flex-direction:column;gap:10px"><input name="bio" value="{{b}}" style="padding:12px"><input name="pic" value="{{p}}" placeholder="Profile Pic Link" style="padding:12px"><button style="padding:12px;background:#1D9BF0;color:#fff;border:none">Save</button></form>',b=cur.get("bio",""),p=cur.get("pic",""))
safe_add("/edit_profile","edit_profile",do_edit)
safe_add("/edit","edit",do_edit)
def do_post():
 u=session.get("username")
 if not u: return redirect("/login")
 if request.method=="POST":
  m.POSTS.append({"user":u,"text":request.form.get("text",""),"img":request.form.get("img",""),"likes":[],"id":len(m.POSTS)}); save_all(); return redirect("/")
 return render_template_string('<h2 style="text-align:center">Create Post</h2><form method="POST" style="max-width:400px;margin:auto;display:flex;flex-direction:column;gap:10px"><textarea name="text" placeholder="What is happening?" style="padding:12px"></textarea><input name="img" placeholder="Image Link" style="padding:12px"><button style="padding:12px;background:#000;color:#fff;border:none">Post</button></form>')
safe_add("/create_post","create_post",do_post)
safe_add("/post","post",do_post)
def do_chat():
 u=session.get("username")
 if not u: return redirect("/login")
 to=request.args.get("to","")
 if request.method=="POST":
  to=request.form.get("to",""); txt=request.form.get("text","")
  if to and txt: m.MESSAGES.append({"from":u,"to":to,"text":txt}); save_all()
  return redirect(f"/chat?to={to}")
 users=[x for x in m.USERS.keys() if x!=u]
 msgs=[x for x in m.MESSAGES if (x["from"]==u and x["to"]==to) or (x["from"]==to and x["to"]==u)] if to else []
 h='<h2 style="text-align:center">Chat</h2><div style="max-width:500px;margin:auto">'
 h+=''.join([f'<a href="/chat?to={x}" style="display:block;padding:10px;border-bottom:1px solid #eee">{x}</a>' for x in users])
 if to:
  h+=f'<h3>Chat with {to}</h3>'
  for x in msgs: h+=f'<p><b>{x["from"]}:</b> {x["text"]}</p>'
  h+=f'<form method="POST" style="display:flex;gap:5px"><input type="hidden" name="to" value="{to}"><input name="text" required style="flex:1;padding:10px"><button style="padding:10px">Send</button></form>'
 return h+'</div>'
safe_add("/chat","chat",do_chat)
def do_like():
 u=session.get("username")
 if not u: return redirect("/login")
 pid=int(request.args.get("id","0"))
 for p in m.POSTS:
  if p.get("id")==pid:
   if u not in p.get("likes",[]): p["likes"].append(u)
   else: p["likes"].remove(u)
   if p["user"]!=u: m.NOTIFS.append({"to":p["user"],"from":u,"text":f"{u} liked your post","time":time.time()})
   break
 save_all(); return redirect("/")
safe_add("/like","like",do_like,methods=["GET"])
def do_comment():
 u=session.get("username")
 if not u: return redirect("/login")
 pid=request.args.get("id","0")
 if request.method=="POST":
  m.COMMENTS.append({"post_id":int(pid),"user":u,"text":request.form.get("text","")}); save_all(); return redirect("/")
 cs=[c for c in m.COMMENTS if str(c.get("post_id"))==str(pid)]
 h='<div style="max-width:500px;margin:auto"><h2>Comments</h2>'
 for c in cs: h+=f'<p><b>{c["user"]}:</b> {c["text"]}</p>'
 h+=f'<form method="POST" style="display:flex;gap:5px"><input name="text" required style="flex:1;padding:12px"><button style="padding:12px">Comment</button></form></div>'
 return h
safe_add("/comment","comment",do_comment)
def do_follow():
 u=session.get("username")
 if not u: return redirect("/login")
 t=request.args.get("user","")
 if t in m.USERS and t!=u:
  if u not in m.USERS[t].get("followers",[]): m.USERS[t]["followers"].append(u); m.USERS[u]["following"].append(t); m.NOTIFS.append({"to":t,"from":u,"text":f"{u} started following you","time":time.time()})
  else: m.USERS[t]["followers"].remove(u); m.USERS[u]["following"].remove(t)
  save_all()
 return redirect("/")
safe_add("/follow","follow",do_follow,methods=["GET"])
def do_search():
 q=request.args.get("q","").lower()
 users=[x for x in m.USERS.keys() if q in x.lower()] if q else list(m.USERS.keys())
 posts=[p for p in m.POSTS if q in p.get("text","").lower()] if q else []
 h='<div style="max-width:500px;margin:auto"><h2>🔍 Search</h2><form style="display:flex;gap:5px"><input name="q" value="'+q+'" placeholder="Search users, posts..." style="flex:1;padding:12px"><button style="padding:12px">Search</button></form>'
 for u in users: h+=f'<p><a href="/follow?user={u}">{u}</a> - <a href="/follow?user={u}">Follow</a> | <a href="/chat?to={u}">Chat</a></p>'
 for p in posts: h+=f'<p><b>{p["user"]}:</b> {p["text"]} - <a href="/like?id={p.get("id",0)}">❤️ {len(p.get("likes",[]))}</a> <a href="/comment?id={p.get("id",0)}">💬 Comment</a></p>'
 return h+'</div>'
safe_add("/search","search",do_search,methods=["GET"])
def do_story():
 u=session.get("username")
 if not u: return redirect("/login")
 if request.method=="POST":
  m.STORIES.append({"user":u,"text":request.form.get("text",""),"img":request.form.get("img",""),"time":time.time()}); save_all(); return redirect("/stories")
 return render_template_string('<h2 style="text-align:center">Add Story</h2><form method="POST" style="max-width:400px;margin:auto;display:flex;flex-direction:column;gap:10px"><input name="text" placeholder="Story text" style="padding:12px"><input name="img" placeholder="Image Link" style="padding:12px"><button style="padding:12px;background:purple;color:#fff;border:none">Add Story</button></form>')
safe_add("/add_story","add_story",do_story)
def do_stories():
 h='<div style="max-width:500px;margin:auto"><h2>📸 Stories</h2><a href="/add_story">+ Add Your Story</a><br><br>'
 for s in reversed(m.STORIES[-20:]): h+=f'<div style="border:1px solid #eee;padding:10px;border-radius:10px;margin-bottom:10px"><b>{s["user"]}</b><p>{s["text"]}</p></div>'
 return h+'</div>'
safe_add("/stories","stories",do_stories,methods=["GET"])
def do_notifs():
 u=session.get("username")
 if not u: return redirect("/login")
 ns=[n for n in reversed(m.NOTIFS) if n.get("to")==u]
 h='<div style="max-width:500px;margin:auto"><h2>🔔 Notifications</h2>'
 if not ns: h+='<p>No notifications yet</p>'
 for n in ns: h+=f'<p style="padding:10px;border-bottom:1px solid #eee">{n["text"]}</p>'
 return h+'</div>'
safe_add("/notifications","notifications",do_notifs,methods=["GET"])
def do_explore():
 h='<div style="max-width:500px;margin:auto"><h2>✨ Explore</h2>'
 for p in reversed(m.POSTS):
  h+=f'<div style="border:1px solid #eee;padding:12px;border-radius:10px;margin-bottom:10px"><b>{p["user"]}</b><p>{p["text"]}</p><a href="/like?id={p.get("id",0)}">❤️ {len(p.get("likes",[]))} Like</a> | <a href="/comment?id={p.get("id",0)}">💬 Comment</a> | <a href="/follow?user={p["user"]}">Follow {p["user"]}</a></div>'
 return h+'</div>'
safe_add("/explore","explore",do_explore,methods=["GET"])
@app.before_request
def o():
 session.permanent=True
@app.after_request
def s(r):
 save_all()
 try:
  if r.content_type and "text/html" in r.content_type:
   h=r.get_data(as_text=True)
   if 'href="/logout"' not in h:
    h=h.replace("Logout", '<a href="/logout" style="color:#ff3b30!important;text-decoration:none;display:block;text-align:center;width:100%">Logout</a>')
   # LOWER MENU - ONLY EXPLORE NOW
   h=h.replace("</body>", s+"</body>") if "</body>" in h else h
   h = h.replace('realyungalhaji', 'realyungalhaji <span style="display:inline-flex;align-items:center;justify-content:center;width:18px;height:18px;background:#1D9BF0;color:#fff;border-radius:50%;font-size:11px;font-weight:900;vertical-align:middle;margin-left:3px">M</span>')
   h = h.replace('</body>', '''''' + '</body>')
   h = h.replace('</body>', '''<script id="vc-real">
document.addEventListener('click', function(e){
  var el = e.target.closest ? e.target.closest('.vc-btn') : null;
  if(!el) return;
  e.preventDefault();
  var card = el;
  for(var i=0;i<8;i++){ if(card.parentElement) card = card.parentElement; }
  var links = card.querySelectorAll('a');
  for(var j=0;j<links.length;j++){
    var h = links[j].getAttribute('href')||'';
    if(h.indexOf('profile')>-1 || h.indexOf('user')>-1 || h.indexOf('@')>-1){ window.location.href = h; return; }
  }
  var m = (card.innerText||'').match(/@([A-Za-z0-9_.]+)/);
  if(m) window.location.href = '/profile/' + m[1];
});
</script>''' + '</body>')
   r.set_data(h)
 except: pass
 return r
app.run(host="0.0.0.0", port=5000, threaded=True)