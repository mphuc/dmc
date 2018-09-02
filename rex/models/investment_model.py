import datetime
from mongokit import Document
from rex import app, db
import validators

__author__ = 'taijoe'


class Investment(Document):
    __collection__ = 'investment'

    structure = {
        'uid' : unicode,
        'user_id': unicode,
        'username' : unicode,
        'amount_usd' : float,
        'package' : float,
        'status' : int,
        'date_added' : datetime.datetime,
        'amount_frofit' : float
    }
    default_values = {
        'date_added': datetime.datetime.utcnow()
        }
    use_dot_notation = True

db.register([Investment])