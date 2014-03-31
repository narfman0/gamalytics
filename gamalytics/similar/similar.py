from scipy.spatial import KDTree
import numpy
from gamalytics.models import Game, Rating

def createRatingMap():
    '''Create map of rating to index'''
    ratingMap={}
    i=0
    for rating in Rating.objects.values_list('tag', flat=True).distinct():
        ratingMap[i]=rating
        i+=1
    return ratingMap

def getGameTagArray(name, ratingCache, ratingMap):
    tags=ratingCache.calculateGameAveragedTagsMap(name)
    tagValues=[None]*len(ratingMap)
    for i,tag in ratingMap.iteritems():
        tagValues[i] = tags[tag] if tag in tags else 0
    return tagValues

def createTree(ratingCache, ratingMap):
    array=[]
    for game in Game.objects.all():
        array.append(getGameTagArray(game.name, ratingCache, ratingMap))
    x = numpy.mgrid[array]
    return KDTree(zip(x.ravel()))

def getSimilar(name, tree, ratingCache, ratingMap):
    return tree.query(getGameTagArray(name, ratingCache, ratingMap), 10)

if __name__ == '__main__':
    x = numpy.mgrid[0:100]
    points = zip(x.ravel())
    tree=KDTree(points)
    print(tree.query([50], 10))