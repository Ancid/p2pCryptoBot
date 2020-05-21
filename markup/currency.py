from telebot import types


def markup_currency():
    mp_currency = types.InlineKeyboardMarkup(row_width=3)
    mp_currency.add(
        types.InlineKeyboardButton(text="USD", callback_data="currency:USD"),
        types.InlineKeyboardButton(text="EUR", callback_data="currency:EUR"),
        types.InlineKeyboardButton(text="GBP", callback_data="currency:GBP"),
    )

    return mp_currency
