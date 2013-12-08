from difflib import SequenceMatcher
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.models import User
from django.core.cache import cache
from django.shortcuts import render,redirect,render_to_response
from django.views.decorators.cache import cache_page
from django.utils import timezone
from gamalytics.models import Game,Rating
from gamalytics.ratingCache import RatingCache
from gamalytics.metacriticParser import getMetacriticScore,scrapeAll

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
  context={'games':games, 'genres':GENRES, 'platforms':PLATFORMS,'user':request.user}
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
  context={'games':games, 'tagged':tagged, 'searchString':searchString,'user':request.user}
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
  try:
    scoreCritic,scoreUser,criticColor,userColor=getMetacriticScore(game.metacritic)
  except:
    scoreCritic,scoreUser,criticColor,userColor=('N/A','N/A','Orange','Orange')
    pass
  context={'game':game, 'ratings':ratings, 'released':released,
      'similar':getSimilar(ratings), 'scoreCritic':scoreCritic,'scoreUser':scoreUser,
      'criticColor':criticColor,'userColor':userColor,'user':request.user}
  return render(request,'game.html',context)

def update(request):
  scrapeAll()
  return render_to_response('Successful update!')

def logout(request):
  auth_logout(request)
  return redirect('/')

def register(request):
  return render(request,'registration/register.html',{'error':'', 'username':''})
  
def registerrequest(request):
  username=request.POST['username']
  password=request.POST['password']
  day=request.POST['day']
  message=''
  try:
    if timezone.now().day != int(day):
      message='Day not correct, failure!'
  except:
    message='Day not a number, failure!'
  if User.objects.filter(username=username).count() > 0:
    message='User already registered, failure!'
  if not message:
    User.objects.create_user(username=username, password=password)
    message='Success'
  return render(request,'registration/register.html',{'message':message, 'username':username})