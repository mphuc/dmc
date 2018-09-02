from flask import Blueprint, request, session, redirect, url_for, render_template, flash
from flask.ext.login import login_user, logout_user, current_user, login_required
from rex import app, db
from rex.models import user_model, deposit_model, history_model, invoice_model
from bson.objectid import ObjectId
import json
import datetime
from datetime import datetime
from datetime import datetime, date, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from bson import json_util
import string
import random
import hashlib
import time
def check_password(pw_hash, password):
    return check_password_hash(pw_hash, password)
__author__ = 'carlozamagni'

dashboard_ctrl = Blueprint('dashboard', __name__, static_folder='static', template_folder='templates')
def finduser_by_id(ids):
	user = db.User.find_one({'_id': ObjectId(ids)})
	return user

digits58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

def id_generator_code():
	time.sleep(1)
	localtime = time.localtime(time.time())
	code = '%s%s%s%s%s%s'%(localtime.tm_mon,localtime.tm_year,localtime.tm_mday,localtime.tm_hour,localtime.tm_min,localtime.tm_sec)
	return hashlib.md5(code).hexdigest()

def is_number(s):
    try:
        complex(s) # for int, long, float and complex
    except ValueError:
        return False
    return True

@dashboard_ctrl.route('/dashboard', methods=['GET', 'POST'])
def dashboard():

	if session.get(u'logged_in') is None:
		return redirect('/user/login')
	else:
		uid = session.get('uid')
		user = db.User.find_one({'customer_id': uid})
		username = user['username']
		refferal_link = 'http://0.0.0.0:58056/auth/register/%s' % (user['customer_id'])
		received = float(user.m_wallet/1000000)
		
		profit_daily_pending = db.profits.find_one({'status': 0})
		# profit_daily = db.profits.find({'status': 1}).limit(5)
		profit_daily = db.profits.find({'status':1}).sort([("date_added", -1)]).limit(5)

		total_refferal = db.users.find({'p_node': uid, 'type': 1}).count()
		print uid
		refferal = db.users.find({'p_node': uid, 'type': 1})

		

		max_out = float(user.max_out)
		total_max_out = int(user.total_max_out)
		if max_out > 0:
			percent_max = total_max_out/max_out
		else:
			percent_max = 0
		data_ticker = db.tickers.find_one({})
		data ={
			'refferal_link' : refferal_link,
		    'user': user,
		    'menu' : 'dashboard',
		    'float' : float,
		    
		    'total_refferal': total_refferal,
		    'refferal': refferal,
		    'profit_daily': profit_daily,
		    'profit_daily_pending': profit_daily_pending,
		    'btc_usd':data_ticker['btc_usd'],
	        'sva_btc':data_ticker['sva_btc'],
	        'sva_usd':data_ticker['sva_usd'],
	        'xvg_usd':data_ticker['xvg_usd'],
	        'xvg_btc':round(0.8/float(data_ticker['btc_usd']),8)
		}
		
		return render_template('account/dashboard.html', data=data)

@dashboard_ctrl.route('/code', methods=['GET', 'POST'])
def code():

	if session.get(u'logged_in') is None:
		return redirect('/user/login')
	else:
		uid = session.get('uid')
		user = db.User.find_one({'customer_id': uid})
		
		data_ticker = db.tickers.find_one({})
		user_id = session.get('user_id')
		uid = session.get('uid')
		datacode = db.codes.find({'customer_id': user_id})

		data ={
		    'user': user,
		    'float' : float,
		    'menu' : 'code',
		    'datacode' : datacode,
		    'btc_usd':data_ticker['btc_usd']
		}
		
		return render_template('account/code.html', data=data)

