from telebot import types


def markup_same_search():
    mk_offer_type = types.InlineKeyboardMarkup(row_width=2)
    mk_offer_type.add(
        types.InlineKeyboardButton(text="Yes", callback_data="same_check:same"),
        types.InlineKeyboardButton(text="New search", callback_data="same_check:new"),
    )

    return mk_offer_type
