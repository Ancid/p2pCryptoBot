import asyncio

import aiogram
import httpx
from aiogram.dispatcher.webhook import get_new_configured_app
from aiogram.types import ContentType, Message
from aiogram.utils.executor import start_webhook
from fastapi import FastAPI

from config import APP_NAME, TOKEN, WEBHOOK_PATH, WEBAPP_HOST, WEBAPP_PORT, WEBHOOK_URL
from markup.currency import CUR_EVEN_MORE, CUR_MORE
from markup.offerType import markup_offer_type
from markup.sameSearch import markup_same_search

from app import db_queries, settings
from app.actions import markup_actions
from app.handler_functions import (
    check_filled_options,
    choosing_currency,
    choosing_payment_method,
    choosing_payment_method_group,
    show_offers,
)
from app.messages import MSG_HELLO, MSG_OOPS, MSG_SELECT_TYPE, MSG_UNSUBSCRIBED
from app.settings import MODE_SEARCH, MODE_SUBSCRIBE
from app.subscriptions import process_subscription

bot = aiogram.Bot(token=settings.TOKEN)
dp = aiogram.Dispatcher(bot)


@dp.message_handler(content_types=ContentType.TEXT)
async def start(message: Message):
    await db_queries.add_user(message.from_user.id, message.from_user.username)
    is_active = await db_queries.check_subscription(message.chat.id)
    await bot.send_message(
        message.chat.id, MSG_HELLO, reply_markup=markup_actions(is_active)
    )


# @dp.callback_query_handler(func=lambda call: True)
@dp.callback_query_handler(lambda c: c.data)
async def callback_inline_offer_type(call):
    if call.message:
        if call.data.startswith("action:search"):
            user = await db_queries.get_user(call.message.chat.id)
            await db_queries.update_user_mode(call.message.chat.id, MODE_SEARCH)
            if check_filled_options(user, MODE_SEARCH):
                # ask the same search
                message = (
                    "Would you like to search for *"
                    + user[MODE_SEARCH]["offer_type"].upper()
                    + "* Btc offers for *"
                    + user[MODE_SEARCH]["payment_method"].upper()
                    + "* in *"
                    + user[MODE_SEARCH]["currency_code"].upper()
                    + "*?"
                )
                await bot.send_message(
                    call.message.chat.id,
                    message,
                    reply_markup=markup_same_search(),
                    parse_mode="Markdown",
                )
            else:
                await bot.send_message(
                    call.message.chat.id,
                    MSG_SELECT_TYPE,
                    reply_markup=markup_offer_type(),
                )

        client = httpx.AsyncClient()

        if call.data.startswith("action:paginate_search"):
            await show_offers(client, call.message.chat.id, True)
        if call.data.startswith("same_check:same"):
            await show_offers(client, call.message.chat.id, False, True)
        if call.data.startswith("same_check:new"):
            await bot.send_message(
                call.message.chat.id, MSG_SELECT_TYPE, reply_markup=markup_offer_type()
            )
        if call.data.startswith("action:subscribe"):
            await db_queries.update_user_mode(call.message.chat.id, MODE_SUBSCRIBE)
            await bot.send_message(
                call.message.chat.id, MSG_SELECT_TYPE, reply_markup=markup_offer_type()
            )
        if call.data.startswith("action:unsubscribe"):
            await db_queries.update_subscription(call.message.chat.id, False)
            await db_queries.log_deactive_subscription(call.message.chat.id)
            await bot.send_message(
                call.message.chat.id, MSG_UNSUBSCRIBED, reply_markup=markup_actions()
            )
        if call.data.startswith("type:"):
            await db_queries.update_offer_type(
                call.message.chat.id, call.data.split(":")[1]
            )
            await choosing_payment_method_group(call.message)
        if call.data.startswith("pm_group:"):
            await choosing_payment_method(call.message, call.data.split(":")[1])
        if call.data.startswith("pm:"):
            await db_queries.update_payment_method(
                call.message.chat.id, call.data.split(":")[1]
            )
            await choosing_currency(call.message)
        if call.data.startswith("currency:"):
            pm = call.data.split(":")[1]
            if pm in [CUR_MORE, CUR_EVEN_MORE]:
                await choosing_currency(call.message, pm)
            else:
                user = await db_queries.get_user(call.message.chat.id)
                subscription_active = user["subscription"]["active"]
                active_mode = user["active_mode"]
                # Because should wait for currency update
                if check_filled_options(
                    await db_queries.update_currency(
                        call.message.chat.id, call.data.split(":")[1]
                    ),
                    user["active_mode"],
                ):
                    if active_mode == MODE_SEARCH:
                        await show_offers(client, call.message.chat.id, False, True)
                    elif active_mode == MODE_SUBSCRIBE:
                        await process_subscription(call.message.chat.id, client)
                    else:
                        await bot.send_message(
                            call.message.chat.id,
                            MSG_OOPS,
                            reply_markup=markup_actions(subscription_active),
                        )
                else:
                    await bot.send_message(
                        call.message.chat.id,
                        MSG_OOPS,
                        reply_markup=markup_actions(subscription_active),
                    )
        if call.data.startswith("search_more:"):
            user = await db_queries.get_user(call.message.chat.id)
            # Because should wait for currency update
            if check_filled_options(user, user["active_mode"]):
                await show_offers(client, call.message.chat.id, True)


# def use_with_debug(app: FastAPI):
#     async def start_polling():
#         app.state.polling = asyncio.create_task(dp.start_polling(timeout=1))
#
#     async def stop_polling():
#         if app.state.polling:
#             app.state.polling.cancel()
#             await app.state.polling
#
#     if settings.APP_DEBUG:
#         app.add_event_handler("startup", start_polling)
#         app.add_event_handler("shutdown", stop_polling)


# async def on_startup(dp):
#     await bot.set_webhook(WEBHOOK_URL)
#     # insert code here to run it after start
#
#     dp.register_message_handler(start, commands=['start'])
#     dp.register_message_handler(callback_inline_offer_type, state='*')

# async def on_shutdown(dp):
#
#     # Remove webhook (not acceptable in some cases)
#     await bot.delete_webhook()
#
#     # Close DB connection (if used)
#     await dp.storage.close()
#     await dp.storage.wait_closed()

# if __name__ == '__main__':
#     # app = get_new_configured_app(dispatcher=dp, path=WEBHOOK_PATH)
#     # app.on_startup.append(on_startup)
#     #
#     start_webhook(
#         dispatcher=dp,
#         webhook_path=WEBHOOK_PATH,
#         on_startup=on_startup,
#         on_shutdown=on_shutdown,
#         skip_updates=True,
#         host=WEBAPP_HOST,
#         port=WEBAPP_PORT,
#     )
