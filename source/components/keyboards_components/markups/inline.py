from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


keyb_markup_write_report_card = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Приход ➕", callback_data="come_work_rc"),
            InlineKeyboardButton(text="Уход ➖", callback_data="left_work_rc")
        ]
    ]
)

keyb_markup_end_delete_mi = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Да  ✅", callback_data="end_delete_menu_item"),
            InlineKeyboardButton(text="Нет  ⛔️", callback_data="cancel_delete_menu_item")
        ]
    ]
)
keyb_markup_end_delete_u = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Да  ✅", callback_data="end_delete_users"),
            InlineKeyboardButton(text="Нет  ⛔️", callback_data="cancel_delete_users")
        ]
    ]
)
keyb_markup_empty_user_list = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="➕", callback_data="add_user")
        ]
    ]
)
keyb_markup_choose_write_menu_sender = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Из подотчета", callback_data="choose_write_menu_sender:me"),
            InlineKeyboardButton(text="От ЮР Лица", callback_data="choose_write_menu_sender:org")
        ]
    ]
)
keyb_markup_pass_check_load = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Пропустить  ⏩", callback_data=f"pass_check_load")
        ]
    ]
)
keyb_markup_get_empty_list_orgs = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="➕", callback_data=f"add_organization")
        ]
    ]
)
keyb_markup_end_delete_org = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Да  ✅", callback_data="end_delete_organizations"),
            InlineKeyboardButton(text="Нет  ⛔️", callback_data="cancel_delete_organizations")
        ]
    ]
)
keyb_markup_get_empty_list_partners = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="➕", callback_data=f"add_partner")
        ]
    ]
)
keyb_markup_end_delete_partners = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Да  ✅", callback_data="end_delete_partners"),
            InlineKeyboardButton(text="Нет  ⛔️", callback_data="cancel_delete_partners")
        ]
    ]
)
keyb_markup_get_empty_list_banks = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="➕", callback_data=f"add_bank")
        ]
    ]
)
keyb_markup_end_delete_banks = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Да  ✅", callback_data="end_delete_banks"),
            InlineKeyboardButton(text="Нет  ⛔️", callback_data="cancel_delete_banks")
        ]
    ]
)
keyb_markup_end_delete_pa = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Да  ✅", callback_data="end_delete_payment_accounts"),
            InlineKeyboardButton(text="Нет  ⛔️", callback_data="cancel_delete_payment_accounts")
        ]
    ]
)
keyb_markup_start_manage_rq = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Согласующие", callback_data="assign:conciliator"),
            InlineKeyboardButton(text="Утверждающий", callback_data="assign:approver"),
        ],
        [
            InlineKeyboardButton(text="Казначей", callback_data="assign:treasurer"),
            InlineKeyboardButton(text="Табельщик", callback_data="assign:timekeeper")
        ]
    ]
)
