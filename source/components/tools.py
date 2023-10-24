from datetime import datetime
from aiofiles.os import remove
from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import InlineKeyboardMarkup, Message, CallbackQuery
from cryptography.fernet import Fernet
from components.keyboards_components.generators import get_gt_url_keyb_markup
from components.text_generators.users import get_notify_request_report_text
from components.texts.users.write_category_to_bd import text_end_add_mi_to_bd
from config import MEMORY_STORAGE, CHECKS_PATH, BANKS_UPRAVLYAIKA, SECRET_KEY, ROLE_BY_STAGES_REPS_REQS
from microservices.sql_models_extends.category import CategoryExtend
from microservices.sql_models_extends.notify_group import NotifyGroupExtend
from microservices.sql_models_extends.user import UserExtend
from microservices.google_api.google_drive import GoogleDrive
from microservices.google_api.google_table import GoogleTable
from models import ConfirmNotification, ReportRequest, PaymentAccount


async def get_users_keyb_names_with_checkbox(users: list, flag_name: str, flag_value: str, include_admin=False,
                                             admin_id=None, radio_buttons=False):
    buttons_names = []
    buttons_callbacks = []
    for u in users:
        selected_emoji = ('🔘 ' if radio_buttons else '☑️ ') if u[flag_name] == flag_value else ''
        if u['chat_id'] == admin_id and include_admin:
            buttons_names.append(f"{selected_emoji} Я")
        else:
            buttons_names.append(f"{selected_emoji}{u['fullname'].split(' ')[1]} - {u['profession']}")
        buttons_callbacks.append(u['chat_id'])
    return {'names': buttons_names, 'callbacks': buttons_callbacks}


async def is_start_select_delete_btns(state: FSMContext):
    st_data = await state.get_data()
    result = False
    if 'start_select_btns_on_delete' not in st_data:
        await state.update_data({'start_select_btns_on_delete': 1})
        result = True
    return result


async def get_ids_delete_objects_from_keyb_callb(callback: CallbackQuery, emoji_flag: str):
    inline_keyboard = callback.message.reply_markup.inline_keyboard
    ids_objects = []
    for row in inline_keyboard:
        for button in row:
            if emoji_flag in button.text:
                ids_objects.append(button.callback_data.split(":")[1])
    return ids_objects


async def get_changed_reply_keyb_with_checkbox(callback: CallbackQuery, select_mode='checkbox',
                                               ignore_emoji: list = None) -> InlineKeyboardMarkup:
    """
    Мощный инструмент для изменения флажков нажатых на inline клавиатуре кнопок.

    :param ignore_emoji: список игнорируемых эмоджи в кнопках
    :param callback: колбэк с inline клавиатурой
    :param select_mode: checkbox/checkbox_minimum_one/radio/radio_with_none по порядку
    1. checkbox - режим выбора нескольких кнопок с возможностью убрать все флажки.
    2. checkbox_minimum_one - режим выбора нескольких кнопок с возможностью убрать флажки, при условии, что остался
    один включенный.
    3. radio - режим при котором можно выбрать только одну кнопку, флажок убрать нельзя.
    4. radio_with_none - режим при котором можно выбрать только одну кнопку, а также можно убрать флажок.
    :return: InlineKeyboardMarkup
    """

    keyboard_markup = callback.message.reply_markup
    number_pressed_btns = 0
    emoji = '🔘' if (select_mode == 'radio' or select_mode == 'radio_with_none') else '☑️'
    irb = []
    # Считаем количество нажатых кнопок (выбранных пунктов)
    if select_mode == 'checkbox_minimum_one':
        for i, row in enumerate(keyboard_markup.inline_keyboard):
            for k, button in enumerate(row):
                if emoji in button.text:
                    number_pressed_btns += 1
    # Получаем индекс выбранной radio кнопки
    if 'radio' in select_mode:
        for i, row in enumerate(keyboard_markup.inline_keyboard):
            for k, button in enumerate(row):
                if emoji in button.text:
                    irb.append(i)
                    irb.append(k)
                    break
    # Находим нажатую в данный момент кнопку и ставим флажок, либо убираем (+- проверка, что должен быть хотя бы один)
    for i, row in enumerate(keyboard_markup.inline_keyboard):
        for k, button in enumerate(row):
            if ignore_emoji:
                if button.text[:1] in ignore_emoji:
                    continue
            if callback.data == button.callback_data:
                if 'checkbox' in select_mode:
                    if emoji in button.text and not (select_mode == 'checkbox_minimum_one'):
                        keyboard_markup.inline_keyboard[i][k].text = button.text[2:]
                    elif emoji in button.text and (select_mode == 'checkbox_minimum_one'):
                        if (number_pressed_btns - 1) > 0:
                            keyboard_markup.inline_keyboard[i][k].text = button.text[2:]
                        else:
                            await callback.answer()
                            break
                    else:
                        keyboard_markup.inline_keyboard[i][k].text = emoji + " " + button.text
                else:
                    if emoji in button.text and not (select_mode == 'radio_with_none'):
                        await callback.answer()
                        break
                    elif emoji in button.text and (select_mode == 'radio_with_none'):
                        keyboard_markup.inline_keyboard[i][k].text = button.text[2:]
                    else:
                        try:
                            keyboard_markup.inline_keyboard[irb[0]][irb[1]].text = \
                            keyboard_markup.inline_keyboard[irb[0]][irb[1]].text[2:]
                        except IndexError:
                            pass
                        keyboard_markup.inline_keyboard[i][k].text = emoji + " " + button.text
                break
    return keyboard_markup


