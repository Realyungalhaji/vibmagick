import pathlib, re, ast, sys
print("=== 1. SYNTAX CHECK ===")
for f in ["app.py","run.py"]:
    try:
        ast.parse(pathlib.Path(f).read_text())
        print(f, "OK")
    except Exception as e:
        print(f, "BROKEN:", e)

print("\n=== 2. ROUTES IN app.py ===")
t = pathlib.Path("app.py").read_text(errors="ignore")
for m in re.findall(r"@app\.route\(['\"](.*?)['\"]", t):
    print("ROUTE:", m)
for m in re.findall(r"@app\.route\(['\"](.*?)['\"].*?methods=\[(.*?)\]", t):
    print("ROUTE+METHOD:", m)

print("\n=== 3. LINKS CHECK ===")
for link in ["/profile/", "/chat/", "/comment", "/post", "/login", "/signup"]:
    print(link, "found" if link in t else "MISSING")

print("\n=== 4. VIEW CREATOR CHECK ===")
print("View Creator found:", "View Creator" in t)
print("View You left:", "View You" in t)
# find the View Creator line
for i,line in enumerate(t.splitlines(),1):
    if "View Creator" in line:
        print(f"Line {i}:", line.strip()[:200])
        break
print("\nDONE - send me this output")
