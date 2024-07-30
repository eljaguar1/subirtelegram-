import requests, json, os, datetime, platform, asyncio
from bs4 import BeautifulSoup
from urllib3 import response
from time import time
from pathlib import Path
from multivolumefile import MultiVolume
from py7zr import FILTER_COPY
from py7zr import SevenZipFile
from io import BufferedReader
import aiohttp
import aiofiles
import platform
sistema_operativo = platform.system()

bar = None
start_time = 0
speed = 0

fi = ['1547', '3', '8']

if sistema_operativo == "Windows":
    cmd = "cls"
elif sistema_operativo == "Linux":
    cmd = "clear"

def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(num) < 1024.0:
            return "%3.2f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.2f%s%s" % (num, 'Yi', suffix)

def format_time(seconds):
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return f'{hours:02d}h:{minutes:02d}m:{seconds:02d}s'

def make_session(type,id):
    session = requests.Session()
    resp = requests.post("http://apiserver.alwaysdata.net/session",json={"type":type,"id":id},headers={'Content-Type':'application/json'})
    data = json.loads(resp.text)
    session.cookies.update(data)
    return session

def create_progress_bar(current, total, length=20):
    filled_length = int(length * current // total)
    bar = '●' * filled_length + '○' * (length - filled_length)
    percentage = round((current / total) * 100, 2)
    elapsed_time = time() - start_time
    if current >= 0:
        speed = current / elapsed_time
        rtime = (total - current) / speed
    else:
        speed = 0
        rtime = (total - current) / speed
    return f"Uploading: {percentage}%\n[{bar}]\n{sizeof_fmt(current)}** of {sizeof_fmt(total)}\nSpeed: {sizeof_fmt(speed)}/s\nETA: {format_time(int(round(rtime)))}"

def progress_callback(current, total):
    global last_update_time
    if time() - last_update_time > 1:
        last_update_time = time()
        progress_bar = create_progress_bar(current, total)
        os.system(cmd)
        print(progress_bar)

class NextcloudClient:
    def __init__(self, base_url):
        self.host = base_url
        self.base_url = base_url

    async def upload_file(self, file_path, cookies):
        try:
            files_url = self.base_url + 'index.php/apps/files/'
            filename = file_path.split('/')[-1]
            upload_url = self.base_url + 'remote.php/webdav/cloud/' + filename
            async with aiohttp.ClientSession(cookies=cookies) as session:
                async with session.get(files_url, ssl=True) as resp:
                    text = await resp.text()
                    soup = BeautifulSoup(text, 'lxml-xml')
                    headers = {'requesttoken': soup.head['data-requesttoken']}
                    async with aiofiles.open(file_path, 'rb') as f:
                        file_size = os.path.getsize(file_path)
                        chunk_size = 1024
                        num_bars = int(file_size / chunk_size)
                        chunk = await f.read(chunk_size)
                        while chunk:
                            async with session.put(upload_url, headers=headers, data=chunk, ssl=True) as resp:
                                chunk = await f.read(chunk_size)
                    url = f'{self.base_url}remote.php/webdav/?dir=/cloud/{filename}'
                    name = url.split("/")[-1]
                    update = datetime.datetime.now()
                    year = update.year
                    month = update.month
                    day = update.day + 6
                    if day > 30:
                        month = month + 1
                        day = day - 30
                        if day < 10:
                            day = '0' + str(day)
                    expire = f"{year}-{month}-{day}"
                    data = {"attributes": "[]", "expireDate": expire, "path": "/cloud/"+name, "shareType": "3"}
                    api = self.base_url + "ocs/v2.php/apps/files_sharing/api/v1/shares"
                    async with session.post(api, data=data, headers=headers, ssl=True) as resp:
                        text = await resp.text()
                        #print(text)
                        soup = BeautifulSoup(text, 'lxml-xml')
                        f = soup.find('url').contents[0]
                        token = str(f).split('/s/')[1]
                        url = self.base_url + 's/' + token + '/download/' + name                    
                        return url
        except Exception as ex:
            return str(ex)
        
    def delete_nexc(self, url, cookies):
        try:
            files = self.host + 'index.php/apps/files/'
            resp = requests.get(files, cookies=cookies)
            soup = BeautifulSoup(resp.text,'lxml-xml')
            requesttoken = soup.find('head')['data-requesttoken']
            files = self.host + 'apps/files/'
            name = url.split("/")[-1]
            resp = requests.get(files, cookies=cookies)
            soup = BeautifulSoup(resp.text,'lxml-xml')
            value_acces = soup.find("div",attrs={"id":"avatardiv-menu"})["data-user"]
            url_delete = self.host + "remote.php/dav/files/" + str(value_acces) + name
            resp = requests.delete(url_delete, headers={"requesttoken":requesttoken}, cookies=cookies)
            return f'{name} eliminado correctamente'
        except Exception as ex:
            print(ex)
            return "error"
        




