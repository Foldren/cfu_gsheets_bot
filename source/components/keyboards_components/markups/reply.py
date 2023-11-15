from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


keyb_markup_start_admin = ReplyKeyboardMarkup(
    resize_keyboard=True,  # меняем размер клавиатуры
    input_field_placeholder='Главное меню админа',
    keyboard=[
        [
            KeyboardButton(text="Сотрудники"),
            KeyboardButton(text="ЮР Лица"),
            KeyboardButton(text="Категории"),

        ],
        [
            KeyboardButton(text="Интеграция с банками"),
            KeyboardButton(text="Управление отчетами"),
            KeyboardButton(text="Поддержка"),
        ],
        [
            KeyboardButton(text="Назначение ролей"),
        ],
        [
            KeyboardButton(text="Режим: Админ 👨‍💼"),
            KeyboardButton(text="📩"),
        ]
    ]
)
keyb_markup_start_user = ReplyKeyboardMarkup(
    resize_keyboard=True,  # меняем размер клавиатуры
    input_field_placeholder='Главное меню юзера',
    keyboard=[
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
)
keyb_markup_start_user_admin = ReplyKeyboardMarkup(
    resize_keyboard=True,  # меняем размер клавиатуры
    input_field_placeholder='Главное меню юзера',
    keyboard=[
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
)
keyb_markup_operation_under_stats = ReplyKeyboardMarkup(
    resize_keyboard=True,  # меняем размер клавиатуры
    input_field_placeholder='Меню операций с подотчетами',
    keyboard=[
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
)
keyb_markup_wallets = ReplyKeyboardMarkup(
    resize_keyboard=True,  # меняем размер клавиатуры
    input_field_placeholder='Меню управления кошельками',
    keyboard=[
        [
            KeyboardButton(text="Перевод на кошелек"),
            KeyboardButton(text="Изменение списка кошельков")
        ],
        [
            KeyboardButton(text="⬅️ Назад в главное меню")
        ]
    ],
)
keyb_markup_operation_integration_banks = ReplyKeyboardMarkup(
    resize_keyboard=True,  # меняем размер клавиатуры
    input_field_placeholder='Меню интеграции с банками',
    keyboard=[
        [
            KeyboardButton(text="Контрагенты"),
            KeyboardButton(text="Банки и расчётные счета"),
        ],
        [
            KeyboardButton(text="⬅️ Назад в главное меню")
        ]
    ]
)

keyb_markup_start_superadmin = ReplyKeyboardMarkup(
    resize_keyboard=True,  # меняем размер клавиатуры
    input_field_placeholder='Главное меню суперадмина',
    keyboard=[
        [
            KeyboardButton(text='Режим: Суперадмин 👨‍💻'),
            KeyboardButton(text='Добавить клиента')
        ]
    ]
)
