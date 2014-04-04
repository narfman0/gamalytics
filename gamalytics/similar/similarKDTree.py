#Return a list of similar games along with how similar they are
from django.utils import timezone
from gamalytics.models import Game, Rating
from scipy.spatial.kdtree import KDTree
import logging,numpy

LOGGER = logging.getLogger(__name__)
kdtree = None
ratingMap = None

def getSimilar(name, ratingCache, ratings, n=10):
  global kdtree
  if kdtree is None:
    #initialize kdtree AND ratingMap
    ratingMap = createRatingMap()
    LOGGER.info('Creating KDTree...')
    start=timezone.now()
    kdtree = createTree(ratingCache, ratingMap)
    LOGGER.info('Done creating KDTree in: ' + str(timezone.now()-start))
  return kdtree.query(getGameTagArray(name, ratingCache, ratingMap), n)

def getGameTagArray(name, ratingCache, ratingMap):
    tags=ratingCache.calculateGameAveragedTagsMap(name)
    tagValues=[None]*len(ratingMap)
    for i,tag in ratingMap.iteritems():
        tagValues[i] = tags[tag] if tag in tags else -100
    return tagValues

def createTree(ratingCache, ratingMap):
    array=[]
    for game in Game.objects.all():
        array.append(getGameTagArray(game.name, ratingCache, ratingMap))
    x = numpy.mgrid[array]
    return KDTree(zip(x.ravel()))

def createRatingMap():
    '''Create map of rating to index'''
    ratingMap={}
    i=0
    for rating in Rating.objects.values_list('tag', flat=True).distinct():
        ratingMap[i]=rating
        i+=1
    return ratingMap