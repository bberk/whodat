from django.db import models


class League(models.Model):
    espn_id = models.IntegerField()
    espn_s2 = models.CharField(max_length=300, null=True)
    swid = models.CharField(max_length=100, null=True)
    league_year = models.IntegerField(default=2021)
    current_week = models.IntegerField()
    nfl_week = models.IntegerField()
    updated_at = models.DateTimeField()

    def __str__(self):
        return f"ESPN League: {self.espn_id}"


class Division(models.Model):
    espn_id = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    league = models.ForeignKey(League, on_delete=models.CASCADE)

    def __str__(self):
        return f"Division: {self.name}"


class Team(models.Model):
    division = models.ForeignKey(Division, on_delete=models.CASCADE)
    espn_id = models.IntegerField()
    name = models.CharField(max_length=200)
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    victory_points = models.IntegerField(default=0)
    points_for = models.FloatField(default=0)

    def __str__(self):
        return self.name


class Matchup(models.Model):
    week = models.IntegerField()
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_team')
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_team')
    home_score = models.FloatField()
    away_score = models.FloatField()

    def __str__(self):
        return f"Matchup wk {self.week}: " \
               f"{self.away_team} {self.away_score} @ {self.home_score} {self.home_team}"
