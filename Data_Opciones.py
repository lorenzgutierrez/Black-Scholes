
# -*- coding: utf-8 -*-
"""
Created on Sun Sep  2 12:00:35 2018

@author: Lorenzo Emiliano
"""
import pandas as pd
import requests
from Secrets import password,mail
from Funciones_auxiliares_inv import get_opcion,webscrape_pdf,extract_volatility_from_pdf

'''El programa inicia sesion en Bullmarket, luego de eso obtiene las Api de las acciones y las opciones.
Luego crea txt's con los datos necesarios para trabajar, nombre de la opcion, cuando vence,
el precio actual de la accion y su volatibilidad'''

''' Diccionario que mapea el nombre de la accion a su correspondiente opcion'''
Acciones = {'AGRO' : 'AGR','ALUA':'ALU','APBR' : 'PBR' ,'AUSO' : 'AUS','BHIP' : 'BHIP','BMA' : 'BMA','BOLT' : 'BOL','BYMA' : 'BYM','CECO2' : 'CEC','CELU' : 'CEL','CEPU' : 'CEP','COME' : 'COM','CRES' : 'CRE','CTIO' : 'CTO','CVH' : 'CVH','DGCU2' : 'DGC','EDN' : 'EDN','BBAR' : 'BBA','GGAL' : 'GFG','HARG' : 'HAR','INDU' : 'IND','LOMA' : 'LOM','METR' : 'MET','MIRG' : 'MIR','PAMP' : 'PAM','PGR' : 'PGR','SAMI' : 'SAM','SUPV' : 'SUP','TECO2' : 'TEC','TGNO4' : 'TGN','TGSU2' : 'TGS','TRAN' : 'TRA','TS' : 'TS.','TXAR' : 'TXA','VALO' : 'GVA','YPFD' : 'YPF'}
'''Funcion para iniciar Sesion'''
def initiate_sesion(url,username,password):
    client = requests.session()
    login_data = dict(username=username, password=password)
    r = client.post(url, data=login_data, headers=dict(Referer=url))
    return r,client

'La respuesta y el cliente se determinan con la Funcion initiatesession'
'Si r = response200 entonces ingreso correctamente'
r,client = initiate_sesion('https://www.bullmarketbrokers.com/#',mail,password) 
                           
'Usando el cliente conseguimos la API de las opciones de bullmarket en tiempo real!!! lo transformamos a formato JSON'
datajson_opciones = client.get('https://www.bullmarketbrokers.com/Information/StockPrice/GetStockPrices?_ts=1535815426812&term=3&index=opciones&sortColumn=ticker&isAscending=true').json()
datajson_acciones = client.get('https://www.bullmarketbrokers.com/Information/StockPrice/GetStockPrices?_ts=1536253774341&term=3&index=merval&sortColumn=ticker&isAscending=true').json()
print('Datos obtenidos')
#############################################################################################
webscrape_pdf()
print("Último reporte intradiario obtenido")

extract_volatility_from_pdf("volatilidad.txt")
print("Volatilidad extraída del reporte")

##############################################################################################
'Si queremos ver los posibles tickers, los tenemos aca'
#Call_Precio = {}
s = open('DATOS_call.txt','w')
p = open('DATOS_put.txt','w')
''' De las json_opciones obtenemos los datos del nombre, la cotizacion, el precio de vencimiento y la accion a la que se corresponde'''
for element in datajson_opciones['result']:
     precio = element['stockState']['price'] #Target
     venta = element['stockOffer']['askTop'][0]['price']
     if element['ticker'][3] =='C':# and precio !=0:
         s.write(str(get_opcion(element['ticker']))+ ' '+ str(precio) +' ' + str(venta) + ' '  + str(float(element['ticker'][4:-2]))+'' ' ' +str(element['ticker'][-2:])+'\n')
     elif element['ticker'][3] =='V':
         p.write(str(get_opcion(element['ticker']))+' ' + str(precio) +' ' + str(venta) + ' '  + str(float(element['ticker'][4:-2]))+'' ' ' +str(element['ticker'][-2:])+'\n')
s.close()
p.close()
print('Toma de datos Call y Puts completada')
###############################################################################################

T = []
'''A cada opcion le agregamos el precio de cotizacion actual de la accion'''     
df = pd.read_csv('DATOS_call.txt', delimiter = ' ',names = ['Opcion','Precio','Venta','Target','Vencimiento'])
df2 = pd.read_csv('DATOS_put.txt', delimiter = ' ',names = ['Opcion','Precio','Venta','Target','Vencimiento'])
#df['Precio_Accion'] = 0.
for element in datajson_acciones['result']:
    ticker = element['ticker']
    try:
        precio = element['rating']['price']
        if precio == 0.0:
            precio = element['stockOffer']['askTop'][0]['price']
    except:
        precio = element['stockState']['price']
        if precio == 0.0:
            precio = element['stockOffer']['askTop'][0]['price']
    T.append([precio,ticker])
    
S = pd.DataFrame(T,columns = ['price','accion'])
print('Toma y creacion de Dataframe de acciones completada')
##################################################################################################
Non_Tickers = ['VALOC','TXARD',"RICH"] #a veces aparecen tickers que no andan.

Volatility = pd.read_csv("volatilidad.txt",names=["accion","volatilidad"])
Volatility.volatilidad = Volatility.volatilidad/100
S["Opcion"] = S.accion.apply(lambda row: Acciones.get(row))
S = pd.merge(S,Volatility,on = "accion",how="left")

df = pd.merge(df,S,on = 'Opcion',how = 'left')
df = df.drop(columns = ['accion'])
df = df.rename(index = str,columns = {'price':'Precio_Accion'})

df2 = pd.merge(df2,S,on = 'Opcion',how = 'left')
df2 = df2.drop(columns = ['accion'])
df2 = df2.rename(index = str,columns = {'price':'Precio_Accion'})

print('Mergeado de Dataframes Acciones y Calls y Puts realizada')   

#####################################################################################################
df.to_csv('DATOS_call.txt',columns = ['Opcion','Precio','Venta','Target','Vencimiento','Precio_Accion','volatilidad'])    
df2.to_csv('DATOS_put.txt',columns = ['Opcion','Precio','Venta','Target','Vencimiento','Precio_Accion','volatilidad'])
print('Guardado de datos en DATOS_call.txt y DATOS_put.txt finalizada')   
client.close()
    