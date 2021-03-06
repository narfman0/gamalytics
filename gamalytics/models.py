from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

class Game(models.Model):
    name = models.CharField(db_index=True, max_length=100)
    metacritic = models.URLField()
    gametrailersReviewURL = models.URLField()
    gametrailersVideo = models.URLField()
    description = models.TextField()
    released = models.DateTimeField(db_index=True, default=timezone.now())
    lastUpdated = models.DateTimeField(default=timezone.now())
    def __unicode__(self):
      return '[Game: name=' + self.name + ']'

class Rating(models.Model):
    username = models.CharField(db_index=True, max_length=100)
    game = models.ForeignKey(Game)
    tag = models.CharField(db_index=True, max_length=100)
    value = models.FloatField(db_index=True, validators = [MinValueValidator(0), MaxValueValidator(100)],default=50)
    time = models.DateTimeField(default=timezone.now())
    def __unicode__(self):
      return '[Rating: tag=' + self.tag + ' value=' + str(value) + ']'