from telebot import types


def markup_payment_method():
    payment_methods = {
        # "Western Union": "western-union",
        "SEPA": "sepa",
        "PayPal": "paypal",
        "Bank Transfer": "bank-transfer",
        "Amazon GC": "amazon-gift-card",
        "Revolut": "revolut",
        "Cash deposit": "cash-deposit-to-bank",
    }

    mk_payment_method = types.InlineKeyboardMarkup(row_width=3)
    mk_payment_method.add(
        *[types.InlineKeyboardButton(text=name, callback_data='pm:' + payment_methods[name]) for name in
          payment_methods]
    )

    return mk_payment_method
