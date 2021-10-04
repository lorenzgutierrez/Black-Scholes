
# -*- coding: utf-8 -*-
"""
Created on Sat Sep  1 12:27:18 2018

@author: Lorenzo Emiliano
"""


import numpy as np
import pandas as pd
import time
import csv
from scipy.stats import norm
import difflib as dif
now = time.time()
month = 2678400
'''Estos datos son los que necesitan ser actualizados'''
DI = time.mktime(((2018,12,21,0,0,0,0,0,0)))
FE = time.mktime((2019,2,15,0,0,0,0,0,0))
AB = time.mktime((2020,4,17,0,0,0,0,0,0))
JU = time.mktime((2020,6,19,0,0,0,0,0,0))
AG = time.mktime((2020,8,22,0,0,0,0,0,0))
OC = time.mktime((2021,10,15,0,0,0,0,0,0))
months = ['AG','OC','AB','JU'] #ir agregando meses
target = "OC"
Risk_interest = 0.34#'Esta es la taza anual de volatibilidad' Debe ser actualizada cada dia

'''Este' Script tiene como objetivo encontrar las opciones que esten cotizando en Bullarket a un precio
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
df =  pd.read_csv('DATOS_call.txt',delimiter = ',',usecols = ['Opcion','Precio','Venta','Target','Vencimiento','Precio_Accion','volatilidad'])
df2 =  pd.read_csv('DATOS_put.txt',delimiter = ',',usecols = ['Opcion','Precio','Venta','Target','Vencimiento','Precio_Accion','volatilidad'])

def  T_month(string):
    global t_month
    if string == 'OC':
        t_month = (OC-now)/(month*10)
    elif string=='DI':
        t_month = (DI-now)/(month*10)
    elif string == 'FE':
        t_month = (FE-now)/(month*10)
    elif string == 'AB':
        t_month = (AB-now)/(month*10)
    elif string == 'JU':
        t_month = (JU-now)/(month*10)
    elif string == 'AG':
        t_month = (AG-now)/(month*10)
    return t_month

def similar(a, b):
    return dif.SequenceMatcher(None, a, b).ratio()  

def Teorico_call(Opcion,X,month,sigma = Risk_interest, dataframe = df):
    aux = df[(df['Opcion'] == Opcion)]
    aux = aux[(aux['P_A']!=np.NaN) & (aux['Vol']!=np.NaN)]
    aux = aux.iloc[0]
    S,Vol= aux[4],aux[5]
    res = bs_call(S,X,T_month(month),sigma,Vol)
    return res


df.loc[df['volatilidad']>0.6,'volatilidad']=0.6
#df2.loc[df2['Volatilidad']>0.6,'Volatilidad']=0.6
df['Teorico'] = 0.
df2['Teorico'] = 0.
for i in range(len(df)):
    for mes in months:
        if (df['Vencimiento'].iloc[i] not in months) and (similar(df['Vencimiento'].iloc[i],mes) > 0.0): df['Vencimiento'].iloc[i] = mes
       
        

df.Teorico = df.apply(lambda row: bs_call(row.Precio_Accion,row.Target,T_month(row.Vencimiento),Risk_interest,row.volatilidad),axis = 1)
df2.Teorico = df.apply(lambda row: bs_put(row.Precio_Accion,row.Target,T_month(row.Vencimiento),Risk_interest,row.volatilidad),axis = 1)        
    
df['Teorico'] = round(df['Teorico'],2)    
#df['P_A'].fillna(0,inplace = True)
df = df.rename(index = str,columns = {"Vencimiento":"Vencmt.","Precio_Accion":"P_A","volatilidad":"Vol"})
#df['Time_to_Venc'] = df.apply(T_month2,axis = 1)
df = df.drop(columns = ['Precio'])
df['%VT'] = round((df['Venta'])*100/df['Teorico'],2)
Useful = df[(df['Vencmt.'] == target)]
Useful = Useful[Useful['Venta']!=0.0]
Useful = Useful[Useful['%VT']<100]

df2['Teorico'] = round(df2['Teorico'],2)    
df2 = df2.replace({'Venta': {0.000:np.nan}})
df2['%VT'] = round((df2['Venta'])*100/df2['Teorico'],2)
df2 = df2.rename(index = str,columns = {"Vencimiento":"Vencmt.","Precio_Accion":"P_A","volatilidad":"Vol"})
Useful2 = df2[df2['Venta']<df2['Teorico']]
                
print(Useful)
#print(Useful2)


    