@dashboard_ctrl.route('/getNewRefferal', methods=['GET', 'POST'])
def getNewRefferal():
	if session.get(u'logged_in') is None:
		return redirect('/user/login')
	else:
		user_id = session.get('user_id')
		uid = session.get('uid')
		total_refferal = db.users.find({'p_node': uid}).count()
		print total_refferal
		datarefferal = db.users.find({'p_node': uid})
		if total_refferal > 0:
			html = ""
			for x in datarefferal:
				html = html + """<tr>
	                <td>"""+x['username']+"""</td>
	                <td>"""+x['username']+"""</td>
	                <td>
	                   <input type="radio" name="choose" value='"""+x['customer_id']+"""'>
	                </td>
	             </tr>"""
			return json.dumps({
				'status': 'success', 
				'refferal': html
			})
		else:
			return json.dumps({
				'status': 'error', 
				'message': 'No data'
			})

@dashboard_ctrl.route('/confrimAddTree', methods=['GET', 'POST'])
def confrimAddTree():
	if session.get(u'logged_in') is None:
		return json.dumps({
			'status': 'error', 
			'message': 'Please login'
		})
	else:
		if request.method=='POST':
			positon = request.form['positon']
			p_binary = request.form['p_binary']
			if float(positon) == 1:
				p = 'left'
			else:
				p = 'right'
			customer_id = request.form['uid']
			customer = db.User.find_one({'customer_id': p_binary})

			refferal = db.User.find_one({'customer_id': customer_id})

			if customer is None or refferal is None:
				return json.dumps({
					'status': 'error', 
					'message': 'Position dose not exits'
				})
			else:
				if customer[p] == '' and refferal['p_binary'] == '':
					db.users.update({ "customer_id" : p_binary }, { '$set': { p: customer_id} })
					db.users.update({ "customer_id" : customer_id }, { '$set': { 'p_binary': p_binary, 'type': 0} })
					return json.dumps({
						'status': 'success', 
						'message': 'Success!'
					})
				else:
					return json.dumps({
						'status': 'error', 
						'message': 'Position exits'
					})
		else:
			return json.dumps({
				'status': 'error', 
				'message': 'Please login'
			})


		

def children_tree (json):
    customer = db.User.find_one({'customer_id': json['id']})
    user_p_left = db.User.find_one({"$and" :[{'p_binary': json['id']}, {'customer_id': customer.left}] })
    if user_p_left is not None:
        tree = {
            "id":user_p_left.customer_id
        }
        json.append(tree)
        children_tree(tree)
    user_p_right = db.User.find_one({"$and" :[{'p_binary': json['id']}, {'customer_id': customer.right}] })
    if user_p_right is not None:
        tree = {
            "id":user_p_right.customer_id
        }
        json.append(tree)
        children_tree(tree)
    return json 

def reduceTree (user):
	json = []
	tree = {
		"id":user.customer_id
	}
	json.append(tree)
	children_tree(tree)

def renderJson(uid) :
    user = db.User.find_one({'customer_id': uid})
    return reduceTree(user)


def LoopPNode(customer_id_list):
    List = db.User.find({"p_binary":{"$in":customer_id_list}})
    customer_id = []
    for x in List:
        customer_id.append(str(x['_id']))
    print customer_id
    if len(customer_id) > 0:
    	return LoopPNode(customer_id)

@dashboard_ctrl.route('/add-tree/<username>', methods=['GET', 'POST'])
def getdataTree(username):
	if session.get(u'logged_in') is None:
		return redirect('/user/login')
	else:
		user_id = session.get('user_id')
		uid = session.get('uid')
		user = db.users.find_one({'username': username})
		if user is None:
			return redirect('/user/login')
		customer_id = []
		customer_id.append(str(uid))
		page_sanitized = json_util.dumps(LoopPNode(customer_id))
		print page_sanitized
		return json.dumps({
			'status': 'error', 
			'message': 'Please enter amount exchange!' 
		})

