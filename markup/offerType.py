from telebot import types


def markup_offer_type():
    mk_offer_type = types.InlineKeyboardMarkup(row_width=2)
    mk_offer_type.add(
        types.InlineKeyboardButton(text="Buy", callback_data="type_buy"),
        types.InlineKeyboardButton(text="Sell", callback_data="type_sell"),
    )

    return mk_offer_type
