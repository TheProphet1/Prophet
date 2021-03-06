# -*- coding: utf-8 -*-
import re
import time
from  resources.modules.client import get_html
global global_var,stop_all#global
global_var=[]
stop_all=0

 
from resources.modules.general import clean_name,check_link,server_data,replaceHTMLCodes,domain_s,similar,all_colors,base_header
from  resources.modules import cache
try:
    from resources.modules.general import Addon
except:
  import Addon
type=['movie','tv','torrent']

import urllib,logging,base64,json

def get_links(tv_movie,original_title,season_n,episode_n,season,episode,show_original_year,id):
    global global_var,stop_all
    
    if tv_movie=='movie':
      search_url=[clean_name(original_title,1).replace(' ','+')+'+'+show_original_year]
      type='movie'
    else:
     
      search_url=[clean_name(original_title,1).replace(' ','+')+'+s'+season_n+'e'+episode_n]
      type='television'
  
    
    
    all_links=[]
    regex='<tr(.+?)</tr>'
    regex1=re.compile(regex,re.DOTALL)
    
    regex='href="magnet(.+?)".+?<a href=".+?">(.+?)<.+?span class=.+?<td>(.+?)</td>'
    regex2=re.compile(regex,re.DOTALL)
            
    for itt in search_url:
      for page in range(1,4):
        if stop_all==1:
            break
       
       
       
        x=get_html('https://bitcq.com/search?q={0}&category%5B%5D=1&page={1}'.format(itt,str(page)),headers=base_header).content()
            
        logging.warning('https://bitcq.com/search?q={0}&category%5B%5D=1&page={1}'.format(itt,str(page)))
        macth_pre=regex1.findall(x)
       
        for items in macth_pre:
            
            
            macth=regex2.findall(items)
           
            if stop_all==1:
                break
            
            for link,title,size in macth:
                         
                         if stop_all==1:
                                break
                         if '4k' in title:
                            res='2160'
                         elif '2160' in title:
                              res='2160'
                         elif '1080' in title:
                              res='1080'
                         elif '720' in title:
                              res='720'
                         elif '480' in title:
                              res='480'
                         elif '360' in title:
                              res='360'
                         else:
                              res='HD'
                        
                         o_link=link
                       
                         try:
                             o_size=size
                             size=float(o_size.replace('GB','').replace('MB','').replace(",",'').strip())
                             if 'MB' in o_size:
                               size=size/1000
                         except:
                            size=0
                         max_size=int(Addon.getSetting("size_limit"))
                  
                         if size<max_size:
                          
                           all_links.append((title.replace('using magnet link','').strip(),'magnet'+link,str(size),res))
                       
                           global_var=all_links
    return global_var
        
    