import json
from data.models import MatchM, TeamM, RoundM
from django.contrib.postgres.search import TrigramSimilarity
import pandas
from django.db import transaction
from django.utils import timezone
from datetime import datetime



def update_league(league, league_info_results, league_obj, season_obj):
    league = "_".join(league.split())
    a = 0
    with open(f'data/management/commands/matches/{league}_2025_2026.json', 'r', encoding='utf-8') as f:
        season = json.load(f)
        season.pop(-1) if "".join(list(season[-1].keys())) == 'teams' else season
    for round in season:
        match_number = 0
        for match in round['matches']:
            match_day = datetime.strptime(f'{match["Date"]} {match["Time"]}', '%Y-%m-%d %H:%M:%S')
            current_day = datetime.now()
            if a < len(league_info_results):
                matches = league_info_results[a]['matches']
                match_score = matches[match_number]

                round_obj = RoundM.objects.get(round_number=match_score['queue'], league_id=league_obj[0].id, season_id=season_obj[0].id)
                matches_obj = MatchM.objects.filter(league_id=league_obj[0].id, season_id=season_obj[0].id,
                                               round_id=round_obj.id)

                match_obj = matches_obj.annotate(similarity=TrigramSimilarity('home_team__name', match_score['host']['name'])).filter(similarity__gt=0.5).order_by('-similarity').first()
                if not match_obj:
                    match_obj = matches_obj.annotate(similarity=TrigramSimilarity('home_team__name', match_score['guest']['name'])).filter(similarity__gt=0.5).order_by('-similarity').first()
                match_day_in_db = match_obj.date
                match_day_in_slzpn = timezone.make_aware(datetime.strptime(" ".join(match_score['dateTime'].split('T')), '%Y-%m-%d %H:%M:%S'))

                if current_day > match_day or match_day_in_db != match_day_in_slzpn:
                    if match_score['scores']:
                        match['home_score'] = int(match_score['scores']['fullTime'].split(':')[0])
                        match['away_score'] = int(match_score['scores']['fullTime'].split(':')[1])

                        match_obj.status = 'FINISHED'
                        match_obj.home_score = int(match_score['scores']['fullTime'].split(':')[0])
                        match_obj.away_score = int(match_score['scores']['fullTime'].split(':')[1])

                    match['home_team'] = match_obj.home_team.name
                    match['away_team'] = match_obj.away_team.name
                    match['Date'] = match_score['dateTime'].split('T')[0]
                    match['Time'] = match_score['dateTime'].split('T')[1]
                    match_day = datetime.strptime(f'{match["Date"]} {match["Time"]}', '%Y-%m-%d %H:%M:%S')
                    match_date_db = timezone.make_aware(match_day)
                    match_obj.date = match_date_db
                    match_obj.save()

            match_number += 1
        a += 1

    with open(f'data/management/commands/matches/{league}_2025_2026.json', 'w', encoding='utf-8') as f:
        json.dump(season, f, ensure_ascii=False, indent=4)


def teams_creator(teams_import):
    team_dict = {}
    teams_from_database = TeamM.objects.all()
    for import_team in teams_import:
        team_an = teams_from_database.annotate(similarity=TrigramSimilarity('name', import_team)).filter(
            similarity__gt=0.5).order_by('-similarity')
        if not team_an:
            team_obj = TeamM.objects.create(name=import_team)
            team_dict[import_team] = team_obj.name
        else:
            teams_in_db = team_an.values_list('name', flat=True)
            f_team = 0
            s_team = 0
            t_team = 0
            len_team_before = len(team_dict)
            for team_db in teams_in_db:
                which_team = team_db.split()[-1]
                if 'II' != which_team and 'II' in import_team:
                    s_team += 1
                elif 'II' in which_team and not 'II' in import_team:
                    f_team += 1
                elif 'III' != which_team and 'III' in import_team:
                    t_team += 1
                if len(teams_in_db) == f_team:
                    new_team = TeamM.objects.create(name=" ".join(team_db.split()[:-1]))
                    team_dict[import_team] = new_team.name
                elif len(teams_in_db) == s_team or len(teams_in_db) == t_team:
                    s_or_t_team = [team_number for team_number in import_team.split() if 'II' in team_number][0]
                    name = team_db.strip('I') + s_or_t_team
                    new_team = TeamM.objects.create(name=name)
                    team_dict[import_team] = new_team.name
            len_team_after = len(team_dict)
            if len_team_before == len_team_after:
                team_dict[import_team] = team_an[0]

    return team_dict


