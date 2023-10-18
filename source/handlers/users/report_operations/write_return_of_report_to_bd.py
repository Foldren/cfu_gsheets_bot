from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from components.filters import IsUserFilter, IsNotMainMenuMessage
from components.keyboards_components.generators import get_inline_keyb_markup
from components.text_generators.users import get_msg_notify_new_return_issuance
from components.texts.users.write_category_to_bd import text_invalid_volume_operation, text_no_menu_items_orgs
from components.texts.users.write_return_issuance_of_report_to_bd import text_set_volume_return_issuance, \
    text_select_payment_method_return_issuance, text_end_return_issuance, text_start_return_issuance
from components.tools import get_callb_content, send_multiply_messages
from microservices.google_api.google_table import GoogleTable
from microservices.redis_models.user import RedisUser
from microservices.redis_models.wallets import RedisUserWallets
from microservices.sql_models_extends.notify_group import NotifyGroupExtend
from microservices.sql_models_extends.organization import OrganizationExtend
from microservices.sql_models_extends.user import UserExtend
from states.user.steps_create_notes_to_bd import StepsWriteIssuanceReport, StepsReturnIssuanceMeans

rt = Router()

# Фильтр на проверку категории доступа пользователя
rt.message.filter(IsUserFilter(), F.chat.type == "private")
rt.callback_query.filter(IsUserFilter(), F.message.chat.type == "private")


@rt.message(F.text == "Возврат подотчета")
async def start_return_issuance_means(message: Message, state: FSMContext, redis_users: RedisUser):
    await state.clear()
    await state.set_state(StepsReturnIssuanceMeans.select_organization)

    admin_id = await redis_users.get_user_admin_id(message.from_user.id)

    organizations = await OrganizationExtend.get_user_organizations(message.from_user.id)

    if organizations:
        keyboard = await get_inline_keyb_markup(
            list_names=[org['name'] for org in organizations],
            list_data=[f"{org['id']}:{org['name']}" for org in organizations],
            callback_str="ip_to_issuance",
            number_cols=2
        )
        await state.set_data({
            'admin_id': admin_id,
        })
        await message.answer(text=text_start_return_issuance, reply_markup=keyboard, parse_mode="html")
    else:
        await message.answer(text=text_no_menu_items_orgs, parse_mode="html")


@rt.callback_query(StepsReturnIssuanceMeans.select_organization, F.data.startswith("ip_to_issuance"))
async def set_volume_for_return_issuance(callback: CallbackQuery, state: FSMContext):
    await state.set_state(StepsReturnIssuanceMeans.set_volume)
    selected_org_params = await get_callb_content(callback.data, multiply_values=True)

    await state.update_data({
        'selected_org_id': selected_org_params[1],
        'selected_org_name': selected_org_params[2],
    })

    await callback.message.edit_text(text=text_set_volume_return_issuance, parse_mode="html")


@rt.message(StepsReturnIssuanceMeans.set_volume, IsNotMainMenuMessage())
async def select_payment_method_return_issuance(message: Message, state: FSMContext, redis_wallets: RedisUserWallets):
    await state.set_state(StepsReturnIssuanceMeans.select_payment_method)

    try:
        volume_op = int(message.text)
    except Exception:
        await state.set_state(StepsWriteIssuanceReport.set_volume)
        await message.answer(text=text_invalid_volume_operation, parse_mode="html")
        return

    await state.update_data({
        'specified_volume': volume_op
    })

    wallets_list = await redis_wallets.get_wallets_list(message.from_user.id)

    keyboard = await get_inline_keyb_markup(
        list_names=wallets_list,
        list_data=wallets_list,
        callback_str="select_payment_method_issuance",
        number_cols=2
    )

    await message.answer(text=text_select_payment_method_return_issuance, reply_markup=keyboard, parse_mode="html")


@rt.callback_query(StepsReturnIssuanceMeans.select_payment_method, F.data.startswith("select_payment_method_issuance"))
async def end_write_return_issuance_to_bd(callback: CallbackQuery, state: FSMContext,
                                          bot_object: Bot, gt_object: GoogleTable):
    selected_payment_method = await get_callb_content(callback.data)
    st_data = await state.get_data()

    user = await UserExtend.get_by_id(callback.message.chat.id)
    admin_info = await UserExtend.get_admin_info(st_data['admin_id'])

    await callback.message.edit_text('Проверяю включение в группы 🔄 \n\n🟩🟩🟩🟩◻◻◻◻◻◻')
    сheck_notify_groups_empty = await NotifyGroupExtend.check_admin_groups_empty(st_data['admin_id'])

    # Проверяем наличие в группах и генерируем сообщение уведомления ---------------------------------------------------
    if сheck_notify_groups_empty:
        await callback.message.edit_text('Похоже я не включен в группы, окей - тогда без уведомления 🤷‍♂️ \n\n🟩🟩🟩🟩◻◻◻◻◻◻')
    else:
        await callback.message.edit_text('Бот включен в группы, отправляю уведомления 📨 \n\n🟩🟩🟩🟩🟩🟩◻◻◻◻')
        notify_groups_chat_ids = await NotifyGroupExtend.get_admin_notify_groups_chat_ids(st_data['admin_id'])
        msg_in_group = await get_msg_notify_new_return_issuance(
            profession_worker=user.profession,
            fullname_worker=user.fullname,
            ip=st_data['selected_org_name'],
            volume=st_data['specified_volume'],
            payment_method=selected_payment_method
        )
        await send_multiply_messages(bot=bot_object, msg_text=msg_in_group, list_chat_ids=notify_groups_chat_ids)

    # Добавляем запись в бд --------------------------------------------------------------------------------------------
    await callback.message.edit_text('Вношу запись в БД гугл таблицы 🆕 \n\n🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩')
    await gt_object.add_issuance_report_to_bd(
        table_encr_url=admin_info.google_table_url,
        chat_id_worker=callback.message.chat.id,
        fullname_recipient=user.fullname,
        volume_op=st_data['specified_volume'],
        payment_method=selected_payment_method,
        org_name=st_data['selected_org_name'],
        return_issuance=True
    )

    await state.clear()
    await callback.message.edit_text(text=text_end_return_issuance, parse_mode="html")










