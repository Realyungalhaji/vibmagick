#!/data/data/com.termux/files/usr/bin/bash
cd ~/vibmagick
python3 save_all.py &
python3 run.py >> ~/app.log 2>&1 &
sleep 5
cloudflared tunnel --url http://localhost:5000 >> ~/tunnel.log 2>&1 &
