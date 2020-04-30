# -*- coding: utf-8 -*-

import os,re,sys,xbmc,xbmcaddon,json,base64,urllib,urlparse,unicodedata,requests,shutil,xbmcplugin,xbmcgui,socket,urllib2
from xbmcplugin import addDirectoryItem, endOfDirectory
import datetime, time


addon_id            = xbmcaddon.Addon().getAddonInfo('id')
addon_name          = xbmcaddon.Addon().getAddonInfo('name')
home_folder         = xbmc.translatePath('special://home/')
addon_folder        = os.path.join(home_folder, 'addons')
art_path            = os.path.join(addon_folder, addon_id)
resources_path      = os.path.join(art_path, 'resources')
lib_path            = os.path.join(resources_path, 'lib')
skin_used           = xbmc.getSkinDir()
addon_icon          = os.path.join(art_path,'icon.png')
addon_fanart        = os.path.join(art_path,'fanart.jpg')
content_type        = "movies"

def addDir(name,url,mode,iconimage,fanart,description):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)+"&fanart="+urllib.quote_plus(fanart)+"&description="+urllib.quote_plus(description)
    ok=True
    liz=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={"Title": name,"Plot":description,})
    liz.setProperty('fanart_image', fanart)
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    return ok
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

def addDirVid(name,url,mode,iconimage,fanart,description):
    ok=True
    liz = xbmcgui.ListItem(label=name, thumbnailImage=iconimage)
    liz.setProperty('fanart_image', fanart)
    liz.setInfo( type="Video", infoLabels={"Title": name,"Plot":description,})
    liz.setProperty('IsPlayable', 'true')
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)+"&fanart="+urllib.quote_plus(fanart)+"&description="+urllib.quote_plus(description)
    is_folder = False
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
    return ok
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

def arconaitv(url):
    User_Agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'
    headers = {'User_Agent':User_Agent}
    url = "https://www.arconaitv.us/"
    html = requests.get(url,headers=headers).content
    block = re.compile('<div class="stream-nav shows" id="shows">(.+?)<div class="acontainer">',re.DOTALL).findall(html)
    match = re.compile('href=(.+?) title=(.+?)>',re.DOTALL).findall(str(block))
    for link,name in match:
        name = name.replace("\\'","").encode('utf-8')
        link = link.replace("\\'","")
        link = "https://www.arconaitv.us/"+link
        image = get_thumb(name,html)
        if not image:
            image = get_other(name,html)
        if not image: image = ""
        addDirVid(name,link,5,image,addon_fanart,name)

def arconaimovie(url):
    User_Agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'
    headers = {'User_Agent':User_Agent}
    url = "https://www.arconaitv.us/"
    html = requests.get(url,headers=headers).content
    block5 = re.compile('<div class="stream-nav movies" id="movies">(.+?)<div class="acontainer">',re.DOTALL).findall(html)
    match5 = re.compile('href=(.+?) title=(.+?)>',re.DOTALL).findall(str(block5)) 
    for link,name in match5:
        name = name.replace("\\'","").encode('utf-8')
        link = link.replace("\\'","")
        link = "https://www.arconaitv.us/"+link
        image = get_other(name,html)
        if not image: image = "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/0d920358-1c79-4669-b107-2b22e0dd7dcd/d8nntky-04e9b7c7-1d09-44d8-8c24-855a19988294.png?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7InBhdGgiOiJcL2ZcLzBkOTIwMzU4LTFjNzktNDY2OS1iMTA3LTJiMjJlMGRkN2RjZFwvZDhubnRreS0wNGU5YjdjNy0xZDA5LTQ0ZDgtOGMyNC04NTVhMTk5ODgyOTQucG5nIn1dXSwiYXVkIjpbInVybjpzZXJ2aWNlOmZpbGUuZG93bmxvYWQiXX0.To4Xk896HVjziIt-LjTSotZR0x7NVCbroAIkiSpik84"
        addDirVid(name,link,5,image,addon_fanart,name)

def arconainetwork(url):
    User_Agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'
    headers = {'User_Agent':User_Agent}
    url = "https://www.arconaitv.us/"
    html = requests.get(url,headers=headers).content
    block4 = re.compile('<div class="stream-nav cable" id="cable">(.+?)<div class="acontainer">',re.DOTALL).findall(html)
    match4 = re.compile('href=(.+?) title=(.+?)>',re.DOTALL).findall(str(block4))
    for link,name in match4:
        name = name.replace("\\'","").encode('utf-8')
        link = link.replace("\\'","")
        link = "https://www.arconaitv.us/"+link
        image = get_thumb(name,html)
        if not image:
            if name == "ABC":
                image = "https://vignette.wikia.nocookie.net/superfriends/images/f/f2/Abc-logo.jpg/revision/latest?cb=20090329152831"
            elif name == "Animal Planet":
                image = "https://seeklogo.com/images/D/discovery-animal-planet-logo-036312EA16-seeklogo.com.png"
            elif name == "Bravo Tv":
                image = "https://kodi.tv/sites/default/files/styles/medium_crop/public/addon_assets/plugin.video.bravo/icon/icon.png?itok=VXH52Iyf"
            elif name == "CNBC":
                image = "https://i2.wp.com/republicreport.wpengine.com/wp-content/uploads/2014/06/cnbc1.png?resize=256%2C256"
            elif name == "NBC":
                image = "https://designobserver.com/media/images/mondrian/39684-NBC_logo_m.jpg"
            elif name == "SYFY":
                image = "https://kodi.tv/sites/default/files/styles/medium_crop/public/addon_assets/plugin.video.syfy/icon/icon.png?itok=ZLTAqywa"
            elif name == "USA Network ":
                image = "https://crunchbase-production-res.cloudinary.com/image/upload/c_lpad,h_256,w_256,f_auto,q_auto:eco/v1442500192/vzcordlt6w0xsnhcsloa.png"
            elif name == "WWOR-TV":
                image = "https://i.ytimg.com/vi/TlhcM0jciZo/hqdefault.jpg"
            elif name == "BBC America":
                image = "https://watchuktvabroad.net/dev/wp-content/uploads/2014/05/bbc1-icon.png"
            elif name == "MavTV":
                image = "https://yt3.ggpht.com/a-/ACSszfGbltb7pvCn52Ojd3vEHPk_2v_1_HJosa_h=s900-mo-c-c0xffffffff-rj-k-no"
            elif name == "MSNBC":
                image = "https://upload.wikimedia.org/wikipedia/commons/7/74/MSNBC_logo.png"
            elif name == "NASA HD":
                image = "http://pluspng.com/img-png/nasa-logo-png-nasa-logo-3400.png"
        if not image: image = ""
        addDirVid(name,link,5,image,addon_fanart,name)

def get_thumb(name,html):
    block2 = re.compile('<div class="content">(.+?)<div class="stream-nav shows" id="shows">',re.DOTALL).findall(html)
    match2 = re.compile('<img src=(.+?) alt=(.+?) />',re.DOTALL).findall(str(block2))
    for image,name2 in match2:
        if name in name2:
            image = image.replace("\\'", "")
            image = "https://www.arconaitv.us"+image
            return image

def get_other(name,html):
    block3 = re.compile("<div class='row stream-list-featured'>(.+?)<div class='row stream-list'>",re.DOTALL).findall(html)
    match3 = re.compile('title=(.+?) class.+?<img src=(.+?) alt',re.DOTALL).findall(str(block3))
    for name3,image3 in match3:
        if name in name3:
            image3 = image3.replace("\\'", "")
            image3 = "https://www.arconaitv.us"+image3
            return image3 