from telebot import types


def markup_actions(active=None):
    if active == True:
        subscription_button = types.InlineKeyboardButton(text="Unsubscribe", callback_data="action:unsubscribe")
    else:
        subscription_button = types.InlineKeyboardButton(text="Subscribe", callback_data="action:subscribe")

    mp_actions = types.InlineKeyboardMarkup(row_width=2)
    mp_actions.add(
        types.InlineKeyboardButton(text="Offer search", callback_data="action:search"),
        subscription_button,
    )

    return mp_actions
