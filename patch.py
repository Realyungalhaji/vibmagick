import pathlib, re
p = pathlib.Path("app.py")
t = p.read_text()
if "import saver" not in t:
    t = "try:\n import saver\nexcept: saver = None\n" + t
    print("added import")
m = re.search(r"app\s*=\s*Flask.*\n", t)
if m and "_safe_auto_save" not in t:
    hook = "\n@app.before_request\ndef _safe_auto_save():\n    try:\n        from flask import request\n        if saver: saver.save_all(request)\n    except: pass\n"
    t = t[:m.end()] + hook + t[m.end():]
    print("added hook")
if "/admin/data" not in t:
    t = t + "\n@app.route('/admin/data')\ndef _view_saved():\n    import sqlite3\n    c = sqlite3.connect('data.db')\n    rows = c.execute('SELECT * FROM saved_data ORDER BY id DESC LIMIT 200').fetchall()\n    c.close()\n    h = '<h1>Saved Data</h1><a href=\"/\">Home</a><hr>'\n    for r in rows:\n        h += '<div>' + str(r) + '</div><hr>'\n    return h\n"
    print("added view page")
p.write_text(t)
print("DONE")
