import os
import pandas as pd
from bs4 import BeautifulSoup
import math
import re
import chardet
import datetime
from tqdm import tqdm


PROJECT_ROOT = r'C:\Users\orlan\OneDrive\Documentos\UFF\NBAPlayers-Prediction-Stats'
DATA_DIR = os.path.join(PROJECT_ROOT, 'Python', 'DATA')
SCORE_DIR = os.path.join(DATA_DIR, 'SCORES')

actual_hour = datetime.datetime.now()
box_scores = os.listdir(SCORE_DIR)
box_scores = [os.path.join(SCORE_DIR, f) for f in box_scores if f.endswith(".html")]


def parse_html(box_score):
    with open(box_score, 'rb') as f:
        data = f.read()
        encoding = chardet.detect(data)['encoding']
    with open(box_score, encoding=encoding) as f:
        html = f.read()

    soup = BeautifulSoup(html, 'lxml')
    [s.decompose() for s in soup.select("tr.over_header")]
    [s.decompose() for s in soup.select("tr.thead")]
    return soup


def read_location_info(soup):
    location_div = soup.select(".scorebox_meta div")[1]
    location = location_div.text.strip()
    return location


def read_hour_info(soup):
    hour_div = soup.select(".scorebox_meta div")[0]
    hour_text = hour_div.text.strip()
    hour_match = re.search(r'(\d{1,2}:\d{2} [APM]+)', hour_text)
    if hour_match:
        hour = hour_match.group(1)
        return hour
    else:
        return None


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
    df['MP'] = df['MP'].map(lambda x: MP_converter(x))
    df = df.apply(pd.to_numeric, errors="coerce")

    return df


def read_title(soup):
    title = soup.find('h1').text
    return title


print(f"Total number of games to be parsed: {len(box_scores)}")

dataframes = []

loading_bar = tqdm(total=len(box_scores), desc="Working...")


for box_score in box_scores:
    soup = parse_html(box_score)
    loading_bar.update(1)
    try:
        line_score = read_line_score(soup)
        teams = list(line_score["team"])
        print(f'\n{teams[0]} x {teams[1]} - {os.path.basename(box_score)[:8]}')

        for team in teams:
            basic = read_stats(soup, team, "basic")
            advanced = pd.DataFrame()
            try:
                advanced = read_stats(soup, team, "advanced")
            except:
                print(f"No advanced box_scores")
            basic.index = basic.index.str.lower()
            if len(advanced.columns) != 0: advanced.index = advanced.index.str.lower()
            summary = pd.concat([basic, advanced], axis=1, join='inner')
            if team == teams[0]:
                summary["opp"] = teams[1]
                summary["team"] = teams[0]
                summary["home"] = 0
            else:
                summary["opp"] = teams[0]
                summary["team"] = teams[1]
                summary["home"] = 1
            summary["season"] = read_season_info(soup)
            summary["date"] = os.path.basename(box_score)[:8]
            summary["date"] = pd.to_datetime(summary["date"], format="%Y%m%d")
            summary["hour"] = read_hour_info(soup)
            summary["location"] = read_location_info(soup)
            summary["title"] = read_title(soup)
            summary = summary.loc[:, ~summary.columns.duplicated()]
            if "team totals" in summary.columns.tolist(): summary.drop("team totals", inplace=True)
            summary.reset_index(inplace=True)
            dataframes.append(summary)


    except Exception as e:
        print(f"Error processing {team} stats for {os.path.basename(box_score)[:8]}: {str(e)}")


loading_bar.close()

finalDF = pd.concat([df.reset_index(drop=True) for df in dataframes], ignore_index=True)
finalDF = finalDF.rename(columns={"Starters": "Name"})

file_path = os.path.join(DATA_DIR, '1975-2023-DF-py.csv')
finalDF.to_csv(file_path, index=False)

actual_hour2 = datetime.datetime.now()
diff = actual_hour2 - actual_hour
print(f"Duration of Script - {diff} \nParsed Files: {len(box_scores)}")
