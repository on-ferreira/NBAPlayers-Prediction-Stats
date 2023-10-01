import os
import time

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

SEASONS = list(range(1977, 2015))

DATA_DIR = "DATA"
STANDINGS_DIR = os.path.join(DATA_DIR, "STANDINGS")
SCORES_DIR = os.path.join(DATA_DIR, "SCORES")


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
                html = page.inner_html(selector)
        except PlaywrightTimeout:
            print(f"Timeout error on {url}")
            continue
        else:
            break
    return html


def scrape_season(season):
    url = f"https://www.basketball-reference.com/leagues/NBA_{season}_games.html"
    html = get_html(url, "#content .filter")

    soup = BeautifulSoup(html, features="html.parser")
    links = soup.find_all("a")
    standings_pages = [f"https://www.basketball-reference.com{l['href']}" for l in links]

    for url in standings_pages:
        save_path = os.path.join(STANDINGS_DIR, url.split("/")[-1])
        if os.path.exists(save_path):
            continue

        html = get_html(url, "#all_schedule")
        with open(save_path, "w+") as f:
            f.write(html)


for season in SEASONS:
    scrape_season(season)

standings_files = os.listdir(STANDINGS_DIR)


def scrape_game(standings_file):
    with open(standings_file, 'r', encoding=None, errors="replace") as f:
        html = f.read()

    soup = BeautifulSoup(html, features="html.parser")
    links = soup.find_all("a")
    hrefs = [l.get('href') for l in links]
    box_scores = [f"https://www.basketball-reference.com{l}" for l in hrefs if l and "boxscore" in l and '.html' in l]

    for url in box_scores:
        save_path = os.path.join(SCORES_DIR, url.split("/")[-1])
        if os.path.exists(save_path):
            continue

        html = get_html(url, "#content")
        if not html:
            continue
        with open(save_path, "w+", encoding=None, errors="replace") as f:
            f.write(html)


standings_files = [s for s in standings_files if ".html" in s]

for f in standings_files:
    filepath = os.path.join(STANDINGS_DIR, f)
    scrape_game(filepath)
