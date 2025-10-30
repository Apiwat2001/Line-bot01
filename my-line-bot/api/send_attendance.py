import os
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import pytz

# ---------------- Timezone ----------------
tz = pytz.timezone("Asia/Bangkok")

# ---------------- LINE Token ----------------
line_token = os.environ.get("LINE_TOKEN")
headers = {
    "Authorization": f"Bearer {line_token}",
    "Content-Type": "application/json"
}

# ---------------- ฟังก์ชันดึง URL ----------------
def get_url():
    """อ่าน URL จากไฟล์ current_link.txt"""
    if not os.path.exists("current_link.txt"):
        print("ไม่พบ current_link.txt")
        return None
    with open("current_link.txt", "r") as f:
        return f.read().strip()

# ---------------- ฟังก์ชันดึงตาราง ----------------
def fetch_attendance():
    url = get_url()
    if not url:
        return {}
    
    try:
        resp = requests.get(url)
        resp.raise_for_status()
    except Exception as e:
        print("ไม่สามารถเข้าถึง URL:", e)
        return {}

    soup = BeautifulSoup(resp.text, 'html.parser')
    table = soup.find('table', class_='greyGridTable')
    emp_data = {}

    if table:
        rows = table.find_all('tr')[1:]  # ข้าม header
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 4:
                emp_id = cols[0].text.strip()
                name = cols[1].text.strip()
                time_in = cols[2].text.strip()
                time_out = cols[3].text.strip()
                emp_data[emp_id] = {"name": name, "time_in": time_in, "time_out": time_out}
    else:
        print("ไม่พบตาราง greyGridTable")
    
    return emp_data

# ---------------- ฟังก์ชันส่ง LINE ----------------
def send_line(emp_data):
    if not os.path.exists("user_id.txt"):
        print("ไม่พบ user_id.txt")
        return
    
    # โหลด user_id.txt
    user_dict = {}
    with open("user_id.txt", "r") as f:
        for line in f:
            if ',' in line:
                k, v = line.strip().split(',', 1)
                user_dict[k.strip()] = v.strip()

    data_date = datetime.now(tz).strftime("%d/%m/%Y")
    for emp_id, info in emp_data.items():
        if emp_id in user_dict:
            user_id = user_dict[emp_id]
            message = f"[ข้อมูลวันที่ {data_date}]\n{emp_id} {info['name']} เข้า: {info['time_in']} ออก: {info['time_out']}"
            data = {"to": user_id, "messages": [{"type": "text", "text": message}]}
            try:
                response = requests.post("https://api.line.me/v2/bot/message/push", headers=headers, json=data)
                if response.status_code != 200:
                    print(f"ส่ง LINE ไม่สำเร็จ {emp_id}: {response.text}")
            except Exception as e:
                print(f"เกิดข้อผิดพลาดตอนส่ง LINE {emp_id}: {e}")

# ---------------- Handler สำหรับ Vercel ----------------
def handler(request):
    emp_data = fetch_attendance()
    if emp_data:
        send_line(emp_data)
    return {"status": "ok"}
