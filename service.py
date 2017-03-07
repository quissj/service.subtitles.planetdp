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
import sublib

import re
import os

domain = "https://www.planetdp.org"
dptoiso = {
           "tr": "tr",
           "en": "en",
           "sp": "es",
           "gr": "de",
           "fr": "fr",
           }
isotoquery = {
           "tr": u"Türkçe",
           "en": u"İngilizce",
           "es": u"İspanyolca",
           "de": u"Almanca",
           "fr": u"Fransızca",
              }


def norm(txt):
    txt = txt.replace(" ", "")
    txt = txt.lower()
    return txt


class planetdp(sublib.service):

    def search(self):
        if self.item.imdb and self.item.imdb.startswith("tt"):
            self.searchimdb()
        if not self.num() and self.item.year:
            self.searchnameyear()
        if not self.num():
            self.searchpredict()

    def download(self, link):
        page = self.query(link)
        token = re.search('<input type="hidden" name="_token" value="(.*?)">', page)
        subid = re.search('rel\-id="(.*?)"', page)
        uniqk = re.search('rel\-tag="(.*?)"', page)

        if token and subid and uniqk:
            data = {
                    "_token": token.group(1),
                    "subtitle_id": subid.group(1),
                    "uniquekey": uniqk.group(1)
                    }
            remfile = self.query(domain + "/subtitle/download", None, data, link, True)
            fname = remfile.info().getheader("Content-Disposition")
            fname = re.search('filename="(.*?)"', fname)
            fname = fname.group(1)
            fname = os.path.join(self.path, fname)
            with open(fname, "wb") as f:
                f.write(remfile.read())
            self.addfile(fname)

    def scrapesubs(self, page):
        for row in re.findall("<tr(.*?)</tr>", page, re.DOTALL):
            index = 0
            link = None
            name = None
            iso = None
            for column in re.findall("<td(.*?)</td>", row, re.DOTALL):
                index += 1
                if index == 1:
                    res = re.search('href="(.*?)".*?title="(.*?)">(.*?)<', column)
                    link = domain + res.group(1)
                    name = "%s: %s" % (res.group(3), res.group(2))
                if index == 2:
                    res = re.search("<img src='(.*?)'", column)
                    if res:
                        country = res.group(1).split("/")[-1].split(".")[0]
                        iso = dptoiso[country]
                    else:
                        iso = "tr"
                if index == 3:
                    res = re.search("<a.*?>(.*?)</a", column)
                    name += " ~ %s" % res.group(1)
            if link and iso and name:
                sub = self.sub(name, iso)
                sub.download(link)
                self.addsub(sub)

    def scrapemovie(self, page):
        for row in re.findall('<tr.*?class="rowinfo(.*?<tr.*?class="alt_div.*?<tr.*?class="alt_div.*?)</tr>', page, re.DOTALL):
            index = 0
            link = None
            name = None
            iso = None
            trans = None
            for column in re.findall("<td(.*?)</td>", row, re.DOTALL):
                index += 1
                if index == 1:
                    res = re.search('href="(.*?)".*?title="(.*?)"', column)
                    link = domain + res.group(1)
                    name = "%s" % res.group(2)
                if index == 2:
                    res = re.search("src='(.*?)'", column)
                    if res:
                        country = res.group(1).split("/")[-1].split(".")[0]
                        iso = dptoiso[country]
                    else:
                        iso = "tr"
                if index == 5:
                    res = re.search("<a.*?>(.*?)</a", column)
                    if res:
                        trans = res.group(1)
                if index == 12:
                    version = re.search(' / Notlar</b>(.*?)</span>', column)
                    if version:
                        name += re.sub("<.*?>", "", version.group(1))
            if link and name and iso:
                if trans:
                    name += " ~ %s" % trans
                sub = self.sub(name, iso)
                sub.download(link)
                self.addsub(sub)

    def scraperesult(self, page):
        #if we are here we must have a year
        divs = re.findall('<div class="col-sm-7(.*?)</div>', page, re.DOTALL)
        nname = norm(self.item.title)
        for div in divs:
            rlinkname = re.search("<a href='(.*?)'  itemprop=\"url\".*?>(.*?)</a>", div)
            if rlinkname:
                link = rlinkname.group(1)
                name1 = rlinkname.group(2)
                name1 = re.sub("<.*?>", "", name1)
            else:
                continue
            akas = []
            aka = re.search('Aka: </strong>(.*?)</p>', div)
            if aka:
                akas = [norm(x.strip()) for x in aka.group(1).split(",")]
            submatch = re.match("(.*?)\s\(([0-9]{4})\)", name1)
            if submatch.lastindex == 2:
                name = submatch.group(1)
                year = int(submatch.group(2))
                if year == self.item.year and \
                    (nname == norm(name) or nname in akas):
                    page = self.request(domain + link)
                    self.scrapemovie(page)
                    break

    def searchimdb(self):
        if self.item.season < 0:
            season = ""
        query = {
                 "title": self.item.imdb,
                 "translator": "",
                 "name": "",
                 "release_info": "",
                 "fps": "",
                 "season": season,
                 "episode": "",
                 "lang": "",
                 }

        page = self.request(domain + "/subtitlelist", query)
        return self.scrapesubs(page)

    def searchnameyear(self):
        #if we are here we must have a year
        query = {
                 "title": self.item.title,
                 "year_date": self.item.year,
                 "is_serial": int(self.item.show)
                 }
        page = self.request(domain + "/movie/search", query)
        ismultiple = re.search("btn--info", page)
        if ismultiple:
            return self.scraperesult(page)
        else:
            return self.scrapemovie(page)

    def searchpredict(self):
        if self.item.season < 0:
            season = ""
        query = {
                 "title": self.item.title,
                 "translator": "",
                 "name": "",
                 "release_info": "",
                 "fps": "",
                 "season": season,
                 "episode": "",
                 "lang": "",
                 }
        page = self.request(domain + "/subtitlelist", query)
        return self.scrapesubs(page)
