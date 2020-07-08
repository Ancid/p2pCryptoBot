from telebot import types

from markup.paymentMethodGroup import *


def markup_payment_method(group):
    payment_methods = {
        PMG_GIFT_CARD: {
            "Google Play GC": "google-play-gift-card",
            "iTunes GC": "itunes-gift-card",
            "Steam Wallet GC": "steam-wallet-gift-card",
            "OneVanilla GC": "onevanilla-visamastercard-gift-card",
            "eBay GC": "ebay-gift-card",
            "Amazon GC": "amazon-gift-card",
        },
        PMG_ONLINE_WALLET: {
            "Chipper Cash": "chipper-cash",
            "Cash app": "cash-app",
            "PayPal": "paypal",
            "MTN Mobile Money": "mtn-mobile-money",
            "M-Pesa": "mpesa",
            "Alipay": "alipay",
        },
        PMG_BANK_TRANSFER: {
            "IMPS Transfer": "imps-transfer",
            "Domestic wire transfer": "domestic-wire-transfer",
            "Bank Transfer": "bank-transfer",
        },
        PMG_CASH: {
            "Cash By Mail": "cash-by-mail",
            "Western Union": "western-union",
            "Cash deposit": "cash-deposit-to-bank",
        },
        PMG_DEBIT_CREDIT: {
            "Bluebird American Express": "bluebird-american-express",
            "ANY Credit/Debit Card": "any-creditdebit-card",
            "Green Dot Card": "green-dot-card",
        }
    }

    mk_payment_method = types.InlineKeyboardMarkup(row_width=3)
    mk_payment_method.add(
        *[types.InlineKeyboardButton(text=name, callback_data='pm:' + payment_methods[group][name]) for name in
          payment_methods[group]]
    )

    return mk_payment_method
