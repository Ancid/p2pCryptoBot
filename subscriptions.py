import asyncio
import os
import time

from mongo_db.MongoManager import db_get_groupped_subscriptions, db_save_offers
from mongo_db.db import db_users
from offersList import get_offers_array, notify_subscribers


async def walk_through_subsciptions():
    very_start_time = time.time()
    subscriptions = db_get_groupped_subscriptions()
    print(len(subscriptions))
    if subscriptions is not None and len(subscriptions):
        ioloop = asyncio.new_event_loop()
        tasks = [process_sunscription(subscription) for subscription in subscriptions]
        ioloop.run_until_complete(asyncio.wait(tasks))
        ioloop.close()

    total_time = time.time() - very_start_time
    if os.environ['DEBUG']:
        print('Total time: '+ str(total_time))
    if total_time > 20:
        print("WARNING! execution time " + str(total_time))

async def process_sunscription(subscription):
    start_time = time.time()
    any_user = db_users.find_one({"subscription.hash": subscription['_id']})
    user_time = time.time() - start_time
    if os.environ['DEBUG']:
        print('Fetch User: '+ str(user_time))
    if any_user['subscription']['active']:
        offers_time = time.time()
        offers = get_offers_array(
            any_user['subscription']['offer_type'],
            any_user['subscription']['payment_method'],
            any_user['subscription']['currency_code']
        )

        if offers is None:
            print("Error response from Paxful API")
        else:
            print(
                'Notify ' + str(subscription['count']) + ' users ' + any_user['subscription']['offer_type'] + '-' +
                any_user['subscription']['payment_method'] + '-' + any_user['subscription']['currency_code']
            )
            notify_subscribers(
                None,
                offers,
                any_user['subscription']['offer_type'],
                any_user['subscription']['payment_method'],
                any_user['subscription']['currency_code']
            )
            if os.environ['DEBUG']:
                notify_time = time.time() - offers_time
                print('notify time: ' + str(notify_time))
                before_save_time = time.time()
                db_save_offers(offers)
                save_time = time.time() - before_save_time
                print('save time: '+ str(save_time))
            else:
                db_save_offers(offers) #Dirty hack for debug logging
