import shutil
shutil.copy2("app.py", "app.py.bak")
text = open("app.py").read()
button = "<button onclick=history.back()>Back to Previous Page</button><br>"
if "history.back" in text:
    print("Already exists")
else:
    text = text.replace("Comments for", button + "Comments for", 1)
    open("app.py", "w").write(text)
    print("Fixed and Saved!")
