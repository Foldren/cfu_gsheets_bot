from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from components.filters import IsUserFilter, IsNotMainMenuMessage
from components.keyboards_components.generators import get_inline_keyb_markup, get_confirm_issuance_keyb_button
from components.text_generators.users import get_msg_notify_new_issuance_of_report
from components.texts.users.write_category_to_bd import text_invalid_volume_operation, text_no_menu_items_orgs
from components.texts.users.write_issuance_of_report_to_bd import text_start_issuance, text_select_worker_issuance, \
    text_set_volume_issuance, text_select_payment_method_issuance, text_no_notify_groups, \
    text_select_notify_group_issuance, text_end_issuance, text_error_issuance
from components.tools import get_callb_content
from microservices.redis_models.user import RedisUser
from microservices.redis_models.wallets import RedisUserWallets
from microservices.sql_models_extends.issuance_report import IssuanceReportExtend
from microservices.sql_models_extends.notify_group import NotifyGroupExtend
from microservices.sql_models_extends.organization import OrganizationExtend
from microservices.sql_models_extends.user import UserExtend
from states.user.steps_create_notes_to_bd import StepsWriteIssuanceReport

rt = Router()

# Фильтр на проверку категории доступа пользователя
rt.message.filter(IsUserFilter(), F.chat.type == "private")
rt.callback_query.filter(IsUserFilter(), F.message.chat.type == "private")


@rt.message(F.text == "Выдача в подотчет")
async def start_write_issuance_of_report_to_bd(message: Message, state: FSMContext, redis_users: RedisUser):
    await state.clear()
    await state.set_state(StepsWriteIssuanceReport.select_organization)

    admin_id = await redis_users.get_user_admin_id(message.chat.id)
    check_admin_empty_groups = await NotifyGroupExtend.check_admin_groups_empty(admin_id)

    if check_admin_empty_groups:
        await message.answer(text=text_no_notify_groups, parse_mode="html")
    else:
        organizations = await OrganizationExtend.get_user_organizations(message.chat.id)

        if organizations:
            keyboard = await get_inline_keyb_markup(
                list_names=[org['name'] for org in organizations],
                list_data=[f"{org['id']}:{org['name']}" for org in organizations],
                callback_str="organization_to_issuance",
                number_cols=2
            )
            await state.set_data({
                'admin_id': admin_id,
            })
            await message.answer(text=text_start_issuance, reply_markup=keyboard, parse_mode="html")
        else:
            await message.answer(text=text_no_menu_items_orgs, parse_mode="html")


@rt.callback_query(StepsWriteIssuanceReport.select_organization, F.data.startswith("organization_to_issuance"))
async def choose_issuance_worker(callback: CallbackQuery, state: FSMContext):
    await state.set_state(StepsWriteIssuanceReport.select_worker)

    selected_org_params = await get_callb_content(callback.data, multiply_values=True)

    await state.update_data({
        'selected_org_id': selected_org_params[1],
        'selected_org_name': selected_org_params[2],
    })

    st_data = await state.get_data()
    ip_workers = await UserExtend.get_admin_users(st_data['admin_id'])

    keyboard = await get_inline_keyb_markup(
        list_names=[f"{w['fullname'].split(' ')[1]} - {w['profession']}" for w in ip_workers],
        list_data=[w['chat_id'] for w in ip_workers],
        callback_str="worker_to_issuance",
        number_cols=2
    )

    await callback.message.edit_text(text=text_select_worker_issuance, reply_markup=keyboard, parse_mode="html")


@rt.callback_query(StepsWriteIssuanceReport.select_worker, F.data.startswith("worker_to_issuance"))
async def set_volume_for_issuance(callback: CallbackQuery, state: FSMContext):
    await state.set_state(StepsWriteIssuanceReport.set_volume)
    selected_worker_id = await get_callb_content(callback.data)
    selected_worker = await UserExtend.get_by_id(selected_worker_id)

    await state.update_data({
        'selected_worker_id': selected_worker_id,
        'selected_worker_nickname': selected_worker.nickname
    })

    await callback.message.edit_text(text=text_set_volume_issuance, parse_mode="html")


@rt.message(StepsWriteIssuanceReport.set_volume, IsNotMainMenuMessage())
async def select_payment_method_issuance(message: Message, state: FSMContext, redis_wallets: RedisUserWallets):
    await state.set_state(StepsWriteIssuanceReport.select_payment_method)

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

    await message.answer(text=text_select_payment_method_issuance, reply_markup=keyboard, parse_mode="html")


@rt.callback_query(StepsWriteIssuanceReport.select_payment_method, F.data.startswith("select_payment_method_issuance"))
async def select_group_for_notify(callback: CallbackQuery, state: FSMContext):
    await state.set_state(StepsWriteIssuanceReport.select_notify_group)
    await state.update_data({
        'selected_payment_method': await get_callb_content(callback.data)
    })

    st_data = await state.get_data()
    notify_groups = await UserExtend.get_notify_groups(st_data['admin_id'])

    keyboard = await get_inline_keyb_markup(
        list_names=[ng['name'] for ng in notify_groups],
        list_data=[ng['chat_id'] for ng in notify_groups],
        callback_str="select_notify_group_issuance",
        number_cols=2
    )

    await callback.message.edit_text(text=text_select_notify_group_issuance, reply_markup=keyboard, parse_mode="html")


@rt.callback_query(StepsWriteIssuanceReport.select_notify_group, F.data.startswith("select_notify_group_issuance"))
async def end_write_issuance_of_report_to_bd(callback: CallbackQuery, state: FSMContext, bot_object: Bot, redis_users: RedisUser):
    selected_notify_group_chat_id = int(await get_callb_content(callback.data))
    st_data = await state.get_data()
    user = await UserExtend.get_by_id(callback.message.chat.id)

    # Генерируем сообщение уведомления ---------------------------------------------------------------------------------
    msg_in_group = await get_msg_notify_new_issuance_of_report(
        profession_worker=user.profession,
        fullname_worker=user.fullname,
        ip=st_data['selected_org_name'],
        nickname_second_worker=st_data['selected_worker_nickname'],
        volume=st_data['specified_volume'],
        payment_method=st_data['selected_payment_method']
    )

    # Создаем запись о новой выдаче под отчет в бд ---------------------------------------------------------------------
    issuance_report = await IssuanceReportExtend.add_new_issuance_report(
        user_id=callback.message.chat.id,
        org_name=st_data['selected_org_name'],
        selected_user_nickname=st_data['selected_worker_nickname'],
        selected_user_id=st_data['selected_worker_id'],
        volume=st_data['specified_volume'],
        payment_method=st_data['selected_payment_method'],
        selected_notify_group_id=selected_notify_group_chat_id
    )

    # Отправляем сообщение с подтверждением в группу -------------------------------------------------------------------
    try:
        message_notify = await bot_object.send_message(
            chat_id=selected_notify_group_chat_id,
            text=msg_in_group,
            parse_mode="html",
            reply_markup=await get_confirm_issuance_keyb_button(issuance_report.id),
        )

        # Добавляем id сообщения
        issuance_report.message_id = message_notify.message_id
        await issuance_report.save()

        await state.clear()
        await callback.message.edit_text(text=text_end_issuance, parse_mode="html")

    except Exception:
        # Удаляем запись о выдаче и группу из бд
        await issuance_report.delete()
        await NotifyGroupExtend.detach_group_from_admin(selected_notify_group_chat_id)
        await callback.answer(text=text_error_issuance, show_alert=True)
        await start_write_issuance_of_report_to_bd(message=callback.message, state=state, redis_users=redis_users)














