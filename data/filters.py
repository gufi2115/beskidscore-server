from django.db.models import Q
import django_filters
from data.models import MatchM, LeagueM



class MatchFilter(django_filters.FilterSet):
    team_id = django_filters.NumberFilter(method='filter_team')
    date = django_filters.DateFilter(
        field_name="date",
        lookup_expr="date"
    )

    class Meta:
        model = MatchM
        fields = ['league_id', 'status', 'date']

    def filter_team(self, queryset, name, value):
        return queryset.filter(
            Q(home_team_id=value) | Q(away_team_id=value)
        )


class LeagueFilter(django_filters.FilterSet):
    league_name = django_filters.CharFilter(method='filter_league_name')

    class Meta:
        model = LeagueM
        fields = []

    def filter_league_name(self, queryset, name, value):
        return queryset.filter(name__icontains=value.replace('_', ' '))