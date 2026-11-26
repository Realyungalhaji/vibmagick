import shutil, re
shutil.copy2("app.py", "app.py.bak12")
t = open("app.py").read()
orig = t
if 'name="profile_pic"' not in t:
    picker = '''<div style="margin:10px 0"><label style="display:block;color:#fff;margin-bottom:6px">Profile Picture</label><input type="file" name="profile_pic" accept="image/*" style="color:#fff;width:100%"><p style="color:#aaa;font-size:12px">Choose from phone - this will become your real profile picture</p></div>'''
    t = t.replace('Save Changes', picker + 'Save Changes', 1)
    idx = t.find('Save Changes')
    fidx = t.rfind('<form', 0, idx)
    if fidx!=-1 and 'enctype' not in t[fidx:idx]:
        t = t[:fidx] + t[fidx:].replace('<form', '<form enctype="multipart/form-data"', 1)
m = re.search(r'(def \w*edit\w*profile\w*\([^)]*\):\s*\n)', t)
if m and 'PROFILE PIC UPLOAD' not in t:
    after = t[m.end():m.end()+2000]
    indent_match = re.search(r'\n([ \t]+)\S', after)
    ind = indent_match.group(1) if indent_match else '    '
    lines = [
        f"{ind}# --- PROFILE PIC UPLOAD ---",
        f"{ind}try:",
        f"{ind}    _f = request.files.get('profile_pic') if 'request' in dir() else None",
        f"{ind}    if _f and getattr(_f, 'filename', ''):",
        f"{ind}        import os as _os, json as _json, glob as _glob",
        f"{ind}        _os.makedirs('static/uploads', exist_ok=True)",
        f"{ind}        _f.save('static/uploads/avatar.jpg')",
        f"{ind}        _new = '/static/uploads/avatar.jpg'",
        f"{ind}        for _pf in ['profile.json'] + sorted(_glob.glob('BACKUP_ALL/*profile.json'), reverse=True)[:1]:",
        f"{ind}            try:",
        f"{ind}                _d = _json.load(open(_pf)) if _os.path.exists(_pf) else {{}}",
        f"{ind}                _d['avatar'] = _new",
        f"{ind}                _json.dump(_d, open(_pf,'w'), indent=2)",
        f"{ind}            except: pass",
        f"{ind}except Exception as _e:",
        f"{ind}    print('pic upload error:', _e)",
    ]
    handler = "\n".join(lines) + "\n"
    t = t[:m.end()] + handler + t[m.end():]
open("app.py","w").write(t)
print("Fixed with correct indent" if t!=orig else "No change")
print("Done - backup app.py.bak12")
