import urllib.request
from bs4 import BeautifulSoup
class Text:
    def __init__(self, url):
        self.__title = None
        self.__text = []
        self.__url = url
    def getTitle(self):
        return self.__title
    def getText(self):
        return self.__text
    def getUrl(self):
        return self.__url
    def setTitle(self, title):
        self.__title = title
    def setText(self, text):
        self.__text.append(text)
class WebScraping:
    def __init__(self):
        self.texts = []
        self.urlError = []
        self.contError = 0
    def getInfosHtml(self, url):
        try:
            page = urllib.request.urlopen(url)
            #Parse o html na variável 'page' e armazene-o no formato BeautifulSoup
            soup = BeautifulSoup(page, 'html5lib')
            text = Text(url)
            text.setTitle(soup.title.text.strip())
            list_item = soup.find('body')
            if 'wikipedia' in url:
                list_item = soup.find('div', attrs={'class': 'mw-content-ltr'})
                p = list_item.find_all(["h2","h3","h4","p","ul"])
            else:
                p = list_item.find_all(["h1","p", "br"])
            for i in p:
                text.setText(i.text.strip())
                # print(i.text.strip())
            self.texts.append(text)
            return True
        except:
            self.contError+=1
            self.urlError.append(url)
            print("Error url")
            return False
            
    def getErros(self):
        return self.contError, self.urlError
    def getTexts(self):
        return self.texts
    