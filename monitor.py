import requests
from bs4 import BeautifulSoup
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

STATE_FILE = "state.json"
URLS_FILE = "urls.txt"

def load_urls():
    with open(URLS_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def get_links(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    }
    resp = requests.get(url, headers=headers, timeout=15, verify=False)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    links = set()
    for a in soup.find_all("a", href=True):
        text = a.get_text(strip=True)
        href = urljoin(url, a["href"])
        if text and len(text) > 5:
            links.add(f"{text} | {href}")
    return links


def check_one(url):
    try:
        return url, get_links(url), None
    except Exception as e:
        return url, None, str(e)

def send_email(subject, body, to_email):
    from_email = os.environ["EMAIL_FROM"]
    password = os.environ["EMAIL_APP_PASSWORD"]
    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(from_email, password)
        server.send_message(msg)

def main():
    urls = load_urls()
    state = load_state()
    to_email = os.environ["EMAIL_TO"]
    new_findings = {}
    failed = []

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(check_one, url): url for url in urls}
        for future in as_completed(futures):
            url, current_links, error = future.result()

            if error:
                print(f"Error fetching {url}: {error}")
                failed.append(url)
                continue

            previous_links = set(state.get(url, []))

            if previous_links:
                new_items = current_links - previous_links
                if new_items:
                    new_findings[url] = sorted(new_items)
            else:
                print(f"First run for {url}, saving baseline ({len(current_links)} links).")

            state[url] = sorted(current_links)

    if failed:
        print(f"\n{len(failed)} site(s) could not be reached:")
        for u in failed:
            print(f"  - {u}")

    save_state(state)

    if new_findings:
        body_lines = ["Notun update paoa gese:\n"]
        for url, items in new_findings.items():
            body_lines.append(f"\n== {url} ==")
            for item in items[:20]:
                body_lines.append(f"- {item}")
        body = "\n".join(body_lines)
        send_email("🔔 Notun Job Circular Update", body, to_email)
        print("Email sent with new findings.")
    else:
        print("No new updates found.")

if __name__ == "__main__":
    main()