async def get_emoji_number(number):
    numbers = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
    emoji_number = ""

    for i in range(0, len(str(number))):
        emoji_number += numbers[int(str(number)[i])]

    return emoji_number


# Получить текст с очередью элементов и уровнем в эмоджи
async def get_msg_queue(level: int, selected_item_name: str = "", queue: str = "", only_queue: bool = False) -> str:
    numbers = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
    emoji_level = ""

    if level == 0:
        if only_queue:
            return f"<u>Вложенность</u>:  <b>Главные категории</b>\n"
        else:
            return f"<u>Уровень</u>: 0️⃣\n"
    elif level == 1:
        if only_queue:
            return f"<u>Вложенность</u>:  <b>{queue}</b>\n"
        else:
            return f"<u>Уровень</u>: 1️⃣ \n" \
                   f"<u>Родительская категория</u>: <b>{selected_item_name}</b>\n"

    for i in range(0, len(str(level))):
        emoji_level += numbers[int(str(level)[i])]

    if only_queue:
        return f"<u>Вложенность</u>:  <b>{queue}</b>\n"
    else:
        return f"<u>Уровень</u>: {emoji_level}\n" \
               f"<u>Родительская категория</u>: <b>{selected_item_name}</b>\n" \
               f"<u>Вложенность</u>:  <b>{queue}</b>\n"


# Получить содержимое колбека
async def get_callb_content(callback_data: str, multiply_values: bool = False):
    return callback_data.split(":") if multiply_values else callback_data.split(":")[1]


# Функция для получения пользовательских данных из колбека
async def get_msg_user_data(msg_data: str) -> dict:
    return {
        'nickname': msg_data.split("\n")[0],
        'fullname': msg_data.split("\n")[1],
        'profession': msg_data.split("\n")[2]
    }


async def get_msg_list_data(msg_data: str) -> list:
    return msg_data.split("\n")


async def generate_zero_array(length: int):
    array_zero_str = list()

    for i in range(0, length):
        array_zero_str.append(0)

    return array_zero_str


async def generate_observers_list(users: dict):
    observers_list = list()

    for u in users:
        observers_list.append(1 if u['observer'] else 0)

    return observers_list


async def generate_wallets_status_list(wallets: list):
    wallets_status_list = list()

    for w in BANKS_UPRAVLYAIKA:
        wallets_status_list.append(1 if (w in wallets) else 0)

    return wallets_status_list


async def get_sure_delete_mi_msg(list_menu_items: list):
    return f"<b>Вы уверены что хотите удалить категории:</b>\n{', '.join(str(mi) for mi in list_menu_items)}❓\n\n" \
           f"<i>⚠️ Важно: при удалении, исчезнут все вложенные подкатегории а также определенные пользователям " \
           f"доступы к этим подкатегориям!</i>"


async def get_sure_delete_org_msg(list_menu_items: list):
    return f"<b>Вы уверены что хотите удалить ЮР Лица:</b>\n{', '.join(str(mi) for mi in list_menu_items)}❓\n\n" \
           f"<i>⚠️ Важно: при удалении исчезнут все определенные пользователям доступы к этим ЮР Лицам, а также, " \
           f"если вы привязали банки к системе и определили эти ЮР Лица для определенных категорий - система " \
           f"перестанет подгружать данные о новых операциях по этим категориям из банка!</i>"


async def get_sure_delete_usr_msg(list_users: list):
    return f"<b>Вы уверены что хотите забрать доступ у:</b>\n{', '.join(str(u) for u in list_users)}❓\n\n" \
           f"<i>⚠️ Важно: при удалении исчезнут все определенные пользователям права видимости к определенным " \
           f"пунктам меню, а доступ пользователей к боту будет анулирован!</i>️"


