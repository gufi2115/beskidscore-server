import requests
from django.core.management.base import BaseCommand
from bs4 import BeautifulSoup
from data.models import TeamM
from django.contrib.postgres.search import TrigramSimilarity
import re
import json


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--url', type=str, default='http://www.90minut.pl/liga/1/liga13085.html')


    def handle(self, *args, **options):
        url=options['url']

        kolejka_header_re = re.compile(r"Kolejka\s+(\d+)")
        score_re = re.compile(r"(\d{1,2})-(\d{1,2})")

        results = self.scrape_90minut(url, kolejka_header_re, score_re)
        teams = []
        for result in results:
            for match in result['matches']:
                if not match['home_team'] in teams:
                    teams.append(match['home_team'])
        results.append({'teams': teams})
        self.save_to_json(results, 'data/management/commands/matches/Klasa_okręgowa_2023_2024.json')

    def parse_match_row(self, cells, score_re):
        if len(cells) != 4:
            return None
        score = cells[1].get_text(strip=True)
        match = score_re.fullmatch(score)
        if not match:
            return None
        teams_obj = TeamM.objects.all()
        home = cells[0].get_text(strip=True)
        home_team_annotate = teams_obj.annotate(similarity=TrigramSimilarity('name', home)).filter(
            similarity__gt=0.3).order_by('-similarity')
        away = cells[2].get_text(strip=True)
        away_team_annotate = teams_obj.annotate(similarity=TrigramSimilarity('name', away)).filter(
            similarity__gt=0.3).order_by('-similarity')
        date = cells[3].get_text(strip=True)
        months = {
        'stycznia': 1,
        'lutego': 2,
        'marca': 3,
        'kwietnia': 4,
        'maja': 5,
        'czerwca': 6,
        'lipca': 7,
        'sierpnia': 8,
        'września': 9,
        'października': 10,
        'listopada': 11,
        'grudnia': 12
        }
        date_split = date.split()
        format_date = ''
        if not "(" in date_split[-1]:
            time = f'{date_split[-1]}:00'
            if 7 <= months[date_split[1].strip(',')] <= 12:
                format_date = f'2023-{months[date_split[1].strip(",")]}-{date_split[0]}'     #USTAW DATE POD LIGE
            else:
                format_date = f'2024-{months[date_split[1].strip(",")]}-{date_split[0]}'
        else:
            time = f'{date_split[-2]}:00'
            if 7 <= months[date_split[1].strip(',')] <= 12:
                format_date = f'2023-{months[date_split[1].strip(",")]}-{date_split[0]}'
            else:
                format_date = f'2024-{months[date_split[1].strip(",")]}-{date_split[0]}'
        home_goals = int(match.group(1))
        away_goals = int(match.group(2))
        return {
            "home_team": home if not home_team_annotate else str(home_team_annotate[0]),
            "away_team": away if not away_team_annotate else str(away_team_annotate[0]),
            "home_score": home_goals,
            "away_score": away_goals,
            "Date": format_date,
            "Time": time
        }

    def scrape_90minut(self, url, kolejka_header_re, score_re):
        response = requests.get(url)
        response.encoding = 'iso-8859-2'
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []

        tables = soup.find_all('table', class_='main')
        kolejka_nr = None

        for table in tables:
            prev = table.find_previous('table', class_='main')
            if prev:
                header = prev.get_text()
                found = kolejka_header_re.search(header)
                if found:
                    kolejka_nr = int(found.group(1))
            else:
                header = table.get_text()
                found = kolejka_header_re.search(header)
                if found:
                    kolejka_nr = int(found.group(1))
            matches = []
            for row in table.find_all('tr'):
                cells = row.find_all('td')
                match = self.parse_match_row(cells, score_re)
                if match:
                    matches.append(match)

            if matches and kolejka_nr:
                results.append({
                    "round": kolejka_nr,
                    "matches": matches
                })

        return results

    def save_to_json(self, data, filename='matches.json'):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
