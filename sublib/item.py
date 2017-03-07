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
import urllib
import json

import xbmc
import xbmcgui

import sublib.utils


class model():
    def __repr__(self):
        return repr(vars(self))

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
            if imdb.startswith("tt"):
                setattr(self, "imdb", imdb)
            for k in ["tvdb", "tmdb", "slug", "trakt"]:
                if k in traktids and not traktids[k].strip() == "":
                    setattr(self, k, traktids[k].strip())
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
