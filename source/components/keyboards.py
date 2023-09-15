from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton


# ReplyKeyboards -------------------------------------------------------------------------------------------------------

keyb_start_admin = [
    [
        KeyboardButton(text="Меню"),
        KeyboardButton(text="Сотрудники"),
        KeyboardButton(text="Отчеты"),
    ],
    [
        KeyboardButton(text="Режим: Админ 👨‍💼")
    ]
]

keyb_start_user = [
    [
        KeyboardButton(text="Операция с категориями"),
        KeyboardButton(text="Операция с подотчетами")
    ],
    [
        KeyboardButton(text="Кошельки"),
        KeyboardButton(text="Отчеты")
    ]
]

keyb_start_user_admin = [
    [
        KeyboardButton(text="Операция с категориями"),
        KeyboardButton(text="Операция с подотчетами")

    ],
    [
        KeyboardButton(text="Кошельки"),
        KeyboardButton(text="Отчеты")
    ],
    [
        KeyboardButton(text="Режим: Юзер 🙎‍♂️")
    ]
]

keyb_operation_under_stats = [
    [
        KeyboardButton(text="Выдача в подотчет"),
        KeyboardButton(text="Возврат подотчета")
    ],
    [
        KeyboardButton(text="⬅️ Назад в главное меню")
    ]
]

keyb_wallets = [
    [
        KeyboardButton(text="Перевод на кошелек"),
        KeyboardButton(text="Изменить кошельки")
    ],
    [
        KeyboardButton(text="⬅️ Назад в главное меню")
    ]
]


# InlineKeyboards ------------------------------------------------------------------------------------------------------

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


# InlineStringsForKeyboards --------------------------------------------------------------------------------------------

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


# ReplyButton конфигурации ---------------------------------------------------------------------------------------------

cf_keyb_start_admin = ReplyKeyboardMarkup(
    keyboard=keyb_start_admin,
    resize_keyboard=True,  # меняем размер клавиатуры
)

cf_keyb_start_user = ReplyKeyboardMarkup(
    keyboard=keyb_start_user,
    resize_keyboard=True,  # меняем размер клавиатуры
)

cf_keyb_start_user_admin = ReplyKeyboardMarkup(
    keyboard=keyb_start_user_admin,
    resize_keyboard=True,  # меняем размер клавиатуры
)

cf_keyb_operation_under_stats = ReplyKeyboardMarkup(
    keyboard=keyb_operation_under_stats,
    resize_keyboard=True,  # меняем размер клавиатуры
)

cf_keyb_wallets = ReplyKeyboardMarkup(
    keyboard=keyb_wallets,
    resize_keyboard=True,  # меняем размер клавиатуры
)


# InlineButton конфигурации --------------------------------------------------------------------------------------------

cf_key_end_delete_mi = InlineKeyboardMarkup(inline_keyboard=keyb_end_delete_mi)

cf_key_end_delete_u = InlineKeyboardMarkup(inline_keyboard=keyb_end_delete_u)

cf_keyb_empty_user_list = InlineKeyboardMarkup(inline_keyboard=keyb_empty_user_list)

cf_keyb_choose_write_menu_sender = InlineKeyboardMarkup(inline_keyboard=keyb_choose_write_menu_sender)







