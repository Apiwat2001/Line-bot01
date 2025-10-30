import os, requests, pytz
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

line_token = os.environ.get("LINE_TOKEN")
headers = {"Authorization": f"Bearer {line_token}", "Content-Type": "application/json"}
tz = pytz.timezone("Asia/Bangkok")

def fetch_attendance():
    if not os.path.exists("current_link.txt"):
        print("ไม่พบไฟล์ current_link.txt")
        return {}
    with open("current_link.txt", "r") as f:
        url1 = f.read().strip()

    service = Service("/usr/bin/chromedriver")  # ใช้ path ที่ cloud รองรับ
    driver = webdriver.Chrome(service=service)
    driver.get(url1)
    try:
        link = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "a")))
        href = link.get_attribute("href")
        driver.get(href)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "greyGridTable")))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        table = soup.find('table', class_='greyGridTable')
        emp_data = {}
        if table:
            rows = table.find_all('tr')[1:]
            for row in rows:
                cols = row.find_all('td')
                emp_id = cols[0].text.strip()
                name = cols[1].text.strip()
                time_in = cols[2].text.strip()
                time_out = cols[3].text.strip()
                emp_data[emp_id] = {"name": name, "time_in": time_in, "time_out": time_out}
    finally:
        driver.quit()
    return emp_data

def send_line(emp_data):
    if not os.path.exists("user_id.txt"):
        return
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
            requests.post("https://api.line.me/v2/bot/message/push", headers=headers, json=data)

def handler(request):
    emp_data = fetch_attendance()
    if emp_data:
        send_line(emp_data)
    return {"status": "ok"}
