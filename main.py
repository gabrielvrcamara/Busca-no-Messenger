
from ClassWebScraping import WebScraping
import os
from flask import Flask, request
import json
import traceback
import requests
from ClassWebSearch import WebSearch
import time
from fpdf import FPDF
from requests_toolbelt import MultipartEncoder
from flask_caching import Cache

inicio = """Olá, Seja bem-vindo(a) ao seu auxiliar de pesquisas no Messenger. Como posso ajudar? 
            \n\n - Escreva as palavras-chave entre colchetes [].
            \n - Digite a lingua que deseja a busca após a duvida. 
            \nEx: [Linguagens de Programação], \n[Como usar Java - Português] """

num_sites = None
token_fb = '__TOKEN__'
senhaAPI = "__TOKEN__"
token_rapidapi = "__TOKEN__"
cache = Cache()


app = Flask(__name__)

cache.init_app(app=app, config={"CACHE_TYPE": "filesystem",'CACHE_DIR': '/tmp'})

pesquisa = WebSearch(token_rapidapi)
def isQuestion(text):
    if "[" in text:
        a = text.split("[")
        if "]" in a[1]:
            b = a[1].split("]")
            return b[0]
        else:
            pass
    else:
        return "Erro de formato"

def send_menssage(sender, text):
    try:
        payload = {'recipient': {'id': sender}, 'message': {'text': str(text)}}
        r = requests.post('https://graph.facebook.com/v2.6/me/messages/?access_token=' + token_fb, json=payload)
        print("usuario: "+ str(sender) +" -- request: " + str(r))
    except:
        print("usuario: "+ str(sender) +" -- Erro ao enviar menssagem.")

def send_file(sender, titulo):
    payload = {'recipient': json.dumps({'id': sender}),'message': json.dumps({'attachment': {'type': 'file', 'payload': {}}}), 'filedata': (str(titulo)+".pdf", open(str(sender) +".pdf", 'rb'))}
    multipart_data = MultipartEncoder(payload)
    multipart_header = {'Content-Type': multipart_data.content_type}
    r = requests.post('https://graph.facebook.com/v2.6/me/messages/?access_token=' + token_fb, data=multipart_data,  headers=multipart_header)
    print("usuario: "+ str(sender) +" -- request: " + str(r))

@app.route('/', methods=['GET', 'POST'])
def webhook():
    global num_sites
    text = ""
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font('Arial', '', 'Arial.ttf', uni=True)
    pdf.set_font("Arial", size=10)
    if request.method == 'POST':
        try:
            resposta_ = ""
            data = json.loads(request.data.decode())
            try:        
                text = data['entry'][0]['messaging'][0]['message']['text']
            except:
                pass
            try:
                num = int(text)
                num = True
            except:
                num = False
            if text != "":
                sender = data['entry'][0]['messaging'][0]['sender']['id']
                if "[" in text and "]" in text:
                    palavraChave = isQuestion(text)
                    print("usuario: " + str(sender) + " -- PalavraChave: "+ palavraChave)
                    send_menssage(sender,"Pesquisando...")
                    site_, titulo_ = pesquisa.search(palavraChave)
                    cache.set("site", site_)
                    cache.set('titulo', titulo_)
                    num_sites = len(cache.get('site')) - (len(cache.get('site')) - 5)
                    for i in range(0,num_sites):
                        resposta_ += str(i) + " - Titulo: " + str(cache.get('titulo')[i]) + " - Url: " + str(cache.get('site')[i]) + "\n\n" 
                    resposta_ += "\nEscolha o numero do site que deseja ler.\nPara mais links digite #"
                    send_menssage(sender,resposta_)
                elif (num or text == '#'):
                    if text == "#":
                        num_sites = num_sites + 5
                        for i in range(0,num_sites):
                            try:
                                resposta_ += str(i) + " - Titulo: " + str(cache.get('titulo')[i]) + " - Url: " + str(cache.get('site')[i]) + "\n\n" 
                            except:
                                break
                        resposta_ += "\nEscolha o numero do site que deseja ler.\nPara mais links digite #"
                        send_menssage(sender,resposta_)
                    else:
                        try:
                            num = int(text)
                            if type(num) is int:
                                print("usuario: "+ str(sender) +" -- numero -- " + str(num))
                                print("usuario: " + str(sender) + " -- url: " + str(cache.get('site')[num]))
                                if cache.get('site')[num][-4::] == ".pdf":
                                    print("pdf")
                                    r = requests.get(str(cache.get('site')[num]), stream=True)
                                    file = open(str(sender) + '.pdf', "wb")
                                    file.write(r.content)
                                    file.close()
                                    send_file(str(sender),str(cache.get('titulo')[num]))
                                    os.remove(str(sender) + '.pdf')
                                else:
                                    texts = WebScraping()
                                    result = texts.getInfosHtml(cache.get('site')[num])
                                    if result:
                                        send_menssage(sender, "Pegando informacoes do site...")
                                        resposta_ += "URL: " + texts.getTexts()[0].getUrl()
                                        resposta_ += "\nTitulo: " + texts.getTexts()[0].getTitle()
                                        resposta_ += "\n\nTexto: "
                                        pdf.multi_cell(h=5.0, align='L', w=0, txt=str(resposta_) + "\n", border=0)
                                        send_menssage(sender, "Gerando PDF...")
                                        for i in texts.getTexts()[0].getText():
                                            pdf.multi_cell(h=5.0, align='L', w=0, txt=str(i) + "\n", border=0)
                                        pdf_ = False
                                        try:
                                            pdf.output(str(sender) + '.pdf')
                                            pdf_ = True
                                        except:
                                            print("usuario: "+ str(sender) +" -- Erro ao criar pdf")
                                            send_menssage(sender,"Erro na ultima fase de gerar o PDF. Desculpe")                                                
                                        time.sleep(1.5)
                                        if pdf_:
                                            send_file(sender, texts.getTexts()[0].getTitle())
                                            os.remove(str(sender) + '.pdf')
                                    else:
                                        send_menssage(sender,"Este link parace estar com problemas. Por favor, escolha outro.")
                                        print("usuario: "+ str(sender) +" -- Erro no link")                                
                        except:
                            send_menssage(sender,"Escolha invalida. Informe o numero do site.")
                            print("usuario: "+ str(sender) +" -- Escolha invalida")
                else:
                    send_menssage(sender, inicio)
        except Exception as e:
            print(traceback.format_exc())
    elif request.method == 'GET': # Para a verificação inicial
        if request.args.get('hub.verify_token') == senhaAPI: 
            return request.args.get('hub.challenge')
        return "Wrong Verify Token"
    return "Nothing"
    
if __name__ == '__main__':
    app.run(debug=True)
