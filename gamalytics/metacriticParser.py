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
    critic=int(soup.find('span',{'itemprop':'ratingValue'}).string)
    user=float(soup.find('div',{'class':'metascore_w user large game positive'}).string)
    result=(critic,user,getColor(critic,100),getColor(user,10))
  return result

def getColor(score,scale):
  if score >= scale*.6:
    return 'Green'
  elif score >= scale*.5:
    return 'Orange'
  else:
    return 'Red'