@dashboard_ctrl.route('/transferusd', methods=['GET', 'POST'])
def transferUSD():
	if session.get(u'logged_in') is None:
		return json.dumps({
			'status': 'error', 
			'message': 'Please Login' 
		})
	else:
		if request.method == 'POST':
			if request.form['amount'] == '':
				return json.dumps({
					'status': 'error', 
					'message': 'Please enter amount transfer!' 
				})
			amount = request.form['amount']
			
			if  is_number(amount):
				if float(amount) < 15:
					return json.dumps({
						'status': 'error', 
						'message': 'Please enter amount is number and value greater than 15 USD' 
					})
			else:
				return json.dumps({
					'status': 'error', 
					'message': 'Please enter amount is number and value greater than 15 USD' 
				})

			if request.form['username'] == '':
				return json.dumps({
					'status': 'error', 
					'message': 'Please enter Email or Username' 
				})


			user_receve = db.User.find_one({"$or" :[{'username': request.form['username']}, {'email': request.form['username']}] })
			if user_receve is None:
				return json.dumps({
					'status': 'error', 
					'message': 'Wrong Username or Email' 
				})

			amount = float(amount)
			
			user_id = session.get('user_id')
			uid = session.get('uid')
			user = db.users.find_one({'_id': ObjectId(user_id)})

			password = request.form['password']
			if check_password(user['password'], password) == False:
				return json.dumps({
					'status': 'error', 
					'message': 'Wrong password' 
				})


			usd_balance = user['usd_balance']
			if float(usd_balance) < float(amount):
				return json.dumps({
					'status': 'error', 
					'message': 'Your balance is not enough!' 
				})
			new_usd_balance = float(usd_balance) - float(amount)
			new_usd_balance = round(new_usd_balance, 2)
			
			db.users.update({ "_id" : ObjectId(user_id) }, { '$set': { "usd_balance": new_usd_balance } })
			data_history = {
				'uid' : uid,
				'user_id': user_id,
				'username' : user['username'],
				'amount': float(amount),
				'type' : 'send',
				'wallet': 'USD',
				'date_added' : datetime.utcnow(),
				'detail': 'Transfer to %s %s USD' %(user_receve['username'],amount),
				'rate': '' ,
				'txtid' : '' ,
				'amount_sub' : 0,
				'amount_add' : 0,
				'amount_rest' : 0
			}
			db.historys.insert(data_history)

			# Receive
			
			usd_balance_receve = user_receve['usd_balance']
			new_usd_balance_receve = float(usd_balance_receve) + float(amount)
			new_usd_balance_receve = round(new_usd_balance_receve, 2)
			db.users.update({ "_id" : ObjectId(user_receve['_id']) }, { '$set': { "usd_balance": new_usd_balance_receve } })
			data_history = {
				'uid' : user_receve['_id'],
				'user_id': user_receve['customer_id'],
				'username' : user_receve['username'],
				'amount': float(amount),
				'type' : 'receive',
				'wallet': 'SVA',
				'date_added' : datetime.utcnow(),
				'detail': 'Receive from %s %s' %(user['username'], amount),
				'rate': '',
				'txtid' : '' ,
				'amount_sub' : 0,
				'amount_add' : 0,
				'amount_rest' : 0
			}
			db.historys.insert(data_history)
			return json.dumps({
				'status': 'success',
				'data_form': amount,
				'new_usd_balance': new_usd_balance,
				'message': 'Transfer to USD Wallet success!'
			})
		else:
			return json.dumps({
				'status': 'error', 
				'message': '403 Forbidden' 
			})


