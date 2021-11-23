from django.core import serializers
from django.http import Http404, HttpResponseServerError
from django.http import HttpResponse

from .espn_utils.refresh_standings import RefreshStandings
from .models import League, Team, Matchup


def index(request):
    return HttpResponse("Enter the espn league id into the url /<league_id>")


def get_league(request, league_id):
    return HttpResponse("Nothing to see here")


def get_results(request, league_id):
    try:
        results = Matchup.objects.filter(home_team__division__league__espn_id=league_id)
        data = serializers.serialize("jsonl", results)
        return HttpResponse(data)
    except Exception:
        raise HttpResponseServerError


def get_teams(request, league_id):
    try:
        teams = Team.objects.filter(division__league__espn_id=league_id).all()
        data = serializers.serialize("jsonl", teams)
        return HttpResponse(data)
    except League.DoesNotExist:
        raise Http404("League {} does not exist".format(league_id))


def refresh(request, league_id):
    """Refreshes/populates all teams & matchups"""
    try:
        league = League.objects.get(espn_id=league_id)
        RefreshStandings(league).refresh()
        return HttpResponse("Refreshed league {}".format(league_id))
    except League.DoesNotExist:
        raise Http404("League {} does not exist".format(league_id))
    except Exception:
        raise HttpResponseServerError
