import pathlib, re
t = pathlib.Path("app.py").read_text(errors="ignore")
print("=== HOW DATA IS SAVED NOW ===")
for word in ["sqlite", "sqlite3", "json.dump", "json.load", "open(", "db =", ".db", "users =", "posts =", "comments =", "chats =", "global"]:
    print(word, "->", "YES" if word in t else "NO")
print("\n=== FILES IN FOLDER ===")
import os
for f in sorted(os.listdir(".")):
    if f.endswith((".db",".json",".txt",".py")):
        print(f, os.path.getsize(f), "bytes")
print("\n=== DATA VARIABLES ===")
for m in re.findall(r"^(users|posts|comments|chats|messages|likes|data)\s*=", t, re.M):
    print("Found variable:", m)
print("\nDONE - send screenshot")
