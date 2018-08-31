import datetime
from mongokit import Document
from rex import app, db
import validators

__author__ = 'taijoe'


class Ticker(Document):
    __collection__ = 'ticker'

    structure = {
        'btc_usd' : float,
        'sva_btc' : float,
        'sva_usd' : float,
        'xvg_usd' : float,
        'xvg_btc' : float
    }
    default_values = {
        'btc_usd' : 0,
        'sva_btc' : 0,
        'sva_usd' : 0,
        'xvg_usd' : 0,
        'xvg_btc' : 0
    }
    use_dot_notation = True

db.register([Ticker])