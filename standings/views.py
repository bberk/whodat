from django.core import serializers
from django.http import Http404, HttpResponseServerError
from django.http import HttpResponse

from .espn_utils.refresh_standings import RefreshStandings
from .models import League, Team


def index(request):
    return HttpResponse("Enter the espn league id into the url /standings/<league_id>/")


def get_standings(request, league_id):
    try:
        league = League.objects.get(espn_id=league_id)
    except League.DoesNotExist:
        raise Http404("League {} does not exist".format(league_id))
    divisions = league.division_set.all()
    teams = Team.objects.filter(division__in=divisions).all()
    data = serializers.serialize("jsonl", teams)
    return HttpResponse(data)


def refresh(request, league_id):
    try:
        league = League.objects.get(espn_id=league_id)
        RefreshStandings(league).refresh()
        return HttpResponse("Refreshed league {}".format(league_id))
    except League.DoesNotExist:
        raise Http404("League {} does not exist".format(league_id))
    except Exception:
        raise HttpResponseServerError
