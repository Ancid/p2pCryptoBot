from telebot import types

PMG_GIFT_CARD = "gift-cards"
PMG_ONLINE_WALLET = "online-transfers"
PMG_BANK_TRANSFER = "bank-transfers"
PMG_CASH = "cash-deposits"
PMG_DEBIT_CREDIT = "debitcredit-cards"


def markup_payment_method_group():
    payment_method_groups = {
        "Debit/Credit Cards": PMG_DEBIT_CREDIT,
        "Cash": PMG_CASH,
        "Online wallets": PMG_ONLINE_WALLET,
        "Bank Transfers": PMG_BANK_TRANSFER,
        "Gift cards": PMG_GIFT_CARD,
    }

    mk_payment_method = types.InlineKeyboardMarkup(row_width=3)
    mk_payment_method.add(
        *[types.InlineKeyboardButton(text=name, callback_data='pm_group:' + payment_method_groups[name]) for name in
          payment_method_groups]
    )

    return mk_payment_method
