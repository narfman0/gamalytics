#!/bin/python
from bs4 import BeautifulSoup
import logging, urllib2
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
  LOGGER.info('Parsing gametrailers embedded review URL from: ' + url)
  soup=parse(url)
  dataVideo = soup.find('div', {'class':'download_button'})['data-video']
  return 'http://media.mtvnservices.com/embed/' + dataVideo

def getGametrailersInfo(game):
  url=parseReviewURL(game)
  video=parseReviewEmbed(url)
  return (url, video)

if __name__ == '__main__':
  url=parseReviewURL('Titanfall')
  video=parseReviewEmbed(url)
  print('URL: ' + url + '\nvideo: ' + video)
