import re, time, random

NAME = 'eporner'
randomArt = random.randint(1,3)
ART = 'artwork-'+str(randomArt)+'.jpg'
ICON = 'icon-default.png'

EPORNER_BASE				= 'http://www.eporner.com'
EPORNER_CONFIG			= 'http://www.eporner.com/config/%s'
EPORNER_RECENT			= 'http://www.eporner.com/%s///%s'
EPORNER_PROMO				= 'http://www.eporner.com/promo//%s/%s/'
EPORNER_SOLOGIRLS		= 'http://www.eporner.com/solo//%s/%s/'
EPORNER_HD					= 'http://www.eporner.com/hd//%s/%s/'
EPORNER_ONAIR				= 'http://www.eporner.com/currently//%s//'
EPORNER_POPULAR			= 'http://www.eporner.com/weekly_top//%s/'
EPORNER_TOPRATED		= 'http://www.eporner.com/top_rated//%s'
EPORNER_KEYWORDS		= 'http://www.eporner.com/keywords/%s/%s/%s'
EPORNER_CATEGORIES	= 'http://www.eporner.com/categories/'

USER_AGENT = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.2.12) Gecko/20101026 Firefox/3.6.12'


####################################################################################################

def Start():
	# Initialize the plugin
	Plugin.AddPrefixHandler('/video/eporner', MainMenu, NAME, ICON, ART)
	Plugin.AddViewGroup("List", viewMode = "List", mediaType = "items")

	# Setup the artwork associated with the plugin
	MediaContainer.art = R(ART)
	MediaContainer.title1 = NAME
	MediaContainer.viewGroup = "List"
	DirectoryItem.thumb = R(ICON)
	VideoItem.thumb = R(ICON)

	HTTP.CacheTime = 3600
	HTTP.Headers['User-Agent'] = USER_AGENT

####################################################################################################

def Thumb(url):
	try:
		data = HTTP.Request(url).content
		return DataObject(data, 'image/jpeg')
	except:
		return Redirect(R(ICON))

def GetDurationFromString(duration):
	try:
		durationArray = duration.split(":")
		if len(durationArray) == 3:
			hours = int(durationArray[0])
			minutes = int(durationArray[1])
			seconds = int(durationArray[2])
		elif len(durationArray) == 2:
			hours = 0
			minutes = int(durationArray[0])
			seconds = int(durationArray[1])
		elif len(durationArray)	==	1:
			hours = 0
			minutes = 0
			seconds = int(durationArray[0])
		return int(((hours)*3600 + (minutes*60) + seconds)*1000)
	except:
		return 0

####################################################################################################

def MainMenu():
	dir = MediaContainer(viewMode = "List")
	dir.Append(Function(PopupDirectoryItem(SortOrderSubMenu, L('HD')), url=EPORNER_HD, mainTitle='HD'))
	dir.Append(Function(PopupDirectoryItem(SortOrderSubMenu, L('Recent')), url=EPORNER_RECENT, mainTitle='Latest'))
	dir.Append(Function(PopupDirectoryItem(SortOrderSubMenu, L('Promo')), url=EPORNER_PROMO, mainTitle='Promo'))
	dir.Append(Function(DirectoryItem(MovieList, L('Popular')), url=EPORNER_POPULAR, mainTitle='Popular'))
	dir.Append(Function(DirectoryItem(MovieList, L('Top Rated')), url=EPORNER_TOPRATED, mainTitle='Top Rated'))
	dir.Append(Function(DirectoryItem(MovieList, L('On-Air')), url=EPORNER_ONAIR, mainTitle='On-Air'))
	dir.Append(Function(PopupDirectoryItem(SortOrderSubMenu, L('Solo Girls')), url=EPORNER_SOLOGIRLS, mainTitle='Solo Girls'))
	dir.Append(Function(DirectoryItem(CategoriesMenu, L('Categories'))))
	dir.Append(Function(InputDirectoryItem(Search, L('Search'), L('Search'), thumb=R(ICON)), url=EPORNER_KEYWORDS))
	return dir

