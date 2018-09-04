import datetime
from mongokit import Document
from rex import app, db
import validators
from bson.objectid import ObjectId
__author__ = 'taijoe'


class User(Document):
    __collection__ = 'users'

    structure = {
        'customer_id' : unicode,
        'email': unicode,
        'code_active': unicode,
        'username': unicode,
        'password': unicode,
        'creation': datetime.datetime,
        'p_binary' : unicode,
        'left' : unicode,
        'right' : unicode,
        'telephone' : float,
        'p_node' : unicode,
        'password_transaction' : unicode,
        'btc_address' : unicode,
        'eth_address' : unicode,
        'ltc_address' : unicode,
        'bch_address' : unicode,
        'usdt_address' : unicode,
        'level' : int,
        'password_custom' : unicode,
        'total_pd_left' : float,
        'total_pd_right' : float,
        'total_amount_left' : float,
        'total_amount_right': float,
        'm_wallet' : float,
        'r_wallet' : float,
        's_wallet' : float,
        'd_wallet' : float,
        'g_wallet' : float,
        'coin_wallet' : float,
        'balance_wallet' : float,
        'status_authen' : int,
        'authentication' : unicode,
        'max_out' : float,
        'total_max_out' : float,
        'total_earn' : float,
        'position' : unicode,
        'country' : unicode,
        'total_invest' : float,
        'status':int,
        'type': int,
        'active_email': int,
        'secret_2fa': unicode,
        'status_2fa': int,
        'status_withdraw' : int,
        'max_daily': float,
        'investment': float,
        'total_node' : float,
        'max_out_day' : float,
        'max_out_package' : float,
        'status_verify': int,
        'personal_info': {
            'document' : unicode,
            'passport' : unicode,
            'date_passport' :unicode,
            'country' :unicode,
            'gender' : unicode,
            'address' : unicode,
            'city' : unicode,
            'zipcode' : unicode,
            'state'  : unicode,
            'phone' : unicode,
            'img_passport_fontside' : unicode,
            'img_passport_backside' : unicode,
            'img_address' : unicode
        }
    }
    validators = {
        'email': validators.max_length(120)
    }
    default_values = {
        'creation': datetime.datetime.utcnow(),
        'm_wallet' : 0,
        'r_wallet' : 0,
        's_wallet' : 0,
        'max_out' : 0,
        'total_earn' : 0,
        'total_pd_left' : 0,
        'total_pd_right' : 0,
        'total_amount_left' : 0,
        'total_amount_right' : 0,
        'level' : 0,
        'status_authen' : 0,
        'authentication' : '',
        'left' : '',
        'right' : '',
        'p_binary' : '',
        'type': 0,
        'balance_wallet' : 0,
        'active_email' : 0,
        'code_active' : '',
        'investment' : 0,
        'coin_wallet' : 0,
        'total_node' : 0,
        'max_out_day' : 0,
        'max_out_package' : 0,
        'status_verify' : 0

        }
    use_dot_notation = True

    def __repr__(self):
        return '<User %r>' % self.name

    # Flask-Login integration
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self._id

    def get_role(self):
        return self.role

    def get_user_home(self):
        role = db['roles'].find_one({'_id': self.get_role()})
        return role['home_page']


db.register([User])