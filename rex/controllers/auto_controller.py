from flask import Blueprint, request, session, redirect, url_for, render_template
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

import collections

from dateutil.relativedelta import relativedelta
version = 2 # API version
block_io = BlockIo('9fd3-ec01-722e-fd89', 'SECRET PIN', version)

__author__ = 'carlozamagni'

auto_ctrl = Blueprint('auto', __name__, static_folder='static', template_folder='templates')


def binaryInsert(customer_ml_p_binary, binary_amount_recieve):
    binary_amount_recieves = float(customer_ml_p_binary.r_wallet) + float(binary_amount_recieve)
    db.users.update({ "customer_id" : customer_ml_p_binary.customer_id }, { '$set': { "r_wallet": binary_amount_recieves } })

    binary_amount_sum = float(customer_ml_p_binary.s_wallet) + float(binary_amount_recieve)
    db.users.update({ "customer_id" : customer_ml_p_binary.customer_id }, { '$set': { "s_wallet": binary_amount_sum } })

    binary_total_earns = float(customer_ml_p_binary.total_earn)+float(binary_amount_recieve)
    db.users.update({ "customer_id" : customer_ml_p_binary.customer_id }, { '$set': { "total_earn": binary_total_earns } })

    binary_data_send = {
        'date_added': datetime.utcnow(),
        'uid' : customer_ml_p_binary.customer_id,
        'name' : customer_ml_p_binary.username,
        'amount_sub' : 0,
        'amount_add' : binary_amount_recieve/1000000,
        'amount_rest' : binary_amount_sum/1000000,
        'type' : "Binary Commission ",
        'detail' : 'Earn 4% Binary bonus on downline'
    }
    history_ids = db.history.insert(binary_data_send)
    return history_ids

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

def get_id_tree(ids):
    listId = ''

    query = db.users.find({'p_binary': ids})
    for x in query:
        listId += ', %s'%(x['customer_id'])
        listId += get_id_tree(x['customer_id'])
    return listId

def binary_left(customer_id):
    check_f1 = db.users.find({'$and' : [{'p_node' : customer_id},{'level':{'$gt': 0 }} ]})
    
    if check_f1.count() > 0:
        listId = ''
        for x in check_f1:
            listId += ',%s'%(x['customer_id'])
        arrId = listId[1:]

        count = db.users.find_one({'customer_id': customer_id})
        if count['left'] == '':
            customer_binary = ',0'
        else:
            ids = count['left']

            count = get_id_tree(count['left'])

            if count:
                customer_binary = '%s , %s'%(count, ids)

            else:
                customer_binary = ',%s'%(ids)

        customer_binary = customer_binary[1:]

        array = '%s, %s'%(arrId, customer_binary)
        customers = array.split(',')
        customers = map(int, customers)

        check_in_left = [item for item, count in collections.Counter(customers).items() if count > 1]

        if len(check_in_left) != 0:
            check_in_left = 1
        else:
            check_in_left = -1
    else:
        check_in_left = -1
    return check_in_left
    

def binary_right(customer_id):
    check_f1 = db.users.find({'$and' : [{'p_node' : customer_id},{'level':{'$gt': 0 }} ]})

    if check_f1.count() > 0:
        listId = ''
        for x in check_f1:
            listId += ', %s'%(x['customer_id'])
        arrId = listId[1:]
        count = db.users.find_one({'customer_id': customer_id})
        if count['right'] == '':
            customer_binary = ',0'
        else:
            ids = count['right']
            count = get_id_tree(count['right'])
            if count:
                customer_binary = '%s , %s'%(count, ids)
            else:
                customer_binary = ',%s'%(ids)
            
        customer_binary = customer_binary[1:]
        array = '%s, %s'%(arrId, customer_binary)
        customers = array.split(',')
        customers = map(int, customers)

        check_in_right = [item for item, count in collections.Counter(customers).items() if count > 1]
        if len(check_in_right) != 0:
            check_in_right = 1
        else:
            check_in_right = -1
    else:
        check_in_right = -1
    return check_in_right

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

# def auto_return_xvg():
#     customer = db.users.find({'sva_balance' : {'$gt': 0 }})
#     for x in customer:
#         amount_recieve = float(x['sva_balance'])*0.040992
#         usd_balance = float(x['usd_balance'])
#         new_usd_balance = float(amount_recieve) + float(usd_balance)
#         db.users.update({ "_id" : ObjectId(x['_id']) }, { '$set': { "usd_balance": round(new_usd_balance,2),"sva_balance" : 0 } })
#         detail = "Convert "+str(x['sva_balance'])+" XVG. Price 1 XVG = 0.040992 USD"
#         SaveHistory(x['customer_id'],x['_id'],x['username'], amount_recieve, 'receive', 'USD', detail, '', '')

# @auto_ctrl.route('/auto-return-xvg', methods=['GET', 'POST'])
# def auto_return_xvgss():
#     auto_return_xvg()
#     return json.dumps({'status' : 'success'})


# @auto_ctrl.route('/auto-add-wtx', methods=['GET', 'POST'])
# def auto_add_wtx():
#     get_invest = db.deposits.find({ "status": 1,"lock_profit": 0 });

#     for x in get_invest:
        
#         customer = db.User.find_one({'_id': ObjectId(x['user_id'])})
        
