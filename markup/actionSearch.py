from telebot import types


def markup_search_actions(active=None, paginate=False):
    mp_actions = types.InlineKeyboardMarkup(row_width=2)
    if active == True:
        mp_actions.add(
            types.InlineKeyboardButton(text="Change subscription", callback_data="action:subscribe"),
            types.InlineKeyboardButton(text="Unsubscribe", callback_data="action:unsubscribe")
        )
    else:
        mp_actions.add(types.InlineKeyboardButton(text="Subscribe", callback_data="action:subscribe"))

    if paginate:
        mp_actions.add(
            types.InlineKeyboardButton(text="Load more", callback_data="action:paginate_search"),
            types.InlineKeyboardButton(text="Offer search", callback_data="action:search")
        )
    else:
        mp_actions.add(types.InlineKeyboardButton(text="Offer search", callback_data="action:search"))


    return mp_actions
