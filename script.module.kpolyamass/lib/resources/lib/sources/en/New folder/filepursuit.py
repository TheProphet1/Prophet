# -*- coding: utf-8 -*-

'''
    Eggman Add-on 
   
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


import re, urllib, urlparse, time, json

from resources.lib.modules import source_utils
from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import workers
#from resources.lib.modules import cfscrape

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['filepursuit.com']
        self.base_link = 'https://filepursuit.com'
        self.search_link = '/srch/%s/type/video'

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

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']

            hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else data['year']

            query = '%s S%02dE%02d' % (data['tvshowtitle'], int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else '%s %s' % (data['title'], data['year'])
            query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', '', query)

            p_data = 'searchQuery=%s&startrow=%s&type=video&filetype=&sort=datedesc'
            urls = [p_data % (urllib.quote_plus(query), '0'),
                    p_data % (urllib.quote_plus(query), '49'),
                    p_data % (urllib.quote_plus(query), '98'),
                    p_data % (urllib.quote_plus(query), '147')]

            threads = []
            for url in urls:
                threads.append(workers.Thread(self._get_sources, url, title, hdlr))
            for i in threads: i.start()

            alive = [x for x in threads if x.is_alive() is True]
            while alive:
                alive = [x for x in threads if x.is_alive() is True]
                time.sleep(0.5)

            return self._sources
        except BaseException:
            return self._sources


    def _get_sources(self, url, title, hdlr):
        items = []
        try:
            p_link = urlparse.urljoin(self.base_link, 'jsn/v1/search.php')
            #scraper = cfscrape.create_scraper()
            headers = {'User-Agent': client.randommobileagent('android')}
            r = client.request(p_link, post=url, headers=headers)
            r = json.loads(r)

            for post in r:
                url = post['link']
                name = post['filename']

                try:
                    size = post['filesize']
                    size = re.findall('((?:\d+\,\d+|\d+\.\d+|\d+)\s*(?:GB|GiB|MB|MiB))', size)[-1]
                    div = 1 if size.endswith(('GB', 'GiB')) else 1024
                    size = float(re.sub('[^0-9|/.|/,]', '', size)) / div
                    size = '%.2f GB' % size
                except BaseException:
                    size = '0'

                items.append((name, url, size))

        except BaseException:
            pass

        for item in items:
            try:
                name = item[0]
                name = client.replaceHTMLCodes(name).replace('%20', '').replace('%27', "'")

                t = name.split(hdlr)[0]
                if not cleantitle.get(t) == cleantitle.get(title): raise Exception()

                try:
                    y = re.findall('[\.|\(|\[|\s|\_|\-](S\d+E\d+|S\d+)[\.|\)|\]|\s|\_|\-]', name, re.I)[-1].upper()
                except BaseException:
                    y = re.findall('[\.|\(|\[|\s\_|\-](\d{4})[\.|\)|\]|\s\_|\-]', name, re.I)[-1].upper()

                if not y == hdlr: raise Exception()

                fmt = re.sub('(.+)(\.|\(|\[|\s)(\d{4}|S\d+E\d+|S\d+)(\.|\)|\]|\s)', '', name.upper())
                fmt = re.split('\.|\(|\)|\[|\]|\s|\-|\_', fmt)
                fmt = [i.lower() for i in fmt]

                if any(i.endswith(('subs', 'sub', 'dubbed', 'dub')) for i in fmt): raise Exception()
                if any(i in ['extras', 'french', 'italian', 'trailer', 'sample'] for i in fmt): raise Exception()

                url = client.replaceHTMLCodes(item[1])
                url = url.encode('utf-8')
                if any(x in url.lower() for x in ['.rar.', '.zip.', '.iso.']) or any(
                        url.lower().endswith(x) for x in ['.rar', '.zip', '.iso']): raise Exception()

                if any(x in url.lower() for x in ['youtube', 'sample', 'trailer']): raise Exception()
                info = []
                if '3d' in fmt or '.3d.' in fmt: info.append('3D')
                if any(i in ['hevc', 'h265', 'x265'] for i in fmt): info.append('HEVC')
                quality, info2 = source_utils.get_release_quality(url, str(fmt))
                if not item[2] == '0': info.append(item[2])
                info = ' | '.join(info)

                self._sources.append({'source': 'DL', 'quality': quality, 'language': 'en', 'url': url, 'info': info, 'direct': True, 'debridonly': False})

            except BaseException:
                pass

    def resolve(self, url):
        return url