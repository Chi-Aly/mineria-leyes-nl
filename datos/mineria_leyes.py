import requests
import os
import pdfplumber
import json
from datetime import datetime

BASE_URL = "https://www.hcnl.gob.mx/trabajo_legislativo/leyes/"
CARPETA_PDFS = "pdfs"
CARPETA_JSON = "json"

os.makedirs(CARPETA_PDFS, exist_ok=True)
os.makedirs(CARPETA_JSON, exist_ok=True)

print("📥 Descargando lista de PDFs...")

html = requests.get(BASE_URL).text

# Extraer enlaces PDF
import re
pdf_links = re.findall(r'href="(.*?\.pdf)"', html)

print(f"📄 PDFs encontrados: {len(pdf_links)}")

for link in pdf_links:
    nombre_pdf = link.split("/")[-1]
    ruta_pdf = os.path.join(CARPETA_PDFS, nombre_pdf)

    if os.path.exists(ruta_pdf):
        continue

    print(f"⬇️ Descargando {nombre_pdf}")
    r = requests.get(link)
    with open(ruta_pdf, "wb") as f:
        f.write(r.content)

print("✅ Descarga terminada")

print("\n📖 Procesando PDFs...")

for archivo in os.listdir(CARPETA_PDFS):
    if not archivo.endswith(".pdf"):
        continue

    ruta_pdf = os.path.join(CARPETA_PDFS, archivo)

    with pdfplumber.open(ruta_pdf) as pdf:
        texto = ""
        for p in pdf.pages:
            if p.extract_text():
                texto += p.extract_text() + "\n"

    data = {
        "archivo": archivo,
        "fecha_extraccion": datetime.now().strftime("%Y-%m-%d"),
        "paginas": len(pdf.pages),
        "vigente": "vigente" in texto.lower(),
        "resumen": texto[:800]
    }

    nombre_json = archivo.replace(".pdf", ".json")
    ruta_json = os.path.join(CARPETA_JSON, nombre_json)

    with open(ruta_json, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

print("✅ JSON generados correctamente")
