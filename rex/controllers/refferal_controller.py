from flask import Blueprint, request, session, redirect, url_for, render_template
from flask.ext.login import login_user, logout_user, current_user, login_required
from rex import app, db
from rex.models import user_model, deposit_model, history_model, invoice_model

__author__ = 'carlozamagni'

refferal_ctrl = Blueprint('refferal', __name__, static_folder='static', template_folder='templates')


@refferal_ctrl.route('/referrals', methods=['GET', 'POST'])
def refferal():
	if session.get(u'logged_in') is None:
		return redirect('/user/login')
	uid = session.get('uid')
	query = db.users.find({'p_node': uid})
	user = db.users.find_one({'customer_id': uid})
	username = user['username']
	
	list_notifications = db.notifications.find({'$or' : [{'uid' : uid},{'type' : 'all'}]})
	number_notifications = list_notifications.count()
	data ={
		'refferal' : query,
		'title': 'my-network',
		'menu' : 'my-network',
		'user': user,
		'uid': uid,
		'number_notifications' : number_notifications,
	    'list_notifications' : list_notifications
	}
	return render_template('account/refferal.html', data=data)
