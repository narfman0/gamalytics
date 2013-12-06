from datetime import datetime
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

class Game(models.Model):
    gamename = models.CharField(db_index=True, max_length=100)
    metacritic = models.URLField()
    gametrailers = models.URLField()
    description = models.TextField()
    released = models.DateTimeField(db_index=True, default=datetime.now)

class Rating(models.Model):
    username = models.CharField(db_index=True, max_length=100)
    game = models.ForeignKey(Game)
    tag = models.CharField(db_index=True, max_length=100)
    value = models.FloatField(db_index=True, validators = [MinValueValidator(0), MaxValueValidator(100)],default=50)
    time = models.DateTimeField(default=datetime.now)
