from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from components.filters import IsAdminFilter, IsNotMainMenuMessage
from components.keyboards_components.generators import get_inline_keyb_markup
from components.texts.admins.manage_partners import text_start_add_partner, text_end_add_partner, \
    text_select_bank_reload_category
from components.tools import get_msg_list_data, get_emoji_number, get_callb_content
from microservices.sql_models_extends.category import CategoryExtend
from microservices.sql_models_extends.partner import PartnerExtend
from states.admin.steps_manage_partners import StepsGetPartnersList, StepsAddPartner

rt = Router()

# Фильтр на проверку категории доступа пользователя
rt.message.filter(IsAdminFilter(), IsNotMainMenuMessage(), F.chat.type == "private")
rt.callback_query.filter(IsAdminFilter(), F.message.chat.type == "private")


@rt.callback_query(StepsGetPartnersList.get_list_partners, F.data.startswith("add_partner"))
async def start_add_partner(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(StepsAddPartner.start_add_partner)
    await callback.message.edit_text(text=text_start_add_partner, parse_mode="html")


@rt.message(StepsAddPartner.start_add_partner)
async def select_bank_reload_category(message: Message, state: FSMContext):
    await state.set_state(StepsAddPartner.select_bank_reload_category)

    data_new_partner = await get_msg_list_data(message.text)
    await state.set_data({
        'inn_new_partner': data_new_partner[0],
        'name_new_partner': data_new_partner[1],
    })

    admin_lower_categories = await CategoryExtend.get_admin_lower_categories_by_id(message.from_user.id)
    result_text = text_select_bank_reload_category
    names_categories_list = []

    i = 1
    for c in admin_lower_categories:
        category_queue = await CategoryExtend.get_parent_categories_names(c.id)
        emoji_number = await get_emoji_number(i)
        result_text += f"{emoji_number} {' → '.join(category_queue)}\n"
        names_categories_list.append(f"{emoji_number} {c.name}")
        i += 1

    keyboard = await get_inline_keyb_markup(
        list_names=names_categories_list,
        list_data=[c.id for c in admin_lower_categories],
        callback_str="selected_category_for_partner",
        number_cols=2,
    )

    await message.answer(text=result_text, reply_markup=keyboard, parse_mode="html")


@rt.callback_query(StepsAddPartner.select_bank_reload_category, F.data.startswith("selected_category_for_partner"))
async def end_add_partner(callback: CallbackQuery, state: FSMContext):
    selected_category_p_id = await get_callb_content(callback.data)
    st_data = await state.get_data()

    await PartnerExtend.add(
        inn=st_data['inn_new_partner'],
        name=st_data['name_new_partner'],
        bank_reload_category_id=selected_category_p_id,
        admin_id=callback.from_user.id,
    )

    await state.clear()
    await callback.message.edit_text(text=text_end_add_partner, parse_mode="html")


