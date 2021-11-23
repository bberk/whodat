from django.contrib import admin

from django.contrib import admin

from .models import League, Division, Team, Matchup

admin.site.register(League)
admin.site.register(Division)
admin.site.register(Team)
admin.site.register(Matchup)
