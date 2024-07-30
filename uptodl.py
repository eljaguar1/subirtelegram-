import requests
from requests import Session
from bs4 import BeautifulSoup


PATH = 'https://www.uptodown.com/'
SEARCH = 'buscar'
HEADERS = {
    'authority': 'ssm.codes',
    'accept': '*/*',
    'accept-language': 'es,es-ES;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'origin': 'https://www.uptodown.com',
    'referer': 'https://www.uptodown.com/',
    'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Microsoft Edge";v="122"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0',
}


def search(name='',tag='windows'):
    global PATH


    session = requests.Session()
    resp = session.get(PATH,headers=HEADERS)

    searchUrl = PATH + tag + '/' + SEARCH
    payload = {'singlebutton':'','q':name}
    resp = session.post(searchUrl,data=payload,headers=HEADERS)
    html = str(resp.text)
    soup = BeautifulSoup(html, "html.parser")
    items = soup.find_all('div',{'class':'item'})
    searchList = []

    for item in items:
        try:
            divname = item.find('div',{'class':'name'}).find('a')
            name = divname.next
            url =  divname['href']
            img = item.find('img')['src']
            searchList.append({'name':name,'url':url,'img':img})
        except:pass

    return searchList

def req_file_size(req):
    try:
        return int(req.headers['content-length'])
    except:
        return 0

def get_info(item,include_down_url=False):
    try:
        downUrl = item['url'] + '/descargar'

        session = requests.Session()

        resp = session.get(downUrl,headers=HEADERS)
        html = str(resp.text)
        soup = BeautifulSoup(html, "html.parser")
        try:
            id = soup.find('a',{'id':'detail-download-button'})['href']
        except:
            id = soup.find('button',{'id':'detail-download-button'})['data-download-version']


        divInfo = soup.find('div',{'class':'detail'})
        text = divInfo.findAll('h2')[0].next

        if include_down_url:
            downUrl = downUrl.replace('/descargar',f'/post-download/{id}')
            resp = session.get(downUrl,headers=HEADERS)
            soup = BeautifulSoup(resp.text, "html.parser")
            data_url = soup.find('div',{'class':'post-download'})['data-url']
            uridown = 'https://dw.uptodown.com/dwn/' + data_url
            resp = session.get(uridown,allow_redirects=True,stream=True,headers=HEADERS)
            directUrl = resp.url

        
        return {'url':directUrl,'text':text,'name':item['name'] + ' Url'}
    except:pass
    return None


	
	
	
	