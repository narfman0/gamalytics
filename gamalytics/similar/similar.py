from gamalytics.models import Game, Rating

def createRatingMap():
    '''Create map of rating to index'''
    ratingMap={}
    i=0
    distinctTags=Rating.objects.values_list('tag', flat=True).distinct()
    for rating in distinctTags:
        ratingMap[i]=rating
        i+=1
    return ratingMap

def similarity(game1, game2, ratingCache, distinctTags):
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