import datetime
from mongokit import Document
from rex import app, db
import validators

__author__ = 'taijoe'


class Deposit(Document):
    __collection__ = 'deposit'

    structure = {
        'uid' : unicode,
        'user_id': unicode,
        'username' : unicode,
        'amount_usd' : float,
        'amount_sva' : float,
        'status' : int,
        'date_added' : datetime.datetime,
        'num_frofit' : float,
        'types' : int,
        'percent' :  float,
        'total_day': float,
        'total_day_earn': float,
        'amount_daily' : float,
        'num_profit' : float,
        'lock_profit': float
    }
    default_values = {
        'date_added': datetime.datetime.utcnow(),
        'num_frofit' : 0.0
        }
    use_dot_notation = True

db.register([Deposit])