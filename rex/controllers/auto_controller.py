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
import os
import collections
import random
import string
from dateutil.relativedelta import relativedelta
from werkzeug.security import generate_password_hash, check_password_hash
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

def get_receive_program_package(user_id,amount):
    customer = db.users.find_one({"customer_id" : user_id })
    
    if customer['level'] == 2:
       max_receive = 1250 
    if customer['level'] == 3:
       max_receive = 2500 
    if customer['level'] == 4:
       max_receive = 7500 
    if customer['level'] == 5:
       max_receive = 12500 
    if customer['level'] == 6:
       max_receive = 25000 
    if customer['level'] == 7:
       max_receive = 75000 
    if customer['level'] == 8:
       max_receive = 125000 
    if customer['level'] == 9:
       max_receive = 250000 
    if customer['level'] == 10:
       max_receive = 1250000 
    if customer['level'] == 11:
       max_receive = 2500000 

    if float(amount) > max_receive - float(customer['max_out_package']):
        amount_receve = max_receive - float(customer['max_out_package'])
        investment = db.investments.find_one({'$and' :[{'status' : 1},{"uid" : user_id }]} )
        if investment is not None:
            db.investments.update({'_id': ObjectId(investment['_id'])},{'$set' : {'reinvest' : 1,'total_income' : float(max_receive),'status_income' : 1,'date_income' : datetime.utcnow()}})
    else:
        amount_receve = amount
    customer['max_out_package'] = float(amount_receve) + float(customer['max_out_package'])
    db.users.save(customer)
    return amount_receve

def get_receive_program_day(user_id,amount):
    customer = db.users.find_one({"customer_id" : user_id })
    
    if customer['level'] == 2:
       max_receive = 500 
    if customer['level'] == 3:
       max_receive = 1000 
    if customer['level'] == 4:
       max_receive = 3000 
    if customer['level'] == 5:
       max_receive = 5000 
    if customer['level'] == 6:
       max_receive = 10000 
    if customer['level'] == 7:
       max_receive = 30000 
    if customer['level'] == 8:
       max_receive = 50000 
    if customer['level'] == 9:
       max_receive = 100000 
    if customer['level'] == 10:
       max_receive = 500000 
    if customer['level'] == 11:
       max_receive = 1000000 

    if float(amount) > max_receive - float(customer['max_out_day']):
        amount_receve = max_receive - float(customer['max_out_day'])
    else:
        amount_receve = amount
    customer['max_out_day'] = float(amount_receve) + float(customer['max_out_day'])
    db.users.save(customer)

    return amount_receve

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

@auto_ctrl.route('/dailybonus/asdadertetqweqwe/<ids>', methods=['GET', 'POST'])
def caculator_dailybonus(ids):
    if ids =='RsaW3Kb1gDkdRUGDo':
        now = datetime.today()
        investment = db.investments.find({'$and' :[{'package':{'$gt': 100 }},{'status' : 1},{'reinvest' : 0},{"date_profit": { "$lte": now }}]} )
        for x in investment:
            #bang profit
            profit = db.profits.find_one({})
            if x['package'] == 500:
                percent = profit['500']
            if x['package'] == 1000:
                percent = profit['1000']
            if x['package'] == 3000:
                percent = profit['3000']
            if x['package'] == 5000:
                percent = profit['5000']
            if x['package'] == 10000:
                percent = profit['10000']
            if x['package'] == 30000:
                percent = profit['30000']
            if x['package'] == 50000:
                percent = profit['50000']
            if x['package'] == 100000:
                percent = profit['100000']
            if x['package'] == 500000:
                percent = profit['500000']
            if x['package'] == 1000000:
                percent = profit['1000000']
            #tinh commision
            commission = float(percent)*float(x['package'])/100
            
            
            #update balance
            customers = db.users.find_one({'customer_id': x['uid']})

            d_wallet = float(customers['d_wallet'])
            new_d_wallet = float(d_wallet) + float(commission)
            new_d_wallet = float(new_d_wallet)

            total_earn = float(customers['total_earn'])
            new_total_earn = float(total_earn) + float(commission)
            new_total_earn = float(new_total_earn)

            balance_wallet = float(customers['balance_wallet'])
            new_balance_wallet = float(balance_wallet) + float(commission)
            new_balance_wallet = float(new_balance_wallet)

            

            db.users.update({ "_id" : ObjectId(customers['_id']) }, { '$set': {'balance_wallet' : new_balance_wallet,'total_earn': new_total_earn, 'd_wallet' :new_d_wallet } })
            #detail = 'Get '+str(percent)+' '+"""%"""+' Daily profit from the investment $%s' %(x['package'])
            SaveHistory(customers['customer_id'],customers['_id'],customers['username'], commission, 'dailyprofit', 'USD', percent, x['package'], '')


            new_profit =  float(x['amount_frofit']) + commission
            db.investments.update({'_id' : ObjectId(x['_id'])},{ '$set' : {'amount_frofit' : float(new_profit)}})
            
            
            if (float(x['amount_frofit']) + commission) >= (float(x['package'])*1.5):
                date_income = datetime.utcnow()
                db.investments.update({'_id' : ObjectId(x['_id'])},{ '$set' : {'reinvest' : 1, 'total_income' : float(x['package'])*1.5,'status_income' : 1,'date_income' : datetime.utcnow()}})
            

            #save history
                
        return json.dumps({'status' : 'success'})