async def get_sure_delete_partner_msg(list_partners: list):
    return f"<b>Вы уверены, что хотите удалить контрагентов:</b>\n{', '.join(str(p) for p in list_partners)}❓\n\n" \
           f"<i>⚠️ Важно: при удалении исчезнут связи контрагентов с категориями и операции из выписок " \
           f"банков перестанут распределяться в вашей таблице!</i>"


async def get_sure_delete_banks_msg(list_banks: list):
    return f"<b>Вы уверены, что хотите удалить банки:</b>\n{', '.join(str(b) for b in list_banks)}❓\n\n" \
           f"<i>⚠️ Важно: при удалении исчезнут также расчетные счета, привязанные к этим банкам, а операции из выписок " \
           f"этих банков перестанут распределяться в вашей таблице!</i>"


async def get_sure_delete_payment_account_msg(list_partners: list):
    return f"<b>Вы уверены, что хотите удалить расчётные счета:</b>\n{', '.join(str(p) for p in list_partners)}❓\n\n" \
           f"<i>⚠️ Важно: При удалении исчезнут связи ЮР Лиц с выбранными расчётными счётами, а операции из выписок банков перестанут " \
           f"подгружаться из выбранных счётов!</i>"


async def answer_or_edit_message(message: Message, flag_answer: bool, text: str,
                                 keyboard_markup: InlineKeyboardMarkup = None):
    if flag_answer:
        message = await message.answer(
            text=text,
            reply_markup=keyboard_markup,
            parse_mode="html"
        )
    else:
        message = await message.edit_text(
            text=text,
            reply_markup=keyboard_markup,
            parse_mode="html"
        )
    return message


async def get_current_frmt_datetime():
    return datetime.now().strftime('%Y-%m-%d&%H-%M-%S')


async def send_multiply_messages(bot: Bot, msg_text: str, list_chat_ids: list[int], keyboard_markup=None):
    for chat_id in list_chat_ids:
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=msg_text,
                parse_mode="html",
                reply_markup=keyboard_markup,
            )
        except TelegramForbiddenError:
            await NotifyGroupExtend.detach_group_from_admin(chat_id)


async def get_msg_notify_new_note_bd(fullname_worker: str, last_queue_e: str, queue: str,
                                     volume_op: str, payment_method: str, sender_is_org: bool = False):
    org_sender_txt = " от имени ЮР Лица" if sender_is_org else ""
    return f"📳 Пользователь <b>{fullname_worker}</b>, только что, оформил{org_sender_txt}: {last_queue_e}\n" \
           f"<u>Очередь операции</u>: <b>{queue}</b>\n" \
           f"<u>Сумма</u>: <b>{volume_op}</b>\n" \
           f"<u>Кошелек</u>: <b>{payment_method}</b>\n"


async def add_new_note_to_bd_handler_algorithm(message: Message, state: FSMContext, bot_object: Bot,
                                               gt_object: GoogleTable, gd_object: GoogleDrive, file_id: str = None):
    current_user = await UserExtend.get_by_id(message.chat.id)
    admin_id = await UserExtend.get_user_admin_id(message.chat.id)
    admin_info = await UserExtend.get_admin_info(admin_id)
    state_data = await state.get_data()
    gt_decr_url = Fernet(SECRET_KEY).decrypt(admin_info.google_table_url).decode("utf-8")
    gd_decr_url = Fernet(SECRET_KEY).decrypt(admin_info.google_drive_dir_url).decode("utf-8")
    keyboard_end_write = await get_gt_url_keyb_markup(gt_decr_url, gd_decr_url)
    sender_org_flag = True if state_data['sender'] == "org" else False

    message = await answer_or_edit_message(
        message=message,
        flag_answer=not sender_org_flag,
        text='Добавляю запись в вашу гугл таблицу 🔄 \n\n🟩🟩🟩◻◻◻◻◻◻◻'
    )

    # Добавляем запись в google
    await gt_object.add_new_str_to_bd(
        table_encr_url=admin_info.google_table_url,
        chat_id_worker=message.chat.id,
        fullname_worker=current_user.fullname,
        volume_op=state_data['volume_operation'],
        org_op=state_data['organization_name'],
        queue_op=state_data['item_queue'],
        type_op=state_data['operation_type'],
        payment_method=state_data['payment_method'],
        sender_is_org=sender_org_flag
    )

    if file_id is not None:
        message = await message.edit_text('Сохраняю чек, проверяю включен ли я в ваши группы 🧐 \n\n🟩🟩🟩🟩🟩🟩◻◻◻◻')

        # Если не юр лицо
        if not sender_org_flag:
            file_name = await get_current_frmt_datetime() + ".png"
            file_path = CHECKS_PATH + str(admin_id) + "/" + file_name

            # Сохраняем чек на сервере если не от юр лица
            await bot_object.download(file=file_id, destination=file_path)

            # Отправляем файл в папку google drive клиента
            await gd_object.upload_check_too_google_drive_dir(
                file_path=file_path,
                google_dir_encr_url=admin_info.google_drive_dir_url,
                file_name_on_gd=file_name
            )

            # Удаляем файл с помощью aiofiles
            await remove(file_path)
    else:
        message = await message.edit_text('Проверяю включен ли я в ваши группы 🧐 \n\n🟩🟩🟩🟩🟩🟩◻◻◻◻')

    await state.clear()

    # Рассылаем уведомление по группам админа
    check_admin_empty_groups = await NotifyGroupExtend.check_admin_groups_empty(admin_id)

    if not check_admin_empty_groups:
        message = await message.edit_text('Включен, отправляю уведомления в группы 📩 \n\n🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩')
        list_ngroups_ids = await NotifyGroupExtend.get_admin_notify_groups_chat_ids(admin_id)
        operation_name = state_data['item_queue'].split(" → ")[-1]

        msg_in_group = await get_msg_notify_new_note_bd(
            fullname_worker=current_user.fullname,
            last_queue_e=operation_name,
            queue=state_data['item_queue'],
            volume_op=state_data['volume_operation'],
            payment_method=state_data['payment_method'],
            sender_is_org=sender_org_flag
        )

        await send_multiply_messages(
            bot=bot_object,
            msg_text=msg_in_group,
            list_chat_ids=list_ngroups_ids
        )

    await message.edit_text(text=text_end_add_mi_to_bd, reply_markup=keyboard_end_write, parse_mode="html")


