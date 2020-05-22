# -*- coding: utf-8 -*-
import hashlib
import datetime
import pymongo

from datetime import datetime, timedelta
from mongo_db.db import db_users, db_offers

user_mode_collections = {
    'subscribe': 'subscription',
    'offers': 'search',
}


def db_add_user(call):
    if not db_users.find_one({"chat_id": call.from_user.id}):
        db_users.insert_one({
            "chat_id": call.from_user.id,
            "username": call.from_user.username,
            "subscription": {"active": False},
            "search": {}
        })


def db_check_subscription(chat_id):
    user = db_users.find_one({
        "chat_id": chat_id
    })
    if user:
        return user['subscription']['active']

    return False


def db_update_user_options(chat_id, options, mode, subscription_active):
    hash_str = options['offer_type'] + options['payment_method'] + options['currency_code']

    options_value = {
        "offer_type": options['offer_type'],
        "payment_method": options['payment_method'],
        "currency_code": options['currency_code'],
        "hash": hashlib.md5(hash_str.encode('utf-8')).hexdigest()
    }
    if mode == 'subscribe':
        options_value["active"] = subscription_active
    db_users.update(
        {"chat_id": chat_id},
        {
            "$set": {
                user_mode_collections[mode]: options_value
            }
        }
    )


def db_check_new_offers(offers_list):
    hashes = []
    for offer in offers_list:
        hashes.append(offer['offer_id'])

    existed_offers = db_offers.find({
        "hash": {"$in": hashes},
        "created_at": {"$gte": datetime.today() - timedelta(days=3)}
    })

    results = []
    if existed_offers.count():
        for offer in existed_offers:
            results.append(offer['hash'] )

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


def db_subscribe(chat_id, active):
    db_users.update({"chat_id": chat_id}, {"$set": {"subscription.active": active}})


def db_get_subscribers(chat_id, offer_type, payment_method, currency_code):
    hash_str = offer_type + payment_method + currency_code
    users = db_users.find({
        "subscription.hash": hashlib.md5(hash_str.encode('utf-8')).hexdigest(),
        "subscription.active": True
    })

    return list(users)


def db_get_groupped_subscriptions():
    return list(db_users.aggregate([{"$group": {"_id": "$subscription.hash", "count": {"$sum": 1}}}]))
