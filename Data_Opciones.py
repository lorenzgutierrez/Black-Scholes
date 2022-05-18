
# -*- coding: utf-8 -*-
"""
Created on Sun Sep  2 12:00:35 2018

@author: Lorenzo Emiliano
"""
import pandas as pd
import requests
from Secrets import password,mail
from Funciones_auxiliares_inv import get_opcion,webscrape_pdf,extract_volatility_from_pdf
from requests.auth import HTTPBasicAuth
import json


'''El programa inicia sesion en Bullmarket, luego de eso obtiene las Api de las acciones y las opciones.
Luego crea txt's con los datos necesarios para trabajar, nombre de la opcion, cuando vence,
el precio actual de la accion y su volatibilidad'''

''' Diccionario que mapea el nombre de la accion a su correspondiente opcion'''
Acciones = {'AGRO' : 'AGR','ALUA':'ALU','APBR' : 'PBR' ,'AUSO' : 'AUS','BHIP' : 'BHIP','BMA' : 'BMA','BOLT' : 'BOL','BYMA' : 'BYM','CECO2' : 'CEC','CELU' : 'CEL','CEPU' : 'CEP','COME' : 'COM','CRES' : 'CRE','CTIO' : 'CTO','CVH' : 'CVH','DGCU2' : 'DGC','EDN' : 'EDN','BBAR' : 'BBA','GGAL' : 'GFG','HARG' : 'HAR','INDU' : 'IND','LOMA' : 'LOM','METR' : 'MET','MIRG' : 'MIR','PAMP' : 'PAM','PGR' : 'PGR','SAMI' : 'SAM','SUPV' : 'SUP','TECO2' : 'TEC','TGNO4' : 'TGN','TGSU2' : 'TGS','TRAN' : 'TRA','TS' : 'TS.','TXAR' : 'TXA','VALO' : 'GVA','YPFD' : 'YPF'}
'''Funcion para iniciar Sesion'''
def initiate_sesion(url,username,password,grant_type):
    client = requests.session() 
    data_post = {"username":username,"password":password,"grant_type":grant_type}
    r = client.post(url,data = data_post)
    return r,client

'La respuesta y el cliente se determinan con la Funcion initiatesession'
'Si r = response200 entonces ingreso correctamente'
r,client = initiate_sesion('https://api.invertironline.com/token',mail,password,"password") 

d = json.loads(r.text)                           

'Usando el cliente conseguimos la API de las opciones de invertironline en tiempo real!!! lo transformamos a formato JSON'
s = open('DATOS.txt','w')

for key in Acciones:    
    datajson_acciones = client.get(f'https://api.invertironline.com/api/v2/bCBA/Titulos/{key}/Cotizacion',headers = {"Authorization":"Bearer " + d["access_token"]}).json()
    datajson_opciones = client.get(f'https://api.invertironline.com/api/v2/bCBA/Titulos/{key}/Opciones',headers = {"Authorization":"Bearer " + d["access_token"]}).json()
    
    precio_accion = datajson_acciones['ultimoPrecio']
    for opcion in datajson_opciones:
        tipo_opcion = opcion["tipoOpcion"]
        target = opcion["descripcion"].split(" ")[2]
        vencimiento = opcion["descripcion"].split(" ")[-1]
        ultimo_precio = opcion["cotizacion"]['ultimoPrecio']
        s.write(f"{key} {precio_accion} {tipo_opcion} {target} {vencimiento} {ultimo_precio}\n")

s.close()

print('Datos obtenidos')


#############################################################################################
webscrape_pdf()
print("Último reporte intradiario obtenido")

extract_volatility_from_pdf("volatilidad.txt")
print("Volatilidad extraída del reporte")

##############################################################################################
# 'Si queremos ver los posibles tickers, los tenemos aca'
# #Call_Precio = {}
# s = open('DATOS_call.txt','w')
# p = open('DATOS_put.txt','w')
# ''' De las json_opciones obtenemos los datos del nombre, la cotizacion, el precio de vencimiento y la accion a la que se corresponde'''
# for element in datajson_opciones['result']:
#      precio = element['stockState']['price'] #Target
#      venta = element['stockOffer']['askTop'][0]['price']
#      if element['ticker'][3] =='C':# and precio !=0:
#          s.write(str(get_opcion(element['ticker']))+ ' '+ str(precio) +' ' + str(venta) + ' '  + str(float(element['ticker'][4:-2]))+'' ' ' +str(element['ticker'][-2:])+'\n')
#      elif element['ticker'][3] =='V':
#          p.write(str(get_opcion(element['ticker']))+' ' + str(precio) +' ' + str(venta) + ' '  + str(float(element['ticker'][4:-2]))+'' ' ' +str(element['ticker'][-2:])+'\n')
# s.close()
# p.close()
# print('Toma de datos Call y Puts completada')
# ###############################################################################################

T = []
'''A cada opcion le agregamos el precio de cotizacion actual de la accion'''     
df = pd.read_csv('DATOS.txt', delimiter = ' ',names = ['Accion','Cotizacion','Tipo_opcion','Target','Vencimiento','Opcion_cotizacion'])

##################################################################################################
Non_Tickers = ['VALOC','TXARD',"RICH"] #a veces aparecen tickers que no andan.

Volatility = pd.read_csv("volatilidad.txt",names=["Accion","volatilidad"])
Volatility.volatilidad = Volatility.volatilidad.astype(float)/100

S = pd.merge(df,Volatility,on = "Accion",how="left")



print('Mergeado de Dataframes Acciones y Calls y Puts realizada')   
#####################################################################################################
S.to_csv('DATOS.txt',columns = ['Accion','Cotizacion','Tipo_opcion','Target','Vencimiento','Opcion_cotizacion','volatilidad'])    
print('Guardado de datos en DATOS_call.txt y DATOS_put.txt finalizada')   
client.close()
    