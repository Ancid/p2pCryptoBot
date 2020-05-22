from telebot import types


def markup_actions(active=None):
    mp_actions = types.InlineKeyboardMarkup(row_width=3)
    if active == True:
        mp_actions.add(
            types.InlineKeyboardButton(text="Offer search", callback_data="action:search"),
            types.InlineKeyboardButton(text="Change subscription", callback_data="action:subscribe"),
        )
    else:
        mp_actions.add(types.InlineKeyboardButton(text="Subscribe", callback_data="action:subscribe"))

    mp_actions.add(types.InlineKeyboardButton(text="Offer search", callback_data="action:search"))

    return mp_actions