@dashboard_ctrl.route('/buycode', methods=['GET', 'POST'])
def buycode():
	if session.get(u'logged_in') is None:
		return json.dumps({
			'status': 'error', 
			'message': 'Please Login' 
		})
	else:
		if request.method == 'POST':
			if request.form['numbercode'] == '':
				return json.dumps({
					'status': 'error', 
					'message': 'Please enter number code transfer!' 
				})
			numbercode = request.form['numbercode']
			
			if  is_number(numbercode) is False:
				
				return json.dumps({
					'status': 'error', 
					'message': 'Please enter number code transfer!' 
				})
			
			
			user_id = session.get('user_id')
			uid = session.get('uid')
			user = db.users.find_one({'_id': ObjectId(user_id)})

			data_ticker = db.tickers.find_one({})

			btc_balance = user['btc_balance']

			amount_payment = round((float(numbercode)*20)/float(data_ticker['btc_usd']),8)

			if float(btc_balance) < float(amount_payment):
				return json.dumps({
					'status': 'error', 
					'message': 'Your balance BTC is not enough!' 
				})
			new_btc_balance = float(btc_balance) - float(amount_payment)
			new_btc_balance = round(new_btc_balance, 8)
			
			db.users.update({ "_id" : ObjectId(user_id) }, { '$set': { "btc_balance": new_btc_balance } })
			data_history = {
				'uid' : uid,
				'user_id': user_id,
				'username' : user['username'],
				'amount': float(amount_payment),
				'type' : 'send',
				'wallet': 'BTC',
				'date_added' : datetime.utcnow(),
				'detail': 'Buy %s code. 1 BTC = %s USD'%(numbercode,data_ticker['btc_usd']),
				'rate': '1 Code = 20 USD' ,
				'txtid' : '' ,
				'amount_sub' : 0,
				'amount_add' : 0,
				'amount_rest' : 0
			}
			db.historys.insert(data_history)

			for x in range(0, int(numbercode)):
				datas = {
	                'status': 0,
			        'code':  id_generator_code(),
			        'date_added' : datetime.utcnow(),
			        'customer_id' : user_id,
			        'username' : user['username'],
			        'uid' : uid
	            }
				
				db.codes.insert(datas)



			return json.dumps({
				'status': 'success',
				'data_form': amount_payment,
				'new_btc_balance': new_btc_balance,
				'message': 'Transfer to USD Wallet success!'
			})
		else:
			return json.dumps({
				'status': 'error', 
				'message': '403 Forbidden' 
			})


@dashboard_ctrl.route('/activecode', methods=['GET', 'POST'])
def activecode():
	if session.get(u'logged_in') is None:
		return json.dumps({
			'status': 'error', 
			'message': 'Please Login' 
		})
	else:
		if request.method == 'POST':
			if request.form['code'] == '':
				return json.dumps({
					'status': 'error', 
					'message': 'Please enter code!' 
				})
			code = (request.form['code'])
			
			code_all = db.codes.find_one({'$and' : [{'status' : 0},{'code': code}]})
			if code_all is None:
				return json.dumps({
					'status': 'error', 
					'message': 'Wrong code!' 
				})	
			else:
				db.codes.update({'code': code}, { '$set': { "status": 1 }})
				db.users.update({'customer_id': request.form['customer_id']}, { '$set': { "roi": 1 }})
				return json.dumps({
					'status': 'success',
					'message': 'Active code success!'
				})


@dashboard_ctrl.route('/dashboard/active-account', methods=['GET', 'POST'])
def activeaccount():
	if session.get(u'logged_in') is None:

		flash({'msg':'Please Login', 'type':'danger'})
		return redirect('/auth/login')
	else : 
		user_id = session.get('user_id')
		uid = session.get('uid')
		user = db.users.find_one({'_id': ObjectId(user_id)})

		data_ticker = db.tickers.find_one({})

		btc_balance = user['btc_balance']

		amount_payment = round(20/float(data_ticker['btc_usd']),8)
		
		if float(btc_balance) < float(amount_payment):
			flash({'msg':'You need %s BTC to activate your account!'%(amount_payment), 'type':'danger'})
			return redirect('/auth/login')
		else:
			new_btc_balance = float(btc_balance) - float(amount_payment)
			new_btc_balance = round(new_btc_balance, 8)
			
			db.users.update({ "_id" : ObjectId(user_id) }, { '$set': { "btc_balance": new_btc_balance,"roi" :1 } })
			data_history = {
				'uid' : uid,
				'user_id': user_id,
				'username' : user['username'],
				'amount': float(amount_payment),
				'type' : 'send',
				'wallet': 'BTC',
				'date_added' : datetime.utcnow(),
				'detail': 'Active Account. 1 BTC = %s USD'%(data_ticker['btc_usd']),
				'rate': '1 Code = 20 USD' ,
				'txtid' : '' ,
				'amount_sub' : 0,
				'amount_add' : 0,
				'amount_rest' : 0
			}
			db.historys.insert(data_history)
			flash({'msg':'Active Account Success!', 'type':'success'})
			return redirect('/account/dashboard')


