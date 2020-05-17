from telebot import types


def get_currency_markup():
    markup = types.InlineKeyboardMarkup(row_width=3)
    markup.add(
        types.InlineKeyboardButton('USD'),
        types.InlineKeyboardButton('EUR'),
        types.InlineKeyboardButton('RUB')
    )

    return markup
