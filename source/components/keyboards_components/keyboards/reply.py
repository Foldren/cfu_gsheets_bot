from aiogram.types import KeyboardButton

keyb_start_admin = [
    [
        KeyboardButton(text="Сотрудники"),
        KeyboardButton(text="ЮР Лица"),
        KeyboardButton(text="Категории"),

    ],
    [
        KeyboardButton(text="Интеграция с банками"),
        KeyboardButton(text="Отчеты"),
        KeyboardButton(text="Поддержка"),
    ],
    [
        KeyboardButton(text="Алгоритм запроса в подотчет"),
    ],
    [
        KeyboardButton(text="Режим: Админ 👨‍💼"),
        KeyboardButton(text="📩"),
    ]
]
keyb_operation_integration_banks = [
    [
        KeyboardButton(text="Контрагенты"),
        KeyboardButton(text="Банки и расчётные счета"),
    ],
    [
        KeyboardButton(text="⬅️ Назад в главное меню")
    ]
]
keyb_start_user = [
    [
        KeyboardButton(text="Операция с категориями"),
        KeyboardButton(text="Операция с подотчетами"),
    ],
    [
        KeyboardButton(text="Кошельки"),
        KeyboardButton(text="Отчеты"),
        KeyboardButton(text="Поддержка"),
    ],
    [
        KeyboardButton(text="📩"),
    ]
]
keyb_start_user_admin = [
    [
        KeyboardButton(text="Операция с категориями"),
        KeyboardButton(text="Операция с подотчетами")

    ],
    [
        KeyboardButton(text="Кошельки"),
        KeyboardButton(text="Отчеты"),
        KeyboardButton(text="Поддержка")
    ],
    [
        KeyboardButton(text="Режим: Юзер 🙎‍♂️"),
        KeyboardButton(text="📩"),
    ]
]
keyb_operation_under_stats = [
    [
        KeyboardButton(text="Выдача в подотчет"),
        KeyboardButton(text="Возврат подотчета")
    ],
    [
        KeyboardButton(text="Остаток в подотчете"),
        KeyboardButton(text="Запрос денег в подотчет"),
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
