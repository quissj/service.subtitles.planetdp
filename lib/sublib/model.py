# -*- coding: utf-8 -*-
'''
    Author    : Huseyin BIYIK <husenbiyik at hotmail>
    Year      : 2016
    License   : GPL

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
import sublib.iso639
import sublib.utils

import json
import urllib
import os
import sys
import urlparse
import shutil

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmcvfs


class sub():
    @property
    def label(self):
        return self._label

    @property
    def iso(self):
        return self._iso

    @property
    def sync(self):
        return self._sync

    @property
    def cc(self):
        return self._cc

    @property
    def rating(self):
        return self._rating

    @label.setter
    def label(self, val):
        if not isinstance(val, (str, unicode)):
            raise(TypeError(type(val)))
        self._label = val

    @iso.setter
    def iso(self, val):
        if val not in sublib.iso639.two:
            raise(ValueError(val))
        self._iso = val

    @cc.setter
    def cc(self, val):
        if not isinstance(val, bool):
            raise(TypeError(type(val)))
        self._cc = val

    @sync.setter
    def sync(self, val):
        if not isinstance(val, bool):
            raise(TypeError(type(val)))
        self._sync = val

    @rating.setter
    def rating(self, val):
        if not isinstance(val, int):
            raise(TypeError(type(val)))
        if val < 0 or val > 5:
            raise(ValueError(val))
        self._sync = val

    def __init__(self, label, iso, rating=0, sync=False, cc=False):
        self.rating = rating
        self.label = label
        self.iso = iso
        self.sync = sync
        self.cc = cc
        self._args = []
        self._kwargs = {}

    def download(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs


class item():
    def __init__(self, preflang, langs):
        self.season = -1  # -1:not known, 0 special, >=1 int
        self.episode = -1  # -1:not known, 0 special, >=1 int
        self.languages = []  # list of 2 letter iso strs
        self.imdb = None  # str
        self.tmdb = None  # str
        self.trakt = None  # str
        self.tvdb = None  # str
        self.slug = None  # str
        self.year = None  # int
        self.title = None  # str
        self.show = False  # bool
        fname = urllib.unquote(xbmc.Player().getPlayingFile().decode('utf-8'))
        self.fname = fname

        # process year
        year = xbmc.getInfoLabel("VideoPlayer.Year").strip()
        if year.isdigit():
            self.year = int(year)

        # process season episode
        season = xbmc.getInfoLabel("VideoPlayer.Season").strip()
        episode = xbmc.getInfoLabel("VideoPlayer.Episode").strip()
        if episode.lower().find("s") > -1:
            season = "0"
            episode = episode[-1:]
        if season.lstrip("-").isdigit():
            self.season = int(season)
        if episode.lstrip("-").isdigit():
            self.episode = int(episode)

        # process tvshow and titles
        otitle = sublib.utils.normstr(
                    xbmc.getInfoLabel("VideoPlayer.OriginalTitle")).strip()
        title = sublib.utils.normstr(
                    xbmc.getInfoLabel("VideoPlayer.Title")).strip()
        stitle = sublib.utils.normstr(
                    xbmc.getInfoLabel("VideoPlayer.TVshowtitle")).strip()
        if not stitle == "":
            self.show = True
            self.title = stitle
        elif not otitle == "":
            self.title = otitle
        elif not title == "":
            self.title = title

        # process ids
        if xbmc.Player().isPlaying():
            imdb = xbmc.Player().getVideoInfoTag().getIMDBNumber().strip()
        else:
            imdb = xbmc.getInfoLabel("ListItem.IMDBNumber").strip()
        # try to load ids from script.trakt property
        traktids = xbmcgui.Window(10000).getProperty('script.trakt.ids')
        try:
            traktids = json.loads(traktids)
            if not imdb.startswith("tt") \
                and "imdb" in traktids \
                    and traktids["imdb"].startswith("tt"):
                imdb = traktids["imdb"]
            for k in ["tvdb", "tmdb", "slug", "trakt"]:
                if k in traktids and not traktids[k].strip() == "":
                    item[k] = traktids[k].strip()
        except:
            pass

        # process languages
        if isinstance(langs, (list, tuple)):
            self.languages = langs
        else:
            preflang = preflang.decode('utf-8')
            preflang = xbmc.convertLanguage(preflang, 0)
            if not preflang == "":
                self.languages.append(preflang)
            languages = urllib.unquote(langs).decode('utf-8')
            languages = languages.split(",")
            for lang in languages:
                lang = xbmc.convertLanguage(lang, 0)
                if lang not in self.languages:
                    self.languages.append(lang)

        # to do process filename for title, season, episode
        print item


class service(object):

    sub = sub

    def __init__(self, ua=None):
        if not ua:
            self._ua = sublib.utils._ua
        else:
            self._ua = ua
        self._subs = []
        self._paths = []
        params = dict(urlparse.parse_qsl(sys.argv[2][1:]))
        params = sublib.utils.dformat(params, json.loads)
        action = params.get("action", None)
        if action:
            method = getattr(self, "_action_%s" % action.lower())
            self._params = params
            method()
        addon = xbmcaddon.Addon()
        self._sid = xbmcaddon.Addon().getAddonInfo('id')
        profile = addon.getAddonInfo('profile')
        self._profile = xbmc.translatePath(profile).decode("utf-8")
        temp = os.path.join(profile, 'temp')
        self.path = xbmc.translatePath(temp).decode("utf-8")
        if xbmcvfs.exists(self.path):
            shutil.rmtree(self.path)
        xbmcvfs.mkdirs(self.path)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def _action_search(self):
        preflang = self._params['preferredlanguage']
        langs = self._params['languages']
        self.item = item(preflang, langs)
        self.search()
        for sub in self._subs:
            listitem = xbmcgui.ListItem(
                        label=xbmc.convertLanguage(sub.iso, xbmc.ENGLISH_NAME),
                        label2=sub.label,
                        iconImage=sub.rating,
                        thumbnailImage=sub.iso + ".gif"
                        )
            listitem.setProperty("sync", '{0}'.format(sub.sync).lower())
            listitem.setProperty("hearing_imp", '{0}'.format(sub.cc).lower())
            args = {
                    "action": "download",
                    "args": sub._args,
                    "kwargs": sub._kwargs,
                    "langs": self.item.languages,
                    }
            url = urllib.urlencode(sublib.utils.dformat(args, json.dumps))
            url = "plugin://%s/?%s" % (self._sid, url)

            xbmcplugin.addDirectoryItem(
                                        handle=int(sys.argv[1]),
                                        url=url,
                                        listitem=listitem,
                                        isFolder=False
                                        )

    def _action_download(self):
        self.item = item(self._params["langs"], None)
        self.download(*self._params["args"], **self._params["kwargs"])
        for fname in self._paths:
            sub = sublib.utils.getsub(
                                    fname,
                                    self._item.show,
                                    self._item.season,
                                    self._item.episode
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

    def search(self, item):
        sub = self.sub("Test Subtitle", "en")
        self.addsub(sub)

    def download(self, *args, **kwargs):
        self.addfile("/path/to/file")

    def request(self, u, query=None, data=None, referer=None, binary=False):
        return sublib.utils.download(u,
                                     query,
                                     data,
                                     referer,
                                     binary,
                                     ua=self._ua
                                     )

    def addsub(self, sub):
        if not isinstance(sub, self.sub):
            raise TypeError(sub)
        self._subs.append(sub)

    def addfile(self, path):
        self._paths.append(path)

