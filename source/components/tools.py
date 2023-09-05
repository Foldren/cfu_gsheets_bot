from datetime import datetime
from typing import List

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from components.texts import text_end_add_mi_to_bd
from config import MEMORY_STORAGE, CHECKS_PATH

# Метод генерации inline клавиатуры с пунктами меню
from services.database_extends.notify_group import NotifyGroupApi
from services.database_extends.user import UserApi
from services.google_api.google_table import GoogleTable


async def get_inline_keyb_markup(list_names: list, list_data: list, callback_str: str, number_cols: int,
                                 add_keyb_to_start=None):
    keyboard: list = [[]]

    number_str_keyboard = 0
    for i in range(0, len(list_data)):
        keyboard[number_str_keyboard].append(InlineKeyboardButton(
            text=list_names[i],
            callback_data=f"{callback_str}:{list_data[i]}"))
        if i % number_cols != 0 and i != (len(list_data) - 1):
            number_str_keyboard += 1
            keyboard.append([])

    if add_keyb_to_start is not None:
        keyboard.insert(0, add_keyb_to_start)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# Метод генерации inline клавиатуры с пользователями
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


# Получить inline клавиатуру с кнопками управления (если нет элементов)
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


# Получить inline клавиатуру с кнопками управления
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


# Получить клавиатуру редактирования пользователя
async def get_inline_keyb_change_user(id_user: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Изменить данные", callback_data=f"change_data_user:{id_user}"),
            InlineKeyboardButton(text="Изменить id", callback_data=f"change_id_user:{id_user}")
        ]
    ])


# Получить текст с очередью элементов и уровнем в эмоджи
async def get_msg_queue(level: int, selected_item_name: str = "", queue: str = "", only_queue: bool = False) -> str:
    numbers = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
    emoji_level = ""

    if level == 1:
        if only_queue:
            return f"<code>Вложенность</code>:  <b>Верхнее меню</b>\n"
        else:
            return f"<code>Уровень</code>: 1️⃣ <b>Верхнее меню</b>\n"

    for i in range(0, len(str(level))):
        emoji_level += numbers[int(str(level)[i])]

    if only_queue:
        return f"<code>Вложенность</code>:  <b>{queue}</b>\n"
    else:
        return f"<code>Уровень</code>: {emoji_level} <b>{selected_item_name}</b>\n" \
               f"<code>Вложенность</code>:  <b>{queue}</b>\n"


# Получить содержимое колбека
async def get_callb_content(callback_data: str):
    return callback_data.split(":")[1]


# Добавить/перезаписать значение в оперативной памяти
async def set_memory_data(bot_object: Bot, message: Message, data_dict: dict):
    await MEMORY_STORAGE.set_data(
        key=StorageKey(bot_id=bot_object.id, chat_id=message.chat.id, user_id=message.chat.id),
        data=data_dict
    )


# Считать значение из ОП
async def get_memory_data(bot_object: Bot, message: Message) -> dict:
    return await MEMORY_STORAGE.get_data(
        key=StorageKey(bot_id=bot_object.id, chat_id=message.chat.id, user_id=message.chat.id)
    )


async def set_memory_state(bot_object: Bot, message: Message, state: State):
    MEMORY_STORAGE.set_state(
        key=StorageKey(bot_id=bot_object.id, chat_id=message.chat.id, user_id=message.chat.id),
        state=state
    )


# Функция для получения пользовательских данных из колбека
async def get_msg_user_data(msg_data: str) -> dict:
    return {
        'nickname': msg_data.split("\n")[0],
        'fullname': msg_data.split("\n")[1],
        'profession': msg_data.split("\n")[2]
    }


async def generate_zero_array(length: int):
    array_zero_str = list()

    for i in range(0, length):
        array_zero_str.append(0)

    return array_zero_str


# Получить клавиатуру редактирования пункта меню
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


async def generate_observers_list(users: dict):
    observers_list = list()

    for u in users:
        observers_list.append(1 if u['observer'] else 0)

    return observers_list


async def get_sure_delete_mi_msg(list_menu_items: list):
    return f"Вы уверены что хотите удалить: <b>{', '.join(str(mi) for mi in list_menu_items)}</b> ❓\n\n" \
           f"При удалении, исчезнут все вложенные категории а также определенные пользователям доступы к этим категориям 🤔‼️"


