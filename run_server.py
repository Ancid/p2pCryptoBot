import nest_asyncio
from telebot import types
from config import *
from bot import bot
from aiohttp import web

from mongo_db.db import db_bench
from subscriptions import walk_through_subsciptions
nest_asyncio.apply()

app = web.Application()


async def webhook(request):
    try:
        request_body_dict = await request.json()
        bot.process_new_updates([types.Update.de_json(request_body_dict)])
        text="Processed"
    except Exception as e:
        text="Error: " + str(e)
    return web.Response(text=text)


async def index(request):
    return web.Response(text="Hello from OffersBot!")


async def reset_webhook(request):
    bot.remove_webhook()
    bot.set_webhook(url="https://{}.herokuapp.com/{}".format(APP_NAME, TOKEN))
    return web.Response(text="Hello from OffersBot!")


async def check_subscriptions(request):
    await walk_through_subsciptions()
    return web.Response(text="Done")


async def bench(request):
    db_bench.insert_one({
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
    return web.json_response({"result": "inserted"})


app.router.add_post("/{token}", webhook)

app.router.add_get("/", index)
app.router.add_get("/reset_webhook", reset_webhook)
app.router.add_get("/check/subscriptions", check_subscriptions)
app.router.add_get("/alias", check_subscriptions)
app.router.add_get("/bench", bench)

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))