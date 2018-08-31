from json import dumps
import json
from flask import Flask, send_from_directory, send_file, Blueprint, jsonify,session, request, redirect, url_for, render_template, json, flash, send_file
from flask.ext.login import login_required, LoginManager, current_user
from flask.ext.mongokit import MongoKit
from flask.templating import render_template
import os
import settings
from random import randint
from hashlib import sha256
import string
import random
from datetime import datetime
from datetime import datetime, date, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_socketio import SocketIO
import requests
import json
from flask_socketio import emit
from bson.objectid import ObjectId
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr

# from flask_recaptcha import ReCaptcha
__author__ = 'carlozamagni'

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static/uploads')

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config.from_object(settings)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
socketio = SocketIO()
socketio.init_app(app)

db = MongoKit(app)

lm = LoginManager()
lm.init_app(app)
lm.login_view = '/auth/login'

from rex.controllers import user_controller
app.register_blueprint(blueprint=user_controller.user_ctrl, url_prefix='/user')

from rex.controllers import auth_controller
app.register_blueprint(blueprint=auth_controller.auth_ctrl, url_prefix='/auth')

from rex.controllers import dashboard_controller
app.register_blueprint(blueprint=dashboard_controller.dashboard_ctrl, url_prefix='/account')

from rex.controllers import ico_controller
app.register_blueprint(blueprint=ico_controller.ico_ctrl, url_prefix='/account')

from rex.controllers import deposit_controller
app.register_blueprint(blueprint=deposit_controller.deposit_ctrl, url_prefix='/account')

from rex.controllers import refferal_controller
app.register_blueprint(blueprint=refferal_controller.refferal_ctrl, url_prefix='/account')
from rex.controllers import support_controller
app.register_blueprint(blueprint=support_controller.support_ctrl, url_prefix='/account')

from rex.controllers import personal_controller
app.register_blueprint(blueprint=personal_controller.personal_ctrl, url_prefix='/account')

from rex.controllers import history_controller
app.register_blueprint(blueprint=history_controller.history_ctrl, url_prefix='/account')

from rex.controllers import withdrawal_controller
app.register_blueprint(blueprint=withdrawal_controller.withdrawal_ctrl, url_prefix='/account')

from rex.controllers import wallet_controller
app.register_blueprint(blueprint=wallet_controller.wallet_ctrl, url_prefix='/account')

from rex.controllers import auto_controller
app.register_blueprint(blueprint=auto_controller.auto_ctrl, url_prefix='/auto')

from rex.controllers import admin_controller
app.register_blueprint(blueprint=admin_controller.admin_ctrl, url_prefix='/admin')
from rex.controllers import admin
app.register_blueprint(blueprint=admin.admin1_ctrl, url_prefix='/admin')

@app.route('/testsendmail', methods = ['GET', 'POST'])
def downlqweroad():
    username = 'no-reply@smartfva.co'
    password = 'rbdlnsmxqpswyfdv'
    msg = MIMEMultipart('mixed')
    mailServer = smtplib.SMTP('smtp.gmail.com', 587) # 8025, 587 and 25 can also be used. 
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(username, password)
    sender = 'no-reply@smartfva.co'
    recipient = 'belindatbeach@gmail.com'

    msg['Subject'] = 'Congratulations. Your account is now active111!'
    msg['From'] = sender
    msg['To'] = recipient
    html = """\
    <div style="font-family:Arial,sans-serif;background-color:#f9f9f9;color:#424242;text-align:center">
    <div class="adM">
    </div>
    <table style="table-layout:fixed;width:90%;max-width:600px;margin:0 auto;background-color:#f9f9f9">
    <tbody>
     <tr>
        <td style="padding:20px 10px 10px 0px;text-align:left">
           <a href="https://smartfva.co/" title="SmartFVA" target="_blank" >
           <img src="https://i.imgur.com/tyjTbng.png" alt="SmartFVA" class="CToWUd" style=" width: 100px; ">
           </a>
        </td>
        <td style="padding:0px 0px 0px 10px;text-align:right">
        </td>
     </tr>
    </tbody>
    </table>
    </div>
    <div style="font-family:Arial,sans-serif;background-color:#f9f9f9;color:#424242;text-align:center">
    <table style="table-layout:fixed;width:90%;max-width:600px;margin:0 auto;background:#fff;font-size:14px;border:2px solid #e8e8e8;text-align:left;table-layout:fixed">
    <tbody>
     <tr>
        <td style="padding:10px 30px;line-height:1.8">Congratulations, Your account on the <a href="https://smartfva.co/" target="_blank">SmartFVA</a> is now registered and active.</td>
     </tr>
     <tr>
        <td style="border-bottom:3px solid #efefef;width:90%;display:block;margin:0 auto;padding-top:30px"></td>
     </tr>
     <tr>
        <td style="padding:30px 30px 30px 30px;line-height:1.3">Best regards,<br> SmartFVA Team<br>  <a href="https://www.smartfva.co/" target="_blank" >www.smartfva.co</a></td>
     </tr>
    </tbody>
    </table>
    </div>
    <div style="font-family:Arial,sans-serif;background-color:#f9f9f9;color:#424242;text-align:center;padding-bottom:10px;     height: 50px;">

    </div>
    """
    html_message = MIMEText(html, 'html')

    msg.attach(html_message)
    mailServer.sendmail(sender, recipient, msg.as_string())
    mailServer.close()

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