async def get_str_format_queue(selected_item_id) -> str:
    menu_items_names_list = await CategoryExtend.get_parent_categories_names(selected_item_id)
    return " → ".join(menu_items_names_list)


async def get_formatted_msg_callb_notifications(notifications: list[ConfirmNotification]):
    result = {
        'fst_message': '',
        'notifications': [],
    }
    variants_messages = {
        'conciliate': 'согласованию запроса в подотчет',
        'approve': 'утверждению запроса в подотчет',
        'treasure': 'подтверждению выдачи средств в подотчет'
    }

    for i, n in enumerate(notifications):
        if n.type == 'report_request':
            rep_req = await n.report_request
            stage = rep_req.stage
            if i == 0:
                result['fst_message'] = f"<b>Уведомления по {variants_messages[stage]}</b>"
            result['notifications'].append({
                'text': f"<u>Запрос от:</u> <b>{rep_req.nickname_sender}</b>\n"
                        f"<u>Сумма:</u> <b>{rep_req.volume}</b>\n"
                        f"<u>Комментарий:</u> <b>{rep_req.comment}</b>",
                'callback': f'n_report_request:{stage}:{n.id}'
            })

    return result


async def change_stage_report_request(bot: Bot, admin_chat_id: int, stage: str, report_request: ReportRequest):
    cfrm_notifications = await report_request.confirm_notifications

    if not cfrm_notifications:
        chat_groups_ids = await UserExtend.get_notify_groups(admin_id=admin_chat_id, only_chat_ids=True)
        volume = report_request.volume
        comment = report_request.comment
        sender_nickname = report_request.nickname_sender

        match stage:
            case 'conciliate':
                report_request.stage = 'approve'
                stage = 'approve'
                await report_request.save()
            case 'approve':
                report_request.stage = 'treasure'
                stage = 'treasure'
                await report_request.save()
            case 'treasure':
                stage = 'end'
                await report_request.delete()

        if stage != 'end':
            users_by_role = await UserExtend.get_users_by_role_and_type(id_admin=admin_chat_id,
                                                                        role=ROLE_BY_STAGES_REPS_REQS[stage],
                                                                        role_type='report_request')
            nicknames = [u['nickname'] for u in users_by_role]
        else:
            nicknames = None

        ftmt_msg = await get_notify_request_report_text(
            stage=stage,
            users_nicknames=nicknames,
            sender_nickname=sender_nickname,
            volume=volume,
            comment=comment
        )

        await send_multiply_messages(
            bot=bot,
            msg_text=ftmt_msg,
            list_chat_ids=chat_groups_ids,
            keyboard_markup=None
        )

        if stage != 'end':
            await UserExtend.send_confirm_notify_to_users_by_role(
                admin_id=admin_chat_id,
                role_recipients=ROLE_BY_STAGES_REPS_REQS[stage],
                volume=volume,
                comment=comment,
                nickname_sender=sender_nickname
            )
