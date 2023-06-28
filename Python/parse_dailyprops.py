import os
import pandas as pd
from bs4 import BeautifulSoup
import re
import csv

DAILY_DIR = "data/DAILYLINES"

player_props = os.listdir(DAILY_DIR)
player_props = [os.path.join(DAILY_DIR, f) for f in player_props if f.endswith(".html")]


def parse_html(pp):
    with open(pp, encoding=None, errors="replace") as f:
        html = f.read()

    soup = BeautifulSoup(html, features="html.parser")

    return soup


def read_stats(soup, market):
    df = pd.read_html(str(soup), attrs={'id': f'row-wrapper'}, index_col=0)[0]
    df = df.apply(pd.to_numeric, errors="coerce")
    return df


markets = {
    'pontos mais/menos': 'PTS',
    'rebotes mais/menos': 'TRB',
    'assistências mais/menos': 'AST',
    'total arremessos de três pontos marcados +/-': '3P',
    'roubos mais/menos': 'STL',
    'bloqueios mais/menos': 'BLK',
    'turnover mais/menos': 'TOV',
    'pontos + rebotes + assistências mais/menos': 'PRA',
    'pontos + rebotes mais/menos': 'PR',
    'pontos + assistências mais/menos': 'PA'
}

teamsDic = {
    'atlanta': 'ATL', 'boston': 'BOS', 'brooklyn': 'BKN', 'charlotte': 'CHA', 'chicago': 'CHI',
    'cleveland': 'CLE', 'dallas': 'DAL', 'denver': 'DEN', 'detroit': 'DET', 'golden': 'GSW',
    'houston': 'HOU', 'indiana': 'IND', 'clippers': 'LAC', 'lakers': 'LAL', 'memphis': 'MEM',
    'miami': 'MIA', 'milwaukee': 'MIL', 'minnesota': 'MIN', 'york': 'NYK', 'orleans': 'NOP',
    'oklahoma': 'OKC', 'orlando': 'ORL', 'philadelphia': 'PHI', 'phoenix': 'PHX', 'portland': 'POR',
    'sacramento': 'SAC', 'san': 'SAS', 'toronto': 'TOR', 'utah': 'UTA', 'washington': 'WAS'}

teams_extended = [
    'boston celtics', 'brooklyn nets', 'new york knicks', 'philadelphia 76ers', 'toronto raptors',
    'chicago bulls', 'cleveland cavaliers', 'detroit pistons', 'indiana pacers', 'milwaukee bucks',
    'golden state warriors', 'los angeles clippers', 'los angeles lakers', 'phoenix suns', 'sacramento kings',
    'atlanta hawks', 'charlotte hornets', 'miami heat', 'orlando magic', 'washington wizards',
    'denver nuggets', 'minnesota timberwolves', 'oklahoma city thunder', 'portland trail blazers', 'utah jazz',
    'dallas mavericks', 'houston rockets', 'memphis grizzlies', 'new orleans pelicans', 'san antonio spurs'
]


def find_teams(archive):
    teams = []
    new = archive.split('\\')[-1]
    new = new.replace('-', ' ')
    new = new.replace('.html', '')
    new = new.split()
    for n in new:
        try:
            teams.append(teamsDic[n])
        except:
            continue
    return teams


def parse_game(player_props):
    for pp in player_props:
        soup = parse_html(pp)
        soup.find_all('div')
        # teams = find_teams(pp)
        teams = ['T1', 'T2']  # fix later - using random values for now
        page = soup.text.split(os.linesep)
        lines = page[0].splitlines()
        remove_index = []
        for j in range(len(lines)):
            lines[j] = lines[j].lower().strip()
            if lines[j] == '' or lines[j] == 'linha mais demenos de':
                remove_index.append(j)
        remove_index.reverse()
        [lines.pop(i) for i in remove_index]
        create_csv(pp, lines, teams)
        print(f'{teams[0]} x {teams[1]}')


def find_opp(name, teams):
    actual_team = ''
    for n in name.split():
        try:
            actual_team = teamsDic[n]
        except:
            continue
    return teams[0] if teams[0] != actual_team else teams[1]


def add_zeros(players_rows):
    max = 0
    for player in players_rows.keys():
        if max < len(players_rows[player]):
            max = len(players_rows[player])
    for player in players_rows.keys():
        if len(players_rows[player]) < max:
            players_rows[player].append(0)
    return players_rows


def create_csv(pp, lines, teams):
    game_html = pp.split('\\')[-1]
    game = game_html.split('.')[0]
    f = open(game + '_players.csv', 'w', newline='', encoding='utf-8')
    w = csv.writer(f)
    opp = ''
    index_row = ['', 'players', 'opp']
    players_rows = {}
    actual = ''
    while len(lines) != 0:
        actual = lines.pop(0)
        if actual == 'rebotes + assistências mais/menos':
            break
        if actual in markets:
            players_rows = add_zeros(players_rows)
            index_row.append(markets[actual])
        elif actual in teams_extended:
            opp = find_opp(actual, teams)
        else:  # player name
            if actual not in players_rows:
                players_rows[actual] = ['']
                players_rows[actual][0] = players_rows[actual].append(actual)  # add name of the player
                players_rows[actual][0] = players_rows[actual].append(opp)
                players_rows[actual][0] = players_rows[actual].append(lines.pop(0))  # add the line of the player
                print(players_rows[actual])
                lines.pop(0)  # pop over odd
                lines.pop(0)  # pop under odd
            else:
                players_rows[actual][0] = players_rows[actual].append(lines.pop(0))  # add line of the player
                lines.pop(0)  # pop over odd
                lines.pop(0)  # pop under odd
    print('---------------------------------------------')
    w.writerow(index_row)
    f.close()
