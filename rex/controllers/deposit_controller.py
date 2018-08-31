from flask import Blueprint, request, session, redirect, url_for, render_template, flash, Response
from flask.ext.login import login_user, logout_user, current_user, login_required
from rex import app, db
from rex.models import user_model, deposit_model, history_model, invoice_model, wallet_model
import json
import urllib
import urllib2
from bson.objectid import ObjectId
from block_io import BlockIo
import datetime
from datetime import datetime
from datetime import datetime, date, timedelta
from time import gmtime, strftime
import time
import requests
import string
import random
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
version = 2 # API version
block_io = BlockIo('9fd3-ec01-722e-fd89', 'SECRET PIN', version)
# BTC TEST
# block_io = BlockIo('c11b-501c-0192-ab2c', 'SECRET PIN', version) 
__author__ = 'carlozamagni'

deposit_ctrl = Blueprint('deposit', __name__, static_folder='static', template_folder='templates')

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
def is_number(s):
    try:
        complex(s) # for int, long, float and complex
    except ValueError:
        return False
    return True
@deposit_ctrl.route('/deposit', methods=['GET', 'POST'])
def deposit():
    
    if session.get(u'logged_in') is None:
        return redirect('/user/login')
    uid = session.get('uid')
    query = db.Deposit.find({'uid': uid})
    uid = session.get('uid')
    user = db.User.find_one({'customer_id': uid})
    dataDeposit = db.deposits.find({'uid': uid})
    data_ticker = db.tickers.find_one({})
    data ={
    'deposit' : query,
    'title' : 'Deposit',
    'menu' : 'deposit',
    'float' : float,
    'int': int,
    'user': user,
    'deposit': dataDeposit,
    'btc_usd':data_ticker['btc_usd'],
    'sva_btc':data_ticker['sva_btc'],
    'sva_usd':data_ticker['sva_usd']
    }
    return render_template('account/deposit.html', data=data)
def binaryAmount(user_id, amount_invest):
    customer_ml = db.User.find_one({"customer_id" : user_id })
    if customer_ml.p_binary != '':  #and float(customer_ml.type) == 0
        while (True):
            customer_ml_p_binary = db.User.find_one({"customer_id" : customer_ml.p_binary })
            if customer_ml_p_binary is None:
                break
            else:
                if customer_ml_p_binary.left == customer_ml.customer_id:
                    #left
                    # count_f1 = db.User.find({"$and" :[{'p_node': customer_ml_p_binary.customer_id}, {'level': 2}] }).count()
                    if customer_ml_p_binary.level >= 2:
                    # if count_f1 >= 2 and customer_ml_p_binary.level == 2:
                        customers = db.User.find_one({"customer_id" : customer_ml_p_binary.customer_id })
                        customers.total_pd_left = float(customers.total_pd_left) + float(amount_invest)
                        customers.total_amount_left = float(customers.total_amount_left) + float(amount_invest)
                        db.users.save(customers)
                    print("left binary")
                else:
                    # count_f1 = db.User.find({"$and" :[{'p_node': customer_ml_p_binary.customer_id}, {'level': 2}] }).count()
                    if customer_ml_p_binary.level >= 2:
                    # if count_f1 >= 2 and customer_ml_p_binary.level == 2:
                        customers = db.User.find_one({"customer_id" : customer_ml_p_binary.customer_id })
                        customers.total_pd_right = float(customers.total_pd_right) + float(amount_invest)
                        customers.total_amount_right = float(customers.total_amount_right) + float(amount_invest)
                        db.users.save(customers)
                    print("right binary")
                    #binary

                # checkNode = db.users.find({"customer_id" : customer_ml_p_binary.customer_id })
                # if checkNode.count() == 0 or customer_ml_p_binary.customer_id == '11201729184651':
                #     break

            customer_ml = db.User.find_one({"customer_id" : customer_ml_p_binary.customer_id })
            if customer_ml is None:
                break
    return True
def SaveHistory(uid, user_id, username, amount, types, wallet, detail, rate, txtid):
    data_history = {
        'uid' : uid,
        'user_id': user_id,
        'username' : username,
        'amount': float(amount),
        'type' : types,
        'wallet': wallet,
        'date_added' : datetime.utcnow(),
        'detail': detail,
        'rate': rate,
        'txtid' : txtid,
        'amount_sub' : 0,
        'amount_add' : 0,
        'amount_rest' : 0
    }
    db.historys.insert(data_history)
    return True

