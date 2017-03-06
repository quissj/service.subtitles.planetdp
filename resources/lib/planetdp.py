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

#{'code': '', 'episode': '', 'temp': True, 'title': 'Doctor Strange', 'season': '', 'year': '2016', 'rar': False, 'tvshow': '', 'file_original_path': u'https://r2---sn-nv47lnl7.googlevideo.com/videoplayback?id=a3d38568da65b255&itag=22&source=webdrive&requiressl=yes&ttl=transient&pl=22&ei=iem7WKyxPMXHqwXPnJpw&mime=video/mp4&lmt=1487275698590738&ip=176.232.180.189&ipbits=0&expire=1488724425&sparams=ei,expire,id,ip,ipbits,itag,lmt,mime,mm,mn,ms,mv,pl,requiressl,source,ttl&signature=3326125CD56AC1DC764C71C5FE77148CF5FC6354.73D83274718CC9E8454C6279663F10636267B00D&key=cms1&app=explorer&cms_redirect=yes&mm=31&mn=sn-nv47lnl7&ms=au&mt=1488714568&mv=m', '3let_language': ['eng', 'tur']}
{'code': 'tt1211837', 'episode': '', 'temp': True, 'title': 'Doctor Strange', 'season': '', 'year': '2016', 'rar': False, 'fps': 'Player.Process(videofps)', 'tvshow': '', 'file_original_path': u'https://r2---sn-nv47lnl7.googlevideo.com/videoplayback?id=a3d38568da65b255&itag=22&source=webdrive&requiressl=yes&ttl=transient&pl=22&ei=iem7WKyxPMXHqwXPnJpw&mime=video/mp4&lmt=1487275698590738&ip=176.232.180.189&ipbits=0&expire=1488724425&sparams=ei,expire,id,ip,ipbits,itag,lmt,mime,mm,mn,ms,mv,pl,requiressl,source,ttl&signature=3326125CD56AC1DC764C71C5FE77148CF5FC6354.73D83274718CC9E8454C6279663F10636267B00D&key=cms1&app=explorer&cms_redirect=yes&mm=31&mn=sn-nv47lnl7&ms=au&mt=1488714568&mv=m', '3let_language': ['eng', 'tur']}
import urllib2
import urllib
import re
import HTMLParser
import os
from cookielib import CookieJar


domain = "https://www.planetdp.org"
encoding = "utf-8"
hparser = HTMLParser.HTMLParser()
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
ua = "KODI / XBMC PlanetDP Subtitle Addon"
cj = CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))


def _page(u, query=None, data=None, referer=None, binary=False):
    if query:
        q = urllib.urlencode(query)
        u += "?" + q
    if data:
        data = urllib.urlencode(data)
    header = {"User-Agent": ua}
    if referer:
        header["Referer"] = referer
    print u
    req = urllib2.Request(u, data, header)
    res = opener.open(req)
    if not binary:
        res = res.read()
        res = res.decode(encoding)
        res = hparser.unescape(res)
    return res


def norm(txt):
    txt = txt.replace(" ", "")
    txt = txt.lower()
    return txt


def scrapesubs(page, langs):
    results = []
    for row in re.findall("<tr(.*?)</tr>", page, re.DOTALL):
        index = 0
        result = {}
        for column in re.findall("<td(.*?)</td>", row, re.DOTALL):
            index += 1
            if index == 1:
                res = re.search('href="(.*?)".*?title="(.*?)">(.*?)<', column)
                result["link"] = domain + res.group(1)
                result["name"] = "%s: %s" % (res.group(3), res.group(2))
            if index == 2:
                res = re.search("<img src='(.*?)'", column)
                country = res.group(1).split("/")[-1].split(".")[0]
                result["iso"] = dptoiso[country]
            if index == 3:
                res = re.search("<a.*?>(.*?)</a", column)
                result["name"] += " ~ %s" % res.group(1)
            if index == 5:
                fps = column.replace(" fps", "") 
                fps = fps.strip()
                if fps.isdigit():
                    result["fps"] = float(fps)
        if not result == {} and result["iso"] in langs:
            results.append(result)
    return results


