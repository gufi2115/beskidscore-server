from django_cron import CronJobBase, Schedule
import logging
from django.core.management import call_command
from django.utils import timezone
from django.utils.timezone import make_aware, get_current_timezone
import json
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta, tzinfo
from .models import MatchM, TeamM, LeagueM, SeasonM, StandingM, StandingEntryM

logger = logging.getLogger(__name__)

class SetMatchToLiveCronJob(CronJobBase):
    # */5 * * * * /path/to/your/venv/bin/python /path/to/your/project/manage.py runcrons >> /tmp/cron.log 2>&1
    """
    Cron job to set matches to live status.
    Runs every minute.
    """
    RUN_EVERY_MINS = 1  # Run every minute

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'data.set_match_to_live_cron_job'  # Unique identifier for the cron job

    def do(self):
        now = datetime.now()
        match_start_low_tolerance = make_aware((now - timedelta(minutes=2)))
        match_start_tolerance = now + timedelta(minutes=4)
        mk_match_start_tolerance = make_aware(match_start_tolerance)
        matches = MatchM.objects.filter(status='SCHEDULED', date__gte=match_start_low_tolerance, date__lte=mk_match_start_tolerance)

        for match in matches:
            match.status = 'LIVE'
            match.home_score = 0
            match.away_score = 0
            match.save()

            print(f"Match {match.id} set to LIVE status.")


class UpdateStandingsCronJob(CronJobBase):
    """
    Cron job to update standings.
    Runs every hour.
    """
    RUN_EVERY_HOUR = 60  # Run every hour

    schedule = Schedule(run_every_mins=RUN_EVERY_HOUR)
    code = 'data.update_standings_cron_job'  # Unique identifier for the cron job

    def do(self):
        league_obj = LeagueM.objects.all()
        try:
            for league in league_obj:
                season_obj = SeasonM.objects.get(league=league.id, year=2025)
                update_standings= call_command('update_standings', league=league.id, season=season_obj.id)
        except Exception as e:
            logger.error(f'Update Standings error: {e}')
        return logger.info(f'Standings update successfully')


class UpdateResultsCronJob(CronJobBase):
    """
        Cron job to update results.
        Runs every hour.
    """
    RUN_EVERY_HOUR = 60
    schedule = Schedule(run_every_mins=RUN_EVERY_HOUR)
    code = 'data.update_results_cron_job'

    def do(self):
        leagues = ['Klasa B', 'Klasa A', 'Klasa okręgowa'][::-1]
        try:
            for league in leagues:
                update_league = call_command('slzpn_fetch', league=league, update=True, verbosity=1)
        except Exception as e:
            logger.error(f"Error updating results: {e}")
            return
        logger.info("Results updated successfully.")


class SetStatusToFinishedCronJob(CronJobBase):
    """
        Cron job to set status to finished.
    """
    RUN_EVERY_HALF_HOUR = 30
    schedule = Schedule(run_every_mins=RUN_EVERY_HALF_HOUR)
    code = 'data.set_status_to_finished_cron_job'
    def do(self):
        now = timezone.now()
        predict_match_end = now - timedelta(minutes=120)
        match_obj = MatchM.objects.filter(status='LIVE', date__lte=predict_match_end)

        for match in match_obj:
            match.status = 'FINISHED'
            match.save()