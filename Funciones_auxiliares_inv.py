# -*- coding: utf-8 -*-
"""
Created on Thu Sep  6 13:40:56 2018

@author: Lorenzo Emiliano
"""

'''Esta funcion actua sobre un Strig de una Call, al hacer esto devuelve el nombre de la opcion. El
 formato de la opciion debe ser : (nombre_opcion)+"C" + target'''
'''Actualizacion: Ahora funciona para puts tambien'''

from bs4 import BeautifulSoup
import urllib
import requests
from pdfminer.high_level import extract_pages
import numpy as np


def get_opcion(s):
    t = True
    while t:
        for i in range(len(s)):
            if s[i]=='C' and s[i+1].isdigit():
                t = False
                return s[0:i]
            if s[i] == 'V' and s[i+1].isdigit():
                t = False
                return s[0:i]
                 
def webscrape_pdf():
    """Websraps el último informe diario del iamc y lo descarga para posterior uso"""
    path = "https://www.iamc.com.ar/informediario/"
    s = requests.get(path)
    text = s.text
    soup = BeautifulSoup(text,'html.parser')
    last_report = soup.find(class_="contenidoListado Acceso-Rapido")
    link = last_report.a["href"]
    download_file(link,"report")


def download_file(download_url, filename):
    """Descarga el pdf del reporte diario"""
    response = urllib.request.urlopen(download_url)    
    file = open(filename + ".pdf", 'wb')
    file.write(response.read())
    file.close()
    
    
def extract_volatility_from_pdf(pdf_path):
    """Usando el reporte diario (pdf) extrae la volatilidad de las acciones"""
    
    pdf_path = "report.pdf"
    a = extract_pages(pdf_path,page_numbers = [1])

    indx = [74,86]

    elements = []
    for page_layout in a:
        for element in page_layout:
            elements.append(element)
        
        data_raw = np.array([elements[indx[0]].get_text().split("\n"),
                    elements[indx[1]].get_text().replace("%","").split("\n")],dtype=str).T

    np.savetxt("volatilidad.txt",data_raw,delimiter = ",",fmt = "%s")