def get_receive_program(user_id,amount):
    customer = db.users.find_one({"customer_id" : user_id })
    if customer['level'] == 2:
       max_receive = 200 
    if customer['level'] == 3:
       max_receive = 1000 
    if customer['level'] == 4:
       max_receive = 2000 
    if customer['level'] == 5:
       max_receive = 4000 
    if customer['level'] == 6:
       max_receive = 10000 
    if customer['level'] == 7:
       max_receive = 20000 
    if customer['level'] == 8:
       max_receive = 40000 
    if customer['level'] == 9:
       max_receive = 100000 

    if float(amount) > float(max_receive):
        amount_receve = max_receive
    else:
        amount_receve = amount
    return amount_receve

def FnRefferalProgram(user_id, amount_invest,amount_xvg_promotion):
    customer = db.users.find_one({"customer_id" : user_id })
    username_invest = customer['username']
    if customer['p_node'] != '0' or customer['p_node'] != '':
        customer_p_node = db.users.find_one({"customer_id" : customer['p_node'] })
        if customer_p_node is None:
            return True
        else:
            if customer_p_node['level'] >= 2:
                if customer_p_node['level'] == 2 or customer_p_node['level'] == 3:
                    percent_daily  = 8
                if customer_p_node['level'] == 4 or customer_p_node['level'] == 5:
                    percent_daily  = 10
                if customer_p_node['level'] == 6 or customer_p_node['level'] == 7:
                    percent_daily  = 11
                if customer_p_node['level'] == 8 or customer_p_node['level'] == 9:
                    percent_daily  = 12

                print(customer_p_node['username'],percent_daily,'reffral')
                commission = float(amount_invest)*percent_daily/100
                commission = round(commission,2)

                amount_max_out_p_node = get_receive_program(customer['p_node'],commission)

                if float(amount_max_out_p_node) > 0:

                    commission = amount_max_out_p_node

                    data_ticker = db.tickers.find_one({})

                    amount_btc_recive = round(float(commission)/float(data_ticker['btc_usd']),8)
                    print(amount_btc_recive)
                    rpc_connection = AuthServiceProxy("http://Ecy4M83321mWk7szPoiY2cw:DrWdoW83321Zrdi2ftYKVPt4P2Cb7HoQUZUuP6@127.0.0.1:23321")
                    dataSend = rpc_connection.sendtoaddress(customer_p_node['wallet'],amount_btc_recive)
                    
                    r_wallet = float(customer_p_node['r_wallet'])
                    new_r_wallet = float(r_wallet) + float(commission)
                    new_r_wallet = float(new_r_wallet)

                    total_earn = float(customer_p_node['total_earn'])
                    new_total_earn = float(total_earn) + float(commission)
                    new_total_earn = float(new_total_earn)

                    new_sva_balance = float(amount_xvg_promotion) + float(customer_p_node['sva_balance'])

                    print(new_sva_balance,"new_sva_balance")

                    db.users.update({ "_id" : ObjectId(customer_p_node['_id']) }, { '$set': {'total_earn': new_total_earn, 'r_wallet' :new_r_wallet, 'sva_balance' : new_sva_balance } })
                    detail = 'Get '+str(percent_daily)+' '+"""%"""+' referral bonus from member %s trade & mining %s USD' %(username_invest, amount_invest)
                    SaveHistory(customer_p_node['customer_id'],customer_p_node['_id'],customer_p_node['username'], commission, 'receive', 'USD', detail, '', '')



                    # usd_balance = float(customer_p_node['usd_balance'])
                    # new_usd_balance = float(commission) + float(usd_balance)

                    # total_earn = float(customer_p_node['total_earn'])
                    # new_total_earn = float(total_earn) + float(commission)
                    # new_total_earn = float(new_total_earn)
                   
                    # r_wallet = float(customer_p_node['r_wallet'])
                    # new_r_wallet = float(r_wallet) + float(commission)
                    # new_r_wallet = float(new_r_wallet)

                    # max_out = float(customer_p_node['max_out'])
                    # new_max_out = float(max_out) + float(commission)
                    # new_max_out = float(new_max_out)
                    
                    # db.users.update({ "_id" : ObjectId(customer_p_node['_id']) }, { '$set': { "usd_balance": new_usd_balance, 'total_earn': new_total_earn, 'r_wallet' :new_r_wallet,'max_out' :new_max_out } })
                    # detail = 'Get '+str(percent_daily)+' '+"""%"""+' referral bonus from member %s trade & mining %s USD' %(username_invest, amount_invest)
                    # SaveHistory(customer_p_node['customer_id'],customer_p_node['_id'],customer_p_node['username'], commission, 'receive', 'USD', detail, '', '')
        
    return True

