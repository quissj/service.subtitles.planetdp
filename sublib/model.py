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
import sublib.utils
import sublib.sub
import sublib.item

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


class service(object):

    sub = sublib.sub.model

    def __init__(self, ua=None):
        if not ua:
            self._ua = sublib.utils._ua
        else:
            self._ua = ua
        self._subs = []
        self._paths = []
        addon = xbmcaddon.Addon()
        self._sid = xbmcaddon.Addon().getAddonInfo('id')
        profile = addon.getAddonInfo('profile')
        self._profile = xbmc.translatePath(profile).decode("utf-8")
        temp = os.path.join(profile, 'temp')
        self.path = xbmc.translatePath(temp).decode("utf-8")
        if xbmcvfs.exists(self.path):
            shutil.rmtree(self.path)
        xbmcvfs.mkdirs(self.path)
        params = dict(urlparse.parse_qsl(sys.argv[2][1:]))
        params = sublib.utils.dformat(params, json.loads)
        action = params.get("action", None)
        if action:
            method = getattr(self, "_action_%s" % action.lower())
            self._params = params
            method()
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def init(self, ua=None):
        return ua

    def _action_search(self):
        preflang = self._params['preferredlanguage']
        langs = self._params['languages']
        self.item = sublib.item.model(preflang, langs)
        self.search()
        for sub in self._subs:
            listitem = xbmcgui.ListItem(
                        label=xbmc.convertLanguage(sub.iso, xbmc.ENGLISH_NAME),
                        label2=sub.label,
                        iconImage=str(sub.rating),
                        thumbnailImage=sub.iso + ".gif"
                        )
            listitem.setProperty("sync", '{0}'.format(sub.sync).lower())
            listitem.setProperty("hearing_imp", '{0}'.format(sub.cc).lower())
            args = {
                    "action": "download",
                    "args": sub.args,
                    "kwargs": sub.kwargs,
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
        self.item = sublib.item.model(None, self._params["langs"])
        self.download(*self._params["args"], **self._params["kwargs"])
        for fname in self._paths:
            sub = sublib.utils.getsub(
                                    fname,
                                    self.item.show,
                                    self.item.season,
                                    self.item.episode
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

    def search(self):
        sub = self.sub("Test Subtitle", "en")
        sub.download(1, 2, test=3)
        self.addsub(sub)

    def download(self, *args, **kwargs):
        print args
        print kwargs
        self.addfile("/path/to/file")

    def num(self, issub=True):
        if issub:
            return len(self._subs)
        else:
            return len(self._paths)

    def request(self, u, query=None, data=None, referer=None, binary=False):
        return sublib.utils.download(u,
                                     query,
                                     data,
                                     referer,
                                     binary,
                                     ua=self._ua
                                     )

    def addsub(self, sub):
        if not isinstance(sub, sublib.sub.model):
            raise TypeError(sub)
        self._subs.append(sub)

    def addfile(self, path):
        self._paths.append(path)
