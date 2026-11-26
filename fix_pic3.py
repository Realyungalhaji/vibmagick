import shutil, re
shutil.copy2("app.py", "app.py.bak13")
lines = open("app.py").readlines()
# find editusername start and end (next @app.route / def after it)
start = next(i for i,l in enumerate(lines) if "def editusername" in l)
end = start+1
while end < len(lines):
    if lines[end].startswith("@app.route") or lines[end].startswith("def "):
        break
    end+=1
print(f"Function lines {start+1} to {end}")
func = "".join(lines[start:end])
print("Has <form:", "<form" in func)
print("Has Save/Update:", [w for w in ["Save","Update","Submit","Change"] if w in func])
# 1. Add enctype to form inside this function only
for i in range(start,end):
    if "<form" in lines[i] and "enctype" not in lines[i]:
        lines[i]=lines[i].replace("<form", '<form enctype="multipart/form-data"',1)
        print("Added enctype line", i+1)
        break
# 2. Add file input before </form> inside function
for i in range(start,end):
    if "</form>" in lines[i] or 'type="submit"' in lines[i] or "type='submit'" in lines[i]:
        picker = '    <label style="color:#fff">Profile Picture</label><input type="file" name="profile_pic" accept="image/*" style="color:#fff;width:100%;margin:8px 0"><br>\n'
        lines.insert(i, picker)
        print("Added picker line", i+1)
        end+=1
        break
# 3. Backend: insert upload handler right after def line, using indent of next line
nxt = lines[start+1]
ind = re.match(r'(\s*)', nxt).group(1) or '    '
handler = [
 f"{ind}# PIC UPLOAD\n",
 f"{ind}try:\n",
 f"{ind}    _f=request.files.get('profile_pic')\n",
 f"{ind}    print('PIC DEBUG got file:', _f.filename if _f else None)\n",
 f"{ind}    if _f and getattr(_f,'filename',''):\n",
 f"{ind}        import os as _os, json as _json\n",
 f"{ind}        _os.makedirs('static/uploads',exist_ok=True)\n",
 f"{ind}        _f.save('static/uploads/avatar.jpg')\n",
 f"{ind}        _d=_json.load(open('profile.json')) if _os.path.exists('profile.json') else {{}}\n",
 f"{ind}        _d['avatar']='/static/uploads/avatar.jpg'\n",
 f"{ind}        _json.dump(_d,open('profile.json','w'),indent=2)\n",
 f"{ind}        print('PIC SAVED')\n",
 f"{ind}except Exception as _e:\n",
 f"{ind}    print('pic error',_e)\n",
]
lines[start+1:start+1]=handler
open("app.py","w").writelines(lines)
print("Done bak13")
