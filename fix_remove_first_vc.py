import shutil
shutil.copy2("app.py", "app.py.bak5")
t = open("app.py").read()
if "remove-first-vc" not in t:
    old = "document.addEventListener('click'"
    new = "setTimeout(function(){var f=document.querySelector('.vc-btn');if(f)f.remove();},200);/*remove-first-vc*/ document.addEventListener('click'"
    if old in t:
        t = t.replace(old, new, 1)
        print("First View Creator will be removed")
    else:
        print("Handler not found - no change")
else:
    print("Already fixed")
open("app.py","w").write(t)
print("Backup app.py.bak5")
