from django.shortcuts import render
from gamalytics.models import Game

def index(request):
  games=Game.objects.filter()
  context={'games':games}
  return render(request,'index.html',context)

def detail(request, gamename):
  game=Game.objects.filter(gamename=gamename)[0]
  context={'game': game}
  return render(request,'game.html',context)
