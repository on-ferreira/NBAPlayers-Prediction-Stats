import os
import time
from datetime import datetime, timedelta

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

DATA_DIR = "data"
DAILY_DIR = os.path.join(DATA_DIR, "DAILYLINES")
POP_UP_BUTTON_XPATH = '//*[@id="landing-page-modal"]/div/div[1]/button'
SHOW_MORE_BUTTON_SELECTOR = 'button.load-more'


def open_Markets(page):
    page.locator(f'xpath={POP_UP_BUTTON_XPATH}').wait_for()
    page.locator(f'xpath={POP_UP_BUTTON_XPATH}').click()

    page.wait_for_selector('.table-layout-container')
    for j in range(2, 12):
        page.locator(f':nth-match(.table-layout-container, {j})').click()
        time.sleep(0.5)


def open_show_more(page):
    try:
        page.eval_on_selector_all(SHOW_MORE_BUTTON_SELECTOR,
                                  'elements => elements.map(element => element.click())')

    except Exception as e:
        print(f"Error clicking 'Show more' button: {e}")
        return


def get_html(page, url, selector, sleep=5, retries=2):
    html = None
    for i in range(1, retries + 1):
        time.sleep(sleep * i)
        try:
            page.goto(url)
            print(page.title())
            if selector == ".markets.tw-m-n":
                open_Markets(page)
                open_show_more(page)
            html = page.locator(selector).inner_html()
        except PlaywrightTimeout:
            print(f"Timeout error on {url}")
            continue
        else:
            break
    return html


def scrape_daily():
    url = "https://br.betano.com/sport/basquete/eua/nba/17106"
    with sync_playwright() as p:
        browser = p.firefox.launch()
        page = browser.new_page()
        html = get_html(page, url, ".league-block")
        browser.close()

    soup = BeautifulSoup(html, features="html.parser")
    links = soup.find_all("a")
    standings_pages = [f"https://br.betano.com{l['href']}?bt=1" for l in links]
    actual_date = datetime.now()
    date_25_dez = datetime(actual_date.year, 12, 25)
    distance_to_xmas_games = (date_25_dez - actual_date).days

    if distance_to_xmas_games > 3:
        games_to_ignore = [
            'https://br.betano.com/odds/new-york-knicks-milwaukee-bucks/37758596/?bt=1',
            'https://br.betano.com/odds/los-angeles-lakers-boston-celtics/37758627/?bt=1',
            'https://br.betano.com/odds/miami-heat-philadelphia-76ers/37758725/?bt=1',
            'https://br.betano.com/odds/phoenix-suns-dallas-mavericks/37758643/?bt=1']
        standings_pages = [page for page in standings_pages if page not in games_to_ignore]

    return standings_pages


def scrape_game(daily_games):
    with sync_playwright() as p:
        browser = p.firefox.launch()

        for url in daily_games:
            save_path = os.path.join(DAILY_DIR, url.split("/")[-2] + ".html")
            if os.path.exists(save_path):
                continue
            page = browser.new_page()
            html = get_html(page, url, ".markets.tw-m-n")
            if not html:
                continue
            with open(save_path, "w+", encoding=None, errors="replace") as f:
                f.write(html)
        browser.close()


daily_games = list(dict.fromkeys(scrape_daily()))
scrape_game(daily_games)
