import datetime
from mongokit import Document
from rex import app, db
import validators

__author__ = 'taijoe'


class Code(Document):
    __collection__ = 'code'

    structure = {
        'status': int
        'code':  unicode,
        'date_added' : datetime.datetime,
        'user_id' : unicode,
        'username' : unicode,
        'uid' : unicode
    }
    use_dot_notation = True

db.register([Code])