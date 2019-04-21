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

import urllib, urlparse
from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['brmovies.org']
        self.base_link = 'http://www.brmovies.net/'
        self.build_link = '%s-720p-1080p'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year, 'aliases': aliases}
            url = urllib.urlencode(url)
            return url
        except BaseException:
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url is None: return sources

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

            query = '%s %s' % (data['title'], data['year'])
            query = self.build_link % urllib.quote_plus(cleantitle.getsearch(query)).replace('+', '-')
            url = urlparse.urljoin(self.base_link, query)
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'}
            headers['Referer'] = self.base_link

            r = client.request(url, headers=headers)

            if not r: return sources
            if not data['imdb'] in r: return sources
            frames = client.parseDOM(r, 'a', ret='data-player', attrs={'class': 'list-player'})
            extra = client.parseDOM(r, 'div', attrs={'id': 'tab-download'})[0]
            frames += client.parseDOM(extra, 'a', ret='href')

            for frame in frames:
                if 'quot' in frame:
                    fix_frame = frame.split('&quot;')
                    fix_frame = [i for i in fix_frame if 'http' in i][0]
                else:
                    fix_frame = frame


                if 'linkbin' in fix_frame:
                    r = client.request(fix_frame, headers=headers)
                    posts = client.parseDOM(r, 'div', attrs={'class': 'link-panel row'})
                    frames_720 = client.parseDOM(posts[0], 'a', ret='href', attrs={'class': 'click-link'})
                    for frame in frames_720:
                        quality = '720p'
                        valid, host = source_utils.is_host_valid(frame, hostprDict)
                        if not valid: continue
                        sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': frame,
                                        'direct': False, 'debridonly': True})
                    frames_1080 = client.parseDOM(posts[1], 'a', ret='href', attrs={'class': 'click-link'})
                    for frame in frames_1080:
                        quality = '1080p'
                        valid, host = source_utils.is_host_valid(frame, hostprDict)
                        if not valid: continue
                        sources.append({'source': host, 'quality': quality, 'language': 'en', 'url':frame,
                                        'direct': False, 'debridonly': True})

                else:
                    valid, host = source_utils.is_host_valid(fix_frame, hostDict)
                    if not valid: continue

                    sources.append({'source': host, 'quality': '720p', 'language': 'en', 'url': fix_frame,
                                    'direct': False, 'debridonly': False})
            return sources
        except BaseException:
            return sources

    def resolve(self, url):
        return url