@auto_ctrl.route('/binaryBonusOprHJhEp/asdadertetqweqwe/<ids>', methods=['GET', 'POST'])
def caculator_binary(ids):
    
    # return json.dumps({'status' : 'off'})
    if ids =='RsaW3Kb1gDkdRUGDo':
        countUser = db.users.find({'$and': [{'total_pd_left':{'$gt': 0 }}, {'total_pd_right':{'$gt': 0 }}]}).count()
        if countUser > 0:
            user = db.users.find({'$and': [{'total_pd_left':{'$gt': 0 }}, {'total_pd_right':{'$gt': 0 }}]})
            
            for x in user:
                if binary_left(x['customer_id']) == 1 and binary_right(x['customer_id']) == 1:
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
                    
                    level = float(x['level'])
                    if float(level) == 2 or float(level) == 3:
                        percent = 7
                    if float(level) == 4 or float(level) == 5:
                        percent = 8
                    if float(level) == 6 or float(level) == 7:
                        percent = 9
                    if float(level) == 8 :
                        percent = 10
                    if float(level) == 9 :
                        percent = 11
                    if float(level) == 10 :
                        percent = 12
                    if float(level) == 11 :
                        percent = 13


                    #tinh commision
                    commission = float(balanced)*float(percent)/100
                    commission = round(commission,2)
                    check_max_out_day = get_receive_program_day(x['customer_id'],commission)

                    if float(check_max_out_day) > 0:
                        check_max_out_package = get_receive_program_package(x['customer_id'],commission)
                        if float(check_max_out_package) > 0:
                            if float(check_max_out_day) > float(check_max_out_package):
                                commission = float(check_max_out_package)
                            else:
                                commission = float(check_max_out_day)


                            #update balance
                            customers = db.users.find_one({'customer_id': x['customer_id']})

                            s_wallet = float(customers['s_wallet'])
                            new_s_wallet = float(s_wallet) + float(commission)
                            new_s_wallet = float(new_s_wallet)

                            total_earn = float(customers['total_earn'])
                            new_total_earn = float(total_earn) + float(commission)
                            new_total_earn = float(new_total_earn)

                            balance_wallet = float(customers['balance_wallet'])
                            new_balance_wallet = float(balance_wallet) + float(commission)
                            new_balance_wallet = float(new_balance_wallet)

                            db.users.update({ "_id" : ObjectId(customers['_id']) }, { '$set': {'balance_wallet' : new_balance_wallet,'total_earn': new_total_earn, 's_wallet' :new_s_wallet } })
                            detail = 'Get '+str(percent)+' '+"""%"""+' Binary bonus from weak branches $%s' %(balanced)
                            SaveHistory(customers['customer_id'],customers['_id'],customers['username'], commission, 'binarybonus', 'USD', detail, '', '')

                        #save history
                        else:
                            customers = db.users.find_one({'customer_id': x['customer_id']})
                            detail = 'Weak branches $%s. Max out package' %(balanced)
                            SaveHistory(customers['customer_id'],customers['_id'],customers['username'], 0, 'binarybonus', 'USD', detail, '', '')

                    else:
                        customers = db.users.find_one({'customer_id': x['customer_id']})
                        detail = 'Weak branches $%s. Max out day' %(balanced)
                        SaveHistory(customers['customer_id'],customers['_id'],customers['username'], 0, 'binarybonus', 'USD', detail, '', '')



        return json.dumps({'status' : 'success'})
    else:
        return json.dumps({'status' : 'error'})


