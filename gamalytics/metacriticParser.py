#Script to scrape metacritic and exrapolate description, metascore link, and description
from bs4 import BeautifulSoup
from datetime import datetime
from django.utils import timezone
from django.core.cache import cache
from gamalytics.models import Game,Rating
import logging, traceback, urllib2

BASE_URL='http://www.metacritic.com'
TEMPLATE_GENRE_URL=BASE_URL + '/browse/games/genre/metascore/GENRE/PLATFORM?view=condensed&page=PAGE'
GENRES=('action','adventure','fighting','first-person','flight',
        'party','platformer','puzzle','racing','real-time','role-playing',
        'simulation','sports','strategy','third-person',)
PLATFORM_MAP={'pc':'pc', 'ps4':'playstation-4', 'ps3':'playstation-3', 
  'xboxone':'xbox-one','xbox360':'xbox-360','wii-u':'wii-u','3ds':'3ds',
  'ios':'ios'}
LOGGER = logging.getLogger(__name__)

def parse(link):
  response = urllib2.urlopen(link)
  soup = BeautifulSoup(response.read())
  response.close()
  return soup

#return critic,user rating tuple
def getMetacriticScore(url):
  result=cache.get(url)
  if result is None:
    soup=parse(url)
    try:
      critic=int(soup.find('span',{'itemprop':'ratingValue'}).string)
    except:
      critic='tbd'
    try:
      user=float(soup.find('div',{'class':'metascore_w user large game positive'}).string)
    except:
      user='tbd'
    result=(critic,user,getColor(critic,100),getColor(user,10))
    cache.set(url,result,60*60*24)
  return result

def getColor(score,scale):
  if isinstance(score, basestring):
    return 'LightGray'
  elif score >= scale*.6:
    return 'Green'
  elif score >= scale*.5:
    return 'Orange'
  else:
    return 'Red'
  
def extractString(element):
  return str(element.contents[0]).strip()
  
#Parse summary from soup
def parseSummary(soup):
  summary = ''
  for summaryDetailsElement in soup.findAll('ul', attrs={'class':'summary_details'}):
    for summaryElement in summaryDetailsElement.findAll('span', attrs={'class':'blurb blurb_collapsed'}):
      summary = extractString(summaryElement)
    for summaryElement in summaryDetailsElement.findAll('span', attrs={'class':'blurb blurb_expanded'}):
      summary += extractString(summaryElement)
    if summary == '':
      for spanElement in summaryDetailsElement.findAll('span', attrs={'class':'data','itemprop':'description'}):
        summary = spanElement.findNext('span').string.strip()
  if summary == '':
    for element in soup.findAll('meta', attrs={'name':'og:description'}):
      summary = element['content'].strip()
  return summary

#Return (description,published) tuple
def parseGame(url,gamename):
  soup=parse(BASE_URL+url) 
  for element in soup.findAll('span', attrs={'itemprop':'datePublished'}):
    published = element.string.strip()
  summary=''
  try:
    summary=parseSummary(soup)
  except:
    LOGGER.error('Failed to parse ' + gamename)
    traceback.print_exc()
    pass 
  return (summary,getTime(published))

def getTime(time):
  try:
    return timezone.get_current_timezone().localize(datetime.strptime(time, '%b %d, %Y'))
  except:
    LOGGER.error('Exception converting time ' + time)
    traceback.print_exc()
    return timezone.now()

def isValid(soup):
  return len(soup.findAll('p', attrs={'class':'no_data'})) == 0

#Get all URLS for all games
def getGameURLs(games,tags,genre,platform):
  x=0
  while True:
    url=TEMPLATE_GENRE_URL.replace('GENRE',genre).replace('PAGE',str(x)).replace('PLATFORM',platform)
    x+=1
    LOGGER.info('Getting URL: ' + url)
    try:
      soup=parse(url)
      if not isValid(soup):
        return
      for productTitleContainer in soup.findAll('div', attrs={'class':'basic_stat product_title'}):
        gameElement=productTitleContainer.findNext('a')
        gamename=gameElement.string.strip()
        
        #keep track of tags
        gametags=list()
        if gamename in tags:
          gametags=tags[gamename]
        gametags.append(genre)
        gametags.append(platform)
        tags[gamename]=gametags
        
        if not gamename in games:
          link=str(gameElement['href']).strip()
          games[gamename]=link
    except:
      traceback.print_exc()
      pass

def parseGameURL(name,url):
  try:
    summary,published=parseGame(url,name)
  except:
    LOGGER.error('Error encountered on: ' + name + ' with url: ' + url)
    summary=''
    published=timezone.now()
    pass
  return (name,url,summary,published)

def scrapeAll():
  games={}
  tags={}
  startTime=timezone.now()
  for genre in GENRES:
    for platform in PLATFORM_MAP.keys():
      getGameURLs(games,tags,genre,platform)
  #add games
  dbGames={}
  for game in list(Game.objects.all()):
    dbGames[game.name]=game
  for gamename,link in games.iteritems():
    if gamename not in dbGames:
      LOGGER.info('Adding game to db: ' + gamename)
      name,url,summary,published=parseGameURL(gamename,link)
      game=Game.objects.create(name=name, metacritic=url, gametrailers='gametrailers.com', 
                               description=summary, released=published)
      #add urls
      for tag in tags[name]:
        Rating.objects.create(username='narfman0',game=game,tag=tag,value=100,time=timezone.now())
    elif dbGames[gamename].released > dbGames[gamename].lastUpdated and \
        dbGames[gamename].released < timezone.now():
      LOGGER.info('Should update game in db: ' + gamename)
  LOGGER.info('Finished scrape in time: ' + str(timezone.now()-startTime))