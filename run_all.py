# run_all.py - works on Android, iOS, Computer + Internal + Browser
import os, json
import app as app_module
from app import app
from flask import send_file

# --- Reuse full save from before ---
SAVE_FILE = "all_data.json"
if os.path.exists(SAVE_FILE):
    try:
        data = json.load(open(SAVE_FILE))
        for k,v in data.items():
            if hasattr(app_module, k):
                setattr(app_module, k, v)
    except: pass

@app.after_request
def _make_universal(response):
    # 1. Save all data
    try:
        out={}
        for k in ["users","posts","messages","comments","followers","following","saved","saved_posts","blocked","blocks","reports","chats","likes"]:
            if hasattr(app_module,k):
                try: json.dumps(getattr(app_module,k)); out[k]=getattr(app_module,k)
                except: pass
        json.dump(out, open(SAVE_FILE,"w"))
    except: pass
    # 2. Make every page mobile + desktop friendly
    try:
        if response.content_type and "text/html" in response.content_type:
            html = response.get_data(as_text=True)
            if "<meta name=\"viewport\"" not in html:
                html = html.replace("<head>", '<head><meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no"><meta name="apple-mobile-web-app-capable" content="yes"><meta name="mobile-web-app-capable" content="yes"><meta name="theme-color" content="#000000"><link rel="manifest" href="/manifest.json">', 1)
                if "<head>" not in html:
                    html = '<meta name="viewport" content="width=device-width, initial-scale=1">' + html
            # Universal responsive CSS - fixes Android/iOS/computer in one go
            css = """<style>
*{box-sizing:border-box;max-width:100%} body{margin:0;padding:0;font-family:system-ui,-apple-system,sans-serif} img,video{max-width:100%;height:auto} input,button,textarea{font-size:16px !important;min-height:44px} button{cursor:pointer} a{word-break:break-word}
@media(max-width:768px){ body{font-size:16px} h1{font-size:24px} h2{font-size:20px} div{flex-wrap:wrap !important} }
@media(min-width:769px){ body{max-width:1200px;margin:0 auto} }
</style>"""
            if "box-sizing:border-box" not in html:
                html = html.replace("</head>", css + "</head>") if "</head>" in html else css + html
            response.set_data(html)
    except: pass
    # Allow all browsers / devices
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response

@app.route("/manifest.json")
def manifest():
    return {"name":"VibMagick","short_name":"VibMagick","display":"standalone","start_url":"/","background_color":"#000000","theme_color":"#000000","icons":[{"src":"/icon.png","sizes":"512x512","type":"image/png"}]}

@app.route("/icon.png")
def icon():
    # simple black icon if none exists
    import io
    try:
        return send_file("static/icon.png")
    except:
        from PIL import Image
        img = Image.new("RGB",(512,512),"black")
        buf = io.BytesIO(); img.save(buf, format="PNG"); buf.seek(0)
        return send_file(buf, mimetype="image/png")

if __name__ == "__main__":
    print("UNIVERSAL: Android + iOS + Computer | http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)