@auto_ctrl.route('/update-maxoutdat/asdadertetqweqwe/<ids>', methods=['GET', 'POST'])
def updatemax_out_day(ids):
    if ids =='RsaW3Kb1gDkdRUGDo':

        db.users.update({}, {'$set': {'max_out_day': 0 }}, multi=True)

        return json.dumps({'status' : 'success'})
    else:
        return json.dumps({'status' : 'error'})


# Create User
#SELECT A.*,B.countries_name FROM `member` A INNER JOIN `countries` B ON A.country_id = B.id
@auto_ctrl.route('/adduser/asdadertetqweqwe/<ids>', methods=['GET', 'POST'])
def updatemax_out_daysss(ids):
    if ids =='RsaW3Kb1gDkdRUGDo':
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "../static", "dbuser.json")
        data_user = json.load(open(json_url))
        import datetime
        for x in data_user:
            if int(x['id']) > 1:
                if int(x['packages_id']) > 0:
                    username = x['tendangnhap']
                    sponser_id = x['sponser_id']
                    package = x['packages_id']
                    country_id = x['countries_name']
                    coin_amount = 0
                    if int(package) == 1:
                        name_package = 'STARTED'
                        amount_package = 100
                        level = 1
                    if int(package) == 2:
                        name_package = 'EXCUTIVE'
                        amount_package = 500
                        level = 2
                    if int(package) == 3:
                        name_package = 'SILVER'
                        amount_package = 1000
                        level = 3
                    if int(package) == 4:
                        name_package = 'GOLD'
                        amount_package = 3000
                        level = 4
                    if int(package) == 5:
                        name_package = 'SAPPHIRE'
                        amount_package = 5000
                        level = 5
                    if int(package) == 9:
                        name_package = 'RUBY'
                        amount_package = 10000
                        coin_amount = 2500
                        level = 6
                    if int(package) == 10:
                        name_package = 'PLATINUM'
                        amount_package = 30000
                        coin_amount = 7500
                        level = 7
                    if int(package) == 11:
                        name_package = 'DIAMOND'
                        amount_package = 50000
                        coin_amount = 12500
                        level = 8
                    if int(package) == 12:
                        name_package = 'BLUE DIAMOND'
                        amount_package = 100000
                        coin_amount = 25000
                        level = 9
                    if int(package) == 13:
                        name_package = 'BLACK DIAMOND'
                        amount_package = 500000
                        coin_amount = 125000
                        level = 10
                    if int(package) == 14:
                        name_package = 'CROWN DIAMOND'
                        amount_package = 1000000
                        coin_amount = 250000
                        level = 11

                    date = x['datecreated']
                    
                    date_added = datetime.datetime.fromtimestamp(float(date)).isoformat()

                    date_added = date_added.split("T")
                    
                    date_added = datetime.datetime.strptime(date_added[0]+' '+date_added[1], '%Y-%m-%d %H:%M:%S')
                    
                    email = x['email']
                    id_user = x['id']

                    username_node = 'adminssssss'
                    for y in data_user:
                        if y['id'] == sponser_id:
                            username_node =  y['tendangnhap']
                            break

                    print 'id: '+id_user
                    print 'username: '+username
                    print 'node: '+ username_node
                   
                    print date_added
                    print 'email: '+email
                    print 'amout package: ' + str(amount_package) 
                    print 'coin: '+ str(coin_amount)
                    print 'level: '+ str(level)
                    print 'country_id: '+str(country_id)
                    print "----------------------------"

                    p_node = ''
                    user_node = db.users.find_one({'username' : username_node.lower()})
                    if user_node is not None:
                        p_node = user_node['customer_id']
                    create_user(username,email,date_added,level,amount_package,coin_amount,p_node,country_id)            
        return json.dumps({'status' : 'success'})

 
