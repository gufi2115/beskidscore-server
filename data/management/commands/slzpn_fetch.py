import json
from email.policy import default
from django.utils import timezone
from django.core.management.base import BaseCommand
import requests
from datetime import datetime, date, timedelta
from data.models import MatchM, TeamM, LeagueM, SeasonM
from data.helpers import update_league


class Command(BaseCommand):
    help = 'Fetch league information and saving data to json file'

    def add_arguments(self, parser):
        parser.add_argument('--league', type=str, help='Write league name')
        parser.add_argument('--spring_round', type=bool, help='Confirm if you want spring round')
        parser.add_argument('--update', type=bool, help='Confirm if you want update', default=False)

    def handle(self, *args, **options):
        league = options.get('league')
        spring_round = options.get('spring_round')
        update = options['update']
        if league:
            seasonid = "e9d66181-d03e-4bb3-b889-4da848f4831d"
            ligi = requests.get(f'https://slzpn.pl/wp-json/zpn-table/v1/leagues?category=MALE&seasonId={seasonid}')
            ligi_in_list = list(ligi.json())
            leagues_dict = {i['name']: i['id'] for i in ligi_in_list if not i['name'][1].isdigit()}


            league_choice = f'https://slzpn.pl/wp-json/zpn-table/v1/plays?category=MALE&leagueId={leagues_dict[league]}&seasonId={seasonid}'

            league_name = list(requests.get(league_choice).json())[0]

            league_id = league_name['id']
            league_info_results = list(requests.get(f'https://slzpn.pl/wp-json/zpn-table/v1/results?playId={league_id}').json())[::-1]
            league_info_schedules = list(requests.get(f'https://slzpn.pl/wp-json/zpn-table/v1/schedules?playId={league_id}').json())

            for info in league_info_schedules:
                league_info_results.append(info)

            rounds = league_info_results[-1]['queue']

            if update:
                league_obj = LeagueM.objects.filter(name__icontains=league)
                season_obj = SeasonM.objects.filter(league_id=league_obj[0].id, year=2025)
                update_league(league, league_info_results, league_obj, season_obj)
            else:
                json_file = self.create_json_with_league(rounds, league_info_results, spring_round)
                self.json_save(json_file, league)
        else:
            self.stdout.write("You didn`t choose league")

    # def update_league(self, league, league_info_results):
    #     league = "_".join(league.split())
    #     a = 0
    #     with open(f'data/management/commands/matches/{league}_2025_2026.json', 'r', encoding='utf-8') as f:
    #         season = json.load(f)
    #         season.pop(-1) if "".join(list(season[-1].keys())) == 'teams' else season
    #     for round in season:
    #         match_number = 0
    #         for match in round['matches']:
    #             match_day = datetime.strptime(f'{match["Date"]} {match["Time"]}', '%Y-%m-%d %H:%M:%S')
    #             current_day = datetime.now()
    #             if current_day > match_day:
    #                 matches = league_info_results[a]['matches']
    #                 match_score = matches[match_number]
    #
    #                 match_date_db = timezone.make_aware(match_day)
    #                 home_team_obj = TeamM.objects.get(name=match['home_team'])
    #                 away_team_obj = TeamM.objects.get(name=match['away_team'])
    #                 match_obj = MatchM.objects.get(home_team=home_team_obj.id, away_team=away_team_obj.id,
    #                                                date=match_date_db)
    #
    #                 if match_score['scores']:
    #                     match['home_score'] = int(match_score['scores']['fullTime'].split(':')[0])
    #                     match['away_score'] = int(match_score['scores']['fullTime'].split(':')[1])
    #                     match['Date'] = match_score['dateTime'].split('T')[0]
    #                     match['Time'] = match_score['dateTime'].split('T')[1]
    #
    #                     match_obj.home_score = match['home_score']
    #                     match_obj.away_score = match['away_score']
    #                     match_day = datetime.strptime(f'{match["Date"]} {match["Time"]}', '%Y-%m-%d %H:%M:%S')
    #                     match_date_db = timezone.make_aware(match_day)
    #                     match_obj.date = match_date_db
    #                     match_obj.save()
    #
    #             match_number += 1
    #         a += 1
    #
    #     with open(f'data/management/commands/matches/{league}_2025_2026.json', 'w', encoding='utf-8') as f:
    #         json.dump(season, f, ensure_ascii=False, indent=4)

    def create_json_with_league(self, rounds, league_info_results, spring_round):
        json_file = []
        teams = []
        a = 0
        while a < rounds:
            json_file.append({'round': a + 1, 'matches': []})
            matches = league_info_results[a]['matches']
            for match in matches:
                if not match['host']['name'] in teams:
                    teams.append(match['host']['name'])

                if match['scores']:
                    json_file[a]['matches'].append({'home_team': match['host']['name'],
                                                    'home_score': int(match['scores']['fullTime'].split(':')[0]),
                                                    'away_team': match['guest']['name'],
                                                    'away_score': int(match['scores']['fullTime'].split(':')[1]),
                                                    'Date': match['dateTime'].split('T')[0],
                                                    'Time': match['dateTime'].split('T')[1]})
                else:
                    json_file[a]['matches'].append({'home_team': match['host']['name'], 'home_score': None,
                                                    'away_team': match['guest']['name'], 'away_score': None,
                                                    'Date': match['dateTime'].split('T')[0],
                                                    'Time': match['dateTime'].split('T')[1]})
            a += 1
        if spring_round:
            a = rounds * 2
            new_round = 0
            probably_start_league = date(2026, 4, 2)
            while a > rounds:
                json_file.append({'round': (new_round + rounds) + 1, 'matches': []})
                matches = league_info_results[new_round]['matches']
                for match in matches:
                    json_file[new_round + rounds]['matches'].append({'home_team': match['guest']['name'],
                                                                     'home_score': None,
                                                                     'away_team': match['host']['name'],
                                                                     'away_score': None,
                                                                     'Date': probably_start_league.strftime("%Y-%m-%d"),
                                                                     'Time': '16:00:00'})
                probably_start_league = probably_start_league + timedelta(days=7)
                new_round += 1
                a -= 1

        json_file.append({'teams': teams})
        return json_file

    def json_save(self, json_file, league):
        league = "_".join(league.split())
        with open(f'data/management/commands/matches/{league}_2025_2026.json', 'w', encoding='utf-8') as f:
            json.dump(json_file, f, ensure_ascii=False, indent=4)




