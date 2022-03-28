from flask import Flask, render_template, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import io
import numpy as np
from io import BytesIO
import base64
import iapws
import pandas as pd
import openpyxl
from parameter import iapws97_Region4_P,iapws97_Region4_T
from enthalpy import isenthalpic
from predrop_twophase import pressuredrop_twophase,pressuredrop_twophase2,pressuredrop_twophase3

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Rb = db.Column(db.Float, nullable=False)
    Sr = db.Column(db.Float, nullable=False)

def fig_to_base64_img(fig):
    """画像を base64 に変換する。
    """
    # png 形式で出力する。
    io = BytesIO()
    fig.savefig(io, format="png")
    # base64 形式に変換する。
    io.seek(0)
    base64_img = base64.b64encode(io.read()).decode()

    return base64_img

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/')
def home2():
    return render_template('home.html')


# ---------------isochron-------------------------------
@app.route('/RbSr', methods=['GET', 'POST'])
def RbSr():
    return render_template('geochemi/RbSr.html')

@app.route('/graph',methods = ['POST', 'GET'])
def graph():
    if request.method == 'POST':
        try:
            Rb_list = request.form.getlist('Rb1')
            Sr_list = request.form.getlist('Sr1')
            Rb_list = [float(n) for n in Rb_list ]
            Sr_list = [float(n) for n in Sr_list ]
            n = len(Rb_list)
            x = Rb_list
            y = Sr_list

            fig = plt.figure(figsize=(15,6))
            # ax = plt.axes()
            ax = fig.add_subplot(111)

            cf1 = np.polyfit(x,y,1)
            func1 = np.poly1d(cf1)
            fig, ay = plt.subplots()
            ay.invert_yaxis()
            plt.plot(x, func1(x),label='d=1')
            plt.xlabel('87Rb/86Sr',fontsize=18)
            plt.ylabel("87Sr/86Sr",fontsize=18)
            # plt.ylim()
            plt.grid()
            plt.tick_params(labelsize=18)
            plt.tight_layout()
            plt.scatter(x,y)

            a = round(cf1[0],4)
            b = round(cf1[1],4) 
            slope = "87Sr/86Sr = " + str(a)+'(87Rb/86Sr) + ' +str(b)
            t = round(((np.log(1+a))/ (1.42*10**(-11))/100000000),3)

            img = fig_to_base64_img(fig)
            return render_template('geochemi/graph.html',img= img ,a=a,b=b,Rb_list=Rb_list,Sr_list=Sr_list,t=t,n=n)

        except ValueError:
            return render_template('error.html')

@app.route('/SmNd', methods=['GET', 'POST'])
def SmNd():
    return render_template('geochemi/SmNd.html')

@app.route('/graph_SmNd',methods = ['POST', 'GET'])
def graph_SmNd():
    if request.method == 'POST':
        try:
            Sm_list = request.form.getlist('Sm1')
            Nd_list = request.form.getlist('Nd1')
            Sm_list = [float(n) for n in Sm_list ]
            Nd_list = [float(n) for n in Nd_list ]
            n = len(Sm_list)
            x = Sm_list
            y = Nd_list

            fig = plt.figure(figsize=(15,6))
            # ax = plt.axes()
            ax = fig.add_subplot(111)

            cf1 = np.polyfit(x,y,1)
            func1 = np.poly1d(cf1)
            fig, ay = plt.subplots()
            ay.invert_yaxis()
            plt.plot(x, func1(x),label='d=1')
            plt.xlabel('87Rb/86Sr',fontsize=18)
            plt.ylabel("87Sr/86Sr",fontsize=18)
            # plt.ylim()
            plt.grid()
            plt.tick_params(labelsize=18)
            plt.tight_layout()
            plt.scatter(x,y)

            a = round(cf1[0],4)
            b = round(cf1[1],4) 
            slope = "87Sr/86Sr = " + str(a)+'(87Rb/86Sr) + ' +str(b)
            t = round(((np.log(1+a))/ (6.54*10**(-12))/100000000),3)

            img = fig_to_base64_img(fig)
            return render_template('geochemi/graph_SmNd.html',img= img ,a=a,b=b,Sm_list=Sm_list,Nd_list=Nd_list,t=t,n=n)

        except ValueError:
            return render_template('error.html')


# ---------------steamtable-------------------------------
@app.route('/steamtable', methods=['GET', 'POST'])
def steam():
    return render_template('steam/steamtable.html')

