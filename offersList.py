import hashlib
import hmac
import json
import time
from json.decoder import JSONDecodeError

import requests
import telebot
from telebot.apihelper import ApiException

from config import *
from markup.paymentMethod import PAYMENT_METHODS
from messages import MSG_YOU_CAN
from mongo_db.MongoManager import db_check_new_offers, db_get_subscribers

bot = telebot.TeleBot(TOKEN)


def get_offers_array(offer_type, payment_method=False, currency_code=False):
    nonce = str(int(time.time()))
    body = 'apikey=' + API_KEY + '&' + 'nonce=' + nonce
    body += '&offer_type=' + offer_type
    if currency_code:
        body += '&currency_code=' + str(currency_code)
        if currency_code == 'USD':
            body += '&visitor_country_iso=US'

    if payment_method:
        body += '&payment_method=' + str(payment_method)

    payment_group = getPaymentMethodGroup(payment_method)
    if payment_group:
        body += '&group=' + str(payment_group)

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

    try:
        response_decoded = json.loads(response.text)
        offer_list = response_decoded['data']['offers']
    except JSONDecodeError:
        return None

    return offer_list


def getPaymentMethodGroup(payment_method):
    for group in PAYMENT_METHODS:
        for pm in PAYMENT_METHODS[group]:
            if payment_method == PAYMENT_METHODS[group][pm]:
                return group

    return False


def make_offer_list_messages(offer_list, limit=None, page=False):
    offer_messages = []
    if limit:
        if page and len(offer_list) > limit:
            start = limit * page - 1
            offer_list = offer_list[start:start + limit]
        else:
            offer_list = offer_list[:limit]
    for offer in offer_list:
        margin = "⬆{0}{1} ".format('%', offer['margin']).replace("-", "")
        if str(offer['margin']).find('-') >= 0:
            margin = "⬇-{0} {1}".format('%', offer['margin']).replace("-", "")
        offer_messages.append(
            '*' + str(offer['fiat_price_per_btc']) + ' ' + str(offer['currency_code']) + '* per 1₿, ' + \
            margin + ", " + 'limits ' + \
            str(offer['fiat_amount_range_min']) + '-' + str(offer['fiat_amount_range_max']) + ' ' + \
            str(offer['currency_code']) + ', user *' + offer['offer_owner_username'] + "*\n" + \
            offer['offer_link'] + '?r=bot'
        )

    return offer_messages


def notify_subscribers(current_chat_id, offer_list, offer_type, payment_method, currency_code):
    subscribers = db_get_subscribers(offer_type, payment_method, currency_code)
    new_offers_filter = makefilter(offer_list)
    filtered_offers = list(filter(new_offers_filter, offer_list))

    print(str(len(filtered_offers)) + ' offers for notify ')
    if len(filtered_offers):
        for user in subscribers:
            if user['chat_id'] != current_chat_id:
                send_found_new_offers(user, filtered_offers)
                try:
                    bot.send_message(user['chat_id'], MSG_YOU_CAN, parse_mode="Markdown")
                    print('offers sent')
                except telebot.apihelper.ApiException:
                    print('User banned a bot: ' + str(user['chat_id']))
                    pass


def makefilter(offer_list):
    existed_offers_hashes = db_check_new_offers(offer_list)

    def myfilter(x):
        return x['offer_id'] not in existed_offers_hashes

    return myfilter


def send_found_new_offers(user, offer_list):
    try:
        messages = make_offer_list_messages(offer_list, SUBSCRIPTION_LIMIT)
        if len(messages):
            chat_id = user['chat_id']
            update_message = "It’s your lucky day! I've found some great offers for *" + \
                             user['subscription']['offer_type'].upper() + "* Btc offers for *" + \
                             user['subscription']['payment_method'].upper() + "* with *" + \
                             user['subscription']['currency_code'].upper() + "*:"
            bot.send_message(chat_id, update_message, parse_mode="Markdown", disable_web_page_preview=True)
            for message in messages:
                bot.send_message(chat_id, message, parse_mode="Markdown", disable_web_page_preview=True)
    except ApiException:
        pass
