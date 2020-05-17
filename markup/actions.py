from telebot import types


def markup_actions(active=None):
    mp_actions = types.InlineKeyboardMarkup(row_width=2)
    if active:
        subscription_button = types.InlineKeyboardButton(text="Unsubscribe", callback_data="action_unsubscribe")
    else:
        subscription_button = types.InlineKeyboardButton(text="Subscribe", callback_data="action_subscribe")

    mp_actions.add(
        types.InlineKeyboardButton(text="Offer search", callback_data="action_search"),
        subscription_button,
    )

    return mp_actions
