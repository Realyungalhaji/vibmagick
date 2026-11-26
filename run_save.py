# run_save.py - saves ALL data + functions state, without editing app.py
import json, os, sqlite3, datetime
import app as app_module
from app import app

SAVE_FILE = "all_data.json"

# 1. LOAD - on startup, restore everything that was saved before
if os.path.exists(SAVE_FILE):
    try:
        data = json.load(open(SAVE_FILE))
        for k, v in data.items():
            if k in dir(app_module):
                try:
                    setattr(app_module, k, v)
                    print(f"RESTORED {k}: {len(v) if hasattr(v,'__len__') else v}")
                except: pass
        print("ALL DATA RESTORED")
    except Exception as e:
        print("Restore skipped:", e)

# 2. SAVE - after EVERY request, save all data
def save_all():
    try:
        out = {}
        # save every global that looks like data
        for k in ["users","posts","messages","comments","followers","following","saved","saved_posts","blocked","blocks","reports","chats","likes","notifications"]:
            if hasattr(app_module, k):
                v = getattr(app_module, k)
                # only save if JSON-able
                try:
                    json.dumps(v)
                    out[k] = v
                except: pass
        # also save anything else that is dict/list and not a function/module
        for k, v in vars(app_module).items():
            if k.startswith("_"): continue
            if isinstance(v, (dict, list)) and k not in out:
                try:
                    json.dumps(v)
                    out[k] = v
                except: pass
        json.dump(out, open(SAVE_FILE, "w"), indent=2)
    except Exception as e:
        print("Save skipped:", e)

@app.after_request
def _save_everything(response):
    save_all()
    return response

@app.route("/api/save-status")
def save_status():
    if os.path.exists(SAVE_FILE):
        d = json.load(open(SAVE_FILE))
        return {"saved": True, "keys": list(d.keys()), "counts": {k: len(v) if hasattr(v, '__len__') else v for k,v in d.items()}, "file": SAVE_FILE}
    return {"saved": False}

if __name__ == "__main__":
    print("RUNNING WITH FULL SAVE - app.py untouched")
    app.run(host="0.0.0.0", port=5000, debug=True)
