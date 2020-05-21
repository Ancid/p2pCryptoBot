import flask
from telebot import types
from config import *
from bot import bot
import os

from subscriptions import walk_through_subsciptions

server = flask.Flask(__name__)


@server.route('/' + TOKEN, methods=['POST'])
def get_message():
    bot.process_new_updates([types.Update.de_json(
        flask.request.stream.read().decode("utf-8"))])
    return "!", 200


@server.route('/', methods=["GET"])
def index():
    return "Hello from OffersBot!", 200


@server.route('/webhook', methods=["GET"])
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url="https://{}.herokuapp.com/{}".format(APP_NAME, TOKEN))
    return "Hello from OffersBot!", 200


@server.route('/check/subscriptions', methods=["GET"])
def crone():
    walk_through_subsciptions()
    return "Done!", 200


@server.route('/alias', methods=["GET"])
def crone_alias():
    walk_through_subsciptions()
    return "Done!", 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
