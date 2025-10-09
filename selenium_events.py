from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import re
import json
import tempfile

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument(f'--user-data-dir={tempfile.mkdtemp()}')

# 第一階段：抓主頁活動
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
driver.get("https://www.kaitaksportspark.com.hk/tc/event")
time.sleep(15)

events = []
for a in driver.find_elements(By.TAG_NAME, "a"):
    href = a.get_attribute("href")
    text = a.text.strip()
    if href and "event" in href and text:
        datesearch = re.search(r"\d{4}/\d{1,2}/\d{1,2}", text)
        date = datesearch.group(0) if datesearch else None
        title = text.replace(date, "").strip() if date else text
        events.append({
            "title": title,
            "link": href,
            "date": date,
            "summary": text
        })
driver.quit()

with open("latest_events.json", "w", encoding="utf-8") as f:
    json.dump(events, f, ensure_ascii=False, indent=2)
print(f"Saved {len(events)} basic events to latest_events.json")

# 第二階段：抓詳細活動頁
detailedevents = []
for event in events:
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get(event["link"])
    time.sleep(5)

    details = {"title": event["title"], "link": event["link"]}
    try:
        for container in driver.find_elements(By.CLASS_NAME, "WiS2D"):
            labelelems = container.find_elements(By.CLASS_NAME, "tlwFT")
            valueelems = container.find_elements(By.CLASS_NAME, "hsVUo")
            if labelelems and valueelems:
                key = labelelems[0].text.strip()
                value = valueelems[0].text.strip()
                details[key] = value
            # 連結類欄位獨立抓
            links = container.find_elements(By.TAG_NAME, "a")
            for l in links:
                if l.get_attribute("href"):
                    details["查看更多"] = l.get_attribute("href")
    except Exception as e:
        print(f"Error extracting details from {event['link']}: {e}")
    detailedevents.append(details)
    driver.quit()

with open("total_events.json", "w", encoding="utf-8") as f:
    json.dump(detailedevents, f, ensure_ascii=False, indent=2)
print(f"Saved {len(detailedevents)} detailed events to total_events.json")
