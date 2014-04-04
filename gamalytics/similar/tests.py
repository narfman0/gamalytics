from gamalytics.ratingCache import RatingCache
from gamalytics.models import Game, Rating
from django.utils import timezone, unittest
from gamalytics.similar import similarBrute, similarKDTree

class Test(unittest.TestCase):
    def setUp(self):
        for i in range(0,3):
            Game.objects.create(name='testgame'+str(i),
                metacritic='http://metacritic.com',
                gametrailersReviewURL='http://gametrailers.com',
                gametrailersVideo='http://gametrailers.com',
                description='description',released=timezone.now(),
                lastUpdated=timezone.now())
            Rating.objects.create(username='username',game_id=str(Game.objects.count()),
                tag='pc',value=100,time=timezone.now())
            Rating.objects.create(username='username',game_id=str(Game.objects.count()),
                tag='role-playing',value=100,time=timezone.now())
        Game.objects.create(name='testgame3',
            metacritic='http://metacritic.com',
            gametrailersReviewURL='http://gametrailers.com',
            gametrailersVideo='http://gametrailers.com',
            description='description',released=timezone.now(),
            lastUpdated=timezone.now())
        Rating.objects.create(username='username',game_id=str(Game.objects.count()),
            tag='pc',value=50,time=timezone.now())
        Rating.objects.create(username='username',game_id=str(Game.objects.count()),
            tag='role-playing',value=50,time=timezone.now())
    
    def tearDown(self):
        Game.objects.filter(name__startswith='testgame').delete()
        Rating.objects.filter(username__iexact='username').delete()

    def testSimilarBrute(self):
        cache=RatingCache(False)
        distinctTags=Rating.objects.values_list('tag', flat=True).distinct()
        self.assertEqual(1.0, similarBrute.calculateSimilarity('testgame1', 'testgame2', cache, distinctTags))
        self.assertEqual(0.5, similarBrute.calculateSimilarity('testgame1', 'testgame3', cache, distinctTags))

    def testSimilarKDTree(self):
        _ratingCache=RatingCache(False)
        #similarKDTree.getSimilar('testgame1', _ratingCache, None)

if __name__ == "__main__":
    unittest.main()