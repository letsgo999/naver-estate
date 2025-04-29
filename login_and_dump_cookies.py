# login_and_dump_cookies.py
from playwright.sync_api import sync_playwright
import json, os, time

NAVER_ID = os.getenv("letsgo99")
NAVER_PW = os.getenv("Star465564$$")
OUTPUT = "/app/data/naver_cookies.json"   # Streamlit이 읽을 위치

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://nid.naver.com/nidlogin.login")
    page.fill("#id", NAVER_ID)
    page.fill("#pw", NAVER_PW)
    page.click("input.btn_login")
    page.wait_for_url("https://www.naver.com/*")
    
    cookies = page.context.cookies()
    # 필요하다면 localStorage에 박힌 JWT 추출
    # token = page.evaluate("localStorage.getItem('someKey')")
    
    with open(OUTPUT, "w") as f:
        json.dump({"cookies": cookies}, f, ensure_ascii=False, indent=2)
    browser.close()
