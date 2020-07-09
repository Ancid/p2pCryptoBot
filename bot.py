#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os

import telebot

from config import *
from markup.actionSearch import markup_search_actions
from markup.currency import markup_currency, CUR_MORE
from markup.paymentMethod import markup_payment_method, PAYMENT_METHODS
from markup.paymentMethodGroup import markup_payment_method_group
from markup.sameSearch import markup_same_search
from messages import *
from markup.actions import markup_actions
from markup.offerType import markup_offer_type
from offersList import make_offer_list_messages, get_offers_array, notify_subscribers
from mongo_db.MongoManager import db_add_user, db_check_subscription, db_save_offers, db_get_user, \
    db_update_subscription, db_update_user_mode, db_update_offer_type, db_update_payment_method, db_update_currency, \
    db_log_deactive_subscription, db_log_active_subscription, db_update_search_page

bot = telebot.TeleBot(TOKEN)
if os.environ['DEBUG'] == 'True':
    bot.remove_webhook()
print(bot.get_me())


@bot.message_handler(content_types=['text'])
def start(message):
    db_add_user(message.from_user.id, message.from_user.username)
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
        if call.data.startswith('action:paginate_search'):
            show_offers(call.message.chat.id, True)
        if call.data.startswith('same_check:same'):
            show_offers(call.message.chat.id, False, True)
        if call.data.startswith('same_check:new'):
            bot.send_message(call.message.chat.id, MSG_SELECT_TYPE, reply_markup=markup_offer_type())
        if call.data.startswith('action:subscribe'):
            db_update_user_mode(call.message.chat.id, MODE_SUBSCRIBE)
            bot.send_message(call.message.chat.id, MSG_SELECT_TYPE, reply_markup=markup_offer_type())
        if call.data.startswith('action:unsubscribe'):
            db_update_subscription(call.message.chat.id, False)
            db_log_deactive_subscription(call.message.chat.id)
            bot.send_message(call.message.chat.id, MSG_UNSUBSCRIBED, reply_markup=markup_actions())
        if call.data.startswith('type:'):
            db_update_offer_type(call.message.chat.id, call.data.split(':')[1])
            choosing_payment_method_group(call.message)
        if call.data.startswith('pm_group:'):
            choosing_payment_method(call.message, call.data.split(':')[1])
        if call.data.startswith('pm:'):
            db_update_payment_method(call.message.chat.id, call.data.split(':')[1])
            choosing_currency(call.message)
        if call.data.startswith('currency:'):
            pm = call.data.split(':')[1]
            if pm == CUR_MORE:
                choosing_currency(call.message, True)
            else:
                user = db_get_user(call.message.chat.id)
                subscription_active = user['subscription']['active']
                active_mode = user['active_mode']
                # Because should wait for currency update
                if check_filled_options(
                        db_update_currency(call.message.chat.id, call.data.split(':')[1]),
                        user['active_mode']
                ):
                    if active_mode == MODE_SEARCH:
                        show_offers(call.message.chat.id, False, True)
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
        if call.data.startswith('search_more:'):
            user = db_get_user(call.message.chat.id)
            # Because should wait for currency update
            if check_filled_options(user, user['active_mode']):
                show_offers(call.message.chat.id, True)

def choosing_payment_method_group(message):
    try:
        bot.send_message(message.chat.id, MSG_CHOOSE_PAYMENT, reply_markup=markup_payment_method_group())
    except Exception as e:
        bot.reply_to(message, str(e))


def choosing_payment_method(message, group):
    try:
        bot.edit_message_reply_markup(message.chat.id, message.message_id, reply_markup=markup_payment_method(group))
    except Exception as e:
        bot.reply_to(message, str(e))


def choosing_currency(message, second=False):
    try:
        if second:
            bot.edit_message_reply_markup(message.chat.id, message.message_id, reply_markup=markup_currency(second))
        else:
            bot.send_message(message.chat.id, MSG_CHOOSE_CURRENCY, reply_markup=markup_currency(second))
    except Exception as e:
        bot.reply_to(message, str(e))


def show_offers(chat_id, paginated=False, reset_page=False):
    if reset_page:
        db_update_search_page(chat_id, 1)
    user = db_get_user(chat_id)
    payment_method = user['search']['payment_method']
    offer_type = user['search']['offer_type']
    currency = user['search']['currency_code']
    subscription_active = user['subscription']['active']

    bot.send_message(
        chat_id,
        "Great! You’ve selected *" + offer_type.upper() + "* Btc offers for *" + payment_method.upper() + "* in *" + \
        currency.upper() + "*. Let me check if I can find some offers for you...",
        parse_mode="Markdown"
    )
    offers = get_offers_array(offer_type, payment_method, currency)
    if offers is None:
        bot.send_message(
            chat_id,
            "Oops. Looks like Paxful doesn't respond for now. Try again later",
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
    else:
        notify_subscribers(chat_id, offers, offer_type, payment_method, currency)
        db_save_offers(offers)

        page = False
        if paginated and 'page' in user['search']:
            page = int(user['search']['page'])
            db_update_search_page(chat_id, page+1)

        offer_messages = make_offer_list_messages(offers, SEARCH_LIMIT, page)
        if len(offer_messages):
            for msg in offer_messages:
                bot.send_message(chat_id, msg, parse_mode="Markdown", disable_web_page_preview=True)
            paginate = len(offers) > SEARCH_LIMIT * (page + 1)
            bot.send_message(
                chat_id,
                MSG_OFFERS,
                reply_markup=markup_search_actions(db_check_subscription(chat_id), paginate)
            )
        else:
            bot.send_message(chat_id, MSG_OFFERS_EMPTY, reply_markup=markup_search_actions(subscription_active))


def process_subscription(chat_id):
    db_update_subscription(chat_id, True)
    user = db_get_user(chat_id)
    db_log_active_subscription(user)
    bot.send_message(
        chat_id,
        "Awesome!  I’ll let you know when new *" + user[MODE_SUBSCRIBE]['offer_type'].upper() + "* Btc offers for *" + \
        user[MODE_SUBSCRIBE]['payment_method'].upper() + "* in *" + user[MODE_SUBSCRIBE]['currency_code'].upper() + \
        "* pop up.",
        parse_mode="Markdown"
    )
    bot.send_message(chat_id, MSG_CHECK_OFFERS, reply_markup=markup_actions(True))


def check_filled_options(user, mode):
    return mode and (user[mode]['offer_type'] or False) \
           and (user[mode]['payment_method'] or False) and (user[mode]['currency_code'] or False)


if os.environ['DEBUG'] == 'True':
    bot.polling(none_stop=True, interval=0)
