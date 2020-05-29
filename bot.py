#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os

import telebot

from config import *
from markup.currency import markup_currency
from markup.paymentMethod import markup_payment_method
from messages import *
from markup.actions import markup_actions
from markup.offerType import markup_offer_type
from mongo_db.MongoManager import db_add_user, db_check_subscription, db_update_user_options, db_subscribe, \
    db_save_offers, db_get_user
from offersList import make_offer_list_messages, get_offers_array, notify_subscribers

bot = telebot.TeleBot(TOKEN)
if os.environ['DEBUG'] == 'True':
    bot.remove_webhook()
print(bot.get_me())

runtime_subscription_active = ''
runtime_payment_method = ''
runtime_selected_mode = ''
runtime_selected_offer_type = ''
runtime_selected_currency = ''


@bot.message_handler(content_types=['text'])
def start(message):
    global runtime_subscription_active
    runtime_subscription_active = db_check_subscription(message.chat.id)
    bot.send_message(message.chat.id, MSG_HELLO, reply_markup=markup_actions(runtime_subscription_active))


@bot.callback_query_handler(func=lambda call: True)
def callback_inline_offer_type(call):
    global runtime_subscription_active
    global runtime_payment_method
    global runtime_selected_mode
    global runtime_selected_offer_type
    global runtime_selected_currency

    if runtime_subscription_active == '':
        runtime_subscription_active = db_check_subscription(call.message.chat.id)
    if call.message:
        if call.data.startswith('action:search'):
            runtime_selected_mode = 'offers'
            bot.send_message(call.message.chat.id, MSG_SELECT_TYPE, reply_markup=markup_offer_type())
        if call.data.startswith('action:subscribe'):
            runtime_selected_mode = 'subscribe'
            bot.send_message(call.message.chat.id, MSG_SELECT_TYPE, reply_markup=markup_offer_type())
        if call.data.startswith('action:unsubscribe'):
            db_subscribe(call.message.chat.id, False)
            runtime_subscription_active = False
            bot.send_message(call.message.chat.id, MSG_UNSUBSCRIBED, reply_markup=markup_actions())
        if call.data.startswith('type:'):
            db_add_user(call)
            runtime_selected_offer_type = call.data.split(':')[1]
            choosing_payment_method(call.message)
        if call.data.startswith('pm:'):
            runtime_payment_method = call.data.split(':')[1]
            choosing_currency(call.message, runtime_payment_method)
        if call.data.startswith('currency:'):
            runtime_selected_currency = call.data.split(':')[1]
            if check_filled_options():
                update_user_options(call)
                if runtime_selected_mode == 'offers':
                    show_offers(call.message)
                elif runtime_selected_mode == 'subscribe':
                    process_subscription(call.message)
                else:
                    bot.send_message(
                        call.message.chat.id,
                        MSG_OOPS,
                        reply_markup=markup_actions(runtime_subscription_active)
                    )
            else:
                bot.send_message(
                    call.message.chat.id,
                    MSG_OOPS,
                    reply_markup=markup_actions(runtime_subscription_active)
                )


def update_user_options(call):
    global runtime_subscription_active
    global runtime_selected_mode
    global runtime_payment_method
    global runtime_selected_offer_type
    global runtime_selected_currency

    user_options = {
        'offer_type': runtime_selected_offer_type,
        'payment_method': runtime_payment_method,
        'currency_code': runtime_selected_currency
    }
    db_update_user_options(call.from_user.id, user_options, runtime_selected_mode, runtime_subscription_active)


def choosing_payment_method(message):
    try:
        bot.send_message(message.chat.id, MSG_CHOOSE_PAYMENT, reply_markup=markup_payment_method())
    except Exception as e:
        bot.reply_to(message, str(e))


def choosing_currency(message, paymentMethod):
    try:
        bot.send_message(message.chat.id, MSG_CHOOSE_CURRENCY, reply_markup=markup_currency())
    except Exception as e:
        bot.reply_to(message, str(e))


def show_offers(message):
    user = db_get_user(message.chat.id)
    payment_method = user['search']['payment_method']
    offer_type = user['search']['offer_type']
    currency = user['search']['currency_code']
    subscription_active = user['subscription']['active']

    bot.send_message(
        message.chat.id,
        "Well, you selected *" + offer_type.upper() + "* Btc offers for *" + payment_method.upper() + "* in *" + \
        currency.upper() + "*. Let\'s me check some offers for you...",
        parse_mode="Markdown"
    )
    offers = get_offers_array(offer_type, payment_method, currency)
    notify_subscribers(message.chat.id, offers, offer_type, payment_method, currency)

    db_save_offers(offers)
    offer_messages = make_offer_list_messages(offers, SEARCH_LIMIT)
    if len(offer_messages):
        for msg in offer_messages:
            bot.send_message(message.chat.id, msg, parse_mode="Markdown", disable_web_page_preview=True)
        bot.send_message(message.chat.id, MSG_OFFERS,
                         reply_markup=markup_actions(db_check_subscription(message.chat.id)))
    else:
        bot.send_message(message.chat.id, MSG_OFFERS_EMPTY, reply_markup=markup_actions(subscription_active))


def process_subscription(message):
    global runtime_subscription_active
    global runtime_payment_method
    global runtime_selected_offer_type
    global runtime_selected_currency

    db_subscribe(message.chat.id, True)
    runtime_subscription_active = True
    bot.send_message(
        message.chat.id,
        "Well, you subscribed for *" + runtime_selected_offer_type.upper() + "* Btc offers for *" + \
        runtime_payment_method.upper() + "* in *" + runtime_selected_currency.upper() + \
        "*. I will send you notification when new offers will appear",
        parse_mode="Markdown"
    )
    bot.send_message(message.chat.id, MSG_CHECK_OFFERS, reply_markup=markup_actions(True))


def check_filled_options():
    global runtime_selected_mode
    global runtime_selected_offer_type
    global runtime_payment_method
    global runtime_selected_currency

    return runtime_selected_mode and runtime_selected_offer_type and runtime_payment_method and runtime_selected_currency


if os.environ['DEBUG'] == 'True':
    bot.polling(none_stop=True, interval=0)
