import math
import iapws
import pandas as pd


#二相流圧力損失計算　
#Homogeneous Flow Model Applied to Intube Flow

def pressuredrop_twophase(P,steam,water,piping,sh,length):
    piping_data = pd.read_excel("piping_datasheet.xlsx",sheet_name='piping_datasheet',header=2,index_col=0)
    pp =  piping_data
    pp.columns = ["外径","sh5_thk","sh5","sh10_thk","sh10","sh20_thk","sh20","sh40_thk","sh40","0","sh80_thk","sh80","sh120_thk","sh120","sh160_thk","sh160"]
    di = pp.at[piping,sh] #mm
    di = di*0.001 #m

    Q = (steam+water) #kg/h
    m_total = Q/3600
    x = steam/(steam+water)
    Psa = P + 0.101325 #MPaA

    parameter = iapws.iapws97._Region4(Psa, x)
    temp = parameter['T']

    # temp = iapws.iapws97._TSat_P(Psa) #K
    waterpara = iapws.iapws97._Region1(temp, Psa)
    steam_parameter = iapws.iapws97._Region2(temp, Psa)
    
    sv_s = round(1/steam_parameter['v'],5)
    sh_s = round(steam_parameter['h'],3)
    cp_s = round(steam_parameter['cp'],4)

    sv_w = round(1/waterpara['v'],6)
    sh_w = round(waterpara['h'],3)
    cp_w = round(waterpara['cp'],4)

    #蒸気粘性 kg/ms
    myu_G = -0.00127*P**2 + 0.003889*P + 0.01263 

    # 熱水粘性 kg/ms
    t= temp-273.15 #℃
    if temp > 100:
        myu_L = 4.665e-06*t**2 - 0.002739*t + 0.4946
    else:
        myu_L = 0.0001644*t**2 - 0.02834*t + 1.546

    #The homogeneous void fraction
    E = 1/(1+(((1-x)/x)*(sv_s/sv_w)*(myu_G/myu_L)))

    #均質密度 kg/m3
    # RoH = sv_w*(1-E)+sv_s*E
    RoH = 1/parameter['v']

    #均質粘性 kg/ms
    myu_tp = x*myu_G + (1-x)*myu_L

    S = math.pi*((di/2)**2) #m2
    m = Q/(S*3600) # kg/h*1/m2*h/s = kg/m2s

    # 流速
    v = m/RoH # kg/m2s * m3/kg = m/s

    #レイノルズ数
    Re =m*di/myu_tp #1mの場合、Ｌが長くなると乱流になりやすい。Re増

    #摩擦係数
    f_tp = 0.079/(Re**0.25)
    # if Re > 2300:
    #     statusH = '乱流'
    #     f_tp = 0.079/(Re**0.25)
    #     #f_tp = 0.046/(Re**0.20)
    # elif Re<2300:
    #     statusH = '層流'
    #     f_tp = 16/Re

    #圧力損失
    delta_P = 2*f_tp*(m**2)/(di*RoH) #N/m2
    delta_P =delta_P/1000 #kPa
    # delta_P =delta_P/1000 #MPa

    total_pressuredrop = delta_P*length

    result = {'predrop':round(total_pressuredrop,5),'Re':round(Re,3),'RoH':round(RoH,3),'εH':E,'μtp':round(myu_tp,3),'velocity':round(v,3),'m':round(m,3)}

    return result


