# -*- coding: utf-8 -*-

"""
    Copyright (C) 2020, TonyH & Skydarks

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
"""

### Imports ###
import xbmc,xbmcaddon,xbmcgui,xbmcplugin,base64,os,re,unicodedata,requests,time,string,sys,urllib,urllib2,json,urlparse,datetime,zipfile,shutil,uuid
import __builtin__
from datetime import timedelta
from bs4 import BeautifulSoup
from resources.lib import tools
import js2py


skin_used           = xbmc.getSkinDir()
addon_id            = xbmcaddon.Addon().getAddonInfo('id')
addon_name          = xbmcaddon.Addon().getAddonInfo('name')
home_folder         = xbmc.translatePath('special://home/')
addon_folder        = os.path.join(home_folder, 'addons')
art_path            = os.path.join(addon_folder, addon_id)
resources_path      = os.path.join(art_path, 'resources')
user_data_folder    = os.path.join(home_folder, 'userdata')
addon_data_folder   = os.path.join(user_data_folder, 'addon_data')
icon                = os.path.join(art_path,'icon.png')
fanart              = os.path.join(art_path,'fanart.jpg')
content_type        = "movies"


def start():
    tools.addDir("[COLOR=orange]ArconaiTV Tv Shows[/COLOR]","arconai_tvshows",1,icon,fanart,"ArconaiTV Tv Shows")
    tools.addDir("[COLOR=orange]ArconaiTV Movie Channels[/COLOR]","arconai_movies",2,icon,fanart,"ArconaiTV Movie Channels")
    tools.addDir("[COLOR=orange]ArconaiTV Network Channels[/COLOR]","arconai_networks",3,icon,fanart,"ArconaiTV Network Channels")

def get_params():
    param=[]
    paramstring=sys.argv[2]
    if len(paramstring)>=2:
        params=sys.argv[2]
        cleanedparams=params.replace('?','')
        if (params[len(params)-1]=='/'):
            params=params[0:len(params)-2]
        pairsofparams=cleanedparams.split('&')
        param={}
        for i in range(len(pairsofparams)):
            splitparams={}
            splitparams=pairsofparams[i].split('=')
            if (len(splitparams))==2:
                param[splitparams[0]]=splitparams[1]
    return param

xbmcplugin.setContent(int(sys.argv[1]), 'movies')


params=get_params()
url=None
name=None
mode=None
iconimage=None
description=None
query=None
type=None


try:
    url=urllib.unquote_plus(params["url"])
except:
    pass
try:
    name=urllib.unquote_plus(params["name"])
except:
    pass
try:
    iconimage=urllib.unquote_plus(params["iconimage"])
except:
    pass
try:
    mode=int(params["mode"])
except:
    pass
try:
    description=urllib.unquote_plus(params["description"])
except:
    pass
try:
    query=urllib.unquote_plus(params["query"])
except:
    pass
try:
    type=urllib.unquote_plus(params["type"])
except:
    pass

if mode==None or url==None or len(url)<1:
    start()
elif mode==1:
    tools.arconaitv(url)
elif mode==2:
    tools.arconaimovie(url)
elif mode==3:
    tools.arconainetwork(url)
elif mode==5:
    agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36"
    data = requests.get(url).content
    soup = BeautifulSoup(data,'html.parser')
    try:
        script = soup.select("script")[6]
        script = re.compile("var _(.+?)</script>",re.DOTALL).findall(str(script))[0].strip()
    except:
        try:
            script = soup.select("script")[7]
            script = re.compile("var _(.+?)</script>",re.DOTALL).findall(str(script))[0].strip()
        except:
            try:
                script = soup.select("script")[8]
                script = re.compile("var _(.+?)</script>",re.DOTALL).findall(str(script))[0].strip()
            except:
                pass
    newScript = script.replace("eval(","var a =")
    newScript = "var _" + newScript
    newScript = newScript[:-1]
    newScript = newScript.replace("decodeURIComponent(escape(r))", "r.slice(305,407)")
    res = js2py.eval_js(newScript)
    link = res.replace("'","") + "|Referer=" + url + "&User-Agent=" + agent
    liz = xbmcgui.ListItem(name, path=link)
    infoLabels={"title": name}
    liz.setInfo(type="video", infoLabels=infoLabels)
    liz.setProperty('IsPlayable', 'true')
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)

xbmcplugin.endOfDirectory(int(sys.argv[1]))