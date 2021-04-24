import urllib
import requests

class WebSearch:

    def __init__(self,token):
        self.token = token
        self.headers = {
            "x-rapidapi-key": self.token[0],
            "x-rapidapi-host" :"google-search3.p.rapidapi.com"
        }

    def search(self, text):
        query = {
            "q": text,
            "num": 20
        }
        chave = True
        while chave:
            resp = requests.get("https://rapidapi.p.rapidapi.com/api/v1/search/" + urllib.parse.urlencode(query), headers=self.headers)
            results = resp.json()
            if 'message' in results:
                if  "You have exceeded" in results['message']:
                    self.headers['x-rapidapi-key'] = self.token[1]
                    print(self.headers)
                    print("\n --- Limite maximo atingido por mes. trocando de api. --- \n")
                    continue
            if len(results['results']) == 0:
                print("resultado = 0")
                continue
            else:
                chave = False 
        links = []
        titulos = []
        for i in results['results']:
            links.append(i['link'])
            titulos.append(i['title'])
            
        return links, titulos