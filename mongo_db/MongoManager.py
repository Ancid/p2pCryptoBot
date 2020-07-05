# -*- coding: utf-8 -*-
import hashlib
import datetime
import pymongo

from datetime import datetime, timedelta
from mongo_db.db import db_users, db_offers, db_users_history


def db_add_user(chat_id, username):
    if not db_users.find_one({"chat_id": chat_id}):
        db_users.insert_one({
            "chat_id": chat_id,
            "username": username,
            "active_mode": False,
            "subscription": {
                "active": False,
                "offer_type": False,
                "payment_method": False,
                "currency_code": False,
                "hash": False
            },
            "search": {
                "offer_type": False,
                "payment_method": False,
                "currency_code": False,
                "hash": False
            }
        })


def db_update_user_mode(chat_id, mode):
    db_users.update({"chat_id": chat_id}, {"$set": {"active_mode": mode}})


def db_get_selected_mode(chat_id):
    mode = db_users.find_one({"chat_id": chat_id})

    return mode['active_mode']


def db_update_offer_type(chat_id, offer_type):
    mode = db_get_selected_mode(chat_id)
    db_users.update({"chat_id": chat_id}, {"$set": {mode + ".offer_type": offer_type}})


def db_update_payment_method(chat_id, method):
    mode = db_get_selected_mode(chat_id)
    db_users.update({"chat_id": chat_id}, {"$set": {mode + ".payment_method": method}})


def db_update_currency(chat_id, currency, db_users_history=None):
    mode = db_get_selected_mode(chat_id)
    user = db_get_user(chat_id)
    hash_str = user[mode]['offer_type'] + user[mode]['payment_method'] + currency
    hash = hashlib.md5(hash_str.encode('utf-8')).hexdigest()
    db_users.update(
        {"chat_id": chat_id},
        {"$set": {mode + ".currency_code": currency, mode + ".hash": hash, mode + ".updated_at": datetime.now()}}
    )

    return db_get_user(chat_id)


def db_check_subscription(chat_id):
    user = db_users.find_one({
        "chat_id": chat_id
    })
    if user:
        return user['subscription']['active']

    return False


def db_update_subscription(chat_id, active):
    db_users.update(
        {"chat_id": chat_id},
        {"$set": {"subscription.active": active, "subscription.updated_at": datetime.now()}}
    )


def db_log_active_subscription(user):
    db_users_history.insert_one({
        "user": user["chat_id"],
        "active": user["subscription"]["active"],
        "currency": user["subscription"]["currency_code"],
        "offer_type": user["subscription"]['offer_type'],
        "payment_method": user["subscription"]['payment_method'],
        "created_at": datetime.now()
    })


def db_log_deactive_subscription(chat_id):
    db_users_history.insert_one({
        "user": chat_id,
        "active": False,
        "created_at": datetime.now()
    })


def db_update_user_options(chat_id, options):
    hash_str = options['offer_type'] + options['payment_method'] + options['currency_code']
    options_value = {
        "offer_type": options['offer_type'],
        "payment_method": options['payment_method'],
        "currency_code": options['currency_code'],
        "hash": hashlib.md5(hash_str.encode('utf-8')).hexdigest()
    }
    user = db_users.find_one({"chat_id": chat_id})
    db_users.update(
        {"chat_id": chat_id},
        {
            "$set": {
                user['active_mode']: options_value
            }
        }
    )


def db_check_new_offers(offers_list):
    hashes = []
    for offer in offers_list:
        hashes.append(offer['offer_id'])

    existed_offers = db_offers.find({
        "hash": {"$in": hashes}
    })
    # "created_at": {"$gte": datetime.today() - timedelta(days=OFFERS_DAYS_FILTER)}

    results = []
    if existed_offers.count():
        for offer in existed_offers:
            results.append(offer['hash'])

    return results


def db_save_offers(offers_list):
    if len(offers_list):
        for offer in offers_list:
            try:
                db_offers.insert(
                    {"hash": offer['offer_id'], "created_at": datetime.now()},
                    continue_on_error=True
                )
            except pymongo.errors.DuplicateKeyError:
                pass


def db_get_subscribers(offer_type, payment_method, currency_code):
    hash_str = offer_type + payment_method + currency_code
    users = db_users.find({
        "subscription.hash": hashlib.md5(hash_str.encode('utf-8')).hexdigest(),
        "subscription.active": True
    })

    return list(users)


def db_get_groupped_subscriptions():
    return list(db_users.aggregate([{"$group": {"_id": "$subscription.hash", "count": {"$sum": 1}}}]))


def db_get_user(chat_id):
    user = db_users.find_one({
        "chat_id": chat_id
    })

    return user


def update_user_hashes():
    users = db_users.find({'subscription.active': True})
    for user in users:
        # print('chat_id: '+str(user['chat_id']))
        # print('name: '+user['username'])
        # print('old: '+user['subscription']['hash'])
        hash_str = user['subscription']['offer_type'] + user['subscription']['payment_method'] + user['subscription'][
            'currency_code']
        hash = hashlib.md5(hash_str.encode('utf-8')).hexdigest()
        # print('new: '+hash)
        # print('-----')
