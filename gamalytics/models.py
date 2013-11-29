from datetime import datetime
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

class User(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    joined = models.DateTimeField(default=datetime.now)

class Game(models.Model):
    gamename = models.CharField(max_length=100)
    metacritic = models.URLField()
    gametrailers = models.URLField()
    description = models.TextField()
    released = models.DateTimeField(default=datetime.now)

class Rating(models.Model):
    username = models.CharField(max_length=100)
    game = models.ForeignKey(Game)
    tag = models.CharField(max_length=100)
    value = models.FloatField(validators = [MinValueValidator(0), MaxValueValidator(100)],default=50)
    time = models.DateTimeField(default=datetime.now)