@dashboard_ctrl.route('/submitbuyxvg', methods=['GET', 'POST'])
def submitbuyxvgs():
	if session.get(u'logged_in') is None:
		return json.dumps({
			'status': 'error', 
			'message': 'Please Login' 
		})
	else:
		if request.method == 'POST':
			if request.form['amount'] == '':
				return json.dumps({
					'status': 'error', 
					'message': 'Please enter amount WTX!' 
				})
			amount = float(request.form['amount'])
			
			if float(amount) < 15:
				return json.dumps({
					'status': 'error', 
					'message': 'Please enter amount is number and value greater than 100 WTX' 
				})
			
			user_id = session.get('user_id')
			uid = session.get('uid')
			user = db.users.find_one({'_id': ObjectId(user_id)})

			btc_balance = user['btc_balance']
			xvg_balance = user['sva_balance']

			data_ticker = db.tickers.find_one({})
			xvg_btc = round(0.8/float(data_ticker['btc_usd']),8)
			
			if float(btc_balance) < (round(float(amount)*float(xvg_btc),8)):
				return json.dumps({
					'status': 'error', 
					'message': 'Your balance is not enough!' 
				})
			new_btc_balance = round(float(btc_balance) - (round(float(amount)*float(xvg_btc), 8)),8)
			new_xvg_balance = round(float(xvg_balance) + float(amount),8)
			db.users.update({ "_id" : ObjectId(user_id) }, { '$set': { "btc_balance": new_btc_balance, "sva_balance": new_xvg_balance } })
			data_history = {
				'uid' : uid,
				'user_id': user_id,
				'username' : user['username'],
				'amount': float(amount),
				'type' : 'Buy WTX',
				'wallet': 'WTX',
				'date_added' : datetime.utcnow(),
				'detail': 'Buy %s WTX'%(amount),
				'rate': '1 WTX = %s BTC' %('{:.8f}'.format(xvg_btc)),
				'txtid' : '' ,
				'amount_sub' : 0,
				'amount_add' : 0,
				'amount_rest' : 0
			}
			db.historys.insert(data_history)
			

			# user_node = db.User.find_one({'customer_id': user['p_node']})

			# if user_node is not None:

			# 	new_xvg_balance_node = float(user_node['sva_balance']) + (float(amount)*0.03)

			# 	db.users.update({ "customer_id" : user_node['customer_id']}, { '$set': { "sva_balance": new_xvg_balance_node} })

			# 	data_history = {
			# 		'uid' : user_node['customer_id'],
			# 		'user_id': user_node['_id'],
			# 		'username' : user_node['username'],
			# 		'amount': float(amount)*0.03,
			# 		'type' : 'receive',
			# 		'wallet': 'XVG',
			# 		'date_added' : datetime.utcnow(),
			# 		'detail': 'Get %s XVG when %s buys %s XVG' %(float(amount)*0.03,user['username'],amount),
			# 		'rate': '',
			# 		'txtid' : '' ,
			# 		'amount_sub' : 0,
			# 		'amount_add' : 0,
			# 		'amount_rest' : 0
			# 	}
			# 	db.historys.insert(data_history)

			return json.dumps({
				'status': 'success',
				'data_form': amount,
				'new_btc_balance': new_btc_balance,
				'new_xvg_balance': new_xvg_balance,
				'message': 'Buy XVG success!'
			})
		else:
			return json.dumps({
				'status': 'error', 
				'message': '403 Forbidden' 
			})

