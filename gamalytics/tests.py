from django.test import TestCase
from gamalytics.models import Game,Rating
from ratingCache import RatingCache
from django.utils import timezone

class RatingCacheTest(TestCase):
  def setUp(self):
    Game.objects.create(name='testgame',
        metacritic='http://metacritic.com',
        gametrailers='http://gametrailers.com',
        description='description',released=timezone.now())
    Rating.objects.create(username='username',game_id='1',
        tag='pc',value=100,time=timezone.now())

  def test_rating_cache_initial(self):
    cache=RatingCache(True)
    tags=cache.getGameTagsAveraged('testgame')
    for tag,value in tags:
      self.assertEqual(tag,'pc')
      self.assertEqual(value,100)

  def test_rating_cache_add_rating(self):
    Rating.objects.create(username='username2',game_id='1',
        tag='pc',value=0,time=timezone.now())
    cache=RatingCache(True)
    tags=cache.getGameTagsAveraged('testgame')
    for tag,value in tags:
      self.assertEqual(tag,'pc')
      self.assertEqual(value,50)
