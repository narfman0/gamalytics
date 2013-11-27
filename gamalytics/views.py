from django.http import HttpResponse

def index(request):
    return HttpResponse("Hello, world. You're at the gamalytics index.")

def detail(request, gamename):
    return HttpResponse("You're looking at game %s." % gamename)
