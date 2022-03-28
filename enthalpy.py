import iapws
import pandas as pd

def isenthalpic(f_s,f_w,p0,t0,p1,t1):  #kg/h,kg/h,MPaG,C
    x0 = f_s/(f_s+f_w)
    
    para_s = iapws.iapws97._Region2(t0+273.15,p0)
    para_w = iapws.iapws97._Region1(t0+273.15,p0)

    para_s2 = iapws.iapws97._Region2(t1+273.15,p1)
    para_w2 = iapws.iapws97._Region1(t1+273.15,p1)

    spefic_enthalpy = iapws.iapws97._Region4(p0,x0)['h'] #kJ/kg
    total_enthalpy = spefic_enthalpy*((f_s+f_w)/3600)

    x1 = (spefic_enthalpy-para_w2['h'])/(para_s2['h']-para_w2['h'])

    f_s1 = x1*(f_s+f_w)
    f_w1 = (1-x1)*(f_s+f_w)

    return {'x0':x0,'x1':x1,'flow_steam':f_s1,'flow_water':f_w1,
            'spefic_enthalpy':spefic_enthalpy,'total_enthalpy':total_enthalpy}