async def get_sure_delete_usr_msg(list_users: list):
    return f"Вы уверены что хотите забрать доступ у: <b>{', '.join(str(u) for u in list_users)}</b> ❓\n\n" \
           f"При удалении исчезнут все определенные пользователям права видимости к определенным пунктам меню, " \
           f"а доступ пользователей к боту будет анулирован 🤔‼️"


# Получить inline клавиатуру с кнопками дохода и расхода по категории для юзера (если нет элементов)
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


async def answer_or_edit_message(message: Message, flag_answer: bool, text: str, keyboard: InlineKeyboardMarkup = None):
    if flag_answer:
        await message.answer(
            text=text,
            reply_markup=keyboard,
            parse_mode="html"
        )
    else:
        await message.edit_text(
            text=text,
            reply_markup=keyboard,
            parse_mode="html"
        )


async def get_current_frmt_datetime():
    return datetime.now().strftime('%Y-%m-%d&%H-%M-%S')


async def send_multiply_messages(bot: Bot, msg_text: str, list_chat_ids: list[int], keyboard_markup=None):
    for chat_id in list_chat_ids:
        await bot.send_message(
            chat_id=chat_id,
            text=msg_text,
            parse_mode="html",
            reply_markup=keyboard_markup,
        )


async def get_msg_notify_new_note_bd(fullname_worker: str, last_queue_e: str, queue: str,
                                     volume_op: str, payment_method: str):
    return f"📳 Пользователь <b>{fullname_worker}</b>, только что, оформил: {last_queue_e}\n"\
           f"<b>Очередь операции</b>: {queue}\n"\
           f"<b>Сумма</b>: {volume_op}\n"\
           f"<b>Кошелек</b>: {payment_method}\n"


async def add_new_note_to_bd_handler_algorithm(message: Message, state: FSMContext, bot_object: Bot,
                                               gt_object: GoogleTable, file_id: str):
    current_user = await UserApi.get_by_id(message.chat.id)
    admin_id = await UserApi.get_user_admin_id(message.chat.id)
    file_path = CHECKS_PATH + str(admin_id) + "/" + await get_current_frmt_datetime() + ".png"
    admin_info = await UserApi.get_admin_info(admin_id)
    state_data = await state.get_data()

    message = await message.answer('Добавляю запись в вашу гугл таблицу 🔄 \n\n🟩🟩🟩◻◻◻◻◻◻◻')
    # Добавляем запись в google
    await gt_object.add_new_str_to_bd(
        table_url=admin_info.google_table_url,
        chat_id_worker=message.chat.id,
        fullname_worker=current_user.fullname,
        volume_op=state_data['volume_operation'],
        queue_op=state_data['item_queue'],
        type_op=state_data['operation_type'],
        payment_method=state_data['payment_method'],
    )

    message = await message.edit_text('Сохраняю чек, проверяю включен ли я в ваши группы 🧐 \n\n🟩🟩🟩🟩🟩◻◻◻◻◻')
    # Сохраняем чек на сервере
    await bot_object.download(file=file_id, destination=file_path)
    await state.clear()

    # Рассылаем уведомление по группам админа
    check_admin_empty_groups = await NotifyGroupApi.check_admin_groups_empty(admin_id)

    if not check_admin_empty_groups:
        message = await message.edit_text('Включен, отправляю уведомления в группы 📩 \n\n🟩🟩🟩🟩🟩🟩🟩◻◻◻')
        list_ngroups_ids = await NotifyGroupApi.get_admin_notify_groups_chat_ids(admin_id)
        operation_name = state_data['item_queue'].split(" → ")[-1]

        msg_in_group = await get_msg_notify_new_note_bd(
            fullname_worker=current_user.fullname,
            last_queue_e=operation_name,
            queue=state_data['item_queue'],
            volume_op=state_data['volume_operation'],
            payment_method=state_data['payment_method']
        )

        await send_multiply_messages(
            bot=bot_object,
            msg_text=msg_in_group,
            list_chat_ids=list_ngroups_ids
        )

    await message.edit_text(text=text_end_add_mi_to_bd)
