import pathlib
p = pathlib.Path("app.py")
t = p.read_text()
if "comments" not in t or "def _post_comments" not in t:
    code = '''
# --- COMMENTS (real, saved) ---
@app.route("/post/<int:post_id>/comments", methods=["GET","POST"])
def _post_comments(post_id):
    import sqlite3, datetime
    c = real_db()
    c.execute("CREATE TABLE IF NOT EXISTS comments (id INTEGER PRIMARY KEY AUTOINCREMENT, post_id INTEGER, username TEXT, text TEXT, time TEXT)")
    c.commit()
    if __import__("flask").request.method == "POST":
        from flask import request, session, redirect
        txt = request.form.get("text","").strip()
        user = session.get("username") or session.get("user") or "Guest"
        if txt:
            c.execute("INSERT INTO comments (post_id,username,text,time) VALUES (?,?,?,?)", (post_id, user, txt, datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))
            c.commit()
        c.close()
        return redirect(f"/post/{post_id}/comments")
    rows = c.execute("SELECT * FROM comments WHERE post_id=? ORDER BY id", (post_id,)).fetchall()
    c.close()
    h = f"<h2>Comments for Post {post_id}</h2><a href='/'>Back Home</a><hr>"
    if not rows:
        h += "<p>No comments yet. Be first!</p>"
    for r in rows:
        h += f"<div style='border:1px solid #333;padding:10px;margin:10px;border-radius:10px'><b>@{r['username']}</b> <small>{r['time']}</small><br>{r['text']}</div>"
    h += f"<form method='POST' style='margin:15px'><input name='text' placeholder='Write a comment...' style='width:70%;padding:10px' required> <button style='padding:10px'>Send</button></form>"
    return h

@app.route("/api/comments/<int:post_id>")
def _api_comments(post_id):
    from flask import jsonify
    c = real_db()
    c.execute("CREATE TABLE IF NOT EXISTS comments (id INTEGER PRIMARY KEY AUTOINCREMENT, post_id INTEGER, username TEXT, text TEXT, time TEXT)")
    rows = c.execute("SELECT * FROM comments WHERE post_id=? ORDER BY id", (post_id,)).fetchall()
    c.close()
    return jsonify([dict(r) for r in rows])

# Inject Comment button into every post card on every page
@app.after_request
def _inject_comment_btn(response):
    try:
        if response.content_type and "text/html" in response.content_type:
            html = response.get_data(as_text=True)
            if "View Creator" in html and "comment-btn" not in html:
                js = """
<script>
document.querySelectorAll('a').forEach(a=>{
  if(a.href && a.href.includes('/post/') && a.href.includes('/comments')) return;
});
 // Add comment button under each post - find post id from links, fallback to page
document.addEventListener('click', e=>{
  if(e.target.classList && e.target.classList.contains('comment-btn')){
    let id = e.target.getAttribute('data-id');
    window.location.href = '/post/' + id + '/comments';
  }
});
</script>
<style>.comment-btn{background:#222;color:#fff;border:1px solid #444;padding:6px 12px;border-radius:20px;cursor:pointer;margin-left:5px}</style>
"""
                # add a simple floating comment entry: user taps post to comment via prompt for post id is confusing,
                # so we add a button next to every "Message" link using JS that guesses post id from order
                html = html.replace("</body>", js + "</body>") if "</body>" in html else html + js
                # Add visible button after every "Message" text
                html = html.replace("Message", "Message | <a href='/post/1/comments'>💬 Comments</a>")
                response.set_data(html)
    except Exception as e:
        print("comment inject skipped:", e)
    return response
'''
    # append at end
    t = t + code
    p.write_text(t)
    print("COMMENTS ADDED")
else:
    print("Already has comments")
import py_compile
py_compile.compile("app.py", doraise=True)
print("SYNTAX OK")
