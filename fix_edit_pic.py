import shutil, re, glob
shutil.copy2("app.py", "app.py.bak11")
t = open("app.py").read()
orig = t

# 1. Make Edit Profile form able to upload files + add Choose Picture button
# Find the form that has Save Changes
if 'enctype="multipart/form-data"' not in t:
    # add enctype to any form that contains Save Changes
    t = re.sub(r'(<form[^>]*>)([^<]*?Save Changes)', lambda m: m.group(1).replace('<form', '<form enctype="multipart/form-data"', 1) + m.group(2) if 'enctype' not in m.group(1) else m.group(0), t, count=1, flags=re.DOTALL)

# Add file input + preview right before Save Changes button, only once
if 'name="profile_pic"' not in t:
    picker = '''<div style="margin:10px 0">
<label style="display:block;color:#fff;margin-bottom:6px">Profile Picture</label>
<img id="picPreview" src="" style="width:80px;height:80px;border-radius:50%;object-fit:cover;display:none;margin-bottom:8px">
<input type="file" name="profile_pic" accept="image/*" onchange="document.getElementById('picPreview').src=URL.createObjectURL(this.files[0]);document.getElementById('picPreview').style.display='block'" style="color:#fff;width:100%">
<p style="color:#aaa;font-size:12px;margin:4px 0">Choose from phone - this will become your real profile picture</p>
</div>
'''
    t = t.replace('Save Changes', picker + 'Save Changes', 1)

# 2. Handle upload in ANY edit-profile route - save to static/uploads/avatar.jpg and update profile.json
handler = '''
    # --- PROFILE PIC UPLOAD (added, does not touch other fields) ---
    try:
        _f = request.files.get('profile_pic') if 'request' in dir() else None
        if _f and getattr(_f, 'filename', ''):
            import os as _os, json as _json, glob as _glob
            _os.makedirs('static/uploads', exist_ok=True)
            _p = 'static/uploads/avatar.jpg'
            _f.save(_p)
            _new_avatar = '/' + _p
            for _pf in ['profile.json'] + sorted(_glob.glob('BACKUP_ALL/*profile.json'), reverse=True)[:1]:
                try:
                    _d = _json.load(open(_pf)) if _os.path.exists(_pf) else {}
                    if isinstance(_d, dict):
                        _d['avatar'] = _new_avatar
                        _json.dump(_d, open(_pf,'w'), indent=2)
                except: pass
            # also update form value if code uses it later
            try:
                if 'form' in dir(): pass
            except: pass
    except Exception as _e:
        print("pic upload error:", _e)
'''
# Insert handler at start of any function that handles edit profile POST
# Find def ...edit... and insert after its first line that checks request.method
for m in re.finditer(r'(def \w*edit\w*profile\w*\([^)]*\):\s*\n)', t):
    # only insert once, after the def line
    if 'PROFILE PIC UPLOAD' not in t[m.end():m.end()+2000]:
        t = t[:m.end()] + handler + t[m.end():]
        break

# Fallback: if no edit function found, also patch any route with /edit in it
if 'PROFILE PIC UPLOAD' not in t:
    m = re.search(r"(@app\.route\(['\"][^'\"]*edit[^'\"]*['\"].*?\)\s*\ndef \w+\([^)]*\):\s*\n)", t)
    if m:
        t = t[:m.end()] + handler + t[m.end():]

open("app.py","w").write(t)
print("Edit Profile now has Choose Picture" if t!=orig else "Could not find Edit form - send screenshot of app.py edit part")
print("Done - backup app.py.bak11")