def send_mail_active_package(email,usernames,amount):
    
    html = """\
        <div style="font-family:Arial,sans-serif;background-color:#f9f9f9;color:#424242;text-align:center">
       <div class="adM">
       </div>
       <table style="table-layout:fixed;width:90%;max-width:600px;margin:0 auto;background-color:#f9f9f9">
          <tbody>
             <tr>
                <td style="padding:20px 10px 10px 0px;text-align:left">
                   <a href="https://worldtrader.info" title="World Trade" target="_blank" >
                   <img src="https://worldtrader.info/static/home/images/logo/logo.png" alt="World Trade" class="CToWUd" style=" width: 200px; ">
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
                <td style="padding:30px 30px 10px 30px;line-height:1.8">Dear <b>"""+str(usernames)+"""</b>,</td>
             </tr>
             <tr>
                <td style="padding:10px 30px;line-height:1.8">You have successfully activated the $ """+str(amount)+""" package from World Trade</td>
             </tr>
             
             <tr>
                <td style="border-bottom:3px solid #efefef;width:90%;display:block;margin:0 auto;padding-top:30px"></td>
             </tr>
             <tr>
                <td style="padding:30px 30px 30px 30px;line-height:1.3">Best regards,<br> <a href="https://worldtrader.info/" target="_blank" >World Trade</a></td>
             </tr>
          </tbody>
       </table>
    </div>
    <div style="font-family:Arial,sans-serif;background-color:#f9f9f9;color:#424242;text-align:center;padding-bottom:10px;     height: 50px;">
   
</div>
    """

    return requests.post(
      "https://api.mailgun.net/v3/worldtrader.info/messages",
      auth=("api", "key-4cba65a7b1a835ac14b7949d5795236a"),
      data={"from": "World Trade <no-reply@worldtrader.info>",
        "to": ["", email],
        "subject": "Trade & Mining",
        "html": html})


