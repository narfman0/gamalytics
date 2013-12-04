#This will manage the tag cache for ratings. Every time it is changed
#for a game, e.g. a rating is added, removed, or changed, it will update
#for that game since we assume more reads than writes.
from gamalytics.models import Game,Rating

class RatingCache:
  allRatings={}

  def __init__(self):
    count=Game.objects.all().count()
    current=1
    for game in Game.objects.all():
      self.updateGameAveragedTags(game.gamename)
      print('Finished cache of game ' + str(current) + '/' + str(count) + ': ' + game.gamename)
      current += 1

  def updateGameAveragedTags(self, gamename):
    ratingMap={}
    for rating in Rating.objects.filter(game__gamename__iexact=gamename):
      s=ratingMap.get(rating.tag,[])
      s.append(rating.value)
      ratingMap[rating.tag]=s
    ratings={}
    for k,v in ratingMap.items():
      ratings[k]=sum(v)/len(v)
    self.allRatings[gamename]=sorted(ratings.items(), key=lambda x: x[1], reverse=True)

  def getGameTagsAveraged(self, gamename):
    if not gamename in self.allRatings:
      self.updateGameAveragedTags(gamename)
    return self.allRatings[gamename]
