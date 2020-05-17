from telebot import types


def markup_payment_method():
    payment_methods = {
        "Bank Transfer": "bank-transfer",
        "Western Union": "western-union",
        "SEPA": "sepa",
        "PayPal": "paypal",
        "Revolut": "revolut",
        "Amazon GC": "amazon-gift-card",
    }

    mk_payment_method = types.InlineKeyboardMarkup(row_width=3)
    mk_payment_method.add(
        *[types.InlineKeyboardButton(text=name, callback_data='pm_' + payment_methods[name]) for name in
          payment_methods]
    )

    return mk_payment_method
