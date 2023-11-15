from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from components.keyboards_components.markups.reply import keyb_markup_start_admin, keyb_markup_start_user_admin, \
    keyb_markup_start_user, keyb_markup_start_superadmin
from config import SUPER_ADMINS_CHAT_ID
from microservices.sql_models_extends.confirm_notification import ConfirmNotificationExtend
from microservices.sql_models_extends.user import UserExtend
from models import ConfirmNotification


async def get_dashboard_url_keyb_markup(url_d: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Ссылка на Dashboard", url=url_d)]
    ])


async def get_dashb_checks_row(dashb_checks_btns: list, checks_url: str):
    result_row = []
    if "Dashboard" in dashb_checks_btns:
        result_row.append(InlineKeyboardButton(text="Dashboard 📊", callback_data='open_dashboard'))
    if "Чеки" in dashb_checks_btns:
        result_row.append(InlineKeyboardButton(text="Чеки 📄", callback_data="disabled_inline_btn", url=checks_url))
    if not dashb_checks_btns:
        result_row = None
    return result_row


async def get_reply_keyb_markup_start(user_chat_id: int, category_user: str):
    result_keyb_markup = keyb_markup_start_user
    role_user = await UserExtend.get_user_role(chat_id=user_chat_id, role_type='normal')

    if (category_user == "user") and (role_user == 'timekeeper'):
        keyb_markup_start_user.keyboard[0] = [
            KeyboardButton(text="Операция с категориями"),
            KeyboardButton(text="Операция с подотчетами"),
            KeyboardButton(text="Табель")
        ]
    elif (category_user == "admin_user") and (role_user == 'timekeeper'):
        keyb_markup_start_user_admin.keyboard[0] = [
            KeyboardButton(text="Операция с категориями"),
            KeyboardButton(text="Операция с подотчетами"),
            KeyboardButton(text="Табель")
        ]
    elif (category_user == "admin_user") and (role_user is None):
        keyb_markup_start_user_admin.keyboard[0] = [
            KeyboardButton(text="Операция с категориями"),
            KeyboardButton(text="Операция с подотчетами")
        ]
    elif (category_user == "user") and (role_user is None):
        keyb_markup_start_user_admin.keyboard[0] = [
            KeyboardButton(text="Операция с категориями"),
            KeyboardButton(text="Операция с подотчетами")
        ]

    if category_user != "superadmin":
        match category_user:
            case "admin_user":
                result_keyb_markup = keyb_markup_start_user_admin
            case "admin":
                result_keyb_markup = keyb_markup_start_admin

        for i, row in enumerate(result_keyb_markup.keyboard):
            for k, button in enumerate(row):
                try:
                    btn_text = button.text
                except AttributeError:
                    btn_text = button
                if "📩" in btn_text:
                    number_n = await ConfirmNotificationExtend.get_user_notifies_number(user_chat_id)
                    result_keyb_markup.keyboard[i][k] = f"{number_n} 📩"
    else:
        result_keyb_markup = keyb_markup_start_superadmin

    return result_keyb_markup


async def get_inline_keyb_markup(callback_str: str, number_cols: int, list_names: list, list_data: list = None,
                                 urls_list: str = None, add_keyb_to_start=None):
    keyboard: list = [[]]
    number_str_keyboard = 0

    for i in range(0, len(list_names)):
        keyboard[number_str_keyboard].append(InlineKeyboardButton(
            text=list_names[i],
            callback_data=f"{callback_str}:{list_data[i]}" if list_data is not None else callback_str,
            url=urls_list[i] if urls_list is not None else None))
        if ((i + 1) % number_cols) == 0:
            number_str_keyboard += 1
            keyboard.append([])

    if add_keyb_to_start is not None:
        keyboard.insert(0, add_keyb_to_start)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


