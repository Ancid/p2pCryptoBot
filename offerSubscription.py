from config import *
from SQLighter import SQLighter


def subscribe():
    db_connect = SQLighter(DB_NAME)
