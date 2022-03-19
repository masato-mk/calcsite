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
from parameter import iapws97_Region4_P,iapws97_Region4_T

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
            
            sv_w = round(waterpara['v'],6)
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




if __name__ == "__main__":
    app.run(debug=True)