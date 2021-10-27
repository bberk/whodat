from django.db import models


class League(models.Model):
    espn_id = models.CharField(max_length=200)
    current_week = models.IntegerField()
    nfl_week = models.IntegerField()
    updated_at = models.DateTimeField()


class Division(models.Model):
    espn_id = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    league = models.ForeignKey(League, on_delete=models.CASCADE)


class Team(models.Model):
    division = models.ForeignKey(Division, on_delete=models.CASCADE)
    espn_id = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    wins = models.IntegerField()
    losses = models.IntegerField()
    victory_points = models.IntegerField()
    points_for = models.FloatField()
