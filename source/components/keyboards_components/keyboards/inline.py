from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

keyb_empty_user_list = [
    [
        InlineKeyboardButton(text="➕", callback_data="add_user")
    ]
]
keyb_end_delete_mi = [
    [
        InlineKeyboardButton(text="Да  ✅", callback_data="end_delete_menu_item"),
        InlineKeyboardButton(text="Нет  ❌", callback_data="cancel_delete_menu_item")
    ]
]
keyb_end_delete_u = [
    [
        InlineKeyboardButton(text="Да  ✅", callback_data="end_delete_users"),
        InlineKeyboardButton(text="Нет  ❌", callback_data="cancel_delete_users")
    ]
]
keyb_choose_write_menu_sender = [
    [
        InlineKeyboardButton(text="Из подотчета", callback_data="choose_write_menu_sender:me"),
        InlineKeyboardButton(text="От ЮР Лица", callback_data="choose_write_menu_sender:org")
    ]
]
keyb_pass_check_load = [
    [
        InlineKeyboardButton(text="Пропустить  ⏩", callback_data=f"pass_check_load")
    ]
]

keyb_get_empty_list_organizations = [
    [
        InlineKeyboardButton(text="➕", callback_data=f"add_organization")
    ]
]

keyb_end_delete_org = [
    [
        InlineKeyboardButton(text="Да  ✅", callback_data="end_delete_organizations"),
        InlineKeyboardButton(text="Нет  ❌", callback_data="cancel_delete_organizations")
    ]
]

keyb_get_empty_list_partners = [
    [
        InlineKeyboardButton(text="➕", callback_data=f"add_partner")
    ]
]

keyb_end_delete_partners = [
    [
        InlineKeyboardButton(text="Да  ✅", callback_data="end_delete_partners"),
        InlineKeyboardButton(text="Нет  ❌", callback_data="cancel_delete_partners")
    ]
]

keyb_get_empty_list_banks = [
    [
        InlineKeyboardButton(text="➕", callback_data=f"add_bank")
    ]
]

keyb_end_delete_banks = [
    [
        InlineKeyboardButton(text="Да  ✅", callback_data="end_delete_banks"),
        InlineKeyboardButton(text="Нет  ❌", callback_data="cancel_delete_banks")
    ]
]

keyb_end_delete_payment_accounts = [
    [
        InlineKeyboardButton(text="Да  ✅", callback_data="end_delete_payment_accounts"),
        InlineKeyboardButton(text="Нет  ❌", callback_data="cancel_delete_payment_accounts")
    ]
]

keyb_start_manage_reports_requests = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Согласующие", callback_data="assign:conciliator"),
        InlineKeyboardButton(text="Утверждающий", callback_data="assign:approver"),
    ],
    [
        InlineKeyboardButton(text="Казначей", callback_data="assign:treasurer")
    ]
])
