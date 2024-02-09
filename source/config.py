from pathlib import Path
from os import getcwd, getenv, environ
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

load_dotenv()

IS_THIS_LOCAL = "Pycharm" in str(Path.cwd())

REDIS_URL = environ["REDIS_URL"] if IS_THIS_LOCAL else getenv('REDIS_URL')

TOKEN = environ["TOKEN_BOT"] if IS_THIS_LOCAL else getenv('TOKEN_BOT')

TECHNICAL_SUPPORT_GROUP_CHAT_ID = -4023565993

MYSQL_URL = environ['MYSQL_URL'] if IS_THIS_LOCAL else getenv("MYSQL_URL")

UPRAV_CREDS_URL = str(getcwd()) + "/source/upravlyaika-credentials.json"

SECRET_KEY = getenv("SECRET_KEY")

MEMORY_STORAGE = MemoryStorage()

BANKS_UPRAVLYAIKA = ["Точка", "Модуль", "Сбер", "Тинькофф", "Альфа", "Наличные", "Другой"]

SUPER_ADMINS_CHAT_ID = [330061031, 708742962]

STATS_UPRAVLYAIKA = ["Ежедневный", "Еженедельный", "Ежемесячный", "Dashboard", "Чеки"]

NAME_GOOGLE_TABLE_BD_LIST = "БД (не редактировать)"

NAME_GOOGLE_TABLE_ACCOUNTING_LIST = "Учёт"

NAME_GOOGLE_TABLE_REPORT_CARD_LIST = "БД Табель (не редактировать)"

NAME_GOOGLE_TABLE_DASHBOARD = "Dashboard"

CHECKS_PATH = getcwd() + "/misc/images/checks/"

IMAGES_PATH = getcwd() + "/misc/images/"

ROLES = ['timekeeper']

DEFINE_STATUSES = ["🔴 Не пришел:", "🟢 На работе:", "🔵 Ушел:"]

BANKS_RUS_NAMES = {
    'tinkoff': 'Тинькофф',
    'module': 'Модуль',
    'tochka': 'Точка'
}

AERICH_CONFIG = {
    "connections": {"default": environ['MYSQL_URL']},
    "apps": {
        "models": {
            "models": ["source.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}

MAIN_MENU_MSGS = ["Меню", "Сотрудники", "Режим: Админ 👨‍💼", "Операция с категориями", "Операция с подотчетами",
                  "Перевод на кошелек", "Выдача в подотчет", "Возврат подотчета", "Режим: Юзер 🙎‍♂️",
                  "Отчеты", "Управление отчетами", "Кошельки", "Изменение списка кошельков", "⬅️ Назад в главное меню",
                  "Ежедневный", "Еженедельный", "Категории", "ЮР Лица",
                  "Ежемесячный", "Остаток в подотчете", "/start", "/restart", "Контрагенты", "Банки и расчётные счета",
                  "Поддержка", "Назначение ролей", "Табель"
                  ]  # Все новые reply кнопки добавлять сюда

STAGES_REPS_REQS_BY_ROLE = {
    'conciliator': 'conciliate',
    'approver': 'approve',
    'treasurer': 'treasure',
}

ROLE_BY_STAGES_REPS_REQS = {
    'conciliate': 'conciliator',
    'approve': 'approver',
    'treasure': 'treasurer',
}

