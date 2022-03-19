import iapws
import pandas as pd


def iapws97_Region4_P(T):#tempC
    n = pd.read_csv('iapws-if97-region4.csv')
    n.index = n['i']
    n = n.drop('i', axis=1)
    
    Ts = T + 273.15
    θ = (Ts/1) + n.at[9,'ni']/((Ts/1)-n.at[10,'ni'])
    A = (θ)**2 + n.at[1,'ni']*(θ) + n.at[2,'ni']
    B = n.at[3,'ni']*((θ)**2) + n.at[4,'ni']*(θ) + n.at[5,'ni']
    C = n.at[6,'ni']*((θ)**2) + n.at[7,'ni']*(θ) + n.at[8,'ni']
    Psta = 1* ((2*C)/(-B+(B**2-4*A*C)**(1/2)))**4
    Psta = round(Psta,7)
    
    return Psta

def iapws97_Region4_T(P):#Pressure(MPaA)
    n = pd.read_csv('iapws-if97-region4.csv')
    n.index = n['i']
    n = n.drop('i', axis=1)
    
    β = P**(1/4)
    E = (β)**2 + n.at[3,'ni']*(β) + n.at[6,'ni']
    F = n.at[1,'ni']*(β)**2 + n.at[4,'ni']*(β) + n.at[7,'ni']
    G = n.at[2,'ni']*(β)**2 + n.at[5,'ni']*(β) + n.at[8,'ni']
    D = (2*G)/(-F-(F**2-4*E*G)**0.5)
    
    Tsp =(n.at[10,'ni'] + D - ((n.at[10,'ni']+D)**2 - 4*(n.at[9,'ni']+n.at[10,'ni']*D))**(0.5)) / 2
    Tsp = round(Tsp,5) - 273.15
    
    return Tsp

def iapws97_Region4_water(P):
    return iapws.iapws97._Region4(P,0)


def iapws97_Region4_steam(P):
    return iapws.iapws97._Region4(P,1)