#send_mail_active_package('vngroup12@gmail.com','vngroup','10000')
@deposit_ctrl.route('/LendingConfirm', methods=['GET', 'POST'])
def LendingConfirm():
    #return json.dumps({ 'status': 'error', 'message': 'Coming soon' })
    if session.get(u'logged_in') is None:
        return json.dumps({
            'status': 'error', 
            'message': 'Please Login' 
        })
    else:
        if request.method == 'POST':
            user_id = session.get('user_id')
            uid = session.get('uid')
            user = db.users.find_one({'_id': ObjectId(user_id)})
            
            usd_amount = request.form['usd_amount']
            
            checkIsNumberUSD = is_number(usd_amount)
            if usd_amount == '' or checkIsNumberUSD == False:
                return json.dumps({
                    'status': 'error',
                    'message': 'Please enter valid quantity' 
                })

            data_ticker = db.tickers.find_one({})
           
            
            convert_usd_btc = float(usd_amount)/float(data_ticker['btc_usd'])
            convert_usd_btc = round(convert_usd_btc, 8)

            btc_balance = float(user['btc_balance'])
            if float(convert_usd_btc) > float(btc_balance):
                return json.dumps({
                    'status': 'error', 
                    'message': 'Your balance is not enough' 
                })

            new_btc_balance = float(btc_balance) - float(convert_usd_btc)
            new_btc_balance = round(new_btc_balance, 8)
            total_invest = float(user['total_invest'])
    
            new_total_invest = float(usd_amount) + float(total_invest)
            new_total_invest = round(new_total_invest, 2)
            new_total_invest = float(new_total_invest)


            amount_xvg_promotion = 0
            if float(usd_amount) == 100:
                level =2
                percent_daily = 0.4
            if float(usd_amount) ==500:
                level =3
                percent_daily = 0.4
            if float(usd_amount) ==1000:
                level =4
                percent_daily = 0.5
            if float(usd_amount) == 2000:
                level =5
                percent_daily = 0.5
            if float(usd_amount) == 5000:
                level =6
                percent_daily = 0.6
                amount_xvg_promotion = 2000
            if float(usd_amount) == 10000:
                level =7
                percent_daily = 0.6
                amount_xvg_promotion = 4500
            if float(usd_amount) == 20000:
                level =8
                percent_daily = 0.65
                amount_xvg_promotion = 10000
            if float(usd_amount) == 50000:
                level =9
                percent_daily = 0.7
                amount_xvg_promotion = 30000
            if float(user['level']) > level:
                level = float(user['level'])

            new_xvg_balance = float(user['sva_balance']) + float(usd_amount)/0.8

            binary = binaryAmount(uid, usd_amount)
            
            db.users.update({ "_id" : ObjectId(user_id) }, { '$set': {"btc_balance": new_btc_balance, "total_invest": new_total_invest, 'level': level ,'sva_balance' : new_xvg_balance} })
            data_history = {
                'uid' : uid,
                'user_id': user_id,
                'username' : user['username'],
                'amount': float(convert_usd_btc),
                'type' : 'send',
                'wallet': 'BTC',
                'date_added' : datetime.utcnow(),
                'detail': 'Paid for trade & mining %s BTC ($ %s)' %(convert_usd_btc, usd_amount),
                'rate': '1 BTC = %s USD' %(data_ticker['btc_usd']),
                'txtid' : '' ,
                'amount_sub' : 0,
                'amount_add' : 0,
                'amount_rest' : 0
            }
            db.historys.insert(data_history)

            if float(usd_amount) >= 100 and float(usd_amount) < 1000:
                day = 300
            if float(usd_amount) >= 1000 and float(usd_amount) < 5000:
                day = 260
            if float(usd_amount) >= 5000 and float(usd_amount) < 20000:
                day = 225
            if float(usd_amount) >= 20000:
                day = 200
            
            data_deposit = {
                'uid' : uid,
                'user_id': user_id,
                'username' : user['username'],
                'amount_usd' : float(usd_amount),
                'amount_sva': float(convert_usd_btc),
                'status' : 1,
                'date_added' : datetime.utcnow(),
                'num_frofit' : 0,
                'types' : 0,
                'percent' :  percent_daily,
                'total_day': day,
                'total_day_earn': 0,
                'amount_daily' : 0,
                'num_profit' : 0,
                'lock_profit': 0
            }
            db.deposits.insert(data_deposit)

            content_send = 'You have successfully activated the %s USD from World Trade'%(usd_amount)
            
            requests.get('http://rest.esms.vn/MainService.svc/json/SendMultipleMessage_V4_get?Phone=%s&Content=%s&ApiKey=0D62EA98FC6D46AC5020E985F75426&SecretKey=A05FE5798D461BD67C1EDD4EC4ABF5&SmsType=4'%(user['telephone'],content_send))
            send_mail_active_package(user['email'],user['username'],usd_amount)

            FnRefferalProgram(uid, usd_amount,0)

            return json.dumps({
                'status': 'success', 
                'message': 'Trade & Mining success',
                'new_btc_balance': new_btc_balance,
                'new_total_invest': new_total_invest
            })

