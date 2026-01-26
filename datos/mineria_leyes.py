import requests
from bs4 import BeautifulSoup
import os
import json
import datetime
import pdfplumber

# -------------------------------
# CONFIGURACIÓN
# -------------------------------
BASE_URL = "https://www.hcnl.gob.mx/trabajo_legislativo/leyes/"
CARPETA_PDFS = "datos/pdfs"
CARPETA_JSON = "datos/json"

os.makedirs(CARPETA_PDFS, exist_ok=True)
os.makedirs(CARPETA_JSON, exist_ok=True)

FECHA_HOY = datetime.date.today().isoformat()

# -------------------------------
# OBTENER LINKS DE PDFs
# -------------------------------
print("🔍 Obteniendo lista de leyes...")

respuesta = requests.get(BASE_URL)
soup = BeautifulSoup(respuesta.text, "html.parser")

links_pdf = [
    a["href"] for a in soup.find_all("a", href=True)
    if a["href"].endswith(".pdf")
]

print(f"📄 PDFs encontrados: {len(links_pdf)}")

# -------------------------------
# PROCESAR PDFs
# -------------------------------
resultados = []

for i, link in enumerate(links_pdf, start=1):
    url_pdf = link if link.startswith("http") else f"https://www.hcnl.gob.mx{link}"
    nombre_pdf = url_pdf.split("/")[-1]
    ruta_pdf = os.path.join(CARPETA_PDFS, nombre_pdf)

    print(f"⬇️ ({i}) Descargando {nombre_pdf}")

    pdf_data = requests.get(url_pdf)
    with open(ruta_pdf, "wb") as f:
        f.write(pdf_data.content)

    # -------------------------------
    # EXTRAER DATOS DEL PDF
    # -------------------------------
    with pdfplumber.open(ruta_pdf) as pdf:
        num_paginas = len(pdf.pages)
        texto = ""

        for pagina in pdf.pages[:2]:  # solo primeras 2 páginas
            extraido = pagina.extract_text()
            if extraido:
                texto += extraido + "\n"

    resumen = texto[:500].replace("\n", " ")

    resultados.append({
        "archivo": nombre_pdf,
        "fecha_descarga": FECHA_HOY,
        "paginas": num_paginas,
        "resumen": resumen,
        "url": url_pdf
    })

# -------------------------------
# GUARDAR JSON
# -------------------------------
archivo_json = os.path.join(CARPETA_JSON, f"leyes_{FECHA_HOY}.json")

with open(archivo_json, "w", encoding="utf-8") as f:
    json.dump(resultados, f, ensure_ascii=False, indent=2)

print("✅ Proceso finalizado")
print(f"📁 Archivo generado: {archivo_json}")
