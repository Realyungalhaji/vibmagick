import shutil
shutil.copy2("app.py", "app.py.bak2")
text = open("app.py").read()
old = "<button onclick=history.back()>Back to Previous Page</button><br>"
text = text.replace(old, "", 1)
text = text.replace("Back to Previous Page", "", 1)
new = "<style>.backbtn{font-weight:900;font-size:18px;padding:10px 22px;border:none;border-radius:12px;color:white;background:linear-gradient(180deg,#4da6ff,#0057d9);box-shadow:0 4px 0 #003a8c,0 8px 15px rgba(0,0,0,.3);text-shadow:0 2px 0 rgba(0,0,0,.3);cursor:pointer}</style><br><button class=backbtn onclick=history.back()>Back</button>"
if "class=backbtn" in text:
    print("Already new style")
else:
    if "Send</button>" in text:
        text = text.replace("Send</button>", "Send</button><br>" + new, 1)
        print("Moved under Send")
    elif "Send" in text:
        text = text.replace("Send", "Send<br>" + new, 1)
        print("Moved under Send 2")
    else:
        print("Send not found")
    open("app.py", "w").write(text)
    print("Saved! Backup app.py.bak2")