@dashboard_ctrl.route('/submitsellxvg', methods=['GET', 'POST'])
def submitsellxvgssss():
	if session.get(u'logged_in') is None:
		return json.dumps({
			'status': 'error', 
			'message': 'Please Login' 
		})
	else:
		if request.method == 'POST':
			if request.form['amount'] == '':
				return json.dumps({
					'status': 'error', 
					'message': 'Please enter amount XVG!' 
				})
			amount = float(request.form['amount'])
			
			if float(amount) < 100:
				return json.dumps({
					'status': 'error', 
					'message': 'Please enter amount is number and value greater than 100 XVG' 
				})
			
			user_id = session.get('user_id')
			uid = session.get('uid')
			user = db.users.find_one({'_id': ObjectId(user_id)})

			btc_balance = user['btc_balance']
			xvg_balance = user['sva_balance']

			data_ticker = db.tickers.find_one({})
			xvg_btc = data_ticker['xvg_btc']
			
			if float(xvg_balance) < float(amount):
				return json.dumps({
					'status': 'error', 
					'message': 'Your balance is not enough!' 
				})
			new_btc_balance = round(float(btc_balance) + ((round(float(amount)*float(xvg_btc), 8)) * 0.97),8)
			new_xvg_balance = round(float(xvg_balance) - float(amount),8)
			db.users.update({ "_id" : ObjectId(user_id) }, { '$set': { "btc_balance": new_btc_balance, "sva_balance": new_xvg_balance } })
			data_history = {
				'uid' : uid,
				'user_id': user_id,
				'username' : user['username'],
				'amount': float(amount),
				'type' : 'Sell XVG',
				'wallet': 'XVG',
				'date_added' : datetime.utcnow(),
				'detail': 'Sell %s XVG.'%(amount),
				'rate': '1 XVG = %s BTC' %(xvg_btc),
				'txtid' : '' ,
				'amount_sub' : 0,
				'amount_add' : 0,
				'amount_rest' : 0
			}
			db.historys.insert(data_history)
			
			return json.dumps({
				'status': 'success',
				'data_form': amount,
				'new_btc_balance': new_btc_balance,
				'new_xvg_balance': new_xvg_balance,
				'message': 'Sell XVG success!'
			})
		else:
			return json.dumps({
				'status': 'error', 
				'message': '403 Forbidden' 
			})

@dashboard_ctrl.route('/submitconvertusdbtc', methods=['GET', 'POST'])
def submitconvertusdbtc():
	if session.get(u'logged_in') is None:
		return json.dumps({
			'status': 'error', 
			'message': 'Please Login' 
		})
	else:
		if request.method == 'POST':
			if request.form['amount'] == '':
				return json.dumps({
					'status': 'error', 
					'message': 'Please enter amount USD!' 
				})
			amount = float(request.form['amount'])
			
			if float(amount) < 50:
				return json.dumps({
					'status': 'error', 
					'message': 'Please enter amount is number and value greater than 50 USD' 
				})
			
			user_id = session.get('user_id')
			uid = session.get('uid')
			user = db.users.find_one({'_id': ObjectId(user_id)})

			btc_balance = user['btc_balance']
			usd_balance = user['usd_balance']

			data_ticker = db.tickers.find_one({})
			usd_btc = data_ticker['btc_usd']
			
			if float(usd_balance) < float(amount):
				return json.dumps({
					'status': 'error', 
					'message': 'Your balance is not enough!' 
				})
			new_btc_balance = round(float(btc_balance) + (round(float(amount)/float(usd_btc), 8)),8)
			new_usd_balance = round(float(usd_balance) - float(amount),8)
			db.users.update({ "_id" : ObjectId(user_id) }, { '$set': { "btc_balance": new_btc_balance, "usd_balance": new_usd_balance } })
			data_history = {
				'uid' : uid,
				'user_id': user_id,
				'username' : user['username'],
				'amount': float(amount),
				'type' : 'Convert USD to BTC',
				'wallet': 'BTC',
				'date_added' : datetime.utcnow(),
				'detail': 'Convert %s USD'%(amount),
				'rate': '1 BTC = %s USD' %(usd_btc),
				'txtid' : '' ,
				'amount_sub' : 0,
				'amount_add' : 0,
				'amount_rest' : 0
			}
			db.historys.insert(data_history)
			
			return json.dumps({
				'status': 'success',
				'data_form': amount,
				'new_btc_balance': new_btc_balance,
				'new_usd_balance': new_usd_balance,
				'message': 'Success!'
			})
		else:
			return json.dumps({
				'status': 'error', 
				'message': '403 Forbidden' 
			})
@dashboard_ctrl.route('/silder', methods=['GET', 'POST'])
def silder():
	data = {}
	return render_template('account/silder.html', data=data)