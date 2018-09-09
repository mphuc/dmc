import datetime
from mongokit import Document
from rex import app, db
import validators

__author__ = 'taijoe'


class Ticker(Document):
    __collection__ = 'ticker'

    structure = {
        'btc_usd' : float,
        'eth_usd' : float,
        'bth_usd' : float,
        'ltc_usd' : float
    }
    default_values = {
        'btc_usd' : 0,
        'eth_usd' : 0,
        'bth_usd' : 0,
        'ltc_usd' : 0
    }
    use_dot_notation = True

db.register([Ticker])