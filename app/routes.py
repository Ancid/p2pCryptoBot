from aiogram import types
from fastapi import APIRouter, Request

from app import telegram
from app.db import db_bench
from app.settings import APP_NAME, TOKEN
from app.subscriptions import walk_through_subscriptions
from app.telegram import bot
from config import WEBHOOK_URL

router = APIRouter()


@router.get("/check/subscriptions", tags=["Subscriptions"])
async def check_subscriptions():
    timeit = await walk_through_subscriptions()

    return {"timeit": timeit}


@router.get("/reset/webhook", tags=["Webhook"])
async def resetWebhook():
    bot.delete_webhook()
    bot.set_webhook(url=WEBHOOK_URL)

    return "OK"


@router.post("/{token}", tags=["Webhook"])
async def webhook(request: Request):
    data = await request.json()
    update = types.Update(**data)

    # response within 60 seconds
    await telegram.dp.updates_handler.notify(update)

    return "OK"


@router.get("/bench", tags=["Subscriptions"])
async def bench(request):
    await db_bench.insert_one({
        "chat_id": 1,
        "username": 'wad',
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
    return {"result": "inserted"}
