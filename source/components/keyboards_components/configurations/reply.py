from aiogram.types import ReplyKeyboardMarkup
from components.keyboards_components.keyboards.reply import keyb_start_admin, keyb_start_user, \
    keyb_start_user_admin, keyb_operation_under_stats, keyb_wallets


cf_keyb_start_admin = ReplyKeyboardMarkup(
    keyboard=keyb_start_admin,
    resize_keyboard=True,  # меняем размер клавиатуры
)
cf_keyb_start_user = ReplyKeyboardMarkup(
    keyboard=keyb_start_user,
    resize_keyboard=True,  # меняем размер клавиатуры
)
cf_keyb_start_user_admin = ReplyKeyboardMarkup(
    keyboard=keyb_start_user_admin,
    resize_keyboard=True,  # меняем размер клавиатуры
)
cf_keyb_operation_under_stats = ReplyKeyboardMarkup(
    keyboard=keyb_operation_under_stats,
    resize_keyboard=True,  # меняем размер клавиатуры
)
cf_keyb_wallets = ReplyKeyboardMarkup(
    keyboard=keyb_wallets,
    resize_keyboard=True,  # меняем размер клавиатуры
)
