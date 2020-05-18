# -*- coding: utf-8 -*-
import hashlib
import datetime

import pymongo

import globals

from datetime import datetime, timedelta
from mongo_db.db import db_users, db_offers

user_mode_collections = {
    'subscribe': 'subscription',
    'offers': 'search',
}


def db_add_user(call):
    if not db_users.find_one({"telegram_user_id": call.from_user.id}):
        db_users.insert_one({
            "telegram_user_id": call.from_user.id,
            "chat_id": call.message.chat.id,
            "username": call.from_user.username,
            "subscription": {"active": False},
            "search": {}
        })
        # db_search_options.insert_one({
        #     "chat_id": call.message.chat.id
        # })
        # db_subscriptions.insert_one({
        #     "chat_id": call.message.chat.id,
        #     "active": False
        # })


def db_check_subscription(chat_id):
    user = db_users.find_one({
        "chat_id": chat_id
    })
    if user:
        return user['subscription']['active']
    # subscription = db_subscriptions.find_one({
    #     "chat_id": chat_id
    # })
    # if subscription:
    #     return subscription.active

    return False


def db_update_user_options(chat_id, options):
    hash_str = options['offer_type'] + options['payment_method'] + options['currency_code']

    options_value = {
        "offer_type": options['offer_type'],
        "payment_method": options['payment_method'],
        "currency_code": options['currency_code'],
        "hash": hashlib.md5(hash_str.encode('utf-8')).hexdigest()
    }
    if globals.selected_mode == 'subscribe':
        options_value["active"] = globals.subscription_active
    db_users.update(
        {"chat_id": chat_id},
        {
            "$set": {
                user_mode_collections[globals.selected_mode]: options_value
            }
        }
    )

    # db_collection = user_mode_collections[globals.selected_mode]
    # db_collection.update({"chat_id": chat_id}, {"$set": {
    #     "offer_type": options['offer_type'],
    #     "payment_method": options['payment_method'],
    #     "currency_code": options['currency_code'],
    #     "hash": hash_val
    # }})


def db_check_new_offers(offers_list):
    hashes = []
    for offer in offers_list:
        hashes.append(offer['offer_id'])

    existed_offers = db_offers.find({
        "hash": {"$in": hashes},
        "created_at": {"$gte": datetime.today() - timedelta(days=1)}
    })

    results = []
    if existed_offers.count():
        results = existed_offers

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
    db_users.update({"chat_id": chat_id}, {"$set": {"subscription.active": True}})


def db_get_subscribers(chat_id, offer_type, payment_method, currency_code):
    hash_str = offer_type + payment_method + currency_code
    users = db_users.find({
        "chat_id": chat_id,
        "subscription.hash": hashlib.md5(hash_str.encode('utf-8')).hexdigest(),
        "subscription.active": True
    })

    columns = ['username', 'telegram_user_id', 'chat_id']
    results = []
    for row in users:
        results.append(dict(zip(columns, row)))

    return results
