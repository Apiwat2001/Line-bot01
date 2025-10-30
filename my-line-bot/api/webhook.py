from flask import Flask, request, jsonify
import json, os, requests

app = Flask(__name__)

line_token = os.environ.get("LINE_TOKEN")  # เก็บใน environment บน Vercel
headers = {"Authorization": f"Bearer {line_token}", "Content-Type": "application/json"}

link_file = "current_link.txt"
user_id_file = "user_id.txt"

@app.route("/api/webhook", methods=["POST"])
def webhook():
    body = request.get_json()
    events = body.get("events", [])
    
    for event in events:
        if event["type"] == "message" and event["message"]["type"] == "text":
            text = event["message"]["text"].strip()
            reply_token = event["replyToken"]
            sender_user_id = event["source"]["userId"]

            if text.lower().startswith("link"):
                url = text[4:].strip()
                with open(link_file, "w") as f:
                    f.write(url)
                send_reply(reply_token, f"URL ถูกบันทึกแล้ว: {url}")

            elif text.lower().startswith("id"):
                emp_id = text[2:].strip()
                if emp_id:
                    user_dict = {}
                    if os.path.exists(user_id_file):
                        with open(user_id_file, "r") as f:
                            for line in f:
                                if ',' in line:
                                    k, v = line.strip().split(',', 1)
                                    user_dict[k.strip()] = v.strip()
                    user_dict[emp_id] = sender_user_id
                    with open(user_id_file, "w") as f:
                        for k, v in user_dict.items():
                            f.write(f"{k},{v}\n")
                    send_reply(reply_token, f"ข้อมูล {emp_id} ถูกบันทึกแล้ว")
                else:
                    send_reply(reply_token, "กรุณาพิมพ์ id ตามด้วยเลข เช่น id 780")
    
    return jsonify({"status": "ok"})

def send_reply(reply_token, message):
    data = {"replyToken": reply_token, "messages": [{"type": "text", "text": message}]}
    requests.post("https://api.line.me/v2/bot/message/reply", headers=headers, json=data)

# ไม่มี app.run() ที่นี่ เพราะ Vercel จะเรียกเอง