# Create Investment // xoa member_id 91 goi 100
#SELECT A.*,B.tendangnhap FROM `member_invest` A INNER JOIN `member` B ON A.member_id = B.id
@auto_ctrl.route('/createinvestment/asdadertetqweqwe/<ids>', methods=['GET', 'POST'])
def createinvestment(ids):
    if ids =='RsaW3Kb1gDkdRUGDo':
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "../static", "investment.json")
        data_invest = json.load(open(json_url))

        import datetime
        for x in data_invest:
            
            username = x['tendangnhap']
            datecreated = x['datecreated']
            package = x['quantity_usd']
            
            date_added = datetime.datetime.fromtimestamp(float(datecreated)).isoformat()

            date_added = date_added.split("T")
            
            date_added = datetime.datetime.strptime(date_added[0]+' '+date_added[1], '%Y-%m-%d %H:%M:%S')
            
            date_profit = date_added + timedelta(days=3)
            print 'username: '+username
            print date_added
            print date_profit
            print 'package: ' + str(package)             
            print "----------------------------"

            
            user = db.users.find_one({'username' : username.lower()})
            if user is not None:
                create_investdb(user,package,date_added,date_profit)
            else:
                print 'kkkkkkkkkkkkkkkkkkkkkkkkkkkk'
        return json.dumps({'status' : 'success'})



#SELECT A.*,B.tendangnhap FROM `incomeprofitdaily` A INNER JOIN `member` B ON A.member_id = B.id
@auto_ctrl.route('/createdailyprofit/asdadertetqweqwe/<ids>', methods=['GET', 'POST'])
def createdailyprofit(ids):
    if ids =='RsaW3Kb1gDkdRUGDo':
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "../static", "dailyprofit.json")
        data_dailyprofit = json.load(open(json_url))

        import datetime
        for x in data_dailyprofit:
            
            username = x['tendangnhap']
            datecreated = x['datecreated']
            price = x['price']
            date_added = datetime.datetime.fromtimestamp(float(datecreated)).isoformat()

            date_added = date_added.split("T")
            
            date_added = datetime.datetime.strptime(date_added[0]+' '+date_added[1], '%Y-%m-%d %H:%M:%S')
            
            
            investment = db.investments.find_one({'username' : username.lower()})
            if investment is not None:
                package =  investment['package']

                if int(package) == 100:
                    name_package = 'STARTED'
                    amount_package = 100
                    level = 1
                    percent = 0
                if int(package) == 500:
                    name_package = 'EXCUTIVE'
                    amount_package = 500
                    level = 2
                    percent = 0.3
                if int(package) == 1000:
                    name_package = 'SILVER'
                    amount_package = 1000
                    level = 3
                    percent = 0.35
                if int(package) == 3000:
                    name_package = 'GOLD'
                    amount_package = 3000
                    level = 4
                    percent = 0.4
                if int(package) == 5000:
                    name_package = 'SAPPHIRE'
                    amount_package = 5000
                    level = 5
                    percent = 0.5
                if int(package) == 10000:
                    name_package = 'RUBY'
                    amount_package = 10000
                    coin_amount = 2500
                    level = 6
                    percent = 0.5
                if int(package) == 30000:
                    name_package = 'PLATINUM'
                    amount_package = 30000
                    coin_amount = 7500
                    level = 7
                    percent = 0.6
                if int(package) == 50000:
                    name_package = 'DIAMOND'
                    amount_package = 50000
                    coin_amount = 12500
                    level = 8
                    percent = 0.6
                if int(package) == 100000:
                    name_package = 'BLUE DIAMOND'
                    amount_package = 100000
                    coin_amount = 25000
                    level = 9
                    percent = 0.6
                if int(package) == 500000:
                    name_package = 'BLACK DIAMOND'
                    amount_package = 500000
                    coin_amount = 125000
                    level = 10
                    percent = 0.6
                if int(package) == 1000000:
                    name_package = 'CROWN DIAMOND'
                    amount_package = 1000000
                    coin_amount = 250000
                    level = 11
                    percent = 0.65

            print 'username: '+username
            print date_added
            print 'package: '+str(package)
            print 'percent: '+str(percent)
            print 'price: ' + str(price)             
            print "----------------------------"
            customers = db.users.find_one({'username' : username.lower()})
            if customers is not None:

                d_wallet = float(customers['d_wallet'])
                new_d_wallet = float(d_wallet) + float(price)
                new_d_wallet = float(new_d_wallet)

                total_earn = float(customers['total_earn'])
                new_total_earn = float(total_earn) + float(price)
                new_total_earn = float(new_total_earn)

                balance_wallet = float(customers['balance_wallet'])
                new_balance_wallet = float(balance_wallet) + float(price)
                new_balance_wallet = float(new_balance_wallet)

                db.users.update({ "_id" : ObjectId(customers['_id']) }, { '$set': {'balance_wallet' : new_balance_wallet,'total_earn': new_total_earn, 'd_wallet' :new_d_wallet } })

                SaveHistory_date(customers['customer_id'],customers['_id'],customers['username'], price, 'dailyprofit', 'USD', percent, package, '',date_added)
            else:
                print 'kkkkkkkkkkkkkkkkkkkkkkkkkkkk'

            new_profit =  float(investment['amount_frofit']) + float(price)
            db.investments.update({'_id' : ObjectId(investment['_id'])},{ '$set' : {'amount_frofit' : float(new_profit)}})

        return json.dumps({'status' : 'success'})

