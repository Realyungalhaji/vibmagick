import shutil
shutil.copy2("app.py", "app.py.bak4")
t = open("app.py").read()

# 1. Make it BLUE - add inline style to vc-btn only
t = t.replace("class='vc-btn'", "class='vc-btn' style='background:#1877F2;color:#fff;padding:6px 14px;border-radius:20px;font-weight:700;cursor:pointer;border:none;display:inline-block'")
t = t.replace('class="vc-btn"', 'class="vc-btn" style="background:#1877F2;color:#fff;padding:6px 14px;border-radius:20px;font-weight:700;cursor:pointer;border:none;display:inline-block"')

# 2. Make click work - go to real creator profile from @username in that post
if "vc-btn-click-fixed" not in t:
    old = "if e.target.classList.contains('comment-btn')"
    new = "if e.target.classList.contains('vc-btn'){let p=e.target.closest('div');let m=p?p.innerText.match(/@(\\w+)/):null;if(m){window.location.href='/profile/'+m[1];}else{window.location.href='/';}return;} /*vc-btn-click-fixed*/ if e.target.classList.contains('comment-btn')"
    if old in t:
        t = t.replace(old, new, 1)
    else:
        print("Click handler not found - only color changed")

open("app.py","w").write(t)
print("View Creator fixed! Backup app.py.bak4")
