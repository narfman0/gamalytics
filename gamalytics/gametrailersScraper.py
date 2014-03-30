#!/bin/python
from bs4 import BeautifulSoup
import logging, urllib2
import traceback
LOGGER = logging.getLogger(__name__)

def parse(link):
  response = urllib2.urlopen(link)
  soup = BeautifulSoup(response.read())
  response.close()
  return soup

def parseReviewURL(game):
  LOGGER.info('Parsing gametrailers review URL for: ' + game)
  soup=parse('http://www.gametrailers.com/search?keywords=' + game + '+review')
  for videoElement in soup.findAll('div',{'id':'videos'}):
    for link in videoElement.findAll('a'):
      return link['href']
  return None

def parseReviewEmbed(url):
  if url is None:
    LOGGER.warning('Url None, skipping parse review')
    return None
  LOGGER.info('Parsing gametrailers embedded review URL from: ' + url)
  soup=parse(url)
  dataVideo = soup.find('div', {'class':'download_button'})['data-video']
  return 'http://media.mtvnservices.com/embed/' + dataVideo

def getGametrailersInfo(game):
  try:
    url=parseReviewURL(game)
    video=parseReviewEmbed(url)
    if not url is None and not video is None:
      LOGGER.info('Gametrailers URL found for game: ' + game)
      return (url,video)
    else:
      LOGGER.warning('Gametrailers URL(s) null for game: ' + game)
  except:
    LOGGER.error('Error retrieving gametrailers urls for: ' + game)
    traceback.print_exc()
  return ('','')

if __name__ == '__main__':
  url=parseReviewURL('Titanfall')
  video=parseReviewEmbed(url)
  print('URL: ' + url + '\nvideo: ' + video)