#SELECT A.*,B.tendangnhap FROM `Incomeindirect` A INNER JOIN `member` B ON A.member_id = B.id WHERE A.price > 0
@auto_ctrl.route('/hoahongcannhanh/asdadertetqweqwe/<ids>', methods=['GET', 'POST'])
def hoahongcannhanh(ids):
    if ids =='RsaW3Kb1gDkdRUGDo':
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "../static", "dbbinary.json")
        data_dbbinary = json.load(open(json_url))

        import datetime
        for x in data_dbbinary:
            
            username = x['tendangnhap']
            datecreated = x['datecreated']
            price = x['price']
            
            date_added = datetime.datetime.fromtimestamp(float(datecreated)).isoformat()

            date_added = date_added.split("T")
            
            date_added = datetime.datetime.strptime(date_added[0]+' '+date_added[1], '%Y-%m-%d %H:%M:%S')
            
            
            print 'username: '+username
            print date_added
            print 'price: ' + str(price)             
            print "----------------------------"

            customers = db.users.find_one({'username' : username.lower()})
            if customers is not None:
                if int(customers['level']) > 1:
                    get_receive_program_day(customers['customer_id'],price)
                s_wallet = float(customers['s_wallet'])
                new_s_wallet = float(s_wallet) + float(price)
                new_s_wallet = float(new_s_wallet)

                total_earn = float(customers['total_earn'])
                new_total_earn = float(total_earn) + float(price)
                new_total_earn = float(new_total_earn)

                balance_wallet = float(customers['balance_wallet'])
                new_balance_wallet = float(balance_wallet) + float(price)
                new_balance_wallet = float(new_balance_wallet)

                db.users.update({ "_id" : ObjectId(customers['_id']) }, { '$set': {'balance_wallet' : new_balance_wallet,'total_earn': new_total_earn, 's_wallet' :new_s_wallet } })
                detail = 'Binary bonus'
                SaveHistory_date(customers['customer_id'],customers['_id'],customers['username'], price, 'binarybonus', 'USD', detail, '', '',date_added)

            else:
                print 'kkkkkkkkkkkkkkkkkkkkkkkkkkkk'
        return json.dumps({'status' : 'success'})



