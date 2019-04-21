# -*- coding: utf-8 -*-

'''
    eggman Add-on

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

import urllib, urlparse, re

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['filmxy.me']
        self.base_link = 'https://www.filmxy.one/'
        self.search_link = 'search/%s/feed/rss2/'
        self.post = 'https://cdn.filmxy.one/asset/json/posts.json'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            url = urllib.urlencode(url)
            return url
        except BaseException:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []
        try:
            if url is None: return
            data = urlparse.parse_qs(url)
            data = dict((i, data[i][0]) for i in data)
            title = data['title']
            year = data['year']

            tit = cleantitle.geturl(title + ' ' + year)
            query = urlparse.urljoin(self.base_link, tit)

            # r = self.scraper.get(query).content
            r = client.request(query, referer=self.base_link, redirect=True)
            if not data['imdb'] in r:
                return sources
            # r = client.parseDOM(r, 'item')
            # links = [(client.parseDOM(i, 'title')[0], client.parseDOM(i, 'link')[0]) for i in r if i]
            # links = [(i[0], i[1]) for i in links if cleantitle.get_simple(i[0].split('(')[0]) in cleantitle.get_simple(title)]
            # links = [i[1] for i in links if year in i[0]]
            # urls = []
            # for i in links:
            #     #r = self.scraper.get(i).content
            #     r = client.request(i, referer=)
            #     url = client.parseDOM(r, 'a', ret='href', attrs={'id':'main-down'})[0]
            #     urls.append(url)
            links = []

            try:
                down = client.parseDOM(r, 'div', attrs={'id': 'tab-download'})[0]
                down = client.parseDOM(down, 'a', ret='href')[0]
                data = client.request(down)
                frames = client.parseDOM(data, 'div', attrs={'class': 'single-link'})
                frames = [client.parseDOM(i, 'a', ret='href')[0] for i in frames if i]
                for i in frames:
                    links.append(i)

            except BaseException:
                pass
            try:
                streams = client.parseDOM(r, 'div', attrs={'id': 'tab-stream'})[0]
                streams = re.findall('''iframe src=(.+?) frameborder''', streams.replace('&quot;', ''),
                                     re.I | re.DOTALL)
                for i in streams:
                    links.append(i)
            except BaseException:
                pass

            for url in links:
                try:
                    valid, host = source_utils.is_host_valid(url, hostDict)
                    if not valid:
                        valid, host = source_utils.is_host_valid(url, hostprDict)
                        if not valid:
                            continue
                        else:
                            rd = True
                    else:
                        rd = False
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')
                    if rd:
                        sources.append(
                            {'source': host, 'quality': '1080p', 'language': 'en', 'url': url,
                             'direct': False,
                             'debridonly': True})
                    else:
                        sources.append(
                            {'source': host, 'quality': '1080p', 'language': 'en', 'url': url,
                             'direct': False,
                             'debridonly': False})
                except BaseException:
                    pass
            return sources
        except BaseException:
            return sources

    def resolve(self, url):
        return url