@app.route('/steamtableresult', methods=['GET', 'POST'])
def steamresult():
    if request.method == 'POST':
        try:
            temp = request.form.get('temp')
            temp = float(temp)
            Psa = iapws97_Region4_P(temp)
            Psg = round(Psa,7) - 0.101325
            Psg = round(Psa,5)

            waterpara = iapws.iapws97._Region1(temp+273.15, Psa)
            steam_parameter = iapws.iapws97._Region2(temp+273.15, Psa)

            sv_s = round(1/steam_parameter['v'],5)
            sh_s = round(steam_parameter['h'],3)
            cp_s = round(steam_parameter['cp'],4)
            cv_s = round(steam_parameter['cv'],4) 
            w_s =  round(steam_parameter['w'],3)
            alfav_s = round(steam_parameter['alfav'],7)
            kt_s =  round(steam_parameter['kt'],3)
            
            sv_w = round(waterpara['v'],6)
            sh_w = round(waterpara['h'],3)
            cp_w = round(waterpara['cp'],4)
            cv_w = round(waterpara['cv'],4)
            w_w = round(waterpara['w'],3)
            alfav_w = round(waterpara['alfav'],7)
            kt_w = round(waterpara['kt'],7)
            
            return render_template('steam/steamresult.html',
                    Psa=Psa,temp=temp,sv_s=sv_s,sh_s=sh_s,cp_s=cp_s,cv_s=cv_s,w_s=w_s,
                    alfav_s=alfav_s,kt_s=kt_s,sv_w=sv_w,sh_w=sh_w,cp_w=cp_w,cv_w=cv_w,w_w=w_w,
                    alfav_w=alfav_w,kt_w=kt_w,Psg=Psg)
        except ValueError:
            return render_template('error.html')

@app.route('/steamtable_pre', methods=['GET', 'POST'])
def steam_pre():
    return render_template('steam/steamtable_pre.html')

@app.route('/steamtableresult_pre', methods=['GET', 'POST'])
def steamresult_pre():
    if request.method == 'POST':
        try:
            Psg = request.form.get('pressure')
            Psg = float(Psg)
            Psa = Psg + 0.101325
            temp = iapws97_Region4_T(Psa)

            waterpara = iapws.iapws97._Region1(temp+273.15, Psa)
            steam_parameter = iapws.iapws97._Region2(temp+273.15, Psa)

            temp = round(temp,3)
            sv_s = round(1/steam_parameter['v'],5)
            sh_s = round(steam_parameter['h'],3)
            cp_s = round(steam_parameter['cp'],4)
            cv_s = round(steam_parameter['cv'],4) 
            w_s =  round(steam_parameter['w'],3)
            alfav_s = round(steam_parameter['alfav'],7)
            kt_s =  round(steam_parameter['kt'],3)
            
            sv_w = round(1/waterpara['v'],6)
            sh_w = round(waterpara['h'],3)
            cp_w = round(waterpara['cp'],4)
            cv_w = round(waterpara['cv'],4)
            w_w = round(waterpara['w'],3)
            alfav_w = round(waterpara['alfav'],7)
            kt_w = round(waterpara['kt'],7)
            
            return render_template('steam/steamresult_pre.html',
                    Psa=Psa,temp=temp,sv_s=sv_s,sh_s=sh_s,cp_s=cp_s,cv_s=cv_s,w_s=w_s,
                    alfav_s=alfav_s,kt_s=kt_s,sv_w=sv_w,sh_w=sh_w,cp_w=cp_w,cv_w=cv_w,w_w=w_w,
                    alfav_w=alfav_w,kt_w=kt_w,Psg=Psg)
        except ValueError:
            return render_template('error.html')


# ---------------enthalpy-------------------------------
@app.route('/enthalpy_calc', methods=['GET', 'POST'])
def enthalpy():
    return render_template('enthalpy/enthalpy.html')

@app.route('/enthalpy_calc_result', methods=['GET', 'POST'])
def enthalpy_result():
    if request.method == 'POST':
        try:
            f_s = float(request.form.get('f_s'))
            f_w = float(request.form.get('f_w'))
            temp = float(request.form.get('temp'))
            psg = iapws.iapws97._PSat_T(temp+273.15)

            temp2 = float(request.form.get('temp2'))
            psg2 = iapws.iapws97._PSat_T(temp2+273.15)

            isentha = isenthalpic(f_s,f_w,psg,temp,psg2,temp2)
            x0 = isentha['x0']
            x1 = isentha['x1']
            steam = isentha['flow_steam']
            water = isentha['flow_water']
            spefic_enthalpy = isentha['spefic_enthalpy']
            total_enthalpy = isentha['total_enthalpy']

            return render_template('enthalpy/enthalpy_result.html',
                x0=round(x0,5),x1=round(x1,5),steam=round(steam,3),water=round(water,3),
                spefic_enthalpy=round(spefic_enthalpy,3),total_enthalpy=round(total_enthalpy,3),
                temp=round(temp,2),psg=round(psg,4),f_s=round(f_s,4),f_w=round(f_w,3),temp2=round(temp2,2),psg2=round(psg2,4))

        except ValueError:
            return "<p>ValueError</p>"


