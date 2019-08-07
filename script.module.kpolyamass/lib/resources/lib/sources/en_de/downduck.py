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

import re, urllib, urlparse

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import debrid
from resources.lib.modules import source_utils
from resources.lib.modules import dom_parser2 as dom
from resources.lib.modules import workers


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['www.downduck.com']
        self.base_link = 'http://www.downduck.com'
        self.search_link = 'index.php?do=search&subaction=search&story={0}&sa=search'

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

            if url is None:
                return self._sources

            if debrid.status() is False:
                raise Exception()

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '')
                         for i in data])

            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']

            hdlr = 'S%02dE%02d' % (int(data['season']), int(
                data['episode'])) if 'tvshowtitle' in data else data['year']

            query = '%s S%02dE%02d' % (data['tvshowtitle'], int(data['season']), int(
                data['episode'])) if 'tvshowtitle' in data else '%s %s' % (data['title'], data['year'])
            query = re.sub(r'(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', ' ', query)

            url = self.search_link.format(urllib.quote_plus(query))
            url = urlparse.urljoin(self.base_link, url)
            self.hostDict = hostprDict + hostDict
            r = client.request(url)
            items = zip(client.parseDOM(r, 'td', attrs={'class': 'ss_topwhite'})[1:],
                        client.parseDOM(r, 'div', attrs={'class': 'short_story'}))

            items = [(i[0]) for i in items if data['imdb'] in i[1]]
            items = [dom.parse_dom(i, 'a', req='href') for i in items]
            items = [(i[0].attrs['href'], i[0].content) for i in items]

            _items = []
            for i in items:
                try:
                    name = i[1]
                    name = client.replaceHTMLCodes(name)
                    t = re.sub(r'(\.|\(|\[|\s)(\d{4}|S\d*E\d*|S\d*|3D)(\.|\)|\]|\s|)(.+|)', '', name, re.I)
                    if not cleantitle.get(t) == cleantitle.get(title):
                        raise Exception()
                    try:
                        y = re.findall(r'(?:\.|\(|\[|\s*|)(S\d+E\d+|S\d+)(?:\.|\)|\]|\s*|)', name, re.I)[-1].upper()
                    except BaseException:
                        y = re.findall(r'(?:\.|\(|\[|\s*|)(\d{4})(?:\.|\)|\]|\s*|)', name, re.I)[0].upper()
                    if not y == hdlr:
                        raise Exception()
                    _items.append((i[0], i[1]))
                except BaseException:
                    pass

            threads = []
            for i in _items:
                threads.append(workers.Thread(self._get_sources, i[0], i[1]))

            [i.start() for i in threads]
            [i.join() for i in threads]

            return self._sources
        except BaseException:
            return self._sources

    def _get_sources(self, url, name):
        try:
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            data = client.request(url)
            quality, info = source_utils.get_release_quality(name, name)
            size = client.parseDOM(data, 'div', attrs={'class': 'short_story'})[0]
            try:
                size = re.findall('((?:\d+\,\d+\.\d+|\d+\.\d+|\d+\,\d+|\d+)\s*(?:GB|GiB|Gb|MB|MiB|Mb))', size)[0]
                div = 1 if size.endswith(('GB', 'GiB', 'Gb')) else 1024
                size = float(re.sub('[^0-9|/.|/,]', '', size.replace(',', '.'))) / div
                size = '%.2f GB' % size
                info.append(size)
            except BaseException:
                pass
            patron = r'''((?:http|ftp|https)://[\w_-]+(?:(?:\.[\w_-]+)+)[\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])'''
            links = re.findall(patron, data, flags=re.MULTILINE | re.DOTALL)
            links = [i for i in links if not any(x in i for x in ['.rar', '.zip', '.iso', '.google'])]
            info = ' | '.join(info)
            for _url in links:
                valid, host = source_utils.is_host_valid(_url, self.hostDict)
                if not valid:
                    continue
                host = client.replaceHTMLCodes(host)
                host = host.encode('utf-8')
                self._sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': _url,
                                      'info': info, 'direct': False, 'debridonly': True})
        except BaseException:
            pass

    def resolve(self, url):
        return url



