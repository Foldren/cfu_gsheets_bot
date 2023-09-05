from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton


# Клавиатуры -----------------------------------------------------------------------------------------------------------

keyb_start_admin = [
    [
        KeyboardButton(text="Меню"),
        KeyboardButton(text="Сотрудники")
    ]
]

keyb_start_user = [
    [
        KeyboardButton(text="Новая запись 🖊")
    ]
]


keyb_empty_user_list = [
    [
        InlineKeyboardButton(text="➕", callback_data="add_user")
    ]
]

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

keyb_end_delete_mi = [
    [
        InlineKeyboardButton(text="Да  ✅", callback_data="end_delete_menu_item"),
        InlineKeyboardButton(text="Нет  ❌", callback_data="cancel_delete_menu_item")
    ]
]

keyb_str_delete_u = [
    InlineKeyboardButton(text="Продолжить ⏩", callback_data="next_step_delete_users")
]

keyb_end_delete_u = [
    [
        InlineKeyboardButton(text="Да  ✅", callback_data="end_delete_users"),
        InlineKeyboardButton(text="Нет  ❌", callback_data="cancel_delete_users")
    ]
]


# Конфигурации ---------------------------------------------------------------------------------------------------------

cf_key_start_admin = ReplyKeyboardMarkup(
    keyboard=keyb_start_admin,
    resize_keyboard=True,  # меняем размер клавиатуры
)

cf_keyb_start_user = ReplyKeyboardMarkup(
    keyboard=keyb_start_user,
    resize_keyboard=True,  # меняем размер клавиатуры
)


cf_key_end_delete_mi = InlineKeyboardMarkup(inline_keyboard=keyb_end_delete_mi)

cf_key_end_delete_u = InlineKeyboardMarkup(inline_keyboard=keyb_end_delete_u)

cf_keyb_empty_user_list = InlineKeyboardMarkup(inline_keyboard=keyb_empty_user_list)





