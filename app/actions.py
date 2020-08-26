from aiogram import types


def markup_actions(active=None):
    if active:
        mp_actions = types.InlineKeyboardMarkup(row_width=3)
        mp_actions.add(
            types.InlineKeyboardButton(
                text="Change subscription", callback_data="action:subscribe"
            ),
            types.InlineKeyboardButton(
                text="Unsubscribe", callback_data="action:unsubscribe"
            ),
        )
    else:
        mp_actions = types.InlineKeyboardMarkup(row_width=2)
        mp_actions.add(
            types.InlineKeyboardButton(
                text="Subscribe", callback_data="action:subscribe"
            )
        )

    mp_actions.add(
        types.InlineKeyboardButton(text="Offer search", callback_data="action:search")
    )

    return mp_actions
