from mongo_db.MongoManager import db_get_groupped_subscriptions, db_save_offers
from mongo_db.db import db_users
from offersList import get_offers_array, notify_subscribers


def walk_through_subsciptions():
    subscriptions = db_get_groupped_subscriptions()
    if subscriptions is not None and len(subscriptions):
        for subscription in subscriptions:
            any_user = db_users.find_one({"subscription.hash": subscription['_id']})
            if any_user['subscription']['active']:
                offers = get_offers_array(
                    any_user['subscription']['offer_type'],
                    any_user['subscription']['payment_method'],
                    any_user['subscription']['currency_code']
                )
                notify_subscribers(
                    None,
                    offers,
                    any_user['subscription']['offer_type'],
                    any_user['subscription']['payment_method'],
                    any_user['subscription']['currency_code']
                )
                db_save_offers(offers)
