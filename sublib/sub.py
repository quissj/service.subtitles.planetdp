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


class model(object):
    @property
    def label(self):
        return self.__label

    @property
    def iso(self):
        return self.__iso

    @property
    def sync(self):
        return self.__sync

    @property
    def cc(self):
        return self.__cc

    @property
    def rating(self):
        return self.__rating

    @property
    def args(self):
        return self.__args

    @property
    def kwargs(self):
        return self.__kwargs

    @label.setter
    def label(self, val):
        if not isinstance(val, (str, unicode)):
            raise(TypeError(type(val)))
        self.__label = val

    @iso.setter
    def iso(self, val):
        if val not in sublib.iso639.two:
            raise(ValueError(val))
        self.__iso = val

    @cc.setter
    def cc(self, val):
        if not isinstance(val, bool):
            raise(TypeError(type(val)))
        self.__cc = val

    @sync.setter
    def sync(self, val):
        if not isinstance(val, bool):
            raise(TypeError(type(val)))
        self.__sync = val

    @rating.setter
    def rating(self, val):
        if not isinstance(val, int):
            raise(TypeError(type(val)))
        if val < 0 or val > 5:
            raise(ValueError(val))
        self.__rating = val

    def __init__(self, label, iso, rating=0, sync=False, cc=False):
        self.__label = None
        self.__iso = None
        self.rating = rating
        self.label = label
        self.iso = iso
        self.sync = sync
        self.cc = cc
        self.__args = []
        self.__kwargs = {}

    def download(self, *args, **kwargs):
        self.__args = args
        self.__kwargs = kwargs

    def __repr__(self):
        return repr({
                     "label": self.__label,
                     "iso": self.__iso,
                     "rating": self.__rating,
                     "sync": self.__sync,
                     "cc": self.__cc,
                     "args": self.__args,
                     "kwargs": self.__kwargs
                     })
