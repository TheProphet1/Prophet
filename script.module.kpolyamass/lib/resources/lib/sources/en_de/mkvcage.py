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

import re, urllib, urlparse, os, time

from resources.lib.modules import control
from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import debrid
from resources.lib.modules import source_utils
from resources.lib.modules import dom_parser2
from resources.lib.modules import workers


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['www.mkvcage.ws']
        self.base_link = 'https://www.mkvcage.fun/'
        self.search_link = '?s=%s'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            url = urllib.urlencode(url)
            return url
        except BaseException:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
            url = urllib.urlencode(url)
            return url
        except BaseException:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url is None: return

            url = urlparse.parse_qs(url)
            url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
            url['title'], url['premiered'], url['season'], url['episode'] = title, premiered, season, episode
            url = urllib.urlencode(url)
            return url
        except BaseException:
            return

    def sources(self, url, hostDict, hostprDict):

        try:
            self._sources = []

            if url is None: return self._sources

            if debrid.status() is False: raise Exception()

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']

            hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else data['year']

            query = '%s S%02dE%02d' % (
                data['tvshowtitle'], int(data['season']),
                int(data['episode'])) if 'tvshowtitle' in data else '%s %s' % (
                data['title'], data['year'])
            query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', ' ', query)

            url = self.search_link % urllib.quote_plus(query)
            url = urlparse.urljoin(self.base_link, url)
            r = client.request(url)

            posts = client.parseDOM(r, 'article', attrs={'id': 'post-.+?'})

            items = []
            hostDict = hostDict + hostprDict

            for post in posts:
                try:
                    data = client.parseDOM(post, 'h2', attrs={'class': 'entry-title'})[0]
                    t = client.parseDOM(data, 'a')[0]
                    u = client.parseDOM(data, 'a', ret='href')[0]
                    try:
                        size = re.findall('((?:\d+\.\d+|\d+\,\d+|\d+)\s*(?:GB|GiB|MB|MiB))', t)[0]
                        div = 1 if size.endswith(('GB', 'GiB')) else 1024
                        size = float(re.sub('[^0-9|/.|/,]', '', size)) / div
                        size = '%.2f GB' % size
                    except BaseException:
                        size = '0'
                    items += [(t, u, size)]
                except BaseException:
                    pass
            urls = []

            for item in items:
                try:
                    name = item[0]
                    name = client.replaceHTMLCodes(name)
                    t = re.sub('(\.|\(|\[|\s)(\d{4}|S\d+E\d+|S\d+|3D)(\.|\)|\]|\s|)(.+|)', '', name, flags=re.I)
                    if not cleantitle.get(t) == cleantitle.get(title): raise Exception()
                    y = re.findall('[\.|\(|\[|\s](\d{4}|S\d*E\d*|S\d*)[\.|\)|\]|\s]', name, re.I)[-1].upper()
                    if not y == hdlr: raise Exception()
                    quality, info = source_utils.get_release_quality(name, item[1])
                    info = item[2]
                    urls.append((item[1], quality, info))
                except BaseException:
                    pass

            threads = []
            for i in urls: threads.append(workers.Thread(self._get_sources, i[0], i[1], i[2], hostDict))
            for i in threads: i.start()

            alive = [x for x in threads if x.is_alive() is True]
            while alive:
                alive = [x for x in threads if x.is_alive() is True]
                time.sleep(0.5)

            return self._sources
        except BaseException:
            return self._sources

    def _get_sources(self, url, quality, info, hostDict):
        try:
            r = client.request(url)
            p_link = dom_parser2.parse_dom(r, 'a', {'class': ['buttn', 'blue']})
            p_link = p_link[0].attrs['href']
            password = dom_parser2.parse_dom(r, 'pre')[-1]
            password = password.content
            post = 'id=%s&mypass=%s&submit=Submit' % (re.findall('(\d+)', p_link)[0], password)
            data = client.request(p_link.replace('http://', 'https://'), post=post)

            extra_link = client.parseDOM(r, 'a', attrs={'class': 'buttn prem'}, ret='href')[0]
            r = client.request(extra_link)
            r = client.parseDOM(r, 'ol')

            links = client.parseDOM(r, 'a', ret='href')
            links += client.parseDOM(data, 'a', ret='href')
            links = [i for i in links if not any(x in url for x in ['.rar.', '.zip.', '.iso.']) or not any(
                url.endswith(x) for x in ['.rar', '.zip', '.iso'])]
            for url in links:
                try:
                    valid, host = source_utils.is_host_valid(url, hostDict)
                    if not valid: continue
                    if 'mega.co.nz' not in url:
                        self._sources.append(
                            {'source': host, 'quality': quality, 'language': 'en', 'url': url, 'info': info,
                             'direct': False, 'debridonly': True})
                except BaseException:
                    pass
        except BaseException:
            pass

    def resolve(self, url):
        return url