from rest_framework import serializers
from .models import LeagueM, SeasonM, TeamM, RoundM, MatchM, EventM, StandingM, StandingEntryM, CSVLeagueFilesM


class LeagueSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeagueM
        fields = ['id', 'name', 'logo']


class SeasonSerializer(serializers.ModelSerializer):

    class Meta:
        model = SeasonM
        fields = ['id', 'year', 'name', 'league']


class TeamSerializer(serializers.ModelSerializer):

    class Meta:
        model = TeamM
        fields = ['id', 'name', 'logo', 'founded', 'stadium', 'website']


class EventSerializer(serializers.ModelSerializer):

    class Meta:
        model = EventM
        fields = ['id', 'match', 'event_type', 'minute', 'team', 'player_id', 'player_name', 'description']


class MatchSerializer(serializers.ModelSerializer):
    league_read = serializers.CharField(source='league.name', read_only=True)
    round_number_read= serializers.CharField(source='round.round_number', read_only=True)
    home_team = serializers.SerializerMethodField()
    away_team = serializers.SerializerMethodField()

    class Meta:
        model = MatchM
        fields = [
            'id', 'league', 'league_read', 'season', 'round', 'round_number_read', 'home_team', 'away_team',
            'home_score', 'away_score', 'status', 'minute', 'date', 'venue'
        ]

    def get_home_team(self, obj):
        return {
            'id': obj.home_team.id,
            'name': obj.home_team.name,
            'score': obj.home_score
        }

    def get_away_team(self, obj):
        return {
            'id': obj.away_team.id,
            'name': obj.away_team.name,
            'score': obj.away_score
        }


class RoundSerializer(serializers.ModelSerializer):
    league_read = serializers.CharField(source='league.name', read_only=True)
    matches = MatchSerializer(many=True, read_only=True)
    season_read = serializers.CharField(source='season.year', read_only=True)

    class Meta:
        model = RoundM
        fields = ['id', 'league', 'league_read', 'season', 'season_read',
                  'round_number', 'name', 'start_date', 'end_date', 'matches']


class StandingEntrySerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(source='team.name', read_only=True)

    class Meta:
        model = StandingEntryM
        fields = [
            'position', 'team', 'team_name', 'played', 'won', 'drawn', 'lost',
            'goals_for', 'goals_against', 'goal_difference', 'points'
        ]


class StandingSerializer(serializers.ModelSerializer):
    league_read = serializers.CharField(source='league.name', read_only=True)
    table = StandingEntrySerializer(many=True, read_only=True)
    promotion_number = serializers.IntegerField(source='season.promotion_number', read_only=True)
    playoffs_number = serializers.IntegerField(source='season.playoffs_number', read_only=True)
    relegation_number = serializers.IntegerField(source='season.relegation_number', read_only=True)


    class Meta:
        model = StandingM
        fields = ['id', 'league', 'league_read', 'promotion_number', 'playoffs_number',
                  'relegation_number', 'season', 'table']


class CSVFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CSVLeagueFilesM
        fields = ['id', 'CSV', 'league', 'season']