@deposit_ctrl.route('/LendingConfirmRe', methods=['GET', 'POST'])
def LendingConfirmRe():
    return json.dumps({ 'status': 'error', 'message': 'Coming soon' })
    if session.get(u'logged_in') is None:
        return json.dumps({
            'status': 'error', 
            'message': 'Please Login' 
        })
    else:
        if request.method == 'POST':
            user_id = session.get('user_id')
            uid = session.get('uid')
            user = db.users.find_one({'_id': ObjectId(user_id)})
            sva_amount = request.form['sva_amount']
            usd_amount = request.form['usd_amount']
            checkIsNumberSVA = is_number(sva_amount)
            usd_amount = round(float(usd_amount), 0)
            if sva_amount == '' or checkIsNumberSVA == False:
                return json.dumps({
                    'status': 'error', 
                    'message': 'Please enter valid quantity (quantity > 100)' 
                })
            checkIsNumberUSD = is_number(usd_amount)
            if usd_amount == '' or checkIsNumberUSD == False or float(usd_amount) < 100 or float(usd_amount) > 100000:
                return json.dumps({
                    'status': 'error',
                    'message': 'Please enter valid quantity (quantity > 100)' 
                })
            usd_balance = float(user['usd_balance'])
            if float(usd_amount) > float(usd_balance):
                return json.dumps({
                    'status': 'error', 
                    'message': 'Your balance is not enough' 
                })
            new_usd_balance = float(usd_balance) - float(usd_amount)
            new_usd_balance = round(new_usd_balance, 2)
            total_invest = float(user['total_invest'])
    
            new_total_invest = float(usd_amount) + float(total_invest)
            new_total_invest = round(new_total_invest, 2)
            new_total_invest = float(new_total_invest)
            if new_total_invest >= 0 and new_total_invest < 1000:
                max_out = 1000
                level =2
            if new_total_invest >= 1000 and new_total_invest < 5000:
                max_out = 5000
                level =3
            if new_total_invest >= 5000 and new_total_invest < 10000:
                max_out = 10000
                level =4
            if new_total_invest >= 10000 and new_total_invest < 50000:
                max_out = 20000
                level =5
            if new_total_invest >= 50000 and new_total_invest < 100000:
                max_out = 30000
                level =6
            if new_total_invest > 100000:
                max_out = 30000
                level =6
            if float(user['level']) > level:
                level = float(user['level'])
            binary = binaryAmount(uid, float(usd_amount))
            FnRefferalProgram(uid, float(usd_amount))
            db.users.update({ "_id" : ObjectId(user_id) }, { '$set': {"usd_balance": new_usd_balance, "total_invest": new_total_invest, 'max_out': max_out, 'level': level } })
            data_history = {
                'uid' : uid,
                'user_id': user_id,
                'username' : user['username'],
                'amount': float(usd_amount),
                'type' : 'send',
                'wallet': 'USD',
                'date_added' : datetime.utcnow(),
                'detail': 'Paid for lent %s USD' %(usd_amount),
                'rate': '',
                'txtid' : '' ,
                'amount_sub' : 0,
                'amount_add' : 0,
                'amount_rest' : 0
            }
            db.historys.insert(data_history)
            if float(usd_amount) >= 100 and float(usd_amount) < 1000:
                day = 180
            if float(usd_amount) >= 1000 and float(usd_amount) < 5000:
                day = 180
            if float(usd_amount) >= 5000 and float(usd_amount) < 10000:
                day = 150
            if float(usd_amount) >= 10000 and float(usd_amount) < 50000:
                day = 120
            if float(usd_amount) >= 50000 and float(usd_amount) < 100000:
                day = 90
            if float(usd_amount) >= 100000:
                day = 90
            data_deposit = {
                'uid' : uid,
                'user_id': user_id,
                'username' : user['username'],
                'amount_usd' : float(usd_amount),
                'amount_sva': 0,
                'status' : 1,
                'date_added' : datetime.utcnow(),
                'num_frofit' : 0,
                'types' : 0,
                'percent' :  0,
                'total_day': day,
                'total_day_earn': 0,
                'amount_daily' : 0,
                'num_profit' : 0,
                'lock_profit': 0
            }
            db.deposits.insert(data_deposit)
            return json.dumps({
                'status': 'success', 
                'message': 'Lending success',
                'new_sva_balance': new_usd_balance,
                'new_total_invest': new_total_invest
            })


