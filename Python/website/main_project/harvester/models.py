from django.db import models


class Team(models.Model):
    name = models.CharField(max_length=255)
    head_coach = models.CharField(max_length=255)
    region = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Player(models.Model):
    name = models.CharField(max_length=255)
    position = models.CharField(max_length=10)
    height = models.FloatField()
    weight = models.FloatField()
    birth_date = models.DateField()
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Game(models.Model):
    date = models.DateField()
    home_team = models.ForeignKey(Team, related_name='home_team', on_delete=models.CASCADE)
    away_team = models.ForeignKey(Team, related_name='away_team', on_delete=models.CASCADE)
    location = models.CharField(max_length=255)


    def __str__(self):
        return f"{self.home_team} vs {self.away_team} on {self.date}"


class GameStatistics(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    MP = models.IntegerField()
    FG = models.IntegerField()
    FGA = models.IntegerField()
    FG_percentage = models.FloatField()
    ThreeP = models.IntegerField()
    ThreePA = models.IntegerField()
    ThreeP_percentage = models.FloatField()
    FT = models.IntegerField()
    FTA = models.IntegerField()
    FT_percentage = models.FloatField()
    ORB = models.IntegerField()
    DRB = models.IntegerField()
    TRB = models.IntegerField()
    AST = models.IntegerField()
    STL = models.IntegerField()
    BLK = models.IntegerField()
    TOV = models.IntegerField()
    PF = models.IntegerField()
    PTS = models.IntegerField()
    plus_minus = models.IntegerField()
    BPM = models.IntegerField()

    def __str__(self):
        return f"Statistics of {self.player} in the game {self.game}"
