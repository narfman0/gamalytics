from django.shortcuts import render
from gamalytics.models import Game,Rating

#Calculate a game's tag value
def getGameTagRating(gamename,tag):
  r = Rating.objects.filter(gamename=gamename,tag=tag)
  ratings=[]
  for rating in r:
    ratings.append(rating.value)
  if len(ratings) == 0:
    return 0.0
  return sum(ratings)/len(ratings)

#Get all games with tag
def getGamesWithTag(tag):
  gamenames=set()
  for rating in Rating.objects.filter(tag=tag):
    gamenames.update((rating.gamename,))
  return gamenames

def getGameAveragedTags(gamename):
  ratingMap={}
  for rating in Rating.objects.filter(gamename=gamename):
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
  for gamename in getGamesWithTag(tag):
    gameMap[gamename]=getGameTagRating(gamename,tag)
  return sorted(gameMap.items(), key=lambda x: x[1], reverse=True)

def index(request):
  games=Game.objects.all()
  context={'games':games}
  return render(request,'index.html',context)

def search(request):
  searchTerms=request.GET['q'].split(',')
  #Search games AND tags
  games=set()
  for term in searchTerms:
    games.update(Game.objects.filter(gamename=term))
  tags=set()
  for term in searchTerms:
    tags.update(Rating.objects.filter(tag=term))
  tagged={}
  for tag in tags:
    tagged[tag.tag]=getGamesSortedTag(tag.tag)
  context={'games':games, 'tagged':tagged}
  return render(request,'search.html',context)

def game(request, gamename):
  game=Game.objects.get(gamename__iexact=gamename)
  ratings=getGameAveragedTags(game.gamename)
  context={'game' : game, 'ratings' : ratings}
  return render(request,'game.html',context)