def AutoLendingConfirm(user_id, uid, sva_amount, usd_amount):
    return json.dumps({ 'status': 'error', 'message': 'Coming soon' })

    user = db.users.find_one({'_id': ObjectId(user_id)})

    checkIsNumberSVA = is_number(sva_amount)
    if sva_amount == '' or checkIsNumberSVA == False:
        return json.dumps({
            'status': 'error', 
            'message': 'Please enter valid quantity (quantity > 100)' 
        })
    checkIsNumberUSD = is_number(usd_amount)
    if usd_amount == '' or checkIsNumberUSD == False or float(usd_amount) < 100:
        return json.dumps({
            'status': 'error',
            'message': 'Please enter valid quantity (quantity > 100)' 
        })

    data_ticker = db.tickers.find_one({})
    sva_usd = 3
    usd_amount = round(usd_amount, 0)
    convert_usd_sva = float(usd_amount)/float(sva_usd)
    convert_usd_sva = round(convert_usd_sva, 8)
    sva_balance = float(user['sva_balance'])
    if float(convert_usd_sva) > float(sva_balance):
        return json.dumps({
            'status': 'error', 
            'message': 'Your balance is not enough' 
        })
    new_sva_balance = float(sva_balance) - float(convert_usd_sva)
    new_sva_balance = round(new_sva_balance, 8)
    total_invest = float(user['total_invest'])

    new_total_invest = float(usd_amount) + float(total_invest)
    new_total_invest = round(new_total_invest, 2)
    new_total_invest = float(new_total_invest)

    binary = binaryAmount(uid, usd_amount)
    FnRefferalProgram(uid, usd_amount)
    data_history = {
        'uid' : uid,
        'user_id': user_id,
        'username' : user['username'],
        'amount': float(convert_usd_sva),
        'type' : 'send',
        'wallet': 'SVA',
        'date_added' : datetime.utcnow(),
        'detail': 'Paid for lent %s SVA ($ %s)' %(convert_usd_sva, usd_amount),
        'rate': '1 SVA = %s USD' %(sva_usd),
        'txtid' : '' ,
        'amount_sub' : 0,
        'amount_add' : 0,
        'amount_rest' : 0
    }
    db.historys.insert(data_history)
    if usd_amount >= 100 and usd_amount < 1000:
        day = 180
    if usd_amount >= 1000 and usd_amount < 5000:
        day = 180
    if usd_amount >= 5000 and usd_amount < 10000:
        day = 150
    if usd_amount >= 10000 and usd_amount < 50000:
        day = 120
    if usd_amount >= 50000 and usd_amount < 100000:
        day = 90
    data_deposit = {
        'uid' : uid,
        'user_id': user_id,
        'username' : user['username'],
        'amount_usd' : float(usd_amount),
        'amount_sva': float(convert_usd_sva),
        'status' : 1,
        'date_added' : datetime.utcnow(),
        'num_frofit' : 0,
        'types' : 0,
        'percent' :  0,
        'total_day': day,
        'total_day_earn': 0,
        'amount_daily' : 0,
        'num_profit' : 0,
        'lock_profit': 0
    }
    db.deposits.insert(data_deposit)
    return 1

@deposit_ctrl.route('/autolendingstep1', methods=['GET', 'POST'])
def autolending():
    return json.dumps({'status':'off'})
    listUser = db.users.find({ '$and': [ { 'sva_balance': { '$ne': 0 } }, { 'sva_balance': { '$ne': '0' } } ] } )
    # listUser = db.users.find({ 'username':'haidat99' } )
    # i = 0
    for x in listUser:
        # 'smarfva, smartfvasmartfva
        # (147, u'leadervn', 44268.77, 39841.893, 4426.877, 159368.0, 5000, 3)
        balance = round(float(x['sva_balance']), 8)
        db.users.update({ "_id" : ObjectId(x['_id']) }, { '$set': {'sva_balance': balance} })
        # amount = float(x['sva_balance'])*0.9
        # amount_invest = amount* 4
        # amount_invest= round(amount_invest, 0)
        # if float(amount_invest) >= 100 and x['username'] != 'svaindia':
        #     uid= x['customer_id']
        #     user_id = x['_id']
        #     username = x['username']
        #     sva_usd = 4
        #     i = i + 1
        #     max_out = 0
        #     level = 0
        #     day = 0
        #     if amount_invest >= 100 and amount_invest < 1000:
        #         max_out = 1000
        #         level =2
        #         day = 180
        #     if amount_invest >= 1000 and amount_invest < 5000:
        #         max_out = 5000
        #         level =3
        #         day = 180
        #     if amount_invest >= 5000 and amount_invest < 10000:
        #         max_out = 10000
        #         level =4
        #         day = 150
        #     if amount_invest >= 10000 and amount_invest < 50000:
        #         max_out = 20000
        #         level =5
        #         day = 120
        #     if amount_invest >= 50000 and amount_invest < 100000:
        #         max_out = 30000
        #         level =6
        #         day = 90
        #     if amount_invest > 100000:
        #         max_out = 30000
        #         level =6
        #         day = 90
        #     if max_out > 0:
        #         balance = round(float(x['sva_balance']), 8)
        #         new_sva_balance = float(balance) - amount
                # time.sleep(1)
                # print(i, x['username'], balance, round(amount, 8), round(float(new_sva_balance), 8), amount_invest, max_out, level)
                # 1
                # db.users.update({ "_id" : ObjectId(x['_id']) }, { '$set': {'max_out': max_out, 'level': level } })
                # For mat sva_balance 8
                # db.users.update({ "_id" : ObjectId(x['_id']) }, { '$set': {'sva_balance': balance} })
                
            

    return json.dumps({'paymentSVA':'success'})

