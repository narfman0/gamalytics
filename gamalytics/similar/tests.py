import unittest
from gamalytics.ratingCache import RatingCache
from gamalytics.similar.similar import createTree, getSimilar, createRatingMap

class Test(unittest.TestCase):
    def setUp(self):
        pass

    def test_similarity(self):
        cache=RatingCache(False)
        ratingMap=createRatingMap()
        tree=createTree(cache, ratingMap)
        print(getSimilar('testgame1', tree, cache, ratingMap))

if __name__ == "__main__":
    unittest.main()