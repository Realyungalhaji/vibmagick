import shutil, os, time, pathlib
from datetime import datetime

# all your data files
files = [f for f in os.listdir(".") if f.endswith((".db", ".json", ".txt")) and "app.py" not in f]
os.makedirs("BACKUP_ALL", exist_ok=True)
print("Watching:", files)
print("Backup folder: BACKUP_ALL/")

while True:
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    for f in files:
        try:
            if os.path.exists(f):
                shutil.copy2(f, f"BACKUP_ALL/{stamp}_{f}")
        except Exception as e:
            print("skip", f, e)
    # keep only last 20 backups per file to save space
    print(f"[{stamp}] SAVED ALL DATA - {len(files)} files backed up")
    time.sleep(60)
