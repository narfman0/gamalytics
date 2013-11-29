from django.shortcuts import render
from gamalytics.models import Game,Rating
from difflib import SequenceMatcher

GENRES=('Action','Adventure','Fighting','First-person','Flight','Party','Platformer','Puzzle','Racing','Real-time','Role-playing','Simulation','Sports','Strategy','Third-person',)
PLATFORMS=('PC','Playstation-4','Playstation-3','Xbox-One','Xbox-360','Wii-U','3DS','IOS','Wii','DS',)

#Calculate a game's tag value
def getGameTagRating(game,tag):
  r = Rating.objects.filter(game__gamename=game.gamename, tag=tag)
  ratings=[]
  for rating in r:
    ratings.append(rating.value)
  if len(ratings) == 0:
    return 0.0
  return sum(ratings)/len(ratings)

#Get all games with tag
def getGamesWithTag(tag):
  games=set()
  for rating in Rating.objects.filter(tag__iexact=tag):
    games.update((rating.game,))
  return games

def getGameAveragedTags(gamename):
  ratingMap={}
  for rating in Rating.objects.filter(game__gamename__iexact=gamename):
    s=ratingMap.get(rating.tag,[])
    s.append(rating.value)
    ratingMap[rating.tag]=s
  ratings={}
  for k,v in ratingMap.items():
    ratings[k]=sum(v)/len(v)
  return sorted(ratings.items(), key=lambda x: x[1], reverse=True)

#Find all games with tag and sort by how applicable they are
def getGamesSortedTag(tag):
  gameMap={}
  for game in getGamesWithTag(tag):
    gameMap[game.gamename]=getGameTagRating(game,tag)
  return sorted(gameMap.items(), key=lambda x: x[1], reverse=True)

def index(request):
  games=list(Game.objects.all().order_by('released'))[-10:]
  context={'games':games, 'genres':GENRES, 'platforms':PLATFORMS}
  return render(request,'index.html',context)

def search(request):
  searchString=request.GET['q']
  searchTerms=searchString.split()
  #Search games AND tags
  games=set()
  for term in searchTerms:
    games.update(Game.objects.filter(gamename__iexact=term))
  games.update(Game.objects.filter(gamename__contains=searchString))
  gamesScoreMap={}
  for game in games:
    gamesScoreMap[game]=int(SequenceMatcher(None,searchString,game.gamename).ratio()*100)
  gamesScoreSorted=sorted(gamesScoreMap.items(), key=lambda x: x[1], reverse=True)
  tags=set()
  for term in searchTerms:
    tags.update(Rating.objects.filter(tag__iexact=term))
  tagged={}
  for tag in tags:
    tagged[tag.tag]=getGamesSortedTag(tag.tag)
  context={'games':gamesScoreSorted, 'tagged':tagged, 'searchString':searchString}
  return render(request,'search.html',context)

def game(request, gamename):
  game=Game.objects.get(gamename__iexact=gamename)
  ratings=getGameAveragedTags(game.gamename)
  released=''
  try:
    released=game.released.strftime('%b. %d, %Y')
  except:
    pass
  context={'game':game, 'ratings':ratings, 'released':released}
  return render(request,'game.html',context)