def pressuredrop_twophase2(P,steam,water,piping,sh,length):
    piping_data = pd.read_excel("piping_datasheet.xlsx",sheet_name='piping_datasheet',header=2,index_col=0)
    pp =  piping_data
    pp.columns = ["外径","sh5_thk","sh5","sh10_thk","sh10","sh20_thk","sh20","sh40_thk","sh40","0","sh80_thk","sh80","sh120_thk","sh120","sh160_thk","sh160"]
    di = pp.at[piping,sh] #mm
    di = di*0.001 #m

    x = steam/(steam+water)
    Psa = P + 0.101325 #MPaA

    parameter = iapws.iapws97._Region4(Psa, x)
    temp = parameter['T']

    # temp = iapws.iapws97._TSat_P(Psa) #K
    waterpara = iapws.iapws97._Region1(temp, Psa)
    steam_parameter = iapws.iapws97._Region2(temp, Psa)
    
    sv_s = round(1/steam_parameter['v'],5)
    sh_s = round(steam_parameter['h'],3)
    cp_s = round(steam_parameter['cp'],4)

    sv_w = round(1/waterpara['v'],6)
    sh_w = round(waterpara['h'],3)
    cp_w = round(waterpara['cp'],4)

    #蒸気粘性 kg/ms
    myu_G = -0.00127*P**2 + 0.003889*P + 0.01263 

    # 熱水粘性 kg/ms
    t= temp-273.15 #℃
    if temp > 100:
        myu_L = 4.665e-06*t**2 - 0.002739*t + 0.4946
    else:
        myu_L = 0.0001644*t**2 - 0.02834*t + 1.546

    QG = steam/3600
    QL = water/3600
    
    S = math.pi*((di/2)**2) #m2
    m = (QG + QL)/S
    mG = QG/S
    mL = QL/S
    ReG =m*di/myu_G
    ReL =m*di/myu_L

    if ReG > 1500:
        if ReL >1500:
            status = '気相、液相ともに乱流、t-t'
            C = 20
        else:
            status = '気相-乱流、液相-層流、t-v'
            C = 12
    else:
        if ReL >1500:
            status = '気相-層流、液相-乱流、v-t'
            C = 10
        else:
            status = '気相-層流、液相-層流、v-v'
            C = 5

    #両相乱流の場合
    #Colburnの式
    a = ((1-x)/x)**0.9
    b = (sv_s/sv_w)**0.5
    c = (myu_L/myu_G)**0.1
    Xtt = a*b*c

    #摩擦損失係数
    f_G = 0.079/(ReG**0.25)
    f_L = 0.079/(ReL**0.25)

    # if ReG <= 1000:
    #     f_G = 64/ReG
    # else:
    #     f_G = 0.079*(ReG**-0.25)

    # if ReL <= 1000:
    #     f_L = 64/ReL
    # else:
    #     f_L = 0.079*(ReL**-0.25)



    if ReL > 4000:
        fai_L = 1+C/Xtt + 1/(Xtt**2)
        dPL = 2*f_L*((m*1-x)**2)/(di*sv_w)
        dP = fai_L*dPL

    else:
        fai_G = 1+C*Xtt + Xtt**2
        dPG = 2*f_G*((m*x)**2)/(di*sv_s)
        dP = fai_G*dPG

    dP = dP/1000




    # #Chisholm-Lairdの式（平滑管）
    # fai_L = (1+C/Xtt + 1/Xtt**2)**0.5
    # fai_G = (1+C*Xtt + Xtt**2)**0.5

    # fai_L = 3.1
    # fai_G = 1.8


    #見かけの圧力損失
    # dP_G = 2*f_G*(m_total**2)/(di*sv_s)
    # dP_L = 2*f_L*(m_total**2)/(di*sv_w)

    # XX = (dP_L/dP_G)**0.5
    XX = 0.5
    fai_L = 0
    fai_G = 0



    # dP1 = (fai_G**2)*dP_G
    # dP1 = dP1*(10**-6)

    # dP2 = (fai_L**2)*dP_L
    # dP2 = dP2*(10**-6)

    # dP = (dP1+dP2)/2

    result = {'predrop':round(dP,5),'ReG':round(ReG,3),'ReL':round(ReL,3),'status':status,
            'parameterX':XX,'φL':fai_L,'φG':fai_G}

    return result

def pressuredrop_twophase3(P,steam,water,piping,sh,length):
    piping_data = pd.read_excel("piping_datasheet.xlsx",sheet_name='piping_datasheet',header=2,index_col=0)
    pp =  piping_data
    pp.columns = ["外径","sh5_thk","sh5","sh10_thk","sh10","sh20_thk","sh20","sh40_thk","sh40","0","sh80_thk","sh80","sh120_thk","sh120","sh160_thk","sh160"]
    di = pp.at[piping,sh] #mm
    di = di*0.001 #m

    x = steam/(steam+water)
    Psa = P + 0.101325 #MPaA

    parameter = iapws.iapws97._Region4(Psa, x)
    temp = parameter['T']

    # temp = iapws.iapws97._TSat_P(Psa) #K
    waterpara = iapws.iapws97._Region1(temp, Psa)
    steam_parameter = iapws.iapws97._Region2(temp, Psa)
    
    sv_s = round(1/steam_parameter['v'],5)
    sh_s = round(steam_parameter['h'],3)
    cp_s = round(steam_parameter['cp'],4)

    sv_w = round(1/waterpara['v'],6)
    sh_w = round(waterpara['h'],3)
    cp_w = round(waterpara['cp'],4)

    #蒸気粘性 kg/ms
    myu_G = -0.00127*P**2 + 0.003889*P + 0.01263 

    # 熱水粘性 kg/ms
    t= temp-273.15 #℃
    if temp > 100:
        myu_L = 4.665e-06*t**2 - 0.002739*t + 0.4946
    else:
        myu_L = 0.0001644*t**2 - 0.02834*t + 1.546

    Q = (steam+water) #kg/h
    S = math.pi*((di/2)**2) #m2
    m = Q/(S*3600) # kg/h*1/m2*h/s = kg/m2s

    RoL = sv_w
    ReL = m*di/myu_L
    fL = 0.0079/(ReL**0.25)

    ReG =  m*di/myu_G
    fG = 0.0079/(ReG**0.25)

    E = (1-x)**2 + (x**2)*(sv_w*fG)/(sv_s*fL)
    F = (x**0.78)*((1-x)**0.224)

    a = (sv_w/sv_s)**0.91
    b = (myu_G/myu_L)**0.19
    c = (1-(sv_s/sv_w))**0.7
    H = a*b*c

    RoH = (x/sv_s + (1-x)/sv_w)**(-1)

    shiguma = 0.0589
    WeL = di*m**2/(RoH*shiguma)

    FrH = m**2/(9.8*di*RoH**2)

    fai_fr = E + 3.24*F*H/((FrH**0.045)*(WeL**0.0035))
    dpL = 4*fL*m**2/(di*2*RoL)

    dp = dpL*fai_fr/1000

    result = {'predrop':dp,'x':x,'ration':myu_L/myu_G}

    return result

    