#         if customer is not None:
#             amount_recieve = float(customer['sva_balance']) + (float(x['amount_usd'])/0.8)
#             db.users.update({ "_id" : ObjectId(x['user_id']) }, { '$set': { "sva_balance": amount_recieve} })
#     return json.dumps({'status' : 'success'})


@auto_ctrl.route('/auto-tickers', methods=['GET', 'POST'])
def auto_tickers():
    response_xvg = urllib2.urlopen("https://api.coinmarketcap.com/v1/ticker/verge/")
    response_xvg = response_xvg.read()
    response_xvg = json.loads(response_xvg)

    response_btc = urllib2.urlopen("https://api.coinmarketcap.com/v1/ticker/bitcoin/")
    response_btc = response_btc.read()
    response_btc = json.loads(response_btc)
    print(response_btc)
    db.tickers.update({},{'$set': {'xvg_usd': response_xvg[0]['price_usd'],'xvg_btc': response_xvg[0]['price_btc'],'btc_usd' : response_btc[0]['price_usd']}})
    return json.dumps({'status' : 'success'})


@auto_ctrl.route('/binaryBonusOprHJhEp/4cLi4bO4ISCjVauHrkNa5oIc/<ids>', methods=['GET', 'POST'])
def caculator_binary(ids):
    
    # return json.dumps({'status' : 'off'})
    if ids =='RsaW3Kb1gDkdRUGDo':
        countUser = db.users.find({'$and': [{'total_pd_left':{'$gt': 0 }}, {'total_pd_right':{'$gt': 0 }}]}).count()
        if countUser > 0:
            user = db.users.find({'$and': [{'total_pd_left':{'$gt': 0 }}, {'total_pd_right':{'$gt': 0 }}]})
            # user = db.users.find({'username':'robertnguyen'})
            for x in user:
                if x['total_pd_left'] > x['total_pd_right']:
                    balanced = x['total_pd_right']
                    pd_left = float(x['total_pd_left'])-float(x['total_pd_right'])
                    db.users.update({ "customer_id" : x['customer_id'] }, { '$set': { "total_pd_left": pd_left } })
                    db.users.update({ "customer_id" : x['customer_id'] }, { '$set': { "total_pd_right": 0 } })
                else:
                    balanced = x['total_pd_left']
                    pd_right = float(x['total_pd_right'])-float(x['total_pd_left'])
                    db.users.update({ "customer_id" : x['customer_id'] }, { '$set': { "total_pd_left": 0 } })
                    db.users.update({ "customer_id" : x['customer_id'] }, { '$set': { "total_pd_right": pd_right } })
                    

                
                if binary_left(x['customer_id']) == 1 and binary_right(x['customer_id']) == 1:
                    percent = 0
                    level = float(x['level'])
                    if float(level) == 2 or float(level) == 3:
                        percent = 6
                    if float(level) == 4 or float(level) == 5:
                        percent = 8
                    if float(level) == 6 or float(level) == 7:
                        percent = 10
                    if float(level) == 8 or float(level) == 9:
                        percent = 12

                    percent_commission = float(percent)/100
                    amount_recieve = balanced*percent_commission
                    
                    amount_recieve = round(float(amount_recieve), 2)
                    
                    amount_recieve = get_receive_program(x['customer_id'],amount_recieve)

                    

                    usd_balance = float(x['usd_balance'])
                    new_usd_balance = float(amount_recieve) + float(usd_balance)
                    total_earn = float(x['total_earn'])
                    new_total_earn = float(total_earn) + float(amount_recieve)
                    new_total_earn = float(new_total_earn)
                    
                    new_s_wallet = float(x['s_wallet']) + float(amount_recieve)

                    print(x['username'], percent, balanced, amount_recieve)
                    print "======================================="
                    db.users.update({ "_id" : ObjectId(x['_id']) }, { '$set': { "usd_balance": round(new_usd_balance,2), 'total_earn': round(new_total_earn,0), 's_wallet': round(new_s_wallet,0) } })
                    detail = 'Get '+str(percent)+' '+"""%"""+' System Commissions (small tree %s USD)' %(balanced)
                    SaveHistory(x['customer_id'],x['_id'],x['username'], amount_recieve, 'receive', 'USD', detail, '', '')
                   
        return json.dumps({'status' : 'success'})
    else:
        return json.dumps({'status' : 'error'})




@auto_ctrl.route('/autoremovetree/4cLi4bO4ISCjVauHrkNa5oIc/<ids>', methods=['GET', 'POST'])
def autoremovetree(ids):
    
    # return json.dumps({'status' : 'off'})
    if ids =='RsaW3Kb1gDkdRUGDo':
        users = db.users.find({'$and': [{'roi':0}, 
            {
                "creation": 
                {
                    "$lt": datetime.utcnow() + timedelta(days=1)
                }
            }
        ]})
        for x in users:
            check_debosit = db.txs.find_one({'user_id' : x['customer_id']})

            if check_debosit is None:
                print(x['username'])
                if x['p_binary'] != '':
                    check_binary = users = db.users.find_one({"customer_id" : x['p_binary']})
                    if check_binary['left'] ==  x['customer_id']:
                        db.users.update({ "customer_id" : check_binary['customer_id'] }, { '$set': { "left": ''} })
                    else:
                        db.users.update({ "customer_id" : check_binary['customer_id'] }, { '$set': { "right": ''} })
                db.users.remove({ "customer_id" : x['customer_id'] })
        return json.dumps({'status' : 'success'})

    else:
        return json.dumps({'status' : 'error'})