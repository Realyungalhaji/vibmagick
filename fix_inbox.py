import pathlib
p = pathlib.Path("app.py")
t = p.read_text()
# Fix only the inbox crash: skip empty followers
old = "for f in followers:"
new = "for f in [x for x in followers if x and str(x).strip()]:"
if old in t:
    t = t.replace(old, new, 1)
    print("FIXED inbox empty follower")
else:
    print("Line not found - check line 285")
# Also make f[0] safe if f is short
t = t.replace("f[0][0]", "(f[0][0] if f and f[0] else '?')")
p.write_text(t)
import py_compile
py_compile.compile("app.py", doraise=True)
print("SYNTAX OK")
