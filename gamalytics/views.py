from difflib import SequenceMatcher
from django.core.cache import cache
from django.shortcuts import render
from django.views.decorators.cache import cache_page
from gamalytics.models import Game,Rating
from gamalytics.ratingCache import RatingCache

CACHE_DURATION=60*60*24
GENRES=('Action','Adventure','Fighting','First-person','Flight','Party','Platformer','Puzzle','Racing','Real-time','Role-playing','Simulation','Sports','Strategy','Third-person',)
PLATFORMS=('PC','Playstation-4','Playstation-3','Xbox-One','Xbox-360','Wii-U','3DS','IOS',)
ratingCache=RatingCache(False)

#Get all games with tag
def getGamesWithTag(tag):
  key=ratingCache.getKey(tag)
  result=cache.get(key)
  if result is None:
    games=[]
    for rating in Rating.objects.filter(tag__iexact=tag).select_related('game'):
      games.append(rating.game)
    result=set(games)
    cache.set(key, result, 0)
  return result

#Return a list of similar games along with how similar they are
def getSimilar(ratings):
  matchedGames=set(Game.objects.all())
  for tag,value in ratings:
    gamesWithTag=getGamesWithTag(tag)
    matchedGames=matchedGames.intersection(gamesWithTag)
  games={}
  for game in matchedGames:
    games[game] = ratingCache.getGameTagsAveraged(game.name)
  return games

def index(request):
  games=list(Game.objects.all().order_by('released'))[-10:]
  context={'games':games, 'genres':GENRES, 'platforms':PLATFORMS, 'title':'Gamalytics'}
  return render(request,'index.html',context)

def searchGames(query):
  games=set()
  for term in query:
    games.update(Game.objects.filter(name__icontains=term))
  gamesScoreMap={}
  for game in games:
    gamesScoreMap[game]=int(SequenceMatcher(None,' '.join(query),game.name).ratio()*100)
  return sorted(gamesScoreMap.items(), key=lambda x: x[1], reverse=True)

def searchTags(query):
  tags={}
  matchedTags=[]
  tags.setdefault(0)
  maxValue=.00000001
  for term in query:
    results=Rating.objects.filter(tag__iexact=term).select_related('game')
    if results.count() > 0:
      matchedTags.append(term)
    for match in results:
      if match.game.name in tags:
        tags[match.game.name]=tags[match.game.name]+match.value
      else:
        tags[match.game.name]=match.value
      maxValue=max(maxValue,tags[match.game.name])
  del tags[0]
  for key in tags.keys():
    tags[key]=int(tags[key]/maxValue*100)
  sortedTags=sorted(tags.items(), key=lambda x: x[1], reverse=True)
  return (sortedTags,matchedTags,)

#Search games and tags
@cache_page(CACHE_DURATION)
def search(request):
  searchString=request.GET['q']
  if ' ' in searchString:
    searchTerms=searchString.split()
  else:
    searchTerms=[searchString]
  tagged,matchedTags=searchTags(searchTerms)
  for matchedTag in matchedTags:
    searchTerms.remove(matchedTag)
  games=searchGames(searchTerms)
  context={'games':games, 'tagged':tagged, 'searchString':searchString,
      'title':'Gamalytics Search - ' + searchString}
  return render(request,'search.html',context)

@cache_page(CACHE_DURATION)
def game(request, name):
  game=Game.objects.get(name__iexact=name)
  ratings=ratingCache.getGameTagsAveraged(name)
  released=''
  try:
    released=game.released.strftime('%b. %d, %Y')
  except:
    pass
  context={'game':game, 'ratings':ratings, 'released':released,
      'similar':getSimilar(ratings), 'title':'Gamalytics - ' + name}
  return render(request,'game.html',context)