def CategoriesMenu(sender):
	dir = MediaContainer(title2 = sender.itemTitle)
	pageContent = HTML.ElementFromURL(EPORNER_CATEGORIES)
	for categoryItem in pageContent.xpath('//div[contains(@class,"categoriesbox")]/a'):
		categoryItemTitle = categoryItem.xpath('h2/text()')[0].replace(' movies', '')
		categoryItemQuery = categoryItem.get('href').replace('/keywords/','').strip('/')
		categoryItemThumb = categoryItem.xpath('img')[0].get('src')
		#Log(categoryItemTitle+'__'+categoryItemQuery+'__'+categoryItemThumb)
		pageFormat = 'keywords'
		dir.Append(Function(PopupDirectoryItem(SortOrderSubMenu, L(categoryItemTitle), thumb=Function(Thumb, url=categoryItemThumb)), url=EPORNER_KEYWORDS, mainTitle=categoryItemTitle, searchQuery=categoryItemQuery, pageFormat=pageFormat))
	return dir

def MovieList(sender,url,mainTitle='',searchQuery='',pageFormat='normal',sortOrder='',page=0):
	#Log(searchQuery+'__'+pageFormat+'__'+sortOrder+'__'+str(page))
	pageShow	= page+1
	pageShowM	= page
	pageShowP	= page+2
	pageM = page-1
	pageP = page+1

	dir = MediaContainer(viewMode = "List", title2 = mainTitle+' | Page: '+str(pageShow))
#	dir = MediaContainer(viewMode = "List", title2 = mainTitle+' | Page: '+str(pageShow), replaceParent = (page>0))
#	if page>0:
#		dir.Append(Function(DirectoryItem(MovieList, L('+++Previous Page ('+str(pageShowM)+')+++')), url=url, mainTitle=mainTitle, searchQuery=searchQuery, pageFormat=pageFormat, sortOrder=sortOrder, page=pageM))
	if pageFormat == 'keywords':
		pageContent = HTML.ElementFromURL(url % (searchQuery, str(page), sortOrder))
	else:
		try:
			pageContent = HTML.ElementFromURL(url % (str(page), sortOrder))
		except:
			pageContent = HTML.ElementFromURL(url % (str(page)))
	initialXpath = '//div[@id="content"]//div[@class="mb" or @class="mb mbr" or @class="mbhd" or @class="mbhd mbr"]'
	for videoItem in pageContent.xpath(initialXpath):
		videoItemTitle = videoItem.xpath('a')[0].get('title').replace('free hd porn tube ','')
		videoItemID	= videoItem.xpath('a')[0].get('id').replace('ah','')
		videoItemURL = EPORNER_BASE+videoItem.xpath('a')[0].get('href')
		videoItemThumb = None
		try: videoItemThumb = videoItem.xpath('a/img')[0].get('src')
		except: pass
		duration = None
		try: duration = videoItem.xpath('div[@class="mbtim"]/text()')[0].strip()
		except: pass
		videoItemDuration = GetDurationFromString(duration)
		videoItemViews = None
		try: videoItemViews = 'Views: '+videoItem.xpath('div[@class="mbvie"]/text()')[0].strip()
		except: pass
		#Log(videoItemTitle+'__'+videoItemID+'__'+videoItemURL+'__'+videoItemThumb+'__'+str(videoItemDuration)+'__'+videoItemViews)
		dir.Append(Function(PopupDirectoryItem(VideoSubMenu, title=videoItemTitle, duration=videoItemDuration, summary=videoItemViews, thumb=Function(Thumb, url=videoItemThumb)), id=videoItemID, title=videoItemTitle, url=videoItemURL))
	if len(pageContent.xpath('//div[@class="numlist2"]/a/span[contains(text(),'+str(pageShowP)+')]')) > 0:
		dir.Append(Function(DirectoryItem(MovieList, L('+++Next Page ('+str(pageShowP)+')+++')), url=url, mainTitle=mainTitle, searchQuery=searchQuery, pageFormat=pageFormat, sortOrder=sortOrder, page=pageP))
	return dir

