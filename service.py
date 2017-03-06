# -*- coding: utf-8 -*-

import os
import sys
import xbmc
import urllib
import urlparse
import xbmcvfs
import xbmcaddon
import xbmcgui
import xbmcplugin
import shutil
import unicodedata
import json

__addon__ = xbmcaddon.Addon()
__author__ = __addon__.getAddonInfo('author')
__scriptid__ = __addon__.getAddonInfo('id')
__scriptname__ = __addon__.getAddonInfo('name')
__version__ = __addon__.getAddonInfo('version')
__language__ = __addon__.getLocalizedString

__cwd__ = xbmc.translatePath(__addon__.getAddonInfo('path')).decode("utf-8")
__profile__ = xbmc.translatePath(__addon__.getAddonInfo('profile')).decode("utf-8")
__resource__ = xbmc.translatePath(os.path.join(__cwd__, 'resources', 'lib')).decode("utf-8")
__temp__ = xbmc.translatePath(os.path.join(__profile__, 'temp')).decode("utf-8")

sys.path.append(__resource__)

import planetdp
import package


def dformat(d, m):
    r = {}
    for k, v in d.iteritems():
        try:
            r[k] = m(v)
        except:
            r[k] = v
    return r


def Search(item):
    results = planetdp.search(item)
    for result in results:
        listitem = xbmcgui.ListItem(
                                    label=xbmc.convertLanguage(result["iso"], xbmc.ENGLISH_NAME),
                                    label2=result["name"],
                                    iconImage="0",
                                    thumbnailImage=result["iso"] + ".gif"
                                    )
        print result["iso"] + ".gif"
        #listitem.setProperty("sync", '{0}'.format("true").lower())
        #listitem.setProperty("hearing_imp", '{0}'.format("false").lower())
        args = {
                "action": "download",
                "link": result["link"],
                "tvshow": item["tvshow"],
                "season": item["season"],
                "episode": item["episode"],
                }
        url = "plugin://%s/?%s" % (__scriptid__, urllib.urlencode(dformat(args, json.dumps)))

        xbmcplugin.addDirectoryItem(
                                    handle=int(sys.argv[1]),
                                    url=url,
                                    listitem=listitem,
                                    isFolder=False
                                    )


def Download(link):
    subtitle_list = []
    if xbmcvfs.exists(__temp__):
        shutil.rmtree(__temp__)
    xbmcvfs.mkdirs(__temp__)
    for subtitle in planetdp.downloadsub(link, __temp__):
        subtitle_list.append(subtitle)

    return subtitle_list


def normalizeString(str):
    str = unicodedata.normalize('NFKD', unicode(unicode(str, 'utf-8')))
    return str.encode('ascii', 'ignore')


def get_params():
    #seriously?
    return dformat(dict(urlparse.parse_qsl(sys.argv[2][1:])), json.loads)

params = get_params()

print params


if params['action'] == 'search':
    item = {}
    item['temp'] = False
    item['rar'] = False
    item['year'] = xbmc.getInfoLabel("VideoPlayer.Year")
    item['season'] = str(xbmc.getInfoLabel("VideoPlayer.Season"))
    item['episode'] = str(xbmc.getInfoLabel("VideoPlayer.Episode"))
    item['tvshow'] = normalizeString(xbmc.getInfoLabel("VideoPlayer.TVshowtitle"))
    item['title'] = normalizeString(xbmc.getInfoLabel("VideoPlayer.OriginalTitle"))
    item['file_original_path'] = urllib.unquote(xbmc.Player().getPlayingFile().decode('utf-8'))
    item['3let_language'] = []
    item["tmdb"] = ""
    item["trakt"] = ""
    item["tvdb"] = ""
    item["slug"] = ""

    if xbmc.Player().isPlaying():
        imdb = xbmc.Player().getVideoInfoTag().getIMDBNumber()
    else:
        imdb = xbmc.getInfoLabel("ListItem.IMDBNumber")
    item["imdb"] = imdb
    preflang = params['preferredlanguage'].decode('utf-8')
    preflang = xbmc.convertLanguage(preflang, 0)
    if not preflang == "":
        item['3let_language'].append(preflang)
    for lang in urllib.unquote(params['languages']).decode('utf-8').split(","):
        lang = xbmc.convertLanguage(lang, 0)
        if not lang in item['3let_language']:
            item['3let_language'].append(lang)

    if item['title'] == "":
        item['title'] = normalizeString(xbmc.getInfoLabel("VideoPlayer.Title"))
    if item['episode'].lower().find("s") > -1:
        item['season'] = "0"
        item['episode'] = item['episode'][-1:]
    if (item['file_original_path'].find("http") > -1):
        item['temp'] = True
    elif (item['file_original_path'].find("rar://") > -1):
        item['rar'] = True
        path = item['file_original_path'][6:]
        item['file_original_path'] = os.path.dirname(path)
    elif (item['file_original_path'].find("stack://") > -1):
        stackPath = item['file_original_path'].split(" , ")
        item['file_original_path'] = stackPath[0][8:]
    for k in ["season", "episode"]:
        item[k] = item[k].replace(" ", "").strip()
        if not item[k].isdigit():
            item[k] = -1
        else:
            item[k] = int(item[k])
    if item["tvshow"].strip == "":
        item["tvshow"] = None
    #try to load ids from script.trakt property
    traktids = xbmcgui.Window(10000).getProperty('script.trakt.ids')
    try:
        traktids = json.loads(traktids)
        if not item["imdb"].startswith("tt") \
        and "imdb" in traktids \
        and traktids["imdb"].startswith("tt"):
            item["imdb"] = traktids["imdb"]
        for k in ["tvdb", "tmdb", "slug", "trakt"]:
            if k in traktids and item[k] == "" and not traktids[""] == "":
                item[k] = traktids[k]
    except:
        pass
    item["imdb"] = ""
    for k in ["tvdb", "tmdb", "slug", "trakt"]:
        if item[k].strip == "":
            item[k] = None
    if item["year"].isdigit():
        item["year"] = int(item["year"])
    else:
        item["year"] = None
    print item
    Search(item)

elif params['action'] == 'download':
    subs = Download(params["link"])
    for fname in subs:
        sub = package.getsub(fname,
                             params["tvshow"],
                             params["season"],
                             params["episode"]
                             )
        if not sub:
            d = xbmcgui.Dialog()
            d.ok("Error in archive", "Archive file %s is either empty or the files are not in the root directory." % fname)
            sys.exit()
        listitem = xbmcgui.ListItem(label=sub)
        xbmcplugin.addDirectoryItem(
                                    handle=int(sys.argv[1]),
                                    url=sub,
                                    listitem=listitem,
                                    isFolder=False
                                    )

xbmcplugin.endOfDirectory(int(sys.argv[1]))