async def get_inline_users_keyb_markup(list_fullnames: list, list_names: list, number_cols: int,
                                       add_keyb_to_start=None, callb="empty", url=True):
    keyboard: list = [[]]

    number_str_keyboard = 0
    for i in range(0, len(list_fullnames)):
        if url:
            keyboard[number_str_keyboard].append(InlineKeyboardButton(
                text=list_fullnames[i],
                callback_data=callb,
                url=f"https://t.me/{list_names[i].replace('@', '')}"))
        else:
            keyboard[number_str_keyboard].append(InlineKeyboardButton(
                text=list_fullnames[i],
                callback_data=f"{callb}:{list_names[i]}"))
        if i % number_cols != 0 and i != (len(list_fullnames) - 1):
            number_str_keyboard += 1
            keyboard.append([])

    if add_keyb_to_start is not None:
        keyboard.insert(0, add_keyb_to_start)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


async def get_inline_keyb_markup_empty(selected_item_id: int = None) -> InlineKeyboardMarkup:
    if selected_item_id is not None:
        keyb = [
            [
                InlineKeyboardButton(text="⬅️", callback_data=f"back_to_upper_level:{selected_item_id}"),
                InlineKeyboardButton(text="➕", callback_data=f"add_menu_item:{selected_item_id}")
            ]
        ]
    else:
        keyb = [
            [
                InlineKeyboardButton(text="➕", callback_data="add_upper_menu_item")
            ]
        ]

    return InlineKeyboardMarkup(inline_keyboard=keyb)


async def get_inline_keyb_str_full(selected_item_id: int = None, upper: bool = False) -> list[InlineKeyboardButton]:
    if (upper is False) and (selected_item_id is not None):
        keyb_line = [
            InlineKeyboardButton(text="⬅️", callback_data=f"back_to_upper_level:{selected_item_id}"),
            InlineKeyboardButton(text="➕", callback_data=f"add_menu_item:{selected_item_id}"),
            InlineKeyboardButton(text="✏️", callback_data=f"change_menu_items:{selected_item_id}"),
            InlineKeyboardButton(text="❌", callback_data=f"delete_menu_items:{selected_item_id}")
        ]
    else:
        keyb_line = [
            InlineKeyboardButton(text="➕", callback_data=f"add_upper_menu_item"),
            InlineKeyboardButton(text="✏️", callback_data=f"change_upper_menu_items"),
            InlineKeyboardButton(text="❌", callback_data=f"delete_upper_menu_items")
        ]

    return keyb_line


async def get_inline_keyb_change_user(id_user: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Изменить данные", callback_data=f"change_data_user:{id_user}"),
            InlineKeyboardButton(text="Изменить id", callback_data=f"change_id_user:{id_user}")
        ]
    ])


async def get_inline_keyb_change_menu_item(id_menu_item: str, status_menu_item: bool):
    status_menu_item = "Скрытый 💤" if status_menu_item == 0 else "Активный ✅"

    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Название", callback_data=f"change_name_menu_item:{id_menu_item}"),
            InlineKeyboardButton(text="Наблюдатели", callback_data=f"start_change_observers_menu_item:{id_menu_item}")
        ],
        [
            InlineKeyboardButton(text=f"Статус: {status_menu_item}",
                                 callback_data=f"change_status_menu_item:{id_menu_item}")
        ]
    ])


async def get_inline_keyb_change_organization(id: str, status: bool):
    status = "Скрытый 💤" if status == 0 else "Активный ✅"

    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Параметры", callback_data=f"change_params_organization:{id}"),
            InlineKeyboardButton(text="Наблюдатели", callback_data=f"start_change_observers_organization:{id}")
        ],
        [
            InlineKeyboardButton(text=f"Статус: {status}", callback_data=f"change_status_organization:{id}")
        ]
    ])


