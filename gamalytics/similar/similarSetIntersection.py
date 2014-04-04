#Return a list of similar games along with how similar they are
from django.utils import timezone
from gamalytics.models import Game, Rating
import logging

LOGGER = logging.getLogger(__name__)

def getSimilar(name, ratingCache, ratings):
  start=timezone.now()
  matchedGames=set(Game.objects.all())
  if len(ratings) > 0:
    for tag,_value in ratings:
      gamesTag=set(rating.game for rating in Rating.objects.filter(tag__iexact=tag).select_related('game'))
      matchedGames=matchedGames.intersection(gamesTag)
  else:
    matchedGames=set()
    LOGGER.error('Ratings empty')
  LOGGER.info('Got similar games with tags in ' + str(timezone.now()-start))
  start=timezone.now()
  games={}
  for game in matchedGames:
    games[game] = ratingCache.getGameTagsAveraged(game.name)
  LOGGER.info('Done getting averaged games in ' + str(timezone.now()-start))
  return games