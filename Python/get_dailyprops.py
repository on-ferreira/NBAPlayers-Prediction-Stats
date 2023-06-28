import os
import time

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

DATA_DIR = "data"
DAILY_DIR = os.path.join(DATA_DIR, "DAILYLINES")


def open_Markets(page):
    page.locator('xpath=//html/body/div[1]/div/section[2]/div[7]/div/div/div[1]/button').wait_for()
    page.locator('xpath=//html/body/div[1]/div/section[2]/div[7]/div/div/div[1]/button').click()
    page.wait_for_selector('.table-layout-container')
    for j in range(2, 11):
        page.locator(f':nth-match(.table-layout-container, {j})').click()
        time.sleep(0.5)


def get_html(url, selector, sleep=5, retries=3):
    html = None
    for i in range(1, retries + 1):
        time.sleep(sleep * i)
        try:
            with sync_playwright() as p:
                browser = p.firefox.launch()
                page = browser.new_page()
                page.goto(url)
                print(page.title())
                if selector == ".markets":
                    open_Markets(page)
                html = page.inner_html(selector)
        except PlaywrightTimeout:
            print(f"Timeout error on {url}")
            continue
        else:
            break
    return html


def scrape_daily():
    url = "https://br.betano.com/sport/basquete/eua/nba/17106"
    html = get_html(url, ".league-block")

    soup = BeautifulSoup(html, features="html.parser")
    links = soup.find_all("a")
    standings_pages = [f"https://br.betano.com{l['href']}?bt=1" for l in links]

    return standings_pages


def scrape_game(daily_games):
    for url in daily_games:
        save_path = os.path.join(DAILY_DIR, url.split("/")[-2] + ".html")
        if os.path.exists(save_path):
            continue
        html = get_html(url, ".markets")
        if not html:
            continue
        with open(save_path, "w+", encoding=None, errors="replace") as f:
            f.write(html)


daily_games = set(scrape_daily())
scrape_game(daily_games)
