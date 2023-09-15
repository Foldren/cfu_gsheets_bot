from aiogram.types import InlineKeyboardButton

keyb_str_user_list = [
    InlineKeyboardButton(text="➕", callback_data=f"add_user"),
    InlineKeyboardButton(text="✏️", callback_data=f"change_user"),
    InlineKeyboardButton(text="❌", callback_data=f"delete_users")
]
keyb_str_pass_add_users_to_mi = [
    InlineKeyboardButton(text="Сохранить изменения ✅", callback_data="save_new_menu_item")
]
keyb_str_change_observers_mi = [
    InlineKeyboardButton(text="Сохранить изменения ✅", callback_data="save_change_obs_menu_item")
]
keyb_str_delete_mi = [
    InlineKeyboardButton(text="Продолжить ⏩", callback_data="next_step_delete_menu_item")
]
keyb_str_delete_u = [
    InlineKeyboardButton(text="Продолжить ⏩", callback_data="next_step_delete_users")
]
keyb_str_change_wallets_list = [
    InlineKeyboardButton(text="Сохранить изменения ✅", callback_data="save_change_wallet_list")
]
keyb_str_change_observers_ps = [
    InlineKeyboardButton(text="Сохранить изменения ✅", callback_data="save_change_observers_ps")
]
