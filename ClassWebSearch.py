import urllib
import requests

class WebSearch:

    def __init__(self,token):
        self.headers = {
            "x-rapidapi-key": token,
            "x-rapidapi-host" :"google-search3.p.rapidapi.com"
        }

    def search(self, text):
        query = {
            "q": text,
            "num": 20
        }
        resp = requests.get("https://rapidapi.p.rapidapi.com/api/v1/search/" + urllib.parse.urlencode(query), headers=self.headers)
        links = []
        titulos = []
        results = resp.json()
        for i in results['results']:
            links.append(i['link'])
            titulos.append(i['title'])
            
        return links, titulos