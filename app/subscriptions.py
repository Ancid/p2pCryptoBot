import asyncio
import os
import time

from mongo_db.MongoManager import db_get_groupped_subscriptions, db_save_offers
from mongo_db.db import db_users
from offersList import get_offers_array, notify_subscribers


async def walk_through_subsciptions():
    very_start_time = time.time()
    tasks = []
    async for subscription in db_get_groupped_subscriptions():
        tasks.append(process_subscription(subscription))

    await asyncio.gather(*tasks)

    total_time = time.time() - very_start_time
    print("Subscriptions checked in: " + str(total_time) + " sec.")

    return total_time


async def process_subscription(subscription):
    start_time = time.time()
    any_user = await db_users.find_one({"subscription.hash": subscription['_id']})
    user_time = time.time() - start_time
    if os.environ['DEBUG'] == 'True':
        print('Fetch User: '+ str(user_time))
    if any_user['subscription']['active']:
        offers_time = time.time()
        offers = await get_offers_array(
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
            # await notify_subscribers(
            #     None,
            #     offers,
            #     any_user['subscription']['offer_type'],
            #     any_user['subscription']['payment_method'],
            #     any_user['subscription']['currency_code']
            # )
            if os.environ['DEBUG'] == 'True':
                notify_time = time.time() - offers_time
                print('notify time: ' + str(notify_time))
                before_save_time = time.time()

                await db_save_offers(offers)

                save_time = time.time() - before_save_time
                print(f'save time: {save_time}')
            else:
                await db_save_offers(offers)  # Dirty hack for debug logging
