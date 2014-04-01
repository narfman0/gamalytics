from django.core.cache import cache
from gamalytics.models import Game, Rating
import logging

LOGGER = logging.getLogger(__name__)

def calculateSimilarity(game1, game2, ratingCache, distinctTags):
    '''Calculate the similarity between game1 and game2. Returns [0-1]f'''
    game1tags=ratingCache.calculateGameAveragedTagsMap(game1)
    game2tags=ratingCache.calculateGameAveragedTagsMap(game2)
    score=0.0
    matched=0.0
    unmatched=0.0
    for tag in distinctTags:
        if tag in game1tags and tag in game2tags:
            score += 1.0 - abs(game1tags[tag]/100.0 - game2tags[tag]/100.0)
            matched+=1
        elif (tag not in game1tags and tag not in game2tags):
            pass
        else:#in one but not the other
            unmatched += 1
    #need to divide by matched since we've added, but it is also in the ratio
    #numerator so changing that to 1 instead
    ratio=1.0/(unmatched+matched)
    return score * ratio

def getSimilarity(game1, game2, ratingCache, distinctTags):
    '''Retrieve similarity between games, [0-1]f. Uses cache if available'''
    #key will be the smaller between game1 and game2 to save space/cpu cycles
    key=ratingCache.getKey('sim' + (game1+game2 if game1 < game2 else game2+game1))
    similarity = cache.get(key)
    if similarity is None:
        similarity = calculateSimilarity(game1, game2, ratingCache, distinctTags)
        cache.set(key, similarity, 0)
    return similarity

def getSimilar(gamename, ratingCache, n=10):
    gameSimilarityMap={}
    distinctTags = Rating.objects.values_list('tag', flat=True).distinct()
    i=0
    for game in Game.objects.all():
        if game.name != gamename:
            similarity = getSimilarity(gamename, game.name, ratingCache, distinctTags)
            gameSimilarityMap[gamename] = similarity
            LOGGER.info('Calculated similarity for ' + gamename + ' and ' + game.name + \
                        ' to be: ' + str(similarity) + '. ' + str(i)+'/'+str(Game.objects.count()))
            i+=1
    sortedGames = sorted(gameSimilarityMap.items(), key=lambda x: x[1], reverse=True)
    return sortedGames[-min(n, len(sortedGames)):]