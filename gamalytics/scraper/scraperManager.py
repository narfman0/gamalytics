from django.utils import timezone
from gamalytics.models import Game, Rating
from gamalytics.scraper import metacriticScraper
import gametrailersScraper, logging

LOGGER = logging.getLogger(__name__)

def scrape():
  startTime=timezone.now()
  games,tags = metacriticScraper.scrapeGamesAndTags()
  #add games
  dbGames={}
  for game in list(Game.objects.all()):
    dbGames[game.name]=game
  for gamename,link in games.iteritems():
    if gamename not in dbGames:
      LOGGER.info('Adding game to db: ' + gamename)
      name,url,summary,published = metacriticScraper.parseGameURL(gamename,link)
      reviewURL,reviewVideo=gametrailersScraper.getGametrailersInfo(name)
      game=Game.objects.create(name=name, metacritic=url, gametrailersReviewURL=reviewURL,
                               gametrailersVideo=reviewVideo, description=summary, 
                               released=published, lastUpdated=timezone.now())
      #add urls
      for tag in tags[name]:
        Rating.objects.create(username='narfman0',game=game,tag=tag,value=100,time=timezone.now())
    elif dbGames[gamename].released > dbGames[gamename].lastUpdated and \
        dbGames[gamename].released < timezone.now():
      LOGGER.info('Should update game in db: ' + gamename)
  LOGGER.info('Finished scrape in time: ' + str(timezone.now()-startTime))

if __name__ == '__main__':
    pass