@deposit_ctrl.route('/autolendingstep2', methods=['GET', 'POST'])
def autolendingautolending():
    return json.dumps({'status':'off'})
    listUser = db.users.find({ '$and': [ { 'sva_balance': { '$ne': 0 } }, { 'sva_balance': { '$ne': '0' } } ] } )
    # listUser = db.users.find({ 'username':'haidat99' } )
    i = 0
    for x in listUser:
        # 'smarfva, smartfvasmartfva
        # (147, u'leadervn', 44268.77, 39841.893, 4426.877, 159368.0, 5000, 3)

        amount = float(x['sva_balance'])*0.6
        amount_invest = amount* 1.5
        amount_invest= round(amount_invest, 0)
        if float(amount_invest) >= 100 and x['username'] != 'svaindia':
            uid= x['customer_id']
            user_id = x['_id']
            username = x['username']
            sva_usd = 1.5
            i = i + 1
            max_out = 0
            level = 0
            day = 0
            if amount_invest >= 100 and amount_invest < 1000:
                max_out = 1000
                level =2
                day = 180
            if amount_invest >= 1000 and amount_invest < 5000:
                max_out = 5000
                level =3
                day = 180
            if amount_invest >= 5000 and amount_invest < 10000:
                max_out = 10000
                level =4
                day = 150
            if amount_invest >= 10000 and amount_invest < 50000:
                max_out = 20000
                level =5
                day = 120
            if amount_invest >= 50000 and amount_invest < 100000:
                max_out = 30000
                level =6
                day = 90
            if amount_invest > 100000:
                max_out = 30000
                level =6
                day = 90
            if max_out > 0:
                balance = round(float(x['sva_balance']), 8)
                new_sva_balance = float(balance) - amount
                # time.sleep(1)
                print(i, x['username'], balance, round(amount, 8), round(float(new_sva_balance), 8), amount_invest, max_out, level)
                # 1
                # db.users.update({ "_id" : ObjectId(x['_id']) }, { '$set': {'max_out': max_out, 'level': level } })
                
                # 2
                binaryAmount(uid, amount_invest)
                FnRefferalProgram(uid, amount_invest)
                db.users.update({ "_id" : ObjectId(x['_id']) }, { '$set': {"sva_balance": new_sva_balance, "total_invest": amount_invest } })
                data_deposit = {
                    'uid' : uid,
                    'user_id': user_id,
                    'username' : username,
                    'amount_usd' : float(amount_invest),
                    'amount_sva': float(amount),
                    'status' : 1,
                    'date_added' : datetime.utcnow(),
                    'num_frofit' : 0,
                    'types' : 0,
                    'percent' :  0,
                    'total_day': day,
                    'total_day_earn': 0,
                    'amount_daily' : 0,
                    'num_profit' : 0,
                    'lock_profit': 0
                }
                db.deposits.insert(data_deposit)
                data_history = {
                    'uid' : uid,
                    'user_id': user_id,
                    'username' : username,
                    'amount': float(amount),
                    'type' : 'send',
                    'wallet': 'SVA',
                    'date_added' : datetime.utcnow(),
                    'detail': 'Paid for lent %s SVA ($ %s)' %(amount, amount_invest),
                    'rate': '1 SVA = %s USD' %(sva_usd),
                    'txtid' : '' ,
                    'amount_sub' : 0,
                    'amount_add' : 0,
                    'amount_rest' : 0
                }
                db.historys.insert(data_history)
                # time.sleep(3)

    return json.dumps({'paymentSVA':'success'})
