from markup.actionSearch import markup_search_actions
from markup.currency import markup_currency
from markup.paymentMethod import markup_payment_method
from markup.paymentMethodGroup import markup_payment_method_group

from app import db_queries
from app.messages import (
    MSG_CHOOSE_CURRENCY,
    MSG_CHOOSE_PAYMENT,
    MSG_OFFERS,
    MSG_OFFERS_EMPTY,
    MSG_OOPS,
)
from app.offers import get_offers_array, make_offer_list_messages, notify_subscribers
from app.settings import SEARCH_LIMIT


def check_filled_options(user, mode):
    return (
        mode
        and (user[mode]["offer_type"] or False)
        and (user[mode]["payment_method"] or False)
        and (user[mode]["currency_code"] or False)
    )


async def show_offers(client, chat_id, paginated=False, reset_page=False):
    from app.telegram import bot

    if reset_page:
        await db_queries.update_search_page(chat_id, 1)
    user = await db_queries.get_user(chat_id)
    payment_method = user["search"]["payment_method"]
    offer_type = user["search"]["offer_type"]
    currency = user["search"]["currency_code"]
    subscription_active = user["subscription"]["active"]
    await bot.send_message(
        chat_id,
        "Great! You’ve selected *"
        + offer_type.upper()
        + "* Btc offers for *"
        + payment_method.upper()
        + "* in *"
        + currency.upper()
        + "*. Let me check if I can find some offers for you...",
        parse_mode="Markdown",
    )

    if paginated is False:
        await db_queries.log_search(user)

    offers = await get_offers_array(client, offer_type, payment_method, currency)
    if offers is None:
        await bot.send_message(
            chat_id,
            "Oops. Looks like Paxful doesn't respond for now. Try again later",
            parse_mode="Markdown",
            disable_web_page_preview=True,
        )
    else:
        await notify_subscribers(chat_id, offers, offer_type, payment_method, currency)
        await db_queries.save_offers(offers)

        page = False
        if paginated and "page" in user["search"]:
            page = int(user["search"]["page"])
            await db_queries.update_search_page(chat_id, page + 1)

        offer_messages = make_offer_list_messages(offers, SEARCH_LIMIT, page)
        if len(offer_messages):
            for msg in offer_messages:
                await bot.send_message(
                    chat_id, msg, parse_mode="Markdown", disable_web_page_preview=True
                )
            paginate = len(offers) > SEARCH_LIMIT * (page + 1)
            is_active = await db_queries.check_subscription(chat_id)
            await bot.send_message(
                chat_id,
                MSG_OFFERS,
                reply_markup=markup_search_actions(is_active, paginate),
            )
        else:
            await bot.send_message(
                chat_id,
                MSG_OFFERS_EMPTY,
                reply_markup=markup_search_actions(subscription_active),
            )


async def choosing_payment_method_group(message):
    from app.telegram import bot

    try:
        await bot.send_message(
            message.chat.id,
            MSG_CHOOSE_PAYMENT,
            reply_markup=markup_payment_method_group(),
        )
    except Exception as e:
        print("choosing_payment_method_group error: " + str(e))
        await bot.send_message(message, MSG_OOPS)


async def choosing_payment_method(message, group):
    from app.telegram import bot

    try:
        await bot.edit_message_reply_markup(
            message.chat.id,
            message.message_id,
            reply_markup=markup_payment_method(group),
        )
    except Exception as e:
        print("choosing_payment_method error: " + str(e))
        await bot.send_message(message, MSG_OOPS)


async def choosing_currency(message, page=False):
    from app.telegram import bot

    try:
        if page:
            await bot.edit_message_reply_markup(
                message.chat.id, message.message_id, reply_markup=markup_currency(page)
            )
        else:
            await bot.send_message(
                message.chat.id, MSG_CHOOSE_CURRENCY, reply_markup=markup_currency(page)
            )
    except Exception as e:
        print("choosing_currency error: " + str(e))
        bot.send_message(message, MSG_OOPS)
