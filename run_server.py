# import flask
import os

import aiohttp
from telebot import types
from config import *
from bot import bot
from aiohttp import web

from subscriptions import walk_through_subsciptions

app = web.Application()


async def webhook(request):
    request_body_dict = await request.json()
    bot.process_new_updates([types.Update.de_json(request_body_dict)])
    return web.Response()


async def index(request):
    return web.Response(text="Hello from OffersBot!")


async def reset_webhook(request):
    bot.remove_webhook()
    bot.set_webhook(url="https://{}.herokuapp.com/{}".format(APP_NAME, TOKEN))
    return web.Response(text="Hello from OffersBot!")


async def check_subscriptions(request):
    walk_through_subsciptions()
    return web.Response(text="Done")

app.router.add_post("/{token}", webhook)
app.router.add_get("/", index)
app.router.add_get("/reset_webhook", reset_webhook)
app.router.add_get("/check/subscriptions", check_subscriptions)
app.router.add_get("/alias", check_subscriptions)

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))

# --------------------------
# server = flask.Flask(__name__)


# @server.route('/' + TOKEN, methods=['POST'])
# def get_message():
#     bot.process_new_updates([types.Update.de_json(
#         flask.request.stream.read().decode("utf-8"))])
#     return "!", 200


# @server.route('/', methods=["GET"])
# def index():
#     return "Hello from OffersBot!", 200
#
#
# @server.route('/webhook', methods=["GET"])
# def webhook():
#     bot.remove_webhook()
#     bot.set_webhook(url="https://{}.herokuapp.com/{}".format(APP_NAME, TOKEN))
#     return "Hello from OffersBot!", 200
#
#
# @server.route('/check/subscriptions', methods=["GET"])
# def crone():
#     walk_through_subsciptions()
#     return "Done!", 200
#
#
# @server.route('/alias', methods=["GET"])
# def crone_alias():
#     walk_through_subsciptions()
#     return "Done!", 200
#
#
# if __name__ == "__main__":
#     server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
