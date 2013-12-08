from bs4 import BeautifulSoup
import urllib2
from django.core.cache import cache

def parse(link):
  response = urllib2.urlopen(link)
  soup = BeautifulSoup(response.read())
  response.close()
  return soup

#return critic,user rating tuple
def getMetacriticScore(url):
  result=cache.get(url)
  if result is None:
    soup=parse(url)
    try:
      critic=int(soup.find('span',{'itemprop':'ratingValue'}).string)
    except:
      critic='tbd'
    try:
      user=float(soup.find('div',{'class':'metascore_w user large game positive'}).string)
    except:
      user='tbd'
    result=(critic,user,getColor(critic,100),getColor(user,10))
  return result

def getColor(score,scale):
  if isinstance(score, basestring):
    return 'LightGray'
  elif score >= scale*.6:
    return 'Green'
  elif score >= scale*.5:
    return 'Orange'
  else:
    return 'Red'