from django.db import transaction
from django.core.management.base import BaseCommand
from data.models import LeagueM, SeasonM, TeamM, RoundM, MatchM
import json
import os
from datetime import datetime
from django.utils.timezone import make_aware

class Command(BaseCommand):
    help = 'Adds a league from a JSON file'

    def handle(self, *args, **options):
        current_dir = os.path.dirname(__file__)
        json_path = os.path.join(current_dir, 'matches/Klasa_B_2025_2026.json')

        with open(json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        with transaction.atomic():
            league = LeagueM.objects.get(name='B Klasa Bielsko-Biała')
            season = SeasonM.objects.get(year='2025', name='2025/2026', season_years='2025/2026', league=league)

            for round_info in data:
                round_name = round_info["round"]
                current_round_number = round_info["round"]
                current_round_name = f"Kolejka {round_info['round']}"
                print(current_round_name)
                if isinstance(round_info['round'], int):
                    round_obj = RoundM.objects.create(round_number=current_round_number, name=current_round_name, league=league, season=season)
                else:
                    round_number = int(round_name.split()[1])
                    round_obj = RoundM.objects.create(round_number=round_number, name=round_name, league=league,
                                                      season=season,)
                print(current_round_name)
                for match in round_info["matches"]:
                    print(match["home_team"])
                    home_team_obj = TeamM.objects.get(name=match["home_team"])
                    away_team_obj = TeamM.objects.get(name=match["away_team"])

                    if match['Date'] and match['Time']:
                        dateTime_str = f'{match["Date"]} {match["Time"]}'
                        dateTime = datetime.strptime(dateTime_str, '%Y-%m-%d %H:%M:%S')
                        dT_local = make_aware(dateTime)
                        match_day = datetime.strptime(dateTime_str.split()[0], '%Y-%m-%d')
                        today = dateTime.now()

                        if match['home_score'] is None and match['away_score'] is None:
                            match['home_score'], match['away_score'] = None, None

                        match_obj = MatchM.objects.create(round=round_obj, league=league, season=season,
                                                         home_team=home_team_obj, away_team=away_team_obj,
                                                         home_score=match["home_score"], away_score=match["away_score"], date=dT_local,
                                                         )
                        if today < match_day:
                            match_obj.status = 'SCHEDULED'
                            match_obj.save()
                        elif today > match_day:
                            match_obj.status = 'FINISHED'
                            match_obj.save()


                    else:
                        match_obj = MatchM.objects.create(round=round_obj, league=league, season=season,
                                                          home_team=home_team_obj, away_team=away_team_obj,
                                                          home_score=match["home_score"], away_score=match["away_score"],
                                                          status='FINISHED', )



