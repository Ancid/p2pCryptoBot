import asyncio
import logging
import time

import httpx

from app import db_queries, settings
from app.db import db_users
from app.offers import get_offers_array, notify_subscribers

logger = logging.getLogger(__name__)


async def walk_through_subscriptions() -> float:
    very_start_time = time.time()
    tasks = []

    subscriptions = await db_queries.get_grouped_subscriptions()

    client = httpx.AsyncClient()

    for subscription in subscriptions:
        tasks.append(process_subscription(subscription, client))

    await asyncio.gather(*tasks)
    await client.aclose()

    total_time = time.time() - very_start_time

    print(f"Subscriptions checked in: {total_time} sec.")

    return total_time


async def process_subscription(subscription, client: httpx.AsyncClient):
    start_time = time.time()
    any_user = await db_users.find_one({"subscription.hash": subscription["_id"]})
    user_time = time.time() - start_time

    if settings.APP_DEBUG:
        print("Fetch User: " + str(user_time))

    if any_user["subscription"]["active"]:
        offers_time = time.time()
        offers = await get_offers_array(
            client,
            any_user["subscription"]["offer_type"],
            any_user["subscription"]["payment_method"],
            any_user["subscription"]["currency_code"],
        )

        if not offers:
            print("Error response from Paxful API")
        else:
            print(
                "Notify "
                + str(subscription["count"])
                + " users "
                + any_user["subscription"]["offer_type"]
                + "-"
                + any_user["subscription"]["payment_method"]
                + "-"
                + any_user["subscription"]["currency_code"]
            )

            await notify_subscribers(
                None,
                offers,
                any_user["subscription"]["offer_type"],
                any_user["subscription"]["payment_method"],
                any_user["subscription"]["currency_code"],
            )

            if settings.APP_DEBUG:
                notify_time = time.time() - offers_time
                print("notify time: " + str(notify_time))
                before_save_time = time.time()

                await db_queries.save_offers(offers)

                save_time = time.time() - before_save_time
                print(f"save time: {save_time}")
            else:
                await db_queries.save_offers(offers)  # Dirty hack for debug logging
