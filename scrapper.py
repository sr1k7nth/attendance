from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import os
import math
import time
from pprint import pprint
import winreg

def find_chrome():
    reg_paths = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe"
    ]

    for reg_path in reg_paths:
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
            chrome_path, _ = winreg.QueryValueEx(key, "")
            if os.path.exists(chrome_path):
                return chrome_path
        except FileNotFoundError:
            pass

    common_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
    ]

    for path in common_paths:
        if os.path.exists(path):
            return path

    for path in os.environ["PATH"].split(";"):
        exe = os.path.join(path, "chrome.exe")
        if os.path.exists(exe):
            return exe

    return None

def scrape_attendance(uid, password):

    chrome_path = find_chrome()
    if not chrome_path:
        raise Exception("Google Chrome NOT found on this system!")
    
    with sync_playwright() as pw:

        user_data_dir = os.path.join(os.getcwd(), "playwright_profile")

        browser = pw.chromium.launch_persistent_context(
            executable_path=chrome_path,
            user_data_dir=user_data_dir,
            headless=True,
        )

        page = browser.new_page()
        url = "https://jssateb.azurewebsites.net/Apps/Login.aspx"
        page.goto(url)

        page.wait_for_selector("#optLoginAsStudent", timeout=10000)
        page.check("#optLoginAsStudent")
        page.fill("#txtUserID", uid)
        page.fill("#txtPassword", password)
        page.click("#myBtn")
        page.wait_for_timeout(1000)

        error_node = page.query_selector("#divModelValidation_alertmsg")
        if error_node:
            msg = error_node.inner_text().strip().lower()
            if "incorrect user id" in msg or "password" in msg:
                browser.close()
                return None

        page.wait_for_load_state("networkidle")

        page.wait_for_selector('a[href*="StudentAttendance"]', timeout=15000)
        page.click('a[href*="StudentAttendance"]')
        page.wait_for_selector('table.table', timeout=10000)

        time.sleep(2)

        soup = BeautifulSoup(page.content(), "lxml")
        table = soup.find("table", {"class": "table"})
        absent_periods = []

        if table:
            table_rows = table.find_all("tr")[1:]
            for row in table_rows:
                day_cell = row.find("td", class_="bg-primary")
                if not day_cell:
                    continue

                day_text = day_cell.get_text(strip=True)
                day_name = "".join(filter(str.isalpha, day_text))
                day_date = day_text[len(day_name):].strip()

                for cell in row.find_all("td")[1:]:
                    for period_info in cell.find_all("div", style="cursor:pointer;", recursive=False):
                        info_divs = period_info.find_all("div", class_="row")

                        if len(info_divs) < 6:
                            continue

                        info_list = [div.get_text(strip=True) for div in info_divs]
                        if any("absent" in text.lower() for text in info_list):
                            absent_periods.append({
                                "day": day_name,
                                "date": day_date,
                                "course": info_list[0] if info_list else "Unknown",
                                "attendance": "Absent",
                            })

        page.get_by_role("button", name="Summary").click()
        page.wait_for_selector("table.fancyTable", timeout=10000)
        time.sleep(1)

        soup = BeautifulSoup(page.content(), "lxml")
        attendance_table = soup.find("table", class_="fancyTable")
        summary = []

        if attendance_table:
            tbody = attendance_table.find("tbody")
            if tbody:
                rows = tbody.find_all("tr")
                for row in rows:
                    cols = [col.text.strip() for col in row.find_all("td")]
                    if len(cols) < 10:
                        continue
                    summary.append({
                        "no": cols[1],
                        "code": cols[2],
                        "name": cols[3],
                        "classes": cols[7],
                        "present": cols[8],
                        "percentage": cols[9],
                    })

        total_classes = 0
        total_present = 0
        for row in summary:
            try:
                total_classes += int(row["classes"])
                total_present += int(row["present"])
            except ValueError:
                continue

        total_avg = round((total_present / total_classes) * 100, 2) if total_classes else 0

        if total_avg >= 85:
            can_miss85 = math.floor((total_present - 0.85 * total_classes) / 0.85)
            need_to_attend85 = 0
        else:
            need_to_attend85 = math.ceil(((0.85 * total_classes) - total_present) / 0.15)
            can_miss85 = 0

        if total_avg >= 75:
            can_miss75 = math.floor((total_present - 0.75 * total_classes) / 0.75)
            need_to_attend75 = 0
        else:
            need_to_attend75 = math.ceil(((0.75 * total_classes) - total_present) / 0.25)
            can_miss75 = 0


        browser.close()

        

        return summary, absent_periods, total_avg, can_miss85, can_miss75, need_to_attend85, need_to_attend75

if __name__ == "__main__":
    pass
