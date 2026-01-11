from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django_ratelimit.decorators import ratelimit
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import filters
from .fb_client import send_message
from django.db import transaction

from tasks.models import ProcessedTasksM
from .models import LeagueM, SeasonM, TeamM, RoundM, MatchM, StandingM, CSVLeagueFilesM
from .serializers import (
    LeagueSerializer, SeasonSerializer, TeamSerializer, RoundSerializer,
    MatchSerializer, EventSerializer, StandingSerializer, CSVFileSerializer,
)
from rest_framework import mixins, viewsets
from django_filters.rest_framework import DjangoFilterBackend
from data.filters import MatchFilter, LeagueFilter



class HealthCheckView(APIView):
    """Health check endpoint"""

    def get(self, request):
        return Response({
            'status': 'OK',
            'message': 'FlashScore Django API is running'
        })


class LeagueViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = LeagueM.objects.all()
    serializer_class = LeagueSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = LeagueFilter


class TeamViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = TeamM.objects.all()
    serializer_class = TeamSerializer


class MatchViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = MatchM.objects.all()
    serializer_class = MatchSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = MatchFilter

    @action(detail=True, methods=['get'])
    def events(self, request, pk=None):
        match = self.get_object()
        events = match.events.all()
        serializer = EventSerializer(events, many=True)
        return Response('siema')


class StandingViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = StandingM.objects.all()
    serializer_class = StandingSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['league', 'season']


class RoundViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = RoundM.objects.all()
    serializer_class = RoundSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['league', 'season', 'season__year']
    ordering_fields = ['round_number']
    ordering = ['round_number']



class SeasonViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = SeasonM.objects.all()
    serializer_class = SeasonSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['league']

@ratelimit(key='ip', rate='6/m', block=True)
def update_match(request, match_id=None):
    match = get_object_or_404(MatchM, pk=match_id)
    if match.status == 'LIVE':
        if request.method == "POST":
            home_score = request.POST.get('home_score')
            away_score = request.POST.get('away_score')
            match.home_score = home_score
            match.away_score = away_score
            match.save()
            return render(request, 'update_match.html', {'match': match, 'success': True})
        return render(request, 'update_match.html', {'match': match})
    return HttpResponse("Match is not live", status=403)

#
# FB_VERIFY_TOKEN = settings.FB_VERIFY_TOKEN
#
# class MessengerWebhookView(APIView):
#     authentication_classes = []
#     permission_classes = []
#
#     def get(self, request):
#         verify_token = request.GET.get("hub.verify_token")
#         challenge = request.GET.get("hub.challenge")
#
#         if verify_token == FB_VERIFY_TOKEN:
#             return HttpResponse(challenge)
#
#         return HttpResponse("Invalid verification token", status=403)
#
#     def post(self, request):
#         data = request.data
#
#         for entry in data.get("entry", []):
#             for messaging in entry.get("messaging", []):
#                 sender_id = messaging["sender"]["id"]
#
#                 if "message" in messaging and "text" in messaging["message"]:
#                     live_matches = MatchM.objects.filter(status="LIVE")
#                     matches = [
#                         {
#                             "id": match.id,
#                             "match": f"{match.home_team.name} vs {match.away_team.name}",
#                         }
#                         for match in live_matches
#                     ]
#
#                     buttons = [
#                         {
#                             "type": "web_url",
#                             "url": f"https://api.beskidscore.pl/api/update_match/{match['id']}/",
#                             "title": match["match"],
#                             "webview_height_ratio": "compact",
#                             # "messenger_extensions": "true",
#                         }
#                         for match in matches
#                     ]
#
#                     send_message(sender_id, buttons)
#
#         return Response({"status": "ok"})


class CSVFileViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = CSVLeagueFilesM.objects.all()
    serializer_class = CSVFileSerializer

    def perform_create(self, serializer):
        file = serializer.save()
        admin = self.request.user
        with transaction.atomic():
            ProcessedTasksM.objects.create(task_name='process_csv_league', admin=admin, file_id=file)