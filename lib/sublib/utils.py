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

import xbmcvfs
import xbmcgui
import re
import urllib
import urllib2
import cookielib.CookieJar
import unicodedata
import HTMLParser

_cj = cookielib.CookieJar()
_opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(_cj))
_hparser = HTMLParser.HTMLParser()

_ua = "KODI / XBMC Sublib Library"

epiregs = [
            r"s([0-9]*)xe([0-9]*)",
            r"s([0-9]*)x([0-9]*)",
            r"s([0-9]*)e([0-9]*)",
            r"s([0-9]*)-e([0-9]*)",
            r"s([0-9]*)_e([0-9]*)",
            r"([0-9]*)x([0-9]*)",
            r"([0-9]*)-([0-9]*)",
            r"([0-9]*)_([0-9]*)",
            r"-([0-9]*)",
            r"_([0-9]*)",
            ]


def normstr(s):
    s = unicodedata.normalize('NFKD', unicode(unicode(str, 'utf-8')))
    return s.encode('ascii', 'ignore')


def dformat(d, m):
    r = {}
    for k, v in d.iteritems():
        try:
            r[k] = m(v)
        except:
            r[k] = v
    return r


def download(u, query=None, data=None, referer=None, binary=False, ua=None,
             encoding="utf-8"):
    if not ua:
        ua = _ua
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
    res = _opener.open(req)
    if not binary:
        res = res.read()
        res = res.decode(encoding)
        res = _hparser.unescape(res)
    return res


def checkarchive(fname):
    with open(fname) as f:
        sign = f.read(4)
    if sign == "Rar!":
        return "rar"
    elif sign == "":
        return "zip"


def selectfile(files):
    dialog = xbmcgui.Dialog()
    index = dialog.select('Choose Subtitle', files)
    return files[index]


def getar(fname, ar, show, season, episode):
    if fname.endswith("/"):
        fname = fname[:-1]
    ds, fs = xbmcvfs.listdir(fname)
    if not len(fs):
        # empty archive
        return
    elif len(fs) == 1:
        # archive with 1 file
        f = fs[0]
    else:
        # archive with lots of file
        if show:
            found = []
            for f in fs:
                matchstr = f.lower().replace(" ", "")
                print matchstr
                if not episode == -1:
                    for reg in epiregs:
                        m = re.search(reg, matchstr)
                        if m and m.lastindex == 2 and\
                                m.group(1).isdigit() and \
                                m.group(2).isdigit() and \
                                int(m.group(1)) == season and \
                                int(m.group(2)) == episode:
                            print 7777
                            print m.lastindex
                            print m.group(1)
                            print "!!!!!!matched %s:%s" % (matchstr, reg)
                            found.append(f)
                            break
                        if m and m.lastindex == 1 and\
                                m.group(1).isdigit() and \
                                int(m.group(1)) == episode:
                            print "!!!!!!matched %s:%s" % (matchstr, reg)
                            found.append(f)
                            break

            if not len(found):
                print 22222222
                found = fs
            if len(found) == 1:
                print 33333333
                f = found[0]
            else:
                print 4444444444
                f = selectfile(found)
            print f
        else:
            f = selectfile(fs)
    return f


def getsub(fname, show, season, episode):
    isar = checkarchive(fname)
    if isar:
        arname = getar(fname, isar, show, season, episode)
        if not arname:
            return
        uri = "%s://[%s]/%s" % (isar, fname, arname)
        # fix for rar filesystem crashes sometimes
        fname = fname + "___unpack"
        f = xbmcvfs.File(uri)
        with open(fname, "w") as out:
            out.write(f.read())
        f.close()
        return fname
    else:
        return fname