def scrapemovie(page, langs):
    results = []
    for row in re.findall('<tr.*?class="rowinfo(.*?</tr>\s*?<tr.*?class="alt_div.*?)</tr>', page, re.DOTALL):
        index = 0
        result = {}
        trans = None
        for column in re.findall("<td(.*?)</td>", row, re.DOTALL):
            index += 1
            if index == 1:
                res = re.search('href="(.*?)".*?title="(.*?)"', column)
                result["link"] = domain + res.group(1)
                result["name"] = "%s" % res.group(2)
            if index == 2:
                res = re.search("src='(.*?)'", column)
                country = res.group(1).split("/")[-1].split(".")[0]
                result["iso"] = dptoiso[country]
            if index == 5:
                res = re.search("<a.*?>(.*?)</a", column)
                if res:
                    trans = res.group(1)
            if index == 3:
                fps = column.replace(" fps", "") 
                fps = fps.strip()
                if fps.isdigit():
                    result["fps"] = float(fps)
            if index == 9:
                version = re.search('title="(.*?)"', column)
                result["name"] += ": %s" % version.group(1)
        if not result == {} and result["iso"] in langs:
            if trans:
                result["name"] += " ~ %s" % trans 
            results.append(result)
    return results


def scraperesult(item, page):
    #if we are here we must have a year
    results = []
    matches = re.findall('<div class="col-sm-7 col-md-9">.*?<a href=\'(.*?)\' class="movie__title link--huge">(.*?)</a>.*?<strong>Aka: </strong>(.*?)</p>', page, re.DOTALL)
    nname = norm(item["title"])
    for link, name1, aka in matches:
        submatch = re.match("(.*?)\s\(([0-9]{4})\)", name1)
        if submatch.lastindex == 2:
            name = submatch.group(1)
            year = int(submatch.group(2))
            if year == item["year"] and \
                (nname == norm(name) or nname == norm(aka)):
                results = scrapemovie(_page(domain + link), item["3let_language"])
                break
    return results


def searchimdb(item):
    query = {
             "title": item["imdb"],
             "translator": "",
             "name": "",
             "release_info": "",
             "fps": "",
             "season": item["season"],
             "episode": "",
             "lang": "",
             }
    return scrapesubs(_page(domain + "/subtitlelist", query), item["3let_language"])


def searchnameyear(item):
    #if we are here we must have a year
    if item["tvshow"]:
        show = 1
    else:
        show = 0
    query = {
             "title": item["title"],
             "year_date": item["year"],
             "is_serial": show
             }
    page = _page(domain + "/movie/search", query)
    ismultiple = re.search("btn--info", page)
    if ismultiple:
        return scraperesult(item, page)
    else:
        return scrapemovie(page, item["3let_language"])


def searchpredict(item):
    query = {
             "title": item["title"],
             "translator": "",
             "name": "",
             "release_info": "",
             "fps": "",
             "season": item["season"],
             "episode": "",
             "lang": "",
             }
    return scrapesubs(_page(domain + "/subtitlelist", query), item["3let_language"])


def search(item):
    if item["tvshow"]:
        item["title"] = item["tvshow"]
        item["season"] = ""
        item["episode"] = ""
    elif item["season"] < 0:
        item["season"] = ""
    results = []
    if item["imdb"] and item["imdb"].startswith("tt"):
        results = searchimdb(item)
    if not len(results) and item["year"]:
        results = searchnameyear(item)
    if not len(results):
        results = searchpredict(item)
    return results


def downloadsub(link, path):
    subs = []
    page = _page(link)
    token = re.search('<input type="hidden" name="_token" value="(.*?)">', page)
    subid = re.search('rel\-id="(.*?)"', page)
    uniqk = re.search('rel\-tag="(.*?)"', page)

    if token and subid and uniqk:
        data = {
                "_token": token.group(1),
                "subtitle_id": subid.group(1),
                "uniquekey": uniqk.group(1)
                }
        remfile = _page(domain + "/subtitle/download", None, data, link, True)
        fname = remfile.info().getheader("Content-Disposition")
        fname = re.search('filename="(.*?)"', fname)
        fname = fname.group(1)
        fname = os.path.join(path, fname)
        with open(fname, "wb") as f:
            f.write(remfile.read())
        subs.append(fname)
    return subs