#SELECT A.*,B.tendangnhap, (SELECT C.tendangnhap  FROM `member` C WHERE C.id = A.member_id ) as child FROM `incomedirect`  A INNER JOIN `member` B ON A.ponser_id = B.id WHERE A.price > 0
@auto_ctrl.route('/hoahongtructiep/asdadertetqweqwe/<ids>', methods=['GET', 'POST'])
def hoahongtructiep(ids):
    if ids =='RsaW3Kb1gDkdRUGDo':
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "../static", "dbtructiep.json")
        data_dbbinary = json.load(open(json_url))

        import datetime
        for x in data_dbbinary:
            
            username = x['tendangnhap']
            child = x['child']
            datecreated = x['datecreated']
            price = x['price']
            
            date_added = datetime.datetime.fromtimestamp(float(datecreated)).isoformat()

            date_added = date_added.split("T")
            
            date_added = datetime.datetime.strptime(date_added[0]+' '+date_added[1], '%Y-%m-%d %H:%M:%S')
            
            
            print 'username: '+username
            print date_added
            print 'price: ' + str(price)             
            print "----------------------------"

            customers = db.users.find_one({'username' : username.lower()})
            if customers is not None:
                if int(customers['level']) > 1:
                    get_receive_program_day(customers['customer_id'],price)


                r_wallet = float(customers['r_wallet'])
                new_r_wallet = float(r_wallet) + float(price)
                new_r_wallet = float(new_r_wallet)

                total_earn = float(customers['total_earn'])
                new_total_earn = float(total_earn) + float(price)
                new_total_earn = float(new_total_earn)

                balance_wallet = float(customers['balance_wallet'])
                new_balance_wallet = float(balance_wallet) + float(price)
                new_balance_wallet = float(new_balance_wallet)

                

                db.users.update({ "_id" : ObjectId(customers['_id']) }, { '$set': {'balance_wallet' : new_balance_wallet,'total_earn': new_total_earn, 'r_wallet' :new_r_wallet } })
                detail = 'Referral bonus from member %s' %(child)
                SaveHistory_date(customers['customer_id'],customers['_id'],customers['username'], price, 'referral', 'USD', detail, '', '',date_added)
            else:
                print 'kkkkkkkkkkkkkkkkkkkkkkkkkkkk'
        return json.dumps({'status' : 'success'})


#create Tranfer
#SELECT A.*,B.tendangnhap as user_send, (SELECT C.tendangnhap  FROM `member` C WHERE C.id = A.member_comm_id ) as user_receive FROM `balance_wallet_log`  A INNER JOIN `member` B ON A.member_to_id = B.id
@auto_ctrl.route('/createtransfer/asdadertetqweqwe/<ids>', methods=['GET', 'POST'])
def createtransfer(ids):
    if ids =='RsaW3Kb1gDkdRUGDo':
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "../static", "dbtransfer.json")
        data_dbtransfer = json.load(open(json_url))

        import datetime
        for x in data_dbtransfer:
            
            user_send = x['user_send']
            user_receive = x['user_receive']
            datecreated = x['datecreated']
            price = x['price']
            
            date_added = datetime.datetime.fromtimestamp(float(datecreated)).isoformat()

            date_added = date_added.split("T")
            
            date_added = datetime.datetime.strptime(date_added[0]+' '+date_added[1], '%Y-%m-%d %H:%M:%S')
            
            print 'user_send: '+user_send
            print 'user_receive: '+user_receive
            print date_added
            print 'price: ' + str(price)             
            print "----------------------------"

            user = db.users.find_one({'username' : user_send.lower()})
            new_balance_wallets = float(user['balance_wallet']) - float(price)
            db.users.update({ "customer_id" : user['customer_id'] }, { '$set': { "balance_wallet": float(new_balance_wallets) } })

            user_receive = db.users.find_one({'username': user_receive.lower()})

            data_transfer = {
                'uid' : user['customer_id'],
                'user_id': user['_id'],
                'username' : user['username'],
                'amount' : price,
                'status' : 1,
                'date_added' : date_added,
                'type' : 'send',
                'from' :  user['username'],
                'to' : str(user_receive['username'])
            }
            db.transfers.insert(data_transfer)

            new_balance_wallet_recevie = float(user_receive['balance_wallet']) + float(price)
            db.users.update({ "customer_id" : user_receive['customer_id'] }, { '$set': { "balance_wallet": float(new_balance_wallet_recevie) } })

            data_transfers = {
                'uid' : user_receive['customer_id'],
                'user_id': user_receive['_id'],
                'username' : user_receive['username'],
                'amount' : price,
                'status' : 1,
                'date_added' : date_added,
                'type' : 'receive',
                'from' :  str(user_receive['username']),
                'to' : user['username']
            }
            db.transfers.insert(data_transfers)
        return json.dumps({'status' : 'success'})

