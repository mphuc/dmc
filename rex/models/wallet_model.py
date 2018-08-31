import datetime
from mongokit import Document
from rex import app, db
import validators

__author__ = 'taijoe'


class Wallet(Document):
    __collection__ = 'wallet_payments'

    structure = {
        'uid':  unicode,
        'username':  unicode,
        'wallet' :  unicode,
        'day_profit' :  float,
        'number_prfit' : float,
        'amount':  float,
        'amount_btc':  float,
        'date_finish':  unicode,
        'total_date': float
    }
    use_dot_notation = True

db.register([Wallet])