from flask import Blueprint, request, session, redirect, url_for, render_template
from flask.ext.login import login_user, logout_user, current_user, login_required
from rex import app, db
from rex.models import user_model, deposit_model, history_model, invoice_model

__author__ = 'carlozamagni'

refferal_ctrl = Blueprint('refferal', __name__, static_folder='static', template_folder='templates')


@refferal_ctrl.route('/refferal', methods=['GET', 'POST'])
def refferal():
	if session.get(u'logged_in') is None:
		return redirect('/user/login')
	uid = session.get('uid')
	query = db.User.find({'p_node': uid})
	user = db.User.find_one({'customer_id': uid})
	username = user['username']
	refferal_link = 'https://worldtrader.info/user/register/%s' % (user['customer_id'])
	data_ticker = db.tickers.find_one({})
	data ={
	'refferal' : query,
	'title': 'Refferal',
	'menu' : 'refferal',
	'user': user,
	'refferal_link' : refferal_link,
	'uid': uid,
	'btc_usd':data_ticker['btc_usd'],
    'sva_btc':data_ticker['sva_btc'],
    'sva_usd':data_ticker['sva_usd']
	}
	return render_template('account/refferal.html', data=data)

# @refferal_ctrl.route('/invite-friends', methods=['GET', 'POST'])
# def inviterefferal():
# 	if session.get(u'logged_in') is None:
# 		return redirect('/user/login')
# 	uid = session.get('uid')
# 	query = db.User.find({'p_node': uid})
# 	user = db.User.find_one({'customer_id': uid})
# 	username = user['username']
# 	refferal_link = 'https://smartfva.co/user/register/%s' % (username)
# 	data_ticker = db.tickers.find_one({})
# 	data ={
# 	'refferal' : query,
# 	'title': 'Refferal',
# 	'menu' : 'refferal',
# 	'user': user,
# 	'refferal_link' : refferal_link,
# 	'uid': uid,
# 	'btc_usd':data_ticker['btc_usd'],
#     'sva_btc':data_ticker['sva_btc'],
#     'sva_usd':data_ticker['sva_usd']
# 	}
# 	return render_template('account/invitefriends.html', data=data)
