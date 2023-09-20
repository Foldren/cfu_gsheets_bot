from aiogram.types import KeyboardButton

keyb_start_admin = [
    [
        KeyboardButton(text="Сотрудники"),
        KeyboardButton(text="Отчеты"),
    ],
    [
        KeyboardButton(text="Категории"),
        KeyboardButton(text="ЮР Лица"),
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
        KeyboardButton(text="Остаток в подотчете")
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
