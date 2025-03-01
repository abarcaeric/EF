import requests
import json
import threading
import time
from flask import Flask
from bs4 import BeautifulSoup
import os

TOKEN = "7539406137:AAEKVhg1M65H6Birs-RpCYObYeOAr6Yfq8g" #token acceso @BotFather 
chat_id = "@hechosesencialeschile" #id grupo
#chat_id = "6697147223" #id bot
timer = 30
fecha_old = ''
EEFF_file_url = ''
AARR_file_url = ''

# Cargar el archivo JSON de empresas a tomar en cuenta
with open("empresas.json", "r") as archivo:
    Empresas = json.load(archivo)

app = Flask(__name__)

def scraping_loop():
    global fecha_old, EEFF_file_url, AARR_file_url
    print ("iniciando...")
    while True:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        url = "https://www.cmfchile.cl/institucional/mercados/novedades_envio_sa_ifrs.php?mm_ifrs=12&aa_ifrs=2024"
        respuesta = requests.get(url, headers=headers)

        if respuesta.status_code == 200:
            print ("iniciando...")
            soup = BeautifulSoup(respuesta.text, "html.parser")

            hechos = soup.find_all("tr")[1]

            fecha_primer_envio = hechos.find_all("td")[0].text.strip()    
            fecha_segundo_envio  = hechos.find_all("td")[1].text.strip()
            razon_social = hechos.find_all("td")[2].text.strip()
            tipo_balance = hechos.find_all("td")[3].text.strip()      
            tipo_envio = hechos.find_all("td")[5].text.strip()
            urlEmpresa = str(hechos.find_all("td")[2].find_all("a")[0]) #empezamos a generar otro link web para extraer los archivos PDF
            urlEmpresa = urlEmpresa.split('"')[1].replace('amp;','')
            
            # Recorrer de las empresas
            for valor in Empresas:
                if fecha_old != fecha_segundo_envio and str(valor) == str(razon_social):

                    urlPdf = "https://www.cmfchile.cl/institucional/mercados/"+urlEmpresa #url final para traer el archivo PDF
                    responsePdf = requests.get(urlPdf, headers=headers)

                    if responsePdf.status_code == 200:
                        # Parsear el contenido HTML de la página
                        soup = BeautifulSoup(responsePdf.content, "html.parser")

                        # Buscar enlaces de descarga (ajusta el selector según la estructura de la página)
                        download_links = soup.find_all("a", href=True)

                        # Filtrar enlaces que contengan archivos de estados financieros
                        for link in download_links:
                            if "Estados financieros (PDF)" in link.text.strip():
                                EEFF_file_url = "https://www.cmfchile.cl/institucional/mercados/"+link["href"]
                            if "Análisis Razonado" in link.text.strip():
                                AARR_file_url = "https://www.cmfchile.cl/institucional/mercados/"+link["href"]
                                
                    else:
                        print(f"Error al acceder a la página: {responsePdf.status_code}")

                    mensaje = 'NUEVO ESTADO FINANCIERO\n\nFecha : ' + str(fecha_segundo_envio) + '\nEmpresa : ' + str(razon_social) + '\nTipo Balance : ' + str(tipo_balance) +  '\nEstado Financiero : ' + str(EEFF_file_url) +  '\nAnalisis Razonado : ' + str(AARR_file_url) 
                    
                    requests.post("https://api.telegram.org/bot"+TOKEN+"/sendMessage",
                        data={"chat_id": chat_id, "text": mensaje})
                    fecha_old = fecha_segundo_envio

            time.sleep(timer)

        else:
            print('Hubo un error en la peticion')
            time.sleep(timer)

# Iniciar el bucle de scraping en un hilo separado
threading.Thread(target=scraping_loop, daemon=True).start()

# Ruta de ejemplo para Flask
@app.route('/')
def home():
    return "Servicio de scraping en ejecución."

# Ejecutar Flask
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8083))  # Usa el puerto de Render o 8083 por defecto
    app.run(host='0.0.0.0', port=port)