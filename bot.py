#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os

import telebot

from config import *
from markup.currency import markup_currency
from markup.paymentMethod import markup_payment_method
from markup.sameSearch import markup_same_search
from messages import *
from markup.actions import markup_actions
from markup.offerType import markup_offer_type
from offersList import make_offer_list_messages, get_offers_array, notify_subscribers
from mongo_db.MongoManager import db_add_user, db_check_subscription, db_save_offers, db_get_user, \
    db_update_subscription, db_update_user_mode, db_update_offer_type, db_update_payment_method, db_update_currency

bot = telebot.TeleBot(TOKEN)
if os.environ['DEBUG'] == 'True':
    bot.remove_webhook()
print(bot.get_me())


@bot.message_handler(content_types=['text'])
def start(message):
    bot.send_message(message.chat.id, MSG_HELLO, reply_markup=markup_actions(db_check_subscription(message.chat.id)))


@bot.callback_query_handler(func=lambda call: True)
def callback_inline_offer_type(call):
    if call.message:
        if call.data.startswith('action:search'):
            user = db_get_user(call.message.chat.id)
            db_update_user_mode(call.message.chat.id, MODE_SEARCH)
            if check_filled_options(user, MODE_SEARCH):
                # ask the same search
                message = "Would you like to search for *" + user[MODE_SEARCH]['offer_type'].upper() + \
                          "* Btc offers for *" + user[MODE_SEARCH]['payment_method'].upper() + "* in *" + \
                          user[MODE_SEARCH]['currency_code'].upper() + "*?"
                bot.send_message(call.message.chat.id, message, reply_markup=markup_same_search(), parse_mode="Markdown")
            else:
                bot.send_message(call.message.chat.id, MSG_SELECT_TYPE, reply_markup=markup_offer_type())
        if call.data.startswith('same_check:same'):
            show_offers(call.message.chat.id)
        if call.data.startswith('same_check:new'):
            bot.send_message(call.message.chat.id, MSG_SELECT_TYPE, reply_markup=markup_offer_type())
        if call.data.startswith('action:subscribe'):
            db_update_user_mode(call.message.chat.id, MODE_SUBSCRIBE)
            bot.send_message(call.message.chat.id, MSG_SELECT_TYPE, reply_markup=markup_offer_type())
        if call.data.startswith('action:unsubscribe'):
            db_update_subscription(call.message.chat.id, False)
            bot.send_message(call.message.chat.id, MSG_UNSUBSCRIBED, reply_markup=markup_actions())
        if call.data.startswith('type:'):
            db_add_user(call)
            db_update_offer_type(call.message.chat.id, call.data.split(':')[1])
            choosing_payment_method(call.message)
        if call.data.startswith('pm:'):
            db_update_payment_method(call.message.chat.id, call.data.split(':')[1])
            choosing_currency(call.message)
        if call.data.startswith('currency:'):
            user = db_get_user(call.message.chat.id)
            subscription_active = user['subscription']['active']
            active_mode = user['active_mode']
            db_update_currency(call.message.chat.id, call.data.split(':')[1])
            if check_filled_options(user, user['active_mode']):
                if active_mode == MODE_SEARCH:
                    show_offers(call.message.chat.id)
                elif active_mode == MODE_SUBSCRIBE:
                    process_subscription(call.message.chat.id)
                else:
                    bot.send_message(
                        call.message.chat.id,
                        MSG_OOPS,
                        reply_markup=markup_actions(subscription_active)
                    )
            else:
                bot.send_message(
                    call.message.chat.id,
                    MSG_OOPS,
                    reply_markup=markup_actions(subscription_active)
                )


def choosing_payment_method(message):
    try:
        bot.send_message(message.chat.id, MSG_CHOOSE_PAYMENT, reply_markup=markup_payment_method())
    except Exception as e:
        bot.reply_to(message, str(e))


def choosing_currency(message):
    try:
        bot.send_message(message.chat.id, MSG_CHOOSE_CURRENCY, reply_markup=markup_currency())
    except Exception as e:
        bot.reply_to(message, str(e))


def show_offers(chat_id):
    user = db_get_user(chat_id)
    payment_method = user['search']['payment_method']
    offer_type = user['search']['offer_type']
    currency = user['search']['currency_code']
    subscription_active = user['subscription']['active']

    bot.send_message(
        chat_id,
        "Well, you selected *" + offer_type.upper() + "* Btc offers for *" + payment_method.upper() + "* in *" + \
        currency.upper() + "*. Let\'s me check some offers for you...",
        parse_mode="Markdown"
    )
    offers = get_offers_array(offer_type, payment_method, currency)
    notify_subscribers(chat_id, offers, offer_type, payment_method, currency)

    db_save_offers(offers)
    offer_messages = make_offer_list_messages(offers, SEARCH_LIMIT)
    if len(offer_messages):
        for msg in offer_messages:
            bot.send_message(chat_id, msg, parse_mode="Markdown", disable_web_page_preview=True)
        bot.send_message(chat_id, MSG_OFFERS, reply_markup=markup_actions(db_check_subscription(chat_id)))
    else:
        bot.send_message(chat_id, MSG_OFFERS_EMPTY, reply_markup=markup_actions(subscription_active))


def process_subscription(chat_id):
    db_update_subscription(chat_id, True)
    user = db_get_user(chat_id)
    bot.send_message(
        chat_id,
        "Well, you've subscribed for *" + user[MODE_SUBSCRIBE]['offer_type'].upper() + "* Btc offers for *" + \
        user[MODE_SUBSCRIBE]['payment_method'].upper() + "* in *" + user[MODE_SUBSCRIBE]['currency_code'].upper() + \
        "*. I will notify you when new offers become available.",
        parse_mode="Markdown"
    )
    bot.send_message(chat_id, MSG_CHECK_OFFERS, reply_markup=markup_actions(True))


def check_filled_options(user, mode):
    return mode and user[mode]['offer_type'] and user[mode]['payment_method'] and user[mode]['currency_code']


if os.environ['DEBUG'] == 'True':
    bot.polling(none_stop=True, interval=0)
