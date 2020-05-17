import hashlib
import hmac
import json
import time
import requests
import telebot

from config import *
from SQLighter import SQLighter

bot = telebot.TeleBot(TOKEN)


def get_offers_message_array(telegram_user_id, offer_type, payment_method=False, currency_code=False):
    nonce = str(int(time.time()))
    body = 'apikey=' + API_KEY + '&' + 'nonce=' + nonce
    body += '&offer_type=' + offer_type
    if currency_code:
        body += '&currency_code=' + str(currency_code)
    if payment_method:
        body += '&payment_method=' + str(payment_method)
    apiseal = hmac.new(API_SECRET, msg=body.encode('UTF-8'), digestmod=hashlib.sha256).hexdigest()
    body += '&apiseal=' + apiseal
    response = requests.post(
        "https://paxful.com/api/offer/all",
        data=body,
        headers={
            'content-type': 'text/plain',
            'accept': 'application/json'
        },
    )

    response_decoded = json.loads(response.text)
    offer_list = response_decoded['data']['offers']
    notify_subscribers(telegram_user_id, offer_list, offer_type, payment_method, currency_code)

    SQLighter.save_offers(offer_list)

    return send_offer_list_messages(offer_list, OFFERS_LIMIT)


# def load_offers():
#     with open('offers.json', 'r') as f:
#         offers_dict = json.load(f)
#
#     return offers_dict['data']['offers']


def send_offer_list_messages(offer_list, limit=None):
    offer_messages = []
    if limit:
        offer_list = offer_list[:limit]
    for offer in offer_list:
        offer_messages.append(
            '*' + str(offer['fiat_price_per_btc']) + ' ' + str(offer['currency_code']) + '* per 1₿, limits ' +
            str(offer['fiat_amount_range_min']) + '-' + str(offer['fiat_amount_range_max']) + "\n" + offer['offer_link']
        )

    return offer_messages


def notify_subscribers(telegram_user_id, offer_list, offer_type, payment_method, currency_code):
    subscribers = SQLighter.get_subscribers(telegram_user_id, offer_type, payment_method, currency_code)
    new_offers_filter = makefilter(offer_list)
    filtered_offers = list(filter(new_offers_filter, offer_list))

    for user in subscribers:
        send_found_new_offers(user, filtered_offers)


def makefilter(offer_list):
    existed_offers_hashes = SQLighter.check_new_offers(offer_list)

    def myfilter(x):
        return x['offer_id'] not in existed_offers_hashes

    return myfilter


def send_found_new_offers(user, offer_list):
    chat_id = user['chat_id']
    messages = send_offer_list_messages(offer_list)
    messages.append("Hi! Your subscription for *BUY* Btc offers for *Paypal* with *USD*. Has new offers:")
    for message in messages:
        bot.send_message(chat_id, message, parse_mode="Markdown", disable_web_page_preview=True)
