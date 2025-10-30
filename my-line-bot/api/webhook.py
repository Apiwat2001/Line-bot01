@app.route("/api/webhook", methods=["POST"])
def webhook():
    try:
        body = request.get_json()
        events = body.get("events", [])

        for event in events:
            if event["type"] == "message" and event["message"]["type"] == "text":
                text = event["message"]["text"].strip()
                reply_token = event["replyToken"]
                sender_user_id = event["source"]["userId"]

                if text.lower().startswith("link"):
                    url = text[4:].strip()
                    # สำหรับตอนนี้เก็บใน memory (แต่จะหายเมื่อ function ถูกเรียกครั้งต่อไป)
                    app.current_link = url
                    send_reply(reply_token, f"URL ถูกบันทึกแล้ว: {url}")

                elif text.lower().startswith("id"):
                    emp_id = text[2:].strip()
                    if emp_id:
                        if not hasattr(app, "user_dict"):
                            app.user_dict = {}
                        app.user_dict[emp_id] = sender_user_id
                        send_reply(reply_token, f"ข้อมูล {emp_id} ถูกบันทึกแล้ว")
                    else:
                        send_reply(reply_token, "กรุณาพิมพ์ id ตามด้วยเลข เช่น id 780")
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        print("Error:", e)
        return jsonify({"status": "error"}), 200  # return 200 even if error
