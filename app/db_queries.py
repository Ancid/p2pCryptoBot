import hashlib
from datetime import datetime

from pymongo.errors import DuplicateKeyError

from app.db import db_offers, db_users, db_users_history


async def add_user(chat_id, username):
    user = await db_users.find_one({"chat_id": chat_id})
    if not user:
        await db_users.insert_one(
            {
                "chat_id": chat_id,
                "username": username,
                "active_mode": False,
                "subscription": {
                    "active": False,
                    "offer_type": False,
                    "payment_method": False,
                    "currency_code": False,
                    "hash": False,
                },
                "search": {
                    "offer_type": False,
                    "payment_method": False,
                    "currency_code": False,
                    "hash": False,
                    "page": 1,
                },
            }
        )


async def update_user_mode(chat_id, mode):
    await db_users.update_one({"chat_id": chat_id}, {"$set": {"active_mode": mode}})


async def update_search_page(chat_id, page):
    await db_users.update_one({"chat_id": chat_id}, {"$set": {"search.page": page}})


async def get_selected_mode(chat_id):
    user = await db_users.find_one({"chat_id": chat_id})
    mode = None
    if user:
        mode = user["active_mode"]

    return mode


async def update_offer_type(chat_id, offer_type):
    mode = await get_selected_mode(chat_id)
    await db_users.update_one(
        {"chat_id": chat_id}, {"$set": {mode + ".offer_type": offer_type}}
    )


async def update_payment_method(chat_id, method):
    mode = await get_selected_mode(chat_id)
    await db_users.update_one(
        {"chat_id": chat_id}, {"$set": {mode + ".payment_method": method}}
    )


async def update_currency(chat_id, currency):
    mode = await get_selected_mode(chat_id)
    user = await get_user(chat_id)
    hash_str = user[mode]["offer_type"] + user[mode]["payment_method"] + currency
    hashed_str = hashlib.md5(hash_str.encode("utf-8")).hexdigest()
    await db_users.update_one(
        {"chat_id": chat_id},
        {
            "$set": {
                mode + ".currency_code": currency,
                mode + ".hash": hashed_str,
                mode + ".updated_at": datetime.now(),
            }
        },
    )

    return await get_user(chat_id)


async def check_subscription(chat_id):
    user = await db_users.find_one({"chat_id": chat_id})
    if user:
        return user["subscription"]["active"]

    return False


async def update_subscription(chat_id, active):
    await db_users.update_one(
        {"chat_id": chat_id},
        {
            "$set": {
                "subscription.active": active,
                "subscription.updated_at": datetime.now(),
            }
        },
    )


def db_log_active_subscription(user):
    db_users_history.insert_one(
        {
            "user": user["chat_id"],
            "mode": "subscription",
            "active": user["subscription"]["active"],
            "currency": user["subscription"]["currency_code"] or False,
            "offer_type": user["subscription"]["offer_type"] or False,
            "payment_method": user["subscription"]["payment_method"] or False,
            "created_at": datetime.now(),
        }
    )


async def log_search(user):
    await db_users_history.insert_one(
        {
            "user": user["chat_id"],
            "mode": "search",
            "currency": user["search"]["currency_code"] or False,
            "offer_type": user["search"]["offer_type"] or False,
            "payment_method": user["search"]["payment_method"] or False,
            "created_at": datetime.now(),
        }
    )


async def log_deactive_subscription(chat_id):
    await db_users_history.insert_one(
        {"user": chat_id, "active": False, "created_at": datetime.now()}
    )


def db_update_user_options(chat_id, options):
    hash_str = (
        options["offer_type"] + options["payment_method"] + options["currency_code"]
    )
    options_value = {
        "offer_type": options["offer_type"],
        "payment_method": options["payment_method"],
        "currency_code": options["currency_code"],
        "hash": hashlib.md5(hash_str.encode("utf-8")).hexdigest(),
    }
    user = db_users.find_one({"chat_id": chat_id})
    db_users.update_one(
        {"chat_id": chat_id}, {"$set": {user["active_mode"]: options_value}}
    )


async def check_new_offers(offers_list):
    hashes = []
    for offer in offers_list:
        hashes.append(offer["offer_id"])

    cur = db_offers.find({"hash": {"$in": hashes}})
    # "created_at": {"$gte": datetime.today() - timedelta(days=OFFERS_DAYS_FILTER)}

    results = []
    for offer in await cur.to_list(None):
        results.append(offer["hash"])

    return results


async def save_offers(offers_list):
    if len(offers_list):
        for offer in offers_list:
            try:
                await db_offers.insert_one(
                    {"hash": offer["offer_id"], "created_at": datetime.now()},
                )
            except DuplicateKeyError:
                pass


async def get_subscribers(offer_type, payment_method, currency_code):
    hash_str = offer_type + payment_method + currency_code
    cur = db_users.find(
        {
            "subscription.hash": hashlib.md5(hash_str.encode("utf-8")).hexdigest(),
            "subscription.active": True,
        }
    )

    return await cur.to_list(length=None)


async def get_grouped_subscriptions():
    cur = db_users.aggregate(
        [{"$group": {"_id": "$subscription.hash", "count": {"$sum": 1}}}]
    )

    return await cur.to_list(None)


async def get_user(chat_id: int):
    user = await db_users.find_one({"chat_id": chat_id})

    return user
