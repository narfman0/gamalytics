#This will manage the tag cache for ratings. Every time it is changed
#for a game, e.g. a rating is added, removed, or changed, it will update
#for that game since we assume more reads than writes.
from gamalytics.models import Game,Rating
from django.core.cache import cache
from hashlib import md5

class RatingCache:
  #prepopulate - if true, calculate all games at startup
  def __init__(self, prepopulate):
    if prepopulate:
      count=Game.objects.all().count()
      current=1.0
      for game in Game.objects.all():
        tags=self.calculateGameAveragedTags(game.name)
        cache.set(self.getKey(game.name), tags, 0)
        print('Cache '+str(100*current/count) + '% done, finished '+game.name)
        current += 1

  def getKey(self,name):
    return md5(name).hexdigest()

  def calculateGameAveragedTags(self, name):
    ratingMap={}
    for rating in Rating.objects.filter(game__name__iexact=name):
      s=ratingMap.get(rating.tag,[])
      s.append(rating.value)
      ratingMap[rating.tag]=s
    ratings={}
    for k,v in ratingMap.items():
      ratings[k]=int(sum(v)/len(v))
    return sorted(ratings.items(), key=lambda x: x[0], reverse=True)
  
  def getGameTagsAveraged(self, name):
    key=self.getKey(name)
    result=cache.get(key)
    if result is None:
      result=self.calculateGameAveragedTags(name)
      cache.set(key, result, 0)
    return result

  def invalidate(self, game):
    cache.delete(self.getKey(game.name))