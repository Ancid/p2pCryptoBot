# -*- coding: utf-8 -*-
import hashlib
import sqlite3
import datetime
from datetime import datetime, timedelta
from config import *

user_option_tables = {
    'subscribe': 'user_subscribe_options',
    'offers': 'user_offers_options',
}


class SQLighter:

    @staticmethod
    def add_user(username, telegram_user_id, chat_id):
        with sqlite3.connect(DB_NAME, check_same_thread=True) as con:
            cursor = con.cursor()
            existed_user = cursor.execute(
                'SELECT id FROM users WHERE telegram_user_id = ?',
                (telegram_user_id,)
            ).fetchall()
            if not len(existed_user):
                cur = cursor.execute(
                    'INSERT INTO users(username, telegram_user_id, chat_id) VALUES(?,?,?)',
                    (username, telegram_user_id, chat_id)
                )
                telegram_user_id = cur.lastrowid
                cursor.execute('INSERT INTO user_offers_options(user_id) VALUES (?)', (telegram_user_id,))
                cursor.execute('INSERT INTO user_subscribe_options(user_id) VALUES (?)', (telegram_user_id,))
            cursor.close()
            con.commit()

    @staticmethod
    def check_subscription(chat_id):
        with sqlite3.connect(DB_NAME, check_same_thread=True) as con:
            active = False
            cursor = con.cursor()
            subscription = cursor.execute(
                'SELECT active FROM user_subscribe_options WHERE user_id = (SELECT id FROM users WHERE chat_id = ?)',
              (chat_id,)
            ).fetchall()
            if len(subscription):
                active = subscription[0][0]

            return active

    @staticmethod
    def update_user_options(user_id, mode, options):
        with sqlite3.connect(DB_NAME, check_same_thread=True) as con:
            cursor = con.cursor()
            hash_str = options['offer_type'] + options['payment_method'] + options['currency_code']
            hash_val = hashlib.md5(hash_str.encode('utf-8')).hexdigest()
            cursor.execute(
                'UPDATE {0} set offer_type=?,payment_method=?,currency_code=?,hash=?'
                'WHERE user_id = (SELECT id FROM users WHERE telegram_user_id = ?)'.format(user_option_tables[mode]),
                (options['offer_type'], options['payment_method'], options['currency_code'], hash_val, user_id)
            )
            cursor.close()
            con.commit()

    @staticmethod
    def subscribe(chat_id, active):
        with sqlite3.connect(DB_NAME, check_same_thread=True) as con:
            cursor = con.cursor()
            cursor.execute(
                'UPDATE user_subscribe_options SET active=?'
                'WHERE user_id = (SELECT id FROM users WHERE chat_id = ?)',
                (active, chat_id)
            )
            cursor.close()
            con.commit()

    @staticmethod
    def get_subscribers(current_user_id, offer_type, payment_method, currency_code):
        with sqlite3.connect(DB_NAME, check_same_thread=True) as con:
            cursor = con.cursor()
            users = cursor.execute(
                'SELECT username, telegram_user_id, chat_id FROM users ''WHERE id IN('
                'SELECT id FROM user_subscribe_options WHERE offer_type=? AND payment_method=? AND currency_code=?)'
                ' AND telegram_user_id <> ?',
                (offer_type, payment_method, currency_code, current_user_id)
            )
            columns = ['username', 'telegram_user_id', 'chat_id']
            results = []
            for row in users.fetchall():
                results.append(dict(zip(columns, row)))
            cursor.close()

        return results

    @staticmethod
    def check_new_offers(offers_list):
        hashes = ','.join('"' + offer['offer_id'] + '"' for offer in offers_list)
        with sqlite3.connect(DB_NAME, check_same_thread=True) as con:
            cursor = con.cursor()
            # @ToDo add datetime filter
            existed_offers = cursor.execute(
                'SELECT hash FROM offers WHERE hash IN(' + hashes + ') AND created_at > ?',
                (datetime.today() - timedelta(days=1),)
            ).fetchall()
            cursor.close()
            con.commit()
            results = []
            for row in existed_offers:
                results.append(row[0])

        return results

    @staticmethod
    def save_offers(offers_list):
        hashes = ','.join('("' + offer['offer_id'] + '")' for offer in offers_list)
        with sqlite3.connect(DB_NAME, check_same_thread=True) as con:
            cursor = con.cursor()
            cursor.execute(
                'INSERT OR IGNORE INTO offers (hash) VALUES ' + hashes
            )
            cursor.close()
            con.commit()