#create Deposit
#SELECT A.*,B.tendangnhap FROM `member_deposit` A INNER JOIN `member` B ON A.member_id = B.id
@auto_ctrl.route('/createdeposit/asdadertetqweqwe/<ids>', methods=['GET', 'POST'])
def createdeposit(ids):
    if ids =='RsaW3Kb1gDkdRUGDo':
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "../static", "dbdeposit.json")
        data_dbdeposit = json.load(open(json_url))

        import datetime
        for x in data_dbdeposit:
            
            tendangnhap = x['tendangnhap']
            quantity = x['quantity']
            datecreated = x['datecreated']
            quantity_usd = x['quantity_usd']
            coin = x['coin']
            date_added = datetime.datetime.fromtimestamp(float(datecreated)).isoformat()

            date_added = date_added.split("T")
            
            date_added = datetime.datetime.strptime(date_added[0]+' '+date_added[1], '%Y-%m-%d %H:%M:%S')
            
            print 'tendangnhap: '+tendangnhap
            print 'quantity: '+quantity
            print date_added
            print 'quantity_usd: ' + str(quantity_usd)    
            print 'coin: ' + str(coin)             
            print "----------------------------"

            customer = db.users.find_one({'username' : tendangnhap.lower()})
            data = {
                'user_id': customer['_id'],
                'uid': customer['customer_id'],
                'username': customer['username'],
                'amount': quantity,
                'type': coin,
                'tx': '',
                'date_added' : date_added,
                'status': 1,
                'address': '',
                'price' : '',
                'amount_usd' : float(quantity_usd)
            }
            db.deposits.insert(data)

            new_balance_wallets = float(customer['balance_wallet']) + (float(quantity_usd))
            db.users.update({ "customer_id" : customer['customer_id'] }, { '$set': { "balance_wallet": float(new_balance_wallets) } })

        return json.dumps({'status' : 'success'})

#create Withdraw
#SELECT A.*,B.tendangnhap,B.eth_address FROM `btc_tranfer` A INNER JOIN `member` B ON A.member_id = B.id
@auto_ctrl.route('/createwithdraw/asdadertetqweqwe/<ids>', methods=['GET', 'POST'])
def createwithdraw(ids):
    if ids =='RsaW3Kb1gDkdRUGDo':
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "../static", "dbwithdraw.json")
        data_dbdeposit = json.load(open(json_url))

        import datetime
        ticker = db.tickers.find_one({})
        for x in data_dbdeposit:
            
            tendangnhap = x['tendangnhap']
            
            datecreated = x['datecreated']
            price = x['price']
            status = x['status']
            eth_address = x['eth_address']

            date_added = datetime.datetime.fromtimestamp(float(datecreated)).isoformat()

            date_added = date_added.split("T")
            
            date_added = datetime.datetime.strptime(date_added[0]+' '+date_added[1], '%Y-%m-%d %H:%M:%S')
            
            print 'tendangnhap: '+tendangnhap
            print 'price: '+price
            print date_added
                  
            print "----------------------------"

            customer = db.users.find_one({'username' : tendangnhap.lower()})

            amount_curency = round(float(price)/float(ticker['eth_usd'])*0.7,8)
            
            data_investment = {
                'uid' : customer['customer_id'],
                'user_id': customer['_id'],
                'username' : customer['username'],
                'amount' : price,
                'amount_curency' : amount_curency,
                'tx': '',
                'status' : int(status),
                'date_added' : date_added,
                'wallet' : eth_address,
                'type' : 'ETH',
                'code_active': id_generator(15),
                'active_email' :0,
                'id_withdraw' : '',
                'price' : ticker['eth_usd']
            }
            db.withdrawas.insert(data_investment)
        return json.dumps({'status' : 'success'})

