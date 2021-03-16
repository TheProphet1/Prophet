# -*- coding: utf-8 -*-

#######################################################################
# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# @tantrumdev wrote this file.  As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return. - Muad'Dib
# ----------------------------------------------------------------------------
#######################################################################

import re

try: from urlparse import parse_qs, urljoin
except ImportError: from urllib.parse import parse_qs, urljoin
try: from urllib import urlencode, unquote_plus, quote
except ImportError: from urllib.parse import urlencode, unquote_plus, quote

from prophetscrapers.modules import cache
from prophetscrapers.modules import cleantitle
from prophetscrapers.modules import client
from prophetscrapers.modules import debrid
from prophetscrapers.modules import source_utils
from prophetscrapers.modules import utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['pirateproxy.live', 'thepiratebay.org', 'thepiratebay.fun', 'thepiratebay.asia', 'tpb.party',
                                'thehiddenbay.com', 'piratebay.live', 'thepiratebay.zone']
        self._base_link = None
        # self.search_link = '/s/?q=%s&page=1&&video=on&orderby=99' #-page flip does not work
        self.search_link = '/search/%s/1/99/200' #-direct link can flip pages


    @property
    def base_link(self):
        if not self._base_link:
            self._base_link = cache.get(self.__get_base_url, 120, 'https://%s' % self.domains[0])
        return self._base_link


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            url = urlencode(url)
            return url
        except:
            return


    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
            url = urlencode(url)
            return url
        except:
            return


    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url is None:
                return
            url = parse_qs(url)
            url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
            url['title'], url['premiered'], url['season'], url['episode'] = title, premiered, season, episode
            url = urlencode(url)
            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url is None:
                return sources

            if debrid.status() is False:
                return sources

            data = parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
            title = title.replace('&', 'and').replace('Special Victims Unit', 'SVU')

            hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else data['year']

            query = '%s %s' % (title, hdlr)
            query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', '', query)

            url = self.search_link % quote(query)
            url = urljoin(self.base_link, url)
            # log_utils.log('url = %s' % url, log_utils.LOGDEBUG)

            html = client.request(url)
            html = html.replace('&nbsp;', ' ')

            try:
                results = client.parseDOM(html, 'table', attrs={'id': 'searchResult'})
            except:
                return sources

            url2 = url.replace('/1/', '/2/')

            html2 = client.request(url2)
            html2 = html2.replace('&nbsp;', ' ')

            try:
                results += client.parseDOM(html2, 'table', attrs={'id': 'searchResult'})
            except:
                return sources

            results = ''.join(results)

            rows = re.findall('<tr(.+?)</tr>', results, re.DOTALL)
            if rows is None:
                return sources

            for entry in rows:
                try:
                    try:
                        url = 'magnet:%s' % (re.findall('a href="magnet:(.+?)"', entry, re.DOTALL)[0])
                        url = str(client.replaceHTMLCodes(url).split('&tr')[0])
                    except:
                        continue

                    try:
                        name = re.findall('class="detLink" title=".+?">(.+?)</a>', entry, re.DOTALL)[0]
                        name = client.replaceHTMLCodes(name)
                        name = unquote_plus(name).replace(' ', '.')

                        t = name.split(hdlr)[0].replace(data['year'], '').replace('(', '').replace(')', '').replace('&', 'and').replace('.US.', '.').replace('.us.', '.')
                        if cleantitle.get(t) != cleantitle.get(title):
                            continue
                    except:
                        continue

                    if hdlr not in name:
                        continue

                    quality, info = source_utils.get_release_quality(name, url)

                    try:
                        size = re.findall('((?:\d+\.\d+|\d+\,\d+|\d+)\s*(?:GB|GiB|MB|MiB))', entry)[-1]
                        dsize, isize = utils._size(size)
                    except:
                        dsize, isize = 0, ''

                    info.insert(0, isize)

                    info = ' | '.join(info)

                    sources.append({'source': 'torrent', 'quality': quality, 'language': 'en', 'url': url,
                                                'info': info, 'direct': False, 'debridonly': True, 'size': dsize})
                except:
                    continue

            return sources

        except:
            return sources


    def __get_base_url(self, fallback):
        try:
            for domain in self.domains:
                try:
                    url = 'https://%s' % domain
                    result = client.request(url, limit=1, timeout='10')
                    result = re.findall('<input type="submit" title="(.+?)"', result, re.DOTALL)[0]
                    if result and 'Pirate Search' in result:
                        return url
                except:
                    pass
        except:
            pass

        return fallback


    def resolve(self, url):
        return url