
# -*- coding: utf-8 -*-
"""
Created on Sat Sep  1 12:27:18 2018

@author: Lorenzo Emiliano
"""


import numpy as np
import pandas as pd
import time
import datetime
from scipy.stats import norm

pd.set_option('display.max_columns', None)


now = time.time()
month = 2678400
Risk_interest = 0.34#'Esta es la taza anual de volatibilidad' Debe ser actualizada cada dia

'''Este' Script tiene como objetivo encontrar las opciones que esten cotizando en la bolsa Argentina a un precio
menor que el teorico segun el modelo de Black Scholes europeo'''

'''Black Scholes Calculator. Creo que funciona con T en meses, no estoy seguro, falta calibracion.
Los datos de vpolatibilidad y interest rate tienen un valor de 1 para 100%'''

#first define these 2 functions
def d1(S,X,T,r,sigma):
    return (np.log(S/X)+(r+sigma*sigma/2.)*T)/(sigma*np.sqrt(T))

def d2(S,X,T,r,sigma):
    return d1(S,X,T,r,sigma)-sigma*np.sqrt(T)

#define the call option price function
def bs_call(S,X,T,r,sigma):
     return S*norm.cdf(d1(S,X,T,r,sigma))-X*np.exp(-r*T)*norm.cdf(d2(S,X,T,r,sigma))

#define the put options price function
def bs_put(S,K,T,r,sigma):
      return K*np.exp(-r*T)-S+bs_call(S,K,T,r,sigma)

def See_Option(string):
    print(df[df['Opcion']==string])
    
'''DATAFRAME CON INFORMACION (VER COLUMNAS)'''          
df =  pd.read_csv('DATOS.txt',delimiter = ',',usecols = ['Accion','Cotizacion','Tipo_opcion','Target','Vencimiento','Opcion_cotizacion','volatilidad'])
df.Target = df.Target.apply(lambda row: float(row.replace(",","")))

df = df[df.Tipo_opcion == "Call"]

### Convertimos el vencimiento a un formato en segundos
def Convert_to_seconds(timestring):
    a = timestring.split("/")
    vencimiento = time.mktime(((int(a[-1]),int(a[1]),int(a[0]),0,0,0,0,0,0)))
    return vencimiento
    
### Calulamos la difrencia con hoy
def  T_diff(seconds):
    global t_month
    t_month = (seconds-now)/(month*10)
    return t_month


df.Vencimiento = df.Vencimiento.apply(lambda row: Convert_to_seconds(row))

df.loc[df['volatilidad']>0.6,'volatilidad']=0.6
df['Teorico'] = 0.

df.Teorico = df.apply(lambda row: bs_call(row.Cotizacion,float(row.Target),T_diff(row.Vencimiento),Risk_interest,row.volatilidad),axis = 1)
    
df['Teorico'] = round(df['Teorico'],2)    
df = df.rename(index = str,columns = {"Vencimiento":"Vencmt.","Cotizacion":"P_A","volatilidad":"Vol"})
df['%VT'] = round((df['Opcion_cotizacion'])*100/df['Teorico'],2)
Useful = df[df['Opcion_cotizacion']!=0.0]
Useful = Useful[Useful['%VT']<100]

Useful["Vencmt."] = Useful["Vencmt."].apply(lambda row: pd.to_datetime(row,unit = "s").strftime("%Y-%m-%d"))
Useful.sort_values(by = "%VT",inplace=True)


Useful.reset_index(inplace=True,drop=True)
Useful.to_csv("finaldata.csv",columns= ["Accion","P_A","Target","Vencmt.","Opcion_cotizacion","Vol","Teorico","%VT"])

print(Useful[["Accion","Tipo_opcion","P_A","Target","Opcion_cotizacion","Vencmt.","%VT"]])


    


