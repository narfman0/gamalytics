from django.shortcuts import render
from gamalytics.models import Game,Rating

def index(request):
  games=Game.objects.all()
  context={'games':games}
  return render(request,'index.html',context)

def detail(request, gamename):
  game=Game.objects.filter(gamename=gamename)[0]
  ratingMap={}
  for rating in Rating.objects.filter(gamename=gamename):
    s=ratingMap.get(rating.tag,[])
    s.append(rating.value)
    ratingMap[rating.tag]=s
  ratings={}
  for k,v in ratingMap.items():
    ratings[k]=sum(v)/len(v)
  sortedRatings=sorted(ratings.items(), key=lambda x: x[1], reverse=True)
  context={'game' : game, 'ratings' : sortedRatings}
  return render(request,'game.html',context)
