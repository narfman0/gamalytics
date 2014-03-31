from django.test import TestCase
from gamalytics.models import Game,Rating
from ratingCache import RatingCache
from django.utils import timezone
from gamalytics.scraper.metacriticScraper import getMetacriticScore
import unittest

class RatingCacheTest(TestCase):
  def setUp(self):
    Game.objects.create(name='testgame',
        metacritic='http://metacritic.com',
        gametrailersReviewURL='http://gametrailers.com',
        gametrailersVideo='http://gametrailers.com',
        description='description',released=timezone.now(),
        lastUpdated=timezone.now())
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

  def test_metacritic_parser(self):
    url='http://www.metacritic.com/game/xbox-360/dead-or-alive-4'
    scores=getMetacriticScore(url)
    self.assertEqual(len(scores),4)
    self.assertTrue(scores[0] > 60 and scores[0] < 90)
    self.assertTrue(scores[1] > 6 and scores[1] < 9)

if __name__ == "__main__":
    unittest.main()