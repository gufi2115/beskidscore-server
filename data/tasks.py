# from celery import shared_task
# from .models import MatchM
# from django.utils import timezone
# from datetime import timedelta
# from django.core.management import call_command
#
#
# @shared_task
# def update_standings_live():
#     now = timezone.now()
#     minute_earlier = now - timedelta(minutes=1)
#     match_obj = MatchM.objects.filter(status='LIVE', updated_at__gte=minute_earlier)
#     for match in match_obj:
#         call_command('update_standings', league=match.league_id, season=match.season_id)