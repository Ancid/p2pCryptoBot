from telebot import types

CUR_MORE = "more"


def markup_currency(second):
    mp_currency = types.InlineKeyboardMarkup(row_width=3)
    if second:
        mp_currency.add(
            types.InlineKeyboardButton(text="GHS", callback_data="currency:AED"),
            types.InlineKeyboardButton(text="GHS", callback_data="currency:GHS"),
            types.InlineKeyboardButton(text="GHS", callback_data="currency:GBP"),
            types.InlineKeyboardButton(text="CHF", callback_data="currency:CHF"),
            types.InlineKeyboardButton(text="INR", callback_data="currency:INR"),
            types.InlineKeyboardButton(text="ARS", callback_data="currency:ARS"),
        )
    else:
        mp_currency.add(
            types.InlineKeyboardButton(text="GBP", callback_data="currency:GBP"),
            types.InlineKeyboardButton(text="EUR", callback_data="currency:EUR"),
            types.InlineKeyboardButton(text="CAD", callback_data="currency:CAD"),
            types.InlineKeyboardButton(text="more...", callback_data="currency:"+CUR_MORE),
            types.InlineKeyboardButton(text="NGN", callback_data="currency:NGN"),
            types.InlineKeyboardButton(text="USD", callback_data="currency:USD"),
        )

    return mp_currency