@app.route('/enthalpy_calc_pre', methods=['GET', 'POST'])
def enthalpy_pre():
    return render_template('enthalpy/enthalpy_pre.html')

@app.route('/enthalpy_calc_pre_result', methods=['GET', 'POST'])
def enthalpy_result_pre():
    if request.method == 'POST':
        # try:
        f_s = float(request.form.get('f_s'))
        f_w = float(request.form.get('f_w'))
        psg = float(request.form.get('pressure'))
        psa = psg + 0.101325
        temp = iapws.iapws97._TSat_P(psa)
        temp = temp - 273.15
        
        psg2 = float(request.form.get('pressure2'))
        psa2 = psg2 + 0.101325
        temp2 = iapws.iapws97._TSat_P(psa2)
        temp2 = temp2 - 273.15

        isentha = isenthalpic(f_s,f_w,psa,temp,psa2,temp2)
        x0 = isentha['x0']
        x1 = isentha['x1']
        steam = isentha['flow_steam']
        water = isentha['flow_water']
        spefic_enthalpy = isentha['spefic_enthalpy']
        total_enthalpy = isentha['total_enthalpy']

        return render_template('enthalpy/enthalpy_pre_result.html',
                x0=round(x0,5),x1=round(x1,5),steam=round(steam,3),water=round(water,3),
                spefic_enthalpy=round(spefic_enthalpy,3),total_enthalpy=round(total_enthalpy,3),
                temp=round(temp,2),psg=round(psg,4),f_s=round(f_s,4),f_w=round(f_w,3),temp2=round(temp2,2),psg2=round(psg2,4))

        # except ValueError:
        #     return "<p>ValueError</p>"



# ---------------pressureloss-------------------------------
@app.route('/predrop_twophase_homo', methods=['GET', 'POST'])
def predrop_twophase_homo():
    return render_template('predrop/predrop_homo.html')

@app.route('/predrop_twophase_homo_result', methods=['GET', 'POST'])
def predrop_twophase_homo_result():
    if request.method == 'POST':
        # try:
        f_s = float(request.form.get('f_s')) #kg/h
        f_w = float(request.form.get('f_w')) #kg/h
        psg = float(request.form.get('pressure'))
        psa = psg + 0.101325
        temp = iapws.iapws97._TSat_P(psa)
        temp=temp-273.15

        piping = request.form.get('piping')
        sh = request.form.get('sh')
        length = float(request.form.get('length'))

        result = pressuredrop_twophase(psg,f_s,f_w,piping,sh,length)

        return render_template('predrop/predrop_homo_result.html',
                predrop=result['predrop'],Re=result['Re'],
                f_s=f_s,f_w=f_w,psg=psg,temp=round(temp,3),sh=sh,piping=piping,length=length,
                velocity=result['velocity'],RoH=result['RoH'],μtp=result['μtp'],m=result['m'])

        # except ValueError:
        #     return "<p>ValueError</p>"


@app.route('/predrop_twophase_LM', methods=['GET', 'POST'])
def predrop_twophase_LM():
    return render_template('predrop/predrop_LMcorrelation.html')

@app.route('/predrop_twophase_LM_result', methods=['GET', 'POST'])
def predrop_twophase_LM_result():
    if request.method == 'POST':
        # try:
        f_s = float(request.form.get('f_s')) #kg/h
        f_w = float(request.form.get('f_w')) #kg/h
        psg = float(request.form.get('pressure'))
        psa = psg + 0.101325
        temp = iapws.iapws97._TSat_P(psa)
        temp=temp-273.15

        piping = request.form.get('piping')
        sh = request.form.get('sh')
        length = float(request.form.get('length'))

        result = pressuredrop_twophase2(psg,f_s,f_w,piping,sh,length)

        return render_template('predrop/predrop_LMcorrelation_result.html',
                predrop=result['predrop'],ReG=result['ReG'],ReL=result['ReL'],
                f_s=f_s,f_w=f_w,psg=psg,temp=round(temp,3),sh=sh,piping=piping,length=length,
                φL=result['φL'],φG=result['φG'],parameterX=result['parameterX'],status=result['status'])


if __name__ == "__main__":
    app.run(debug=True)