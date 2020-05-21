from telebot import types


def markup_subscription():
    mp_actions = types.InlineKeyboardMarkup(row_width=2)
    subscription_button = types.InlineKeyboardButton(text="Unsubscribe", callback_data="action_unsubscribe")

    mp_actions.add(
        types.InlineKeyboardButton(text="Change subscription", callback_data="action_subscribe"),
        subscription_button,
    )

    return mp_actions
