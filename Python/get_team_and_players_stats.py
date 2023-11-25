import os
import time
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

DATA_DIR = "DATA"
TEAMS_DIR = os.path.join(DATA_DIR, "TEAMS")


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


def scrape_teams():
    url = "https://www.nba.com/stats/teams"
    selector = "div.StatsTeamsList_divContent__JvxSY"
    html = get_html(url, selector)
    soup = BeautifulSoup(html, 'html.parser')
    team_links = soup.find_all('a', class_='StatsTeamsList_teamLink__q_miK')

    teams_pages = ["https://www.nba.com" + link['href'] for link in team_links]

    for url in teams_pages:
        save_path = os.path.join(TEAMS_DIR, (url.split("/")[-1] + ".html"))
        if os.path.exists(save_path):
            continue

        html = get_html(url, "html")
        with open(save_path, "w+") as f:
            f.write(html)


scrape_teams()
