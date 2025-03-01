import requests
import json
import time
import os
from flask import Flask
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

TOKEN = "7539406137:AAEKFhg1M65H6Birs-RpCYObYeOAr6Yfq8g"  # Token del bot
chat_id = "@hechosesencialeschile"  # ID del grupo de Telegram
timer = 30
fecha_old = ''
EEFF_file_url = ''
AARR_file_url = ''

# Cargar empresas desde JSON
with open("empresas.json", "r") as archivo:
    Empresas = json.load(archivo)

app = Flask(__name__)

def scraping_loop():
    global fecha_old, EEFF_file_url, AARR_file_url

    while True:
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
            url = "https://www.cmfchile.cl/institucional/mercados/novedades_envio_sa_ifrs.php?mm_ifrs=12&aa_ifrs=2024"
            respuesta = requests.get(url, headers=headers, timeout=10)

            if respuesta.status_code == 200:
                print("Iniciando scraping...")
                soup = BeautifulSoup(respuesta.text, "html.parser")
                hechos = soup.find_all("tr")[1]

                fecha_primer_envio = hechos.find_all("td")[0].text.strip()
                fecha_segundo_envio = hechos.find_all("td")[1].text.strip()
                razon_social = hechos.find_all("td")[2].text.strip()
                tipo_balance = hechos.find_all("td")[3].text.strip()
                tipo_envio = hechos.find_all("td")[5].text.strip()
                urlEmpresa = str(hechos.find_all("td")[2].find_all("a")[0]).split('"')[1].replace('amp;', '')

                # Recorrer empresas
                for valor in Empresas:
                    if fecha_old != fecha_segundo_envio and str(valor) == str(razon_social):

                        urlPdf = "https://www.cmfchile.cl/institucional/mercados/" + urlEmpresa
                        responsePdf = requests.get(urlPdf, headers=headers, timeout=10)

                        if responsePdf.status_code == 200:
                            soup = BeautifulSoup(responsePdf.content, "html.parser")
                            download_links = soup.find_all("a", href=True)

                            for link in download_links:
                                if "Estados financieros (PDF)" in link.text.strip():
                                    EEFF_file_url = "https://www.cmfchile.cl/institucional/mercados/" + link["href"]
                                if "Análisis Razonado" in link.text.strip():
                                    AARR_file_url = "https://www.cmfchile.cl/institucional/mercados/" + link["href"]

                        else:
                            print(f"Error al acceder a la página de la empresa: {responsePdf.status_code}")

                        mensaje = (f"NUEVO ESTADO FINANCIERO\n\nFecha: {fecha_segundo_envio}\n"
                                   f"Empresa: {razon_social}\nTipo Balance: {tipo_balance}\n"
                                   f"Estado Financiero: {EEFF_file_url}\nAnálisis Razonado: {AARR_file_url}")

                        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                                      data={"chat_id": chat_id, "text": mensaje})

                        fecha_old = fecha_segundo_envio

            else:
                print('Error en la petición:', respuesta.status_code)

        except requests.RequestException as e:
            print(f"Error de conexión: {e}")

        time.sleep(timer)

def keep_awake():
    """ Envía un ping cada 5 minutos para evitar que Render apague la app. """
    while True:
        try:
            requests.get("https://ef-5nl1.onrender.com", timeout=5)
            print("Ping enviado para mantener la app activa")
        except requests.RequestException:
            print("Error al enviar el ping")
        time.sleep(300)  # 5 minutos

# Iniciar tareas en segundo plano
executor = ThreadPoolExecutor(max_workers=2)
executor.submit(scraping_loop)
executor.submit(keep_awake)

@app.route('/')
def home():
    return "Servicio de scraping en ejecución."

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8083))  # Usa el puerto de Render o 8083 por defecto
    app.run(host='0.0.0.0', port=port)