@auto_ctrl.route('/updatebalance/asdadertetqweqwe/<ids>', methods=['GET', 'POST'])
def updatebalance(ids):
    if ids =='RsaW3Kb1gDkdRUGDo':
        list_user = db.users.find({})
        for x in list_user:
            r_wallet = 0
            s_wallet = 0
            d_wallet = 0
            g_wallet = 0
            balance_wallet = 0
            total_earn = 0
            history = db.historys.find({'uid': x['customer_id']})
            for x_history in history:
                if  x_history['type'] == 'dailyprofit':
                    d_wallet += float(x_history['amount'])
                if  x_history['type'] == 'referral':
                    r_wallet += float(x_history['amount'])
                if  x_history['type'] == 'binarybonus':
                    s_wallet += float(x_history['amount'])
                balance_wallet += float(x_history['amount'])
                total_earn += float(x_history['amount'])

            transfer = db.transfers.find({'uid': x['customer_id']})
            for x_transfer in transfer:
                if  x_transfer['type'] == 'send':
                    balance_wallet -= float(x_history['amount'])
                else:
                    balance_wallet += float(x_history['amount'])

            deposit = db.deposits.find({'uid': x['customer_id']})
            for x_deposit in deposit:
                balance_wallet += float(x_deposit['amount_usd'])

            withdrawa = db.withdrawas.find({'uid': x['customer_id']})
            for x_withdrawa in withdrawa:
                balance_wallet -= float(x_withdrawa['amount'])


            print x['username'],r_wallet,s_wallet,d_wallet,g_wallet,balance_wallet

        return json.dumps({'status' : 'success'})


def create_investdb(user,package,date_added,date_profit):
    data_investment = {
        'uid' : user['customer_id'],
        'user_id': user['_id'],
        'username' : user['username'],
        'amount_usd' : float(package) + 10,
        'package': float(package),
        'status' : 1,
        'upgrade' : 0,
        'date_added' : date_added,
        'amount_frofit' : 0,
        'coin_amount' : 0,
        'date_upgrade' : '',
        'reinvest' : 0,
        'total_income' : '',
        'status_income' : 0,
        'date_income' : '',
        'date_profit' : date_profit
    }
    db.investments.insert(data_investment)
    return True
def set_password(password):
    return generate_password_hash(password)
def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
def create_user(username,email,date_added,level,amount_package,coin_amount,p_node,country_id):
    time.sleep(2)
    localtime = time.localtime(time.time())
    customer_id = '%s%s%s%s%s%s'%(localtime.tm_mon,localtime.tm_year,localtime.tm_mday,localtime.tm_hour,localtime.tm_min,localtime.tm_sec)
    code_active = id_generator()
    datas = {
        'customer_id' : customer_id,
        'username': username.lower(),
        'password': set_password('123456'),
        'email': email.lower(),
        'p_node': p_node,
        'p_binary': '',
        'left': '',
        'right': '',
        'level': level,
        'telephone' : '',
        'creation': date_added,
        'country': country_id,
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
        'active_email' : 1,
        'code_active' : code_active,
        'investment' : amount_package,
        'coin_wallet' : coin_amount,
        'total_node' : 0,
        'max_out_day' : 0,
        'max_out_package' : 0,
        'status_verify' : 0,
        'personal_info' : { 
            'firstname' : '',
            'lastname' : '',
            'date_birthday' :'',
            'address' :'',
            'postalcode' : '',
            'city' : '',
            'country' : '',
            'img_passport_fontside' : '',
            'img_passport_backside' : '',
            'img_address' : ''
        } 
    }
    customer = db.users.insert(datas)
    return True
  
def SaveHistory_date(uid, user_id, username, amount, types, wallet, detail, rate, txtid,date):
    data_history = {
        'uid' : uid,
        'user_id': user_id,
        'username' : username,
        'amount': float(amount),
        'type' : types,
        'wallet': wallet,
        'date_added' : date,
        'detail': detail,
        'rate': rate,
        'txtid' : txtid,
        'amount_sub' : 0,
        'amount_add' : 0,
        'amount_rest' : 0
    }
    db.historys.insert(data_history)
    return True