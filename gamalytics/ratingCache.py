#This will manage the tag cache for ratings. Every time it is changed
#for a game, e.g. a rating is added, removed, or changed, it will update
#for that game since we assume more reads than writes.
from gamalytics.models import Game,Rating
from django.core.cache import cache
from hashlib import md5

#Stupid memcached. This class checks if memcached is active, if so, uses it.
#Otherwise it uses a local map.
class RatingCache:
  tagCache={}
  #prepopulate - if true, calculate all games at startup
  def __init__(self, prepopulate):
    if prepopulate:
      count=Game.objects.all().count()
      current=1.0
      for game in Game.objects.all():
        tags=self.calculateGameAveragedTags(game.name)
        if self.isMemcachedActive():
          cache.set(self.getKey(game.name), tags, 0)
        else:
          self.tagCache[game.name]=tags
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
      ratings[k]=sum(v)/len(v)
    return sorted(ratings.items(), key=lambda x: x[1], reverse=True)
  
  def isMemcachedActive(self):
    key='ismemcachedactivekey'
    cache.set(key,"value",0)
    return cache.get(key) != None

  def getGameTagsAveraged(self, name):
    if self.isMemcachedActive():
      key=self.getKey(name)
      result=cache.get(key)
      if result is None:
        result=self.calculateGameAveragedTags(name)
        cache.set(key, result, 0)
    else:
      if name not in self.tagCache:
        self.tagCache[name]=self.calculateGameAveragedTags(name)
      result=self.tagCache[name]
    return result
