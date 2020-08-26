from aiogram import types


def markup_subscription():
    mp_actions = types.InlineKeyboardMarkup(row_width=2)
    subscription_button = types.InlineKeyboardButton(text="Unsubscribe", callback_data="action:unsubscribe")

    mp_actions.add(
        types.InlineKeyboardButton(text="Change subscription", callback_data="action:subscribe"),
        subscription_button,
    )

    mp_actions.add(
        types.InlineKeyboardButton(text="Offer search", callback_data="action:search"),
        subscription_button,
    )

    return mp_actions
