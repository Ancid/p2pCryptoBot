#!/usr/bin/python
# -*- coding: UTF-8 -*-
import telebot
from config import *
from telebot import types
from SQLighter import SQLighter
from markup.actions import markup_actions
from markup.currency import markup_currency
from markup.offerType import markup_offer_type
from markup.paymentMethod import markup_payment_method
from offersList import get_offers_message_array

selected_offer_type = ''
selected_currency = ''
selected_payment_method = ''
selected_mode = ''
db_connect = SQLighter()
subscription_active = False

WEBHOOK_HOST = '146.255.180.71'
WEBHOOK_PORT = 8443  # 443, 80, 88 или 8443 (порт должен быть открыт!)
WEBHOOK_LISTEN = '127.0.0.1'

WEBHOOK_SSL_CERT = 'webhook_cert.pem'  # Путь к сертификату
WEBHOOK_SSL_PRIV = 'webhook_pkey.pem'  # Путь к приватному ключу

WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % TOKEN

bot = telebot.TeleBot(TOKEN)


# - - - messages

@bot.message_handler(content_types=['text'])
def start(message):
    global selected_mode
    global subscription_active
    subscription_active = SQLighter.check_subscription(message.chat.id)
    bot.send_message(
        message.chat.id,
        "Hey! I'm the smart bot and can help you find offer or subscribe for updates. What are you wanna do?",
        reply_markup=markup_actions(subscription_active)
    )


def choosing_payment_method(message):
    try:
        bot.send_message(message.chat.id, "Choose payment method:", reply_markup=markup_payment_method())
    except Exception as e:
        bot.reply_to(message, str(e))


def choosing_currency(message):
    try:
        bot.send_message(message.chat.id, "Choose currency:", reply_markup=markup_currency())
    except Exception as e:
        bot.reply_to(message, str(e))


def show_offers(message):
    global selected_offer_type
    global selected_currency
    global selected_payment_method
    global subscription_active
    bot.send_message(
        message.chat.id, "Well, you selected *" + selected_offer_type.upper() + "* Btc offers for *" + \
                         selected_payment_method.upper() + "* in *" + selected_currency.upper() + \
                         "*. Let\'s me check some offers for you...",
        parse_mode="Markdown"
    )
    offers = get_offers_message_array(message.chat.id, selected_offer_type, selected_payment_method, selected_currency)
    if len(offers):
        for msg in offers:
            bot.send_message(message.chat.id, msg, parse_mode="Markdown", disable_web_page_preview=True)
        bot.send_message(
            message.chat.id,
            "Didn't get the best offer? Subscribe for updates or start a new search",
            reply_markup=markup_actions(subscription_active)
        )
    else:
        bot.send_message(
            message.chat.id,
            "Offers with you parameters  doesn't exist yet. Try again or subscribe for updates ",
            reply_markup=markup_actions(subscription_active)
        )


def process_subscription(message):
    global selected_offer_type
    global selected_currency
    global selected_payment_method
    global subscription_active
    SQLighter.subscribe(message.chat.id, True)
    subscription_active = True
    bot.send_message(
        message.chat.id, "Well, you subscribed for *" + selected_offer_type.upper() + "* Btc offers for *" + \
                         selected_payment_method.upper() + "* in *" + selected_currency.upper() + \
                         "*. I will send you notification when new offers will appear",
        parse_mode="Markdown"
    )
    bot.send_message(
        message.chat.id,
        "Don't want to wait? Check offers right now!",
        reply_markup=markup_actions(True)
    )


@bot.callback_query_handler(func=lambda call: True)
def callback_inline_offer_type(call):
    global selected_offer_type
    global selected_currency
    global selected_payment_method
    global selected_mode
    global selected_mode
    global subscription_active
    if call.message:
        if call.data.startswith('action_search'):
            selected_mode = 'offers'
            bot.send_message(call.message.chat.id, "OK, firstly select offer type:", reply_markup=markup_offer_type())
        if call.data.startswith('action_subscribe'):
            selected_mode = 'subscribe'
            bot.send_message(call.message.chat.id, "OK, firstly select offer type:", reply_markup=markup_offer_type())
        if call.data.startswith('action_unsubscribe'):
            SQLighter.subscribe(call.message.chat.id, False)
            subscription_active = False
            bot.send_message(call.message.chat.id, "You have been unsubscribed:", reply_markup=markup_actions())
        if call.data.startswith('type_'):
            db_connect.add_user(call.from_user.username, call.from_user.id, call.message.chat.id)
            selected_offer_type = call.data.split('_')[1]
            choosing_payment_method(call.message)
        if call.data.startswith('pm_'):
            selected_payment_method = call.data.split('_')[1]
            choosing_currency(call.message)
        if call.data.startswith('currency_'):
            selected_currency = call.data.split('_')[1]
            if check_filled_options():
                update_user_options(call)
                if selected_mode == 'offers':
                    show_offers(call.message)
                else:
                    process_subscription(call.message)
            else:
                bot.send_message(
                    call.message.chat.id,
                    "Try again /offers to check offers or /subscribe to subscribe",
                    parse_mode="Markdown"
                )


def update_user_options(call):
    global db_connect
    global selected_offer_type
    global selected_payment_method
    global selected_currency
    user_options = {
        'offer_type': selected_offer_type,
        'payment_method': selected_payment_method,
        'currency_code': selected_currency
    }
    db_connect.update_user_options(call.from_user.id, selected_mode, user_options)


def check_filled_options():
    global selected_offer_type
    global selected_payment_method
    global selected_currency
    return selected_offer_type and selected_payment_method and selected_currency


# bot.polling(none_stop=True, interval=0)