def columns_validator(columns_names):
    possibilities = {
        "Data": [
            "data", "date", "match_date", "data_meczu", "data meczu", "matchdate",
            "game_date", "gamedate", "matchday", "datum", "czas", "czas_meczu",
            "data_i_godzina", "datamatch", "match_time", "datetime", "game_time"
        ],
        "Gospodarze": [
            "gospodarze", "gospodarz", "home", "home_team", "home team", "hometeam",
            "druzyna_a", "drużyna a", "team1", "team_1", "team a", "dom", "gospodarzy",
            "zespol_a", "zespół a", "1st_team", "first_team", "host", "hosts",
            "home_side", "gospodarze_domowi", "gospodarze_dom", "domowa_drużyna", "pierwszy zespół"
        ],
        "Goście": [
            "goscie", "goście", "gosc", "away", "away_team", "away team", "awayteam",
            "druzyna_b", "drużyna b", "team2", "team_2", "team b", "wyjazd", "gość",
            "przyjezdni", "visitors", "visitor", "zespol_b", "zespół b", "2nd_team",
            "second_team", "away_side", "goscie_wyjazdowi", "drugi zespół"
        ],
        "Wynik": [
            "wynik", "score", "result", "wynik_meczu", "final_score", "finalscore",
            "goals", "wynik_koncowy", "resultat", "score_final", "ft", "full_time",
            "fulltime", "ft_score", "wynik_ft", "goals_home", "goals_away", "rezultat",
            "wynik_90min", "wynik_po_90", "koncowy_wynik"
        ],

        "Kolejka": [
            "kolejka", "kolejka_nr", "nr_kolejki", "kolejka_nr", "round", "matchday",
            "match_day", "gameweek", "gw", "kolejka ligowa", "runda", "numer_kolejki",
            "kolejka numer", "week", "spieltag", "jornada", "giornata", "queue",
            "kolejka_pucharowa", "turniej_kolejka", "etap", "numer kolejki"
        ]
    }

    good_name_list = []
    bad_name = 0
    for column_name in columns_names:
        for name, possibilities_name in possibilities.items():
            column_name = column_name.strip()
            if name == column_name.capitalize() or column_name.lower() in possibilities_name:
                good_name_list.append(name)
            else:
                continue

    if len(good_name_list) == len(columns_names):
        return good_name_list

    return None


class ProcessLeagueCSV:
    def __init__(self, task):
        self.task = task

    def run(self):
        task = self.task
        file_obj = task.file_id
        dr = pandas.read_csv(file_obj.CSV)
        columns_names = list(dr.columns)
        columns = columns_validator(columns_names)
        if columns:
            teams = []
            dr.columns = columns
            for team in list(dr.Gospodarze):
                if not team.upper() in teams:
                    teams.append(team.upper())
            team_validate = teams_creator(teams)
            for i in dr.itertuples(index=False):
                home_team = i.Gospodarze.upper()
                away_team = i.Goście.upper()
                result = i.Wynik.split([r for r in i.Wynik if not r.isdecimal()][0])
                home_team_obj = team_validate[home_team]
                away_team_obj = team_validate[away_team]
                match_day_csv = datetime.strptime(i.Data, '%Y-%m-%d %H:%M')
                match_day_db = timezone.make_aware(match_day_csv)
                if match_day_db > timezone.now():
                    status = 'SCHEDULED'
                else:
                    status = 'FINISHED'
                with transaction.atomic():
                    round_obj, created = RoundM.objects.get_or_create(round_number=i.Kolejka, name=f'Kolejka {i.Kolejka}',
                                                                      league=file_obj.league, season=file_obj.season)
                    match_obj = MatchM.objects.create(home_score=int(result[0]), away_score=int(result[1]), date=match_day_db,
                                                      status=status, home_team=home_team_obj, away_team=away_team_obj,
                                                      league=file_obj.league, season=file_obj.season, round=round_obj)
            task.status = 'COMPLETED'
            task.save()
        else:
            task.status = 'FAILED'
            task.error_name = 'Yours columns are bad'
            task.save()