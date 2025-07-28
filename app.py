import os
import uuid
from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
from utils.prompt_templates import make_prompt, load_styles
from utils.dalle_api import generate_image
from utils.image_logo import add_logo
import base64

UPLOAD_DIR = 'static/uploads'
OUTPUT_DIR = 'static/output'
LOGO_PATH = 'static/logo/LOGO.PNG'

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

app = Flask(__name__)
CORS(app)

# 用 dict 模擬記憶體快取任務（正式建議用DB或Redis）
tasks = {}

@app.route("/")
def home():
    return render_template("frontend.html", styles=load_styles())

@app.route("/generate", methods=["POST"])
def generate():
    try:
        data = request.json
        style = data.get("style")
        colors = data.get("colors", "")
        image_b64 = data.get("image_base64").split(',')[-1]
        img_bytes = base64.b64decode(image_b64)
        # 檔案大小限制
        if len(img_bytes) > 2*1024*1024:
            return jsonify({"status":"failed", "error":"圖片超過2MB"}), 413
        filename = f"{uuid.uuid4()}.png"
        up_path = os.path.join(UPLOAD_DIR, filename)
        with open(up_path, "wb") as f:
            f.write(img_bytes)
        prompt = make_prompt(style, colors)
        # 呼叫 OpenAI 產圖
        try:
            img_url = generate_image(prompt)
        except Exception as e:
            return jsonify({"status":"failed", "error":f"OpenAI API failed: {e}"}), 500
        # 下載產生圖
        import requests
        r = requests.get(img_url)
        gen_img_path = os.path.join(OUTPUT_DIR, f"{filename}_gen.png")
        with open(gen_img_path, 'wb') as f:
            f.write(r.content)
        # 加 LOGO
        logo_img_path = os.path.join(OUTPUT_DIR, f"{filename}_logo.png")
        add_logo(gen_img_path, LOGO_PATH, logo_img_path)
        task_id = filename.split('.')[0]
        tasks[task_id] = {
            "original": "/" + up_path,
            "styled": "/" + logo_img_path
        }
        return jsonify({"task_id": task_id, "status": "processing"})
    except Exception as e:
        return jsonify({"status": "failed", "error": str(e)}), 500

@app.route("/status/<task_id>")
def status(task_id):
    info = tasks.get(task_id)
    if not info:
        return jsonify({"status":"processing"})
    return jsonify({
        "status": "completed",
        "original_image_url": info["original"],
        "styled_image_url": info["styled"]
    })

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

@app.route('/styles')
def styles():
    return jsonify(load_styles())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
