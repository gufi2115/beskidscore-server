from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator


class LeagueM(models.Model):
    name = models.CharField(max_length=100)
    logo = models.CharField(max_length=200, blank=True)
    additional_info = models.CharField(max_length=1000, blank=True, null=True)

    def __str__(self):
        return self.name


class SeasonM(models.Model):
    year = models.CharField(max_length=10)
    season_years = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255)
    league = models.ForeignKey(LeagueM, on_delete=models.CASCADE, related_name='seasons')
    extra_info = models.CharField(max_length=1000, blank=True, null=True)
    promotion_number = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    playoffs_number = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    relegation_number = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    def __str__(self):
        return f"{self.league.name} - {self.name}"


class TeamM(models.Model):
    name = models.CharField(max_length=100)
    logo = models.CharField(max_length=200, blank=True)
    founded = models.IntegerField(null=True, blank=True)
    stadium = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)

    def __str__(self):
        return self.name


class RoundM(models.Model):
    league = models.ForeignKey(LeagueM, on_delete=models.CASCADE, related_name='rounds')
    season = models.ForeignKey(SeasonM, on_delete=models.CASCADE, related_name='rounds')
    round_number = models.IntegerField()
    name = models.CharField(max_length=50)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.league.name} - {self.name}"


class MatchM(models.Model):
    """Match/Fixture model"""
    STATUS_CHOICES = [
        ('LIVE', 'Live'),
        ('FINISHED', 'Finished'),
        ('SCHEDULED', 'Scheduled'),
        ('POSTPONED', 'Postponed'),
        ('CANCELLED', 'Cancelled'),
    ]

    league = models.ForeignKey(LeagueM, on_delete=models.CASCADE, related_name='matches')
    season = models.ForeignKey(SeasonM, on_delete=models.CASCADE, related_name='matches')
    round = models.ForeignKey(RoundM, on_delete=models.CASCADE, related_name='matches', null=True, blank=True)

    home_team = models.ForeignKey(TeamM, on_delete=models.CASCADE, related_name='home_matches')
    away_team = models.ForeignKey(TeamM, on_delete=models.CASCADE, related_name='away_matches')

    home_score = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0)])
    away_score = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0)])

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='SCHEDULED')
    minute = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(120)])

    date = models.DateTimeField(blank=True, null=True)
    venue = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.home_team.name} vs {self.away_team.name}"


class EventM(models.Model):
    EVENT_TYPES = [
        ('GOAL', 'Goal'),
        ('YELLOW_CARD', 'Yellow Card'),
        ('RED_CARD', 'Red Card'),
        ('SUBSTITUTION', 'Substitution'),
        ('PENALTY', 'Penalty'),
        ('OWN_GOAL', 'Own Goal'),
    ]

    match = models.ForeignKey(MatchM, on_delete=models.CASCADE, related_name='events')
    team = models.ForeignKey(TeamM, on_delete=models.CASCADE, related_name='events')

    event_type = models.CharField(max_length=15, choices=EVENT_TYPES)
    minute = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(120)])

    player_id = models.CharField(max_length=20, blank=True)
    player_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.match} - {self.event_type} by {self.player_name}"


class StandingM(models.Model):
    league = models.ForeignKey(LeagueM, on_delete=models.CASCADE, related_name='standings')
    season = models.ForeignKey(SeasonM, on_delete=models.CASCADE, related_name='standings')

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.league.name} - {self.season.name} Standings"


class StandingEntryM(models.Model):
    standing = models.ForeignKey(StandingM, on_delete=models.CASCADE, related_name='table')
    team = models.ForeignKey(TeamM, on_delete=models.CASCADE)

    position = models.IntegerField(validators=[MinValueValidator(1)])
    played = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    won = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    drawn = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    lost = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    goals_for = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    goals_against = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    goal_difference = models.IntegerField(default=0)
    points = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    def save(self, *args, **kwargs):
        self.goal_difference = self.goals_for - self.goals_against
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.position}. {self.team.name} - {self.points} pts"

    class Meta:
        unique_together = ['standing', 'team']


class CSVLeagueFilesM(models.Model):
    CSV = models.FileField(validators=[FileExtensionValidator(allowed_extensions=['csv'])])
    processed = models.BooleanField(default=False)

    season = models.ForeignKey(SeasonM, on_delete=models.CASCADE, related_name='season')
    league = models.ForeignKey(LeagueM, on_delete=models.CASCADE, related_name='league')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.league.name} - {self.season.name}"