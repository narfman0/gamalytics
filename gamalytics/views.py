from django.http import HttpResponse
from django.shortcuts import render
from gamalytics.models import Game

def index(request):
    return HttpResponse("Hello, world. You're at the gamalytics index.")

def detail(request, gamename):
    game=Game.objects.filter(gamename=gamename)[0]
    context = {'game': game}
    return render(request,'game.html',context)
