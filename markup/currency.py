from telebot import types

CUR_MORE = "more"
CUR_EVEN_MORE = "even_more"


def markup_currency(page):
    mp_currency = types.InlineKeyboardMarkup(row_width=3)
    if page == CUR_EVEN_MORE:
        mp_currency.add(
            types.InlineKeyboardButton(text="AED", callback_data="currency:AED"),
            types.InlineKeyboardButton(text="CHF", callback_data="currency:CHF"),
            types.InlineKeyboardButton(text="ZAR", callback_data="currency:ZAR"),
            types.InlineKeyboardButton(text="ARS", callback_data="currency:ARS"),
            types.InlineKeyboardButton(text="PKR", callback_data="currency:PKR"),
            types.InlineKeyboardButton(text="AUD", callback_data="currency:PHP"),
        )
    elif page == CUR_MORE:
        mp_currency.add(
            types.InlineKeyboardButton(text="AUD", callback_data="currency:AUD"),
            types.InlineKeyboardButton(text="GHS", callback_data="currency:GHS"),
            types.InlineKeyboardButton(text="CAD", callback_data="currency:CAD"),
            types.InlineKeyboardButton(text="more...", callback_data="currency:"+CUR_EVEN_MORE),
            types.InlineKeyboardButton(text="KES", callback_data="currency:KES"),
            types.InlineKeyboardButton(text="GBP", callback_data="currency:GBP")
        )
    else:
        mp_currency.add(
            types.InlineKeyboardButton(text="INR", callback_data="currency:INR"),
            types.InlineKeyboardButton(text="EUR", callback_data="currency:EUR"),
            types.InlineKeyboardButton(text="NGN", callback_data="currency:NGN"),
            types.InlineKeyboardButton(text="more...", callback_data="currency:"+CUR_MORE),
            types.InlineKeyboardButton(text="CNY", callback_data="currency:CNY"),
            types.InlineKeyboardButton(text="USD", callback_data="currency:USD"),

        )

    return mp_currency
