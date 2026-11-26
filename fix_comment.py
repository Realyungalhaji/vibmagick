import shutil
shutil.copy2("app.py", "app.py.bak3")
lines = open("app.py").read().splitlines()
out = []
for line in lines:
    if "post/1/comments" in line and "html.replace" in line:
        out.append("        # hardcoded Post 1 link removed - JS comment button handles real post id")
        continue
    line = line.replace("class=backbtn onclick", "class=backbtn type=button onclick")
    out.append(line)
open("app.py", "w").write("\n".join(out) + "\n")
print("Comment fixed! Backup app.py.bak3")
