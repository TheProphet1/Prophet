# -*- coding: utf-8 -*-

'''
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

import re

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['123movies4u.pro', '123movies4u.ch', '123movies4u.me']
        self.base_link = 'https://123movies4u.pro'
        self.movie_link = '/movie/%s'
        self.tv_link = '/show/%s/season/%s/episode/%s'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            title = cleantitle.geturl(title)
            url = self.base_link + self.movie_link % title
            return url
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = cleantitle.geturl(tvshowtitle)
            return url
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if not url: return
            url = self.base_link + self.tv_link % (url, season, episode)
            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []
        if 'movie' in url:
            quality = '720p'
        if 'show' in url:
            quality = 'SD'
        try:
            r = client.request(url)
            try:
                match = re.compile('<IFRAME style="z-index:9999;WIDTH:100%; " SRC="(.+?)://(.+?)/(.+?)"').findall(r)
                for http, host, url in match:
                    url = '%s://%s/%s' % (http, host, url)
                    host = host.replace('www.', '')
                    valid, host = source_utils.is_host_valid(host, hostDict)
                    if valid:
                        sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url, 'direct': False, 'debridonly': False})
                match2 = re.compile('onclick="window.open\("(.+?)://(.+?)/(.+?)"\)').findall(r)
                for http, host, url in match2:
                    url = '%s://%s/%s' % (http, host, url)
                    host = host.replace('www.', '')
                    valid, host = source_utils.is_host_valid(host, hostDict)
                    if valid:
                        sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url, 'direct': False, 'debridonly': False})
            except:
                return
        except Exception:
            return
        return sources

    def resolve(self, url):
        return url

