import glob, pathlib
# 1. Change text in ALL files where it lives
for f in glob.glob("*.py"):
    t = pathlib.Path(f).read_text(errors="ignore")
    if "View Creator" in t:
        t = t.replace("View Creator", "View Creator")
        pathlib.Path(f).write_text(t)
        print(f"CHANGED TEXT IN {f}")
# 2. Make click go to creator - add to run.py
p = pathlib.Path('run.py')
t = p.read_text()
js = """<script>
document.addEventListener('click', function(e){
  if(e.target.textContent && e.target.textContent.trim() === 'View Creator'){
    var card = e.target;
    for(var i=0;i<8;i++){ if(card.parentElement) card = card.parentElement; }
    var m = (card.innerText||'').match(/@([A-Za-z0-9_.]+)/);
    if(m) window.location.href = '/profile/' + m[1];
  }
});
</script>"""
if 'View Creator' not in t and 'view-creator-js' not in t:
    # add after_request if it exists, else append it
    if 'after_request' in t:
        t = t.replace("r.set_data(h)", "h = h.replace('</body>', '''" + js.replace("view-creator-js","view-creator-js") + "''' + '</body>')\n   r.set_data(h)", 1)
    else:
        t += "\n@app.after_request\ndef _creator(r):\n    try:\n        h = r.get_data(as_text=True)\n        h = h.replace('</body>', '''" + js + "''' + '</body>')\n        r.set_data(h)\n    except: pass\n    return r\n"
    p.write_text(t)
    print('ADDED CLICK')
else:
    print('CLICK ALREADY THERE')
print('DONE')
