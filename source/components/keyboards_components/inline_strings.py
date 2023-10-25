from aiogram.types import InlineKeyboardButton


keyb_str_user_list = [
    InlineKeyboardButton(text="➕", callback_data=f"add_user"),
    InlineKeyboardButton(text="✏️", callback_data=f"change_user"),
    InlineKeyboardButton(text="❌", callback_data=f"delete_users")
]
keyb_str_pass_add_users_to_mi = [
    InlineKeyboardButton(text="Сохранить изменения 💾", callback_data="save_new_menu_item")
]
keyb_str_change_observers_mi = [
    InlineKeyboardButton(text="Сохранить изменения 💾", callback_data="save_change_obs_menu_item")
]
keyb_str_delete_mi = [
    InlineKeyboardButton(text="Продолжить ⏩", callback_data="next_step_delete_menu_item")
]
keyb_str_delete_u = [
    InlineKeyboardButton(text="Продолжить ⏩", callback_data="next_step_delete_users")
]
keyb_str_change_wallets_list = [
    InlineKeyboardButton(text="Сохранить изменения 💾", callback_data="save_change_wallet_list")
]
keyb_str_change_observers_ps = [
    InlineKeyboardButton(text="Сохранить изменения 💾", callback_data="save_change_observers_ps")
]

keyb_str_get_full_list_organizations = [
    InlineKeyboardButton(text="➕", callback_data=f"add_organization"),
    InlineKeyboardButton(text="❌", callback_data=f"delete_organizations")
]

keyb_str_pass_add_users_to_org = [
    InlineKeyboardButton(text="Сохранить изменения 💾", callback_data="save_new_organization")
]

keyb_str_change_observers_org = [
    InlineKeyboardButton(text="Сохранить изменения 💾", callback_data="save_change_obs_organization")
]

keyb_str_delete_org = [
    InlineKeyboardButton(text="Продолжить ⏩", callback_data="next_step_delete_organization")
]

keyb_str_get_full_list_partners = [
    InlineKeyboardButton(text="➕", callback_data=f"add_partner"),
    InlineKeyboardButton(text="❌", callback_data=f"delete_partners")
]

keyb_str_delete_partner = [
    InlineKeyboardButton(text="Продолжить ⏩", callback_data="next_step_delete_partner")
]

keyb_str_get_full_list_banks = [
    InlineKeyboardButton(text="➕", callback_data=f"add_bank"),
    InlineKeyboardButton(text="❌", callback_data=f"delete_banks")
]

keyb_str_delete_banks = [
    InlineKeyboardButton(text="Продолжить ⏩", callback_data="next_step_delete_banks")
]

keyb_str_delete_payment_accounts = [
    InlineKeyboardButton(text="Продолжить ⏩", callback_data="next_step_delete_pa")
]



