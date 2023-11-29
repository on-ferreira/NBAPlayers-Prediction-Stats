import os
from bs4 import BeautifulSoup
from datetime import datetime
import csv
from harvester.models import GameStatistics, Player, Game, Team
from django.core.management.base import BaseCommand
import time


class Command(BaseCommand):
    help = 'Import data from external sources'

    def handle(self, *args, **options):

        DATA_DIR = "C:\\Users\\orlan\\OneDrive\\Documentos\\UFF\\NBAPlayers-Prediction-Stats\\Python\\website\\main_project\\harvester\\DATA"
        TEAMS_DIR = os.path.join(DATA_DIR, "TEAMS")

        teams_extended = {
            'boston celtics': 'BOS', 'brooklyn nets': 'BRK', 'new york knicks': 'NYK', 'philadelphia 76ers': 'PHI',
            'toronto raptors': 'TOR',
            'chicago bulls': 'CHI', 'cleveland cavaliers': 'CLE', 'detroit pistons': 'DET', 'indiana pacers': 'IND',
            'milwaukee bucks': 'MIL',
            'golden state warriors': 'GSW', 'la clippers': 'LAC', 'los angeles lakers': 'LAL',
            'phoenix suns': 'PHO',
            'sacramento kings': 'SAC',
            'atlanta hawks': 'ATL', 'charlotte hornets': 'CHO', 'miami heat': 'MIA', 'orlando magic': 'ORL',
            'washington wizards': 'WAS',
            'denver nuggets': 'DEN', 'minnesota timberwolves': 'MIN', 'oklahoma city thunder': 'OKC',
            'portland trail blazers': 'POR', 'utah jazz': 'UTA',
            'dallas mavericks': 'DAL', 'houston rockets': 'HOU', 'memphis grizzlies': 'MEM',
            'new orleans pelicans': 'NOP',
            'san antonio spurs': 'SAS'
        }

        def parse_html(page):
            with open(page, encoding=None, errors="replace") as f:
                html = f.read()

            soup = BeautifulSoup(html, features="html.parser")

            return soup

        def find_team(soup):
            selector = "div.TeamHeader_name__MmHlP"
            element = soup.select_one(selector)

            if element:
                text_content = element.get_text().replace('\xa0', ' ')
                return text_content
            else:
                return "Team not found"

        def find_region(soup):
            selector = "div.TeamHeader_record__wzofp"
            element = soup.select_one(selector)

            if element:
                text_content = element.get_text().split()[-1]
                return text_content
            else:
                return "Region not found"

        def find_players_info(soup):
            selector = "div.Crom_container__C45Ti"
            table_element = soup.select_one(selector)

            if table_element:
                rows = table_element.find_all('tr')
                table = []

                for row in rows:
                    cells = row.find_all('td')
                    row_data = [cell.get_text(strip=True) for cell in cells]
                    table.append(row_data)

                return table
            else:
                return "Table element not found"

        def find_head_coach(soup):
            selector = "#__next > div.Layout_base__6IeUC.Layout_justNav__2H4H0 > div.Layout_mainContent__jXliI > main > div.MaxWidthContainer_mwc__ID5AG > section.Block_block__62M07.nba-stats-content-block > div > div.w-full.sm\:w-1\/3.px-0.mx-0.mt-5.mb-1 > div > div.Crom_container__C45Ti.crom-container > table > tbody > tr:nth-child(1) > td:nth-child(2)"
            # I know this isn't a good practice, but I'm not being able to choose the correct selector
            element = soup.select_one(selector)

            if element:
                text_content = element.get_text(strip=True)
                return text_content
            else:
                return "Coach not found"

        def create_or_update_team(soup):
            team_name = find_team(soup)
            team_abrev = teams_extended[team_name.lower()]
            team_region = find_region(soup)
            team_head_coach = find_head_coach(soup)

            team, created = Team.objects.get_or_create(
                name=team_name,
                abbreviation=team_abrev,
                head_coach=team_head_coach,
                region=team_region
            )
            return team

        def convert_height_to_cm(height_str):
            feet, inches = map(int, height_str.split('-'))
            total_inches = feet * 12 + inches
            total_cm = total_inches * 2.54
            return total_cm

        def create_or_update_player(player_data, team):
            player_name, _, position, height_str, weight_str, birth_date_str, _, _, _, _ = player_data

            player_name = player_name.lower()

            birth_date = datetime.strptime(birth_date_str, "%b %d, %Y").date()

            height = convert_height_to_cm(height_str)
            weight = int(weight_str.split(' ')[0])

            player, created = Player.objects.get_or_create(
                name=player_name,
                defaults={'position': position, 'height': height, 'weight': weight, 'birth_date': birth_date,
                          'team': team}
            )
            return created

        csv_file_path = os.path.join(DATA_DIR, '2016-2023-cleaned-csv.csv')

        teams_pages = os.listdir(TEAMS_DIR)
        teams_pages = [os.path.join(TEAMS_DIR, f) for f in teams_pages if f.endswith(".html")]

        for team in teams_pages:
            soup = parse_html(team)
            team = create_or_update_team(soup)
            players = find_players_info(soup)
            for player in players:
                if len(player) > 0:
                    create_or_update_player(player, team)

        with open(csv_file_path, 'r') as file:
            reader = csv.DictReader(file)

            default_team, _ = Team.objects.get_or_create(
                name="Not registered",
                abbreviation="NOT",
                head_coach="Not registered",
                region="Not registered"
            )

            default_player_values = {
                'position': 'Not',
                'height': 0,
                'weight': 0,
                'birth_date': datetime(2000, 1, 1),
                'team': default_team
            }

            for row in reader:
                player, created = Player.objects.get_or_create(name=row['Name'], defaults=default_player_values)

                team = Team.objects.get(abbreviation=row['team'])
                opp = Team.objects.get(abbreviation=row['opp'])

                if row['home'] == '1':
                    home_team = team
                    away_team = opp
                else:
                    home_team = opp
                    away_team = team

                game, created = Game.objects.get_or_create(date=datetime.strptime(row['date'], "%Y-%m-%d"),
                                                           home_team=home_team,
                                                           away_team=away_team,
                                                           location=row['location'])

                FG = int(row['FG'])
                FGA = int(row['FGA'])
                ThreeP = int(row['3P'])
                ThreePA = int(row['3PA'])
                FT = int(row['FT'])
                FTA = int(row['FTA'])

                GameStatistics.objects.create(
                    game=game,
                    player=player,
                    team=team,
                    opp=opp,
                    MP=float(row['MP']),
                    FG=int(row['FG']),
                    FGA=int(row['FGA']),
                    FG_percentage=FG / FGA if FGA > 0 else 0,
                    ThreeP=int(row['3P']),
                    ThreePA=int(row['3PA']),
                    ThreeP_percentage=ThreeP / ThreePA if ThreePA > 0 else 0,
                    FT=int(row['FT']),
                    FTA=int(row['FTA']),
                    FT_percentage=FT / FTA if FTA > 0 else 0,
                    ORB=int(row['ORB']),
                    DRB=int(row['DRB']),
                    TRB=int(row['TRB']),
                    AST=int(row['AST']),
                    STL=int(row['STL']),
                    BLK=int(row['BLK']),
                    TOV=int(row['TOV']),
                    PF=int(row['PF']),
                    PTS=int(row['PTS']),
                    plus_minus=int(row['+/-']),
                    BPM=float(row['BPM'])
                )

        self.stdout.write(self.style.SUCCESS('Successfully imported data from external sources.'))

    def wait(self, seconds):
        self.stdout.write(self.style.SUCCESS(f'Waiting for {seconds} seconds...'))
        time.sleep(seconds)
        self.stdout.write(self.style.SUCCESS('Wait complete!'))
