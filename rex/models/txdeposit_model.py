import datetime
from mongokit import Document
from rex import app, db
import validators

__author__ = 'taijoe'


class TxDeposit(Document):
    __collection__ = 'txdeposit'

    structure = {
        'confirmations': int,
        'user_id': unicode,
        'uid': unicode,
        'username': unicode,
        'tx':  unicode,
        'amount': float,
        'type': unicode,
        'date_added' : datetime.datetime,
        'status': int,
        'address': unicode
    }
    use_dot_notation = True

db.register([TxDeposit])