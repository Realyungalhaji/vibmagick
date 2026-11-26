import shutil, re
shutil.copy2("app.py", "app.py.bak6")
t = open("app.py").read()

# 1. Unify ALL DBs to app.db + auto-save (autocommit) + allow threads
t = t.replace('sqlite3.connect("data.db")', 'sqlite3.connect("app.db", check_same_thread=False, isolation_level=None)')
t = t.replace("sqlite3.connect('data.db')", "sqlite3.connect('app.db', check_same_thread=False, isolation_level=None)")
t = t.replace('sqlite3.connect("app.db")', 'sqlite3.connect("app.db", check_same_thread=False, isolation_level=None)')
t = t.replace("sqlite3.connect('app.db')", "sqlite3.connect('app.db', check_same_thread=False, isolation_level=None)")
# also c = sqlite3.connect(...) variant
t = re.sub(r'sqlite3\.connect\("app\.db"[^)]*\)', 'sqlite3.connect("app.db", check_same_thread=False, isolation_level=None)', t)

# 2. Make sure every write is saved - add commit where INSERT/UPDATE/DELETE is used without commit nearby
# We do NOT change logic, just ensure isolation_level=None already auto-commits, so no extra change needed

open("app.py","w").write(t)
print("Unified to app.db + autocommit")

# 3. Migrate old data.db -> app.db if it exists
import os, sqlite3
if os.path.exists("data.db"):
    try:
        src = sqlite3.connect("data.db")
        dst = sqlite3.connect("app.db", check_same_thread=False, isolation_level=None)
        for (sql,) in src.execute("SELECT sql FROM sqlite_master WHERE sql IS NOT NULL"):
            try: dst.execute(sql)
            except: pass
        for (tbl,) in src.execute("SELECT name FROM sqlite_master WHERE type='table'"):
            try:
                rows = src.execute(f"SELECT * FROM \"{tbl}\"").fetchall()
                cols = len(rows[0]) if rows else 0
                if rows:
                    q = ",".join(["?"]*cols)
                    dst.executemany(f"INSERT OR IGNORE INTO \"{tbl}\" VALUES ({q})", rows)
                    print(f"Migrated {tbl}: {len(rows)} rows")
            except Exception as e: print(tbl, e)
        src.close(); dst.close()
        print("Migration done - old data.db kept as backup")
    except Exception as e: print("Migrate error:", e)
else:
    print("No data.db to migrate")
