from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from components.filters import IsUserFilter
from components.keyboards_components.inline_strings import keyb_str_change_wallets_list
from components.tools import get_callb_content, generate_wallets_status_list, \
    generate_zero_array
from components.keyboards_components.generators import get_inline_keyb_markup
from components.texts.users.change_wallet_list import text_change_wallets_list, text_end_change_wallets_list
from config import BANKS_UPRAVLYAIKA
from microservices.redis_models.wallets import RedisUserWallets
from states.user.steps_change_wallet_list import StepsChangeWalletList

rt = Router()

# Фильтр на проверку категории доступа пользователя
rt.message.filter(IsUserFilter(), F.chat.type == "private")
rt.callback_query.filter(IsUserFilter(), F.message.chat.type == "private")


@rt.message(F.text == "Изменение списка кошельков")
async def start_change_wallets_list(message: Message, state: FSMContext, redis_wallets: RedisUserWallets):
    await state.clear()
    await state.set_state(StepsChangeWalletList.change_wallets_list)

    user_wallets = await redis_wallets.get_wallets_list(message.from_user.id)
    list_index_wallets = []
    list_buttons_name = []

    # Генерируем список порядкового номера кошельков в клавиатуре
    for i in range(0, len(BANKS_UPRAVLYAIKA)):
        list_index_wallets.append(i)

    if user_wallets is not None:
        # Генерируем список наименований кнопок с кошельками
        for w in BANKS_UPRAVLYAIKA:
            status_emoji = "☑️ " if (w in user_wallets) else ""
            list_buttons_name.append(f'{status_emoji}{w}')

        status_list = await generate_wallets_status_list(user_wallets)
    else:
        list_buttons_name = BANKS_UPRAVLYAIKA
        status_list = await generate_zero_array(len(BANKS_UPRAVLYAIKA))

    keyboard = await get_inline_keyb_markup(
        list_names=list_buttons_name,
        list_data=list_index_wallets,
        callback_str="change_user_wallets_list",
        number_cols=2,
        add_keyb_to_start=keyb_str_change_wallets_list
    )

    # Сохраняем название выбранного пункта и лист статусов пользователей (выбран или нет)
    await state.update_data({
        'list_index_wallets': list_index_wallets,
        'status_list': status_list,
        'user_wallets': user_wallets,
    })

    await message.answer(text=text_change_wallets_list, reply_markup=keyboard, parse_mode="html")


@rt.callback_query(StepsChangeWalletList.change_wallets_list, F.data.startswith("change_user_wallets_list"))
async def change_wallets_list(callback: CallbackQuery, state: FSMContext):
    data_state = await state.get_data()
    number_choose_wallet = int(await get_callb_content(callback.data))
    data_state['status_list'][number_choose_wallet] = 1 if data_state['status_list'][number_choose_wallet] == 0 else 0
    continue_run_script = True

    for i in range(0, len(data_state['status_list'])):
        if data_state['status_list'][i] == 1:
            break
        if i == (len(data_state['status_list']) - 1):
            continue_run_script = False

    if continue_run_script:
        list_buttons_name = []

        await state.update_data({
            'status_list': data_state['status_list'],
        })

        for i in range(0, len(BANKS_UPRAVLYAIKA)):
            status_emoji = '' if data_state['status_list'][i] == 0 else '☑️ '
            list_buttons_name.append(f'{status_emoji} {BANKS_UPRAVLYAIKA[i]}')

        keyboard = await get_inline_keyb_markup(
            list_names=list_buttons_name,
            list_data=data_state['list_index_wallets'],
            callback_str="change_user_wallets_list",
            number_cols=2,
            add_keyb_to_start=keyb_str_change_wallets_list
        )

        await callback.message.edit_text(text=text_change_wallets_list, reply_markup=keyboard, parse_mode="html")


@rt.callback_query(StepsChangeWalletList.change_wallets_list, F.data == "save_change_wallet_list")
async def end_change_wallets_list(callback: CallbackQuery, state: FSMContext, redis_wallets: RedisUserWallets):
    data_state = await state.get_data()
    await state.clear()

    new_list_names_wallets = []

    # Генерируем список выбранных пользователей
    for i in range(0, len(BANKS_UPRAVLYAIKA)):
        if data_state['status_list'][i] == 1:
            new_list_names_wallets.append(BANKS_UPRAVLYAIKA[i])

    await redis_wallets.set_new_wallets_list(callback.message.chat.id, new_list_names_wallets)

    await callback.message.edit_text(text=text_end_change_wallets_list, parse_mode="html")