async def get_inline_keyb_profit_cost(selected_item_id: int = None) -> InlineKeyboardMarkup:
    keyb = [
        [
            InlineKeyboardButton(text="Назад ⬅️", callback_data=f"back_to_upper_level_u:{selected_item_id}"),
            InlineKeyboardButton(text="Доход ➕", callback_data=f"profit_item:{selected_item_id}"),
            InlineKeyboardButton(text="Расход ➖", callback_data=f"cost_item:{selected_item_id}")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyb)


async def get_inline_keyb_str_back_to_parent_items_u(selected_item_id: int = None) -> list[InlineKeyboardButton]:
    keyb = [
        InlineKeyboardButton(text="Назад ⬅️", callback_data=f"back_to_upper_level_u:{selected_item_id}")
    ]

    return keyb


async def get_gt_url_keyb_markup(google_table_url, google_drive_url):
    keyboard = [
        [
            InlineKeyboardButton(text="Ссылка на таблицу", url=google_table_url),
            InlineKeyboardButton(text="Ссылка на чеки", url=google_drive_url)
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


async def get_confirm_issuance_keyb_button(id_issuance_report: int):
    keyboard = [
        [
            InlineKeyboardButton(text="Подтвердить  ✅", callback_data=f"confirm_issuance:{id_issuance_report}")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


async def get_keyb_str_manage_payment_accounts(bank_id):
    return [
        InlineKeyboardButton(text="⬅️", callback_data=f"back_to_banks"),
        InlineKeyboardButton(text="➕", callback_data=f"add_payment_account:{bank_id}"),
        InlineKeyboardButton(text="❌", callback_data=f"delete_payment_accounts:{bank_id}")
    ]


async def get_keyb_empty_list_payment_accounts(bank_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⬅️", callback_data=f"back_to_banks"),
            InlineKeyboardButton(text="➕", callback_data=f"add_payment_account:{bank_id}")
        ]
    ])


async def get_keyb_row_save_changes(callback_data_str: str) -> list[InlineKeyboardButton]:
    """
    Функция для генерации inline строки сохранения изменений

    :param callback_data_str: значение колбека кнопки, в формате строки
    :return: [InlineKeyboardButton]
    """
    return [
        InlineKeyboardButton(text="Сохранить изменения  💾", callback_data=callback_data_str)
    ]


async def get_keyb_list_notify_types_user(user_role: str,
                                          user_notifications: list[ConfirmNotification]) -> InlineKeyboardMarkup:
    inline_keyboard = []

    notifies = {
        # 'issuance_of_report': {
        #     'count': 0,
        #     'btn_text': "Подтверждения на выдачу в подотчет:",
        #     'callb_d': 'n_issuance_report',
        # }
    }

    match user_role:
        case 'conciliator':
            notifies['conciliate_requests_report'] = {
                'count': 0,
                'btn_text': "Согласование запросов в подотчет:",
                'callb_d': 'n_conciliate_requests_report',
            }
        case 'approver':
            notifies['approve_requests_report'] = {
                'count': 0,
                'btn_text': "Утверждения запросов в подотчет:",
                'callb_d': 'n_approve_requests_report',
            }
        case 'treasurer':
            notifies['treasure_requests_report'] = {
                'count': 0,
                'btn_text': "Выдать средства по запросу в подотчет:",
                'callb_d': 'n_treasure_requests_report',
            }

    for n in user_notifications:
        if n.type == 'report_request':
            nrq = await n.report_request
            try:
                match nrq.stage:
                    case 'conciliate':
                        notifies['conciliate_requests_report']['count'] += 1
                    case 'approve':
                        notifies['approve_requests_report']['count'] += 1
                    case 'treasure':
                        notifies['treasure_requests_report']['count'] += 1
            except KeyError:
                await nrq.delete()
                continue
        elif n.type == 'issuance_of_report':
            notifies['issuance_of_report']['count'] += 1

    for e in notifies.values():
        if e['count'] > 0:
            ikb = InlineKeyboardButton(text=f"{e['btn_text']} {e['count']} 🔻", callback_data=f"{e['callb_d']}")
            inline_keyboard.append([ikb])
        else:
            ikb = InlineKeyboardButton(text=e['btn_text'] + " 0", callback_data='disabled_inline_btn')
            inline_keyboard.append([ikb])

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


async def get_notify_keyboard_btn(callback_d: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Подтвердить ✅", callback_data=callback_d)
    ]])
