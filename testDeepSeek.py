import requests
from bs4 import BeautifulSoup
import os

# URL de la página de la CMF
url = "https://www.cmfchile.cl/institucional/mercados/entidad.php?auth=&send=&mercado=V&rut=96639280&rut_inc=&grupo=0&tipoentidad=RGAGF&vig=VI&row=AAAwy2ACTAAABzXAAS&mm=12&aa=2024&tipo=I&orig=lista&control=svs&tipo_norma=IFRS&pestania=3"

# Encabezados para simular una solicitud de navegador
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Realizar la solicitud HTTP
response = requests.get(url, headers=headers)

# Verificar si la solicitud fue exitosa
print (response.status_code)
if response.status_code == 200:
    # Parsear el contenido HTML de la página
    soup = BeautifulSoup(response.content, "html.parser")

    # Buscar enlaces de descarga (ajusta el selector según la estructura de la página)
    download_links = soup.find_all("a", href=True)

    # Filtrar enlaces que contengan archivos de estados financieros
    for link in download_links:
        #print (link.text.strip())
        if "Estados financieros (PDF)" in link.text.strip():
            print (link.text.strip())

            file_url = link["href"]
            print (file_url)
            
            # Descargar el archivo
            #file_response = requests.get(file_url, headers=headers)

            #if file_response.status_code == 200:
                # Guardar el archivo en el directorio actual
            #    file_name = os.path.basename(file_url)
            #    with open(file_name, "wb") as file:
            #        file.write(file_response.content)
            #    print(f"Archivo descargado: {file_name}")
            #else:
            #    print(f"Error al descargar el archivo: {file_url}")
else:
    print(f"Error al acceder a la página: {response.status_code}")