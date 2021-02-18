#!/usr/bin/env python
# coding: utf-8

# ## Imports


import pandas as pd
from bs4 import BeautifulSoup
from datetime import date
from msedge.selenium_tools import Edge, EdgeOptions
import time

# ## Initialize 

options = EdgeOptions()
options.use_chromium = True

prefs = {'profile.default_content_setting_values': {'cookies': 2, 'images': 2, 'javascript': 2, 
                            'plugins': 2, 'popups': 2, 'geolocation': 2, 
                            'notifications': 2, 'auto_select_certificate': 2, 'fullscreen': 2, 
                            'mouselock': 2, 'mixed_script': 2, 'media_stream': 2, 
                            'media_stream_mic': 2, 'media_stream_camera': 2, 'protocol_handlers': 2, 
                            'ppapi_broker': 2, 'automatic_downloads': 2, 'midi_sysex': 2, 
                            'push_messaging': 2, 'ssl_cert_decisions': 2, 'metro_switch_to_desktop': 2, 
                            'protected_media_identifier': 2, 'app_banner': 2, 'site_engagement': 2, 
                            'durable_storage': 2}}
options.add_experimental_option('prefs', prefs)
options.add_argument("start-maximized")
options.add_argument("disable-infobars")
options.add_argument("--disable-extensions")

driver = Edge(options = options)

records = []

driver.get('https://www.google.com/search?q=tangsel&safe=strict&tbs=sbd:1,qdr:d&tbm=nws&sxsrf=ALeKk03UP-ODOblunk0JH9Lkg-Te07lcew:1613352141124&ei=zcwpYJ2HB-TC3LUPt7i4kAw&start=0&sa=N&ved=0ahUKEwjdoZOK3eruAhVkIbcAHTccDsI4ChDy0wMIhgE&biw=1242&bih=597&dpr=1.1')


def extract_records(item):
    judul_berita = item.h3.text
    tanggal = item.find('span', {'class': 'r0bn4c rQMQod'}).text
    sumber_berita = item.find('div', {'class': 'BNeawe UPmit AP7Wnd'}).text
    highlight = item.find('div', {'class': 'BNeawe s3v9rd AP7Wnd'}).text.split('·')[1]
    URL = item.a.get('href')[7:]
            
    result = (judul_berita, tanggal, sumber_berita, highlight, URL )
    return result


def compiler():
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    list_berita = soup.find_all('div', {'class':'ZINbbc xpd O9g5cc uUPGi'})
            
    for item in list_berita:
        records.append(extract_records(item))
        
        
def execute():
    time.sleep(3)
    compiler()
    while True:
        try:
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            next_page = soup.find('a', {'aria-label':'Halaman berikutnya'})
            next_page = next_page.get('href')
            next_page = 'https://www.google.com/'+ next_page
            compiler()
            driver.get(next_page)
        except AttributeError:
            driver.quit()
            break
            
execute()
df_result = pd.DataFrame(records, columns=['Judul Berita', 'Tanggal Posting', 'Sumber', 'Highlight', 'URL'])




df_result['URL'] = df_result['URL'].map(lambda x: x.split('&')[0])
df_result['URL'] = df_result['URL'].map(lambda x: x.split('%')[0])
filter1 = df_result['Highlight'].map(lambda x: x.lower())
baca_juga = list(df_result[filter1.str.contains('baca juga')].index)
df_result = df_result.drop(index=baca_juga)
seputar_tangsel = list(df_result[filter1.str.contains('seputar tangsel')].index)
df_result = df_result.drop(index=seputar_tangsel)
kabartangsel = list(df_result[df_result['Sumber'].str.contains('Kabartangsel.com')].index)
df_result = df_result.drop(index=kabartangsel)
df_result.drop_duplicates(subset='Judul Berita', keep='first', inplace=True, ignore_index=True)








today = str( date.today().strftime("%d-%b-%Y"))
df_result.to_excel(r'E:\berita_tangsel{}.xlsx'.format(today),index=False)


