PMG_GIFT_CARD = "gift-cards"
PMG_ONLINE_WALLET = "online-transfers"
PMG_BANK_TRANSFER = "bank-transfers"
PMG_CASH = "cash-deposits"
PMG_DEBIT_CREDIT = "debitcredit-cards"

PAYMENT_METHODS = {
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
        "Cash in person": "cash-in-person",
    },
    PMG_DEBIT_CREDIT: {
        "Bluebird American Express": "bluebird-american-express",
        "ANY Credit/Debit Card": "any-creditdebit-card",
        "Green Dot Card": "green-dot-card",
    },
}