def VideoSubMenu(sender,id,title,url):
	dir = MediaContainer()
	dir.Append(Function(VideoItem(PlayVideo,L('Play Video')), id=id, start=0))
	dir.Append(Function(DirectoryItem(VideoSceneSelect, L('Scene Select'), ''), id=id, title=title, url=url))
	return dir

def SortOrderSubMenu(sender,url,mainTitle,searchQuery='',pageFormat='normal'):
	dir = MediaContainer()
	if pageFormat == 'keywords':
		dir.Append(Function(DirectoryItem(MovieList, L('Most Recent')), url=url, mainTitle=mainTitle, searchQuery=searchQuery, pageFormat=pageFormat, sortOrder='recent'))
	else:
		dir.Append(Function(DirectoryItem(MovieList, L('Most Recent')), url=url, mainTitle=mainTitle, searchQuery=searchQuery, pageFormat=pageFormat, sortOrder=''))
	dir.Append(Function(DirectoryItem(MovieList, L('Most Viewed')), url=url, mainTitle=mainTitle, searchQuery=searchQuery, pageFormat=pageFormat, sortOrder='most_viewed'))
	if pageFormat == 'keywords':
		dir.Append(Function(DirectoryItem(MovieList, L('Top Rated')), url=url, mainTitle=mainTitle, searchQuery=searchQuery, pageFormat=pageFormat, sortOrder='top_rated'))
	dir.Append(Function(DirectoryItem(MovieList, L('Longest')), url=url, mainTitle=mainTitle, searchQuery=searchQuery, pageFormat=pageFormat, sortOrder='longest'))
	dir.Append(Function(DirectoryItem(MovieList, L('Shortest')), url=url, mainTitle=mainTitle, searchQuery=searchQuery, pageFormat=pageFormat, sortOrder='shortest'))
	return dir

def VideoSceneSelect(sender,id,title,url):
	dir = MediaContainer(title2 = title)
	pageVSSContent = HTML.ElementFromURL(url)
	sceneNo = 0
	for videoVSSItem in pageVSSContent.xpath('//div[@id="cutscenes"]/div[@class="cutscenesbox"]'):
		sceneNo = sceneNo+1
		videoVSSItemTitle = 'Scene No. '+str(sceneNo)
		videoVSSItemID	= id
		if len(videoVSSItem.xpath('a/img')) > 0:
			videoVSSItemThumb = videoVSSItem.xpath('a/img')[0].get('src')
		else:
			videoVSSItemThumb = ''
		duration = None
		try: duration = videoVSSItem.xpath('div[@class="thuminitime"]/text()')[0].strip()
		except: pass
		videoVSSItemDuration = GetDurationFromString(duration)
		videoVSSItemDurationSec = int(videoVSSItemDuration/1000)
		#Log(videoVSSItemTitle+'__'+str(videoVSSItemID)+'__'+str(videoVSSItemDurationSec)+'__'+videoVSSItemThumb)
		dir.Append(Function(VideoItem(PlayVideo, title=videoVSSItemTitle, duration=videoVSSItemDuration, thumb=Function(Thumb, url=videoVSSItemThumb)), id=videoVSSItemID, start=videoVSSItemDurationSec))
	return dir

def Search(sender,url,query='',mainTitle='Search',pageFormat='keywords'):
	dir = MediaContainer()
	searchQueryCorrect = String.Quote(query)
	dir = SortOrderSubMenu(sender=None, url=url, mainTitle=mainTitle+': '+query, searchQuery=searchQueryCorrect, pageFormat=pageFormat)
	return dir

####################################################################################################

def PlayVideo(sender, id, start=0):
	content = XML.ElementFromURL(EPORNER_CONFIG % str(id))
	vidurl = content.xpath('//file')[0].text+'?start='+str(start)
	#Log(vidurl)
	if len(vidurl) > 0:
		return Redirect(vidurl)
	else:
		return None
