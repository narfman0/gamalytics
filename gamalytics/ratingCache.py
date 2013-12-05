#This will manage the tag cache for ratings. Every time it is changed
#for a game, e.g. a rating is added, removed, or changed, it will update
#for that game since we assume more reads than writes.
from gamalytics.models import Game,Rating
from django.core.cache import cache
from hashlib import md5

CACHE_DURATION=60*60*24

class RatingCache:
  #prepopulate - if true, calculate all games at startup
  def __init__(self, prepopulate):
    if prepopulate:
      count=Game.objects.all().count()
      current=1.0
      for game in Game.objects.all():
        cache.set(self.getKey(game.gamename), self.calculateGameAveragedTags(game.gamename), CACHE_DURATION)
        print('Cache '+str(100*current/count) + '% done, finished '+game.gamename)
        current += 1

  def getKey(self,gamename):
    return md5(gamename).hexdigest()

  def calculateGameAveragedTags(self, gamename):
    ratingMap={}
    for rating in Rating.objects.filter(game__gamename__iexact=gamename):
      s=ratingMap.get(rating.tag,[])
      s.append(rating.value)
      ratingMap[rating.tag]=s
    ratings={}
    for k,v in ratingMap.items():
      ratings[k]=sum(v)/len(v)
    return sorted(ratings.items(), key=lambda x: x[1], reverse=True)

  def getGameTagsAveraged(self, gamename):
    key=self.getKey(gamename)
    result=cache.get(key)
    if result is None:
      result=self.calculateGameAveragedTags(gamename)
      cache.set(key,result,CACHE_DURATION)
    return result
