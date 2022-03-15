from flask import Flask, render_template, redirect, request, flash,jsonify
from flask_sqlalchemy import SQLAlchemy
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import io
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg
from io import BytesIO
from matplotlib.figure import Figure
import base64



app = Flask(__name__)
app.secret_key = 'hogehoge'
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


@app.route('/input')
def input():
    return render_template('geochemi/input.html')

@app.route('/delete/<int:id>')
def delete(id):
    post = Post.query.get(id)
    db.session.delete(post)
    db.session.commit()
    return redirect('/')

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    post = Post.query.get(id)
    if request.method == 'GET':
        return render_template('geochemi/update.html', post=post)

    else:
        post.Rb = request.form.get('Rb')
        post.Sr = request.form.get('Sr')
        db.session.commit()
        return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)