@app.route('/whitepaper.pdf', methods = ['GET', 'POST'])
def download():
    return send_from_directory(os.path.join(app.root_path, 'static/uploads'), 'whitepaper.pdf', as_attachment=False, attachment_filename=None)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico')
@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'sitemap.xml')
# @app.route("/robots.txt")
# def robots_txt():
#     print 11111111111111111111111111
#     return send_from_directory(os.path.join(app.root_path, 'static'), 'robots.txt')
@app.route('/api/getInfo') 
def function():
    

    url = 'https://api.coindesk.com/v1/bpi/currentprice.json'
    r = requests.get(url)
    response_dict = r.json()
    price_btc_usd = response_dict["bpi"]["USD"]['rate_float']
    price_btc_usd = round(price_btc_usd,2)
    data_ticker = db.tickers.find_one({})
    new_sva_btc = float(data_ticker['sva_usd'])/float(price_btc_usd)
    new_sva_btc = round(new_sva_btc, 8)
    data_ticker['btc_usd'] = float(price_btc_usd)
    data_ticker['sva_btc'] = float(new_sva_btc)
    db.tickers.save(data_ticker)
    return json.dumps({'status': 'success'})

# @app.route('/api/getInfo') 
# def function():
#     url = 'https://api.coinmarketcap.com/v1/ticker/bitcoin'
#     r = requests.get(url)
#     response_dict = r.json()
#     print response_dict
#     price_btc_usd = response_dict[0]['price_usd']
#     price_btc_usd =float(price_btc_usd)
#     price_btc_usd = round(price_btc_usd,2)
#     data_ticker = db.tickers.find_one({})
#     new_sva_btc = float(data_ticker['sva_usd'])/float(price_btc_usd)
#     new_sva_btc = round(new_sva_btc, 8)
#     data_ticker['btc_usd'] = float(price_btc_usd)
#     data_ticker['sva_btc'] = float(new_sva_btc)
#     db.tickers.save(data_ticker)
#     return json.dumps({'status': 'success'})

@app.route('/getInfo')
def getInfo(): # date = datetime object.
    data_ticker = db.tickers.find_one({})
    data = {
        'btc_usd':data_ticker['btc_usd'],
        'sva_btc':data_ticker['sva_btc'],
        'sva_usd':data_ticker['sva_usd']
    }
    return json.dumps(data)


@app.route('/info-ico', methods=['GET', 'POST'])
def countIco():
    ico = db.icosums.find_one({})
    percent = ico['percent']
    percent = float(percent)/1000000
    percent = float(percent)*100
    data = {
        'percent': round(percent, 2)
    }
    return json.dumps(data)
@app.template_filter()
def format_date(date): # date = datetime object.
    return date.strftime('%Y-%m-%d %H:%M:%S')
@app.template_filter()
def format_only_date(date): # date = datetime object.
    return date.strftime('%Y-%m-%d')
@app.template_filter()
def find_username(uid): # date = datetime object.
    if uid:
        uid = uid
    else:
        uid ='1111111'
    user = db.User.find_one({'customer_id': uid})
    if user is None:
        return ''
    else:
        return user.username

@app.template_filter()
def find_user_usd(uid): # date = datetime object.
    if uid:
        uid = str(uid)
    else:
        uid ='1111111'
    user = db.users.find_one({'_id': ObjectId(uid)})
    if user is None:
        return ''
    else:
        return user['usd_balance']

@app.template_filter()
def find_user_sva(uid): # date = datetime object.
    if uid:
        uid = uid
    else:
        uid ='1111111'
    user = db.users.find_one({'_id': ObjectId(uid)})
    if user is None:
        return ''
    else:
        return user['sva_balance']

@app.template_filter()
def to_string(value):
    
    return str(value)
@app.template_filter()
def number_format(value, tsep=',', dsep='.'):
    s = unicode(value)
    cnt = 0
    numchars = dsep + '0123456789'
    ls = len(s)
    while cnt < ls and s[cnt] not in numchars:
        cnt += 1

    lhs = s[:cnt]
    s = s[cnt:]
    if not dsep:
        cnt = -1
    else:
        cnt = s.rfind(dsep)
    if cnt > 0:
        rhs = dsep + s[cnt+1:]
        s = s[:cnt]
    else:
        rhs = ''

    splt = ''
    while s != '':
        splt = s[-3:] + tsep + splt
        s = s[:-3]

    return lhs + splt[:-1] + rhs
@app.template_filter()
def format_round(value):
    value = float(value)
    return '{:20,.8f}'.format(value)
@app.template_filter()
def format_usd(value):
    value = float(value)
    return '{:20,.2f}'.format(value)

@app.template_filter()
def format_satoshi(value):
    value = float(value)
    return '{:.8f}'.format(value)

@app.template_filter()
def format_btc_usd(value):
    data_ticker = db.tickers.find_one({})
    btc_usd = data_ticker['btc_usd']
    value = float(value)*float(btc_usd)
    return '{:20,.2f}'.format(value)

@app.template_filter()
def format_xvg_usd(value):
    data_ticker = db.tickers.find_one({})
    xvg_usd = data_ticker['xvg_usd']
    value = float(value)*0.8
    return '{:20,.2f}'.format(value)


@app.template_filter()
def format_usds(value):
    value = float(value)
    return '{:20,.0f}'.format(value)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
@app.route('/user/uploader-avatar', methods = ['GET', 'POST'])
def upload_file():
    if session.get(u'logged_in') is None:
        return redirect('/user/login')
    uid = session.get('uid')
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            extension = os.path.splitext(file.filename)[1]
            name = id_generator()+uid
            f_name = str(name) + extension

            user = db.User.find_one({'customer_id': uid})
            if user.img_profile != '':
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], user.img_profile))

            db.users.update({ "customer_id" : uid }, { '$set': { "img_profile": f_name } })

            file.save(os.path.join(app.config['UPLOAD_FOLDER'], f_name))
            flash({'msg':'Update Avatar success!', 'type':'success'})
            return redirect('/user/setting')
    return redirect('/user/setting')
# ================================
# return redirect('/maintenance')
@app.route('/maintenance')
def maintenance():
    data ={
    'menu' : 'maintenance'
    }
    return render_template('maintenace.html', data=data)
@app.route('/account/exchange')
def exchnageApp():
    if session.get(u'logged_in') is None:
        return redirect('/user/login')
    else:
        uid = session.get('uid')
        user = db.User.find_one({'customer_id': uid})
    data ={
    'user': user,
    'menu' : 'exchange'
    }
    return render_template('account/exchange.html', data=data)
@app.route('/login')
def home_pagelogin():
    data ={
    'menu' : 'home'
    }
    return redirect('auth/login')

@app.route('/')
def home_page():
    from datetime import datetime
    from dateutil.relativedelta import relativedelta

    print 'Today: ',datetime.now().strftime('%d/%m/%Y %H:%M:%S') 
    date_after_month = datetime.now()+ relativedelta(days=1)
    print 'After 5 Days:', date_after_month.strftime('%d/%m/%Y %H:%M:%S')
    data ={
    'menu' : 'home'
    }
    # return redirect('/user/login')
    return render_template('homev2/index.html', data=data)
@app.route('/policy.html')
def home_policy():
    data ={
    'menu' : 'Policy'
    }
    # return redirect('/user/login')
    return render_template('homev2/policy.html', data=data)
@app.route('/investment.html')
def home_lending():
    data ={
    'menu' : 'Trade & Mining'
    }
    # return redirect('/user/login')
    return render_template('homev2/investment.html', data=data)
@app.route('/affiliate.html')
def home_affiliate():
    data ={
    'menu' : 'affiliate'
    }
    # return redirect('/user/login')
    return render_template('homev2/affiliate.html', data=data)
@app.route('/help.html')
def home_roadmap():
    data ={
    'menu' : 'roadmap'
    }
    # return redirect('/user/login')
    return render_template('homev2/help.html', data=data)
@app.route('/faq.html')
def home_ico():
    data ={
    'menu' : 'ico'
    }
    # return redirect('/user/login')
    return render_template('homev2/faq.html', data=data)

@app.route('/news.html')
def home_news():
    data ={
    'menu' : 'news'
    }
    return render_template('homev2/news.html', data=data)

@app.route('/faq-all-question')
def home_adfpage():
    data ={
    'menu' : 'faq'
    }
    # return redirect('/user/login')
    return render_template('home/faq-all-question.html', data=data)
@app.route('/about-us')
def about_us():
    data ={
    'menu' : 'home'
    }
    return redirect('/user/login')
    return render_template('home/about-two.html', data=data)
@app.route('/buy-bitcoin')
def buy_bitcoin():
    data ={
    'menu' : 'home'
    }
    return redirect('/user/login')
    return render_template('home/buy-bitcoin.html', data=data)

@app.route('/contact')
def contact_us():
    data ={
    'menu' : 'home'
    }
    return redirect('/user/login')
    return render_template('home/contact-style-2.html', data=data)
def set_password(password):
    return generate_password_hash(password)
@app.route('/setup')
def setup():
    inserted = []
    return json.dumps({'status' : 'error'})
    
    # db.users.update({'customer_id': '1010101001'}, {'$set': {'creation':datetime.utcnow()}})
    # return json.dumps({'status' : 'error'})
    users = [{"_id" : "5995a569587b3b15a14174e0",
    "roi" : 100920,
    "right" : "",
    "p_binary" : "",
    "m_wallet" : 600000000,
    "creation" : datetime.utcnow(),
    "telephone" : "000000000",
    "password_transaction" : set_password('12345'),
    "total_amount_right" : int("0"),
    "total_pd_right" : int("0"),
    "btc_wallet" : "19WpQavvcEcy4MmWk7szPoiY2cwvi8jt9E",
    "p_node" : "",
    "r_wallet" : 600000000,
    "password_custom" : set_password('12345'),
    "total_pd_left" : 9700,
    "customer_id" : "1010101001",
    "email" : "meccafunds@meccafund.org",
    "total_amount_left" : 10500,
    "username" : "root",
    "s_wallet" : 1000000000,
    "total_invest" : 100000,
    "password" : set_password('12345'),
    "img_profile" : "",
    "max_out" : 500000,
    "max_binary" : 500000,
    "name" : "MECCAFUND",
    "level" : int("3"),
    "country" : "French Southern territories",
    "wallet" : "",
    "status" : 1,
    "total_earn" : 10000,
    "position" : "",
    'sva_balance': 0,
    'sva_address': '',
    'btc_balance': 0,
    'btc_address': '',
    'usd_balance': 0,
    'total_max_out': 0,
    'total_capital_back': 0,
    'total_commission': 0,
    'secret_2fa':'',
    'status_2fa': 0,
    "left" : "",
    's_left': 0,
    's_right': 0,
    's_p_node': 0,
    's_p_binary': 0,
    's_token': 0,
    's_id': 0
    }]
    db['users'].drop()
    db['users'].insert(users)
    inserted.append(users)

    admin = [{
        "_id" : "1175a9437u2b3b15a14174e0",
        'username':  'admin',
        'email' :  'admin@admin.com',
        'password': set_password('12345'),
        'sum_withdraw': 0,
        'sum_invest' : 0
    }]
    db['admins'].drop()
    db['admins'].insert(admin)
    inserted.append(admin)

    ticker = [{
        'btc_usd' : 7500,
        'sva_btc' : 0.00013333,
        'sva_usd' : 1
    }]
    db['tickers'].drop()
    db['tickers'].insert(ticker)

    return json.dumps(inserted)
   


@socketio.on('getInfo', namespace='/SmartFVA')
def test_message(message):
    print('Client connect', request.sid)
    data_ticker = db.tickers.find_one({})
    data = {
        'btc_usd':data_ticker['btc_usd'],
        'sva_btc':data_ticker['sva_btc'],
        'sva_usd':data_ticker['sva_usd']
    }
    emit('my_response',data,broadcast=True)

@socketio.on('clidisconnect')
def disconnect_user():
    print 'discocccccccccc================================================='
    print('Client disconnected', request.sid)


@app.route('/getBalance')
def homewalqwrwlet():
    if session.get(u'logged_in') is None:
        return json.dumps({ 'status': 'error' })
    else:
        uid = session.get('uid')
        user_id = session.get('user_id')
        user = db.User.find_one({'customer_id': uid})
        data = {
            'status': 'success',
            'sva_balance': user['sva_balance'],
            'btc_balance': user['btc_balance'],
            'usd_balance': user['usd_balance'],
            'total_capital_back': user['total_capital_back'],
            'total_invest': user['total_invest'],
            'total_earn': user['total_earn']

        }
        return json.dumps(data)

