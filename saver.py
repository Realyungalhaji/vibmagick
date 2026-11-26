import sqlite3, json, datetime, os, threading
LOCK = threading.Lock()
DB = "data.db"
BACKUP = "backup.json"
def _init():
    c = sqlite3.connect(DB)
    c.execute("CREATE TABLE IF NOT EXISTS saved_data (id INTEGER PRIMARY KEY AUTOINCREMENT, time TEXT, path TEXT, method TEXT, ip TEXT, form TEXT, args TEXT, json_data TEXT)")
    c.commit(); c.close()
def save_all(request):
    try:
        _init()
        row = [datetime.datetime.now().isoformat(), request.path, request.method, request.remote_addr, json.dumps(dict(request.form)), json.dumps(dict(request.args)), json.dumps(request.get_json(silent=True) or {})]
        with LOCK:
            c = sqlite3.connect(DB)
            c.execute("INSERT INTO saved_data (time,path,method,ip,form,args,json_data) VALUES (?,?,?,?,?,?,?)", row)
            c.commit(); c.close()
            data = []
            if os.path.exists(BACKUP):
                try: data = json.load(open(BACKUP))
                except: data = []
            data.append({"time":row[0],"path":row[1],"method":row[2],"ip":row[3],"form":row[4],"args":row[5],"json":row[6]})
            json.dump(data[-5000:], open(BACKUP, "w"))
    except Exception as e:
        print("saver skipped:", e)
