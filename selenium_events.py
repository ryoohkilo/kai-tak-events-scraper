from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import re
import json

# 1. Scrape main event page for event links and basic info
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get("https://www.kaitaksportspark.com.hk/tc/event")
time.sleep(15)

events = []

for a in driver.find_elements(By.TAG_NAME, "a"):
    href = a.get_attribute("href")
    text = a.text.strip()
    if href and "/event/" in href and text:
        date_search = re.search(r"\d{4}年\d{1,2}月\d{1,2}[日至及]*\d*日?", text)
        date = date_search.group(0) if date_search else ""
        title = text.replace(date, "").strip() if date else text
        summary = ""
        events.append({
            "title": title,
            "link": href,
            "date": date,
            "summary": summary
        })

driver.quit()

with open("latest_events.json", "w", encoding="utf-8") as f:
    json.dump(events, f, ensure_ascii=False, indent=2)

print(f"Saved {len(events)} basic events to latest_events.json")

# 2. Visit each event page for deeper info
detailed_events = []
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

for event in events:
    driver.get(event["link"])
    time.sleep(5)

    # Dictionaries for extracted info
    details = {"title": event["title"], "link": event["link"]}

    # Find all event details field-value pairs
    try:
        for container in driver.find_elements(By.CLASS_NAME, "WiS2D"):
            label_elems = container.find_elements(By.CLASS_NAME, "tlwFT")
            value_elems = container.find_elements(By.CLASS_NAME, "hsVUo")
            if label_elems and value_elems:
                key = label_elems[0].text.strip()
                value = value_elems[0].text.strip()
                details[key] = value
            # Special case for a label linking out (eg. 查看更多)
            links = container.find_elements(By.TAG_NAME, "a")
            for l in links:
                if l.get_attribute("href"):
                    details["查看更多"] = l.get_attribute("href")
    except Exception as e:
        print(f"Error extracting details from {event['link']}: {e}")

    detailed_events.append(details)

driver.quit()

# 3. Save all detailed events
with open("total_events.json", "w", encoding="utf-8") as f:
    json.dump(detailed_events, f, ensure_ascii=False, indent=2)

print(f"Saved {len(detailed_events)} detailed events to total_events.json")
