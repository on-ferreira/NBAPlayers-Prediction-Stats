import os
import pandas as pd
from bs4 import BeautifulSoup
import math
import re

SCORE_DIR = "data/SCORES"
PLAYERS_DIR = "data/PLAYERS"

box_scores = os.listdir(SCORE_DIR)
box_scores = [os.path.join(SCORE_DIR, f) for f in box_scores if f.endswith(".html")]
player_scores = os.listdir(PLAYERS_DIR)


def parse_html(box_score):
    with open(box_score, encoding=None, errors="replace") as f:
        html = f.read()

    soup = BeautifulSoup(html,features="html.parser")
    [s.decompose() for s in soup.select("tr.over_header")]
    [s.decompose() for s in soup.select("tr.thead")]
    return soup


def read_season_info(soup):
    nav = soup.select("#bottom_nav_container")[0]
    hrefs = [a["href"] for a in nav.find_all('a')]
    season = os.path.basename(hrefs[1]).split("_")[0]
    return season


def read_line_score(soup):
    line_score = pd.read_html(str(soup), attrs={'id': 'line_score'})[0]
    cols = list(line_score.columns)
    cols[0] = "team"
    cols[-1] = "total"
    line_score.columns = cols

    line_score = line_score[["team", "total"]]

    return line_score


def MP_converter(time):
    re_minsec = r'(\d{1,2}):(\d{1,2})'
    total = 'a'
    if re.search(re_minsec, time):
        minutes, seconds = map(int, time.split(':'))
        total = minutes + seconds / 60
        total = math.floor(total * 100) / 100
    return total


def read_stats(soup, team, stat):
    df = pd.read_html(str(soup), attrs={'id': f'box-{team}-game-{stat}'}, index_col=0)[0]
    df['MP'] = df['MP'].apply(MP_converter)
    df = df.apply(pd.to_numeric, errors="coerce")
    return df


players = {}

for box_score in box_scores:
    soup = parse_html(box_score)
    try:
        line_score = read_line_score(soup)
        teams = list(line_score["team"])
        print(f'{teams[0]} x {teams[1]} - {os.path.basename(box_score)[:8]}')

        for team in teams:
            basic = read_stats(soup, team, "basic")
            advanced = read_stats(soup, team, "advanced")
            basic.index = basic.index.str.lower()
            advanced.index = advanced.index.str.lower()
            summary = pd.concat([basic, advanced], axis=1, join='inner')
            if team == teams[0]:
                summary["opp"] = teams[1]
            else:
                summary["opp"] = teams[0]
            summary["season"] = read_season_info(soup)
            summary["date"] = os.path.basename(box_score)[:8]
            summary["date"] = pd.to_datetime(summary["date"], format="%Y%m%d")
            summary.drop("team totals", inplace=True)
            for i in range(summary.shape[0]):
                nome = summary.iloc[i].name
                dados = summary.iloc[i].to_frame().T
                if nome not in players:
                    players[nome] = dados
                else:
                    players[nome] = pd.concat([players[nome], dados])
    except:
        continue

for s in players.keys():
    players[s] = players[s].sort_values(by='date')
    players[s] = players[s].reset_index(drop=True)
    csv_name = "data/PLAYERS/" + s + ".csv"
    try:
        players[s].to_csv(csv_name)
    except:
        print("Erro no jogador "+ csv_name)
