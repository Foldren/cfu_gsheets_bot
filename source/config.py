from pathlib import Path
from os import getcwd, getenv
from aiogram.fsm.storage.memory import MemoryStorage
from environs import Env

env = Env()
env.read_env('.env')

IS_THIS_LOCAL = "Pycharm" in str(Path.cwd())
REDIS_URL = getenv("REDIS_URL") if IS_THIS_LOCAL else env('REDIS_URL')
TOKEN = getenv("LOCAL_TOKEN_BOT") if IS_THIS_LOCAL else env('TOKEN_BOT')
TECHNICAL_SUPPORT_GROUP_CHAT_ID = -4023565993
MYSQL_URL = getenv('MYSQL_URL') if IS_THIS_LOCAL else env("MYSQL_URL")  # getenv для терминала Pycharm
# К сожалению для миграций придется указывать ссылку напрямую
AERICH_CONFIG = {
    "connections": {"default": "mysql://root:KLyXjPfvDL1tKbNHK8_sVwUBrdTFER@158.160.105.173:3306/upravlyaika_db"},
    "apps": {
        "models": {
            "models": ["source.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}  # "connections": {"default": "sqlite://source/upravlyaika.db"},
MEMORY_STORAGE = MemoryStorage()
BANKS_UPRAVLYAIKA = ["Точка", "Модуль", "Сбер", "Тинькофф", "Альфа", "Наличные", "Другой"]
BANKS_RUS_NAMES = {
    'tinkoff': 'Тинькофф',
    'module': 'Модуль',
    'tochka': 'Точка',
}
STATS_UPRAVLYAIKA = ["Dashboard", "Ежедневный", "Еженедельный", "Ежемесячный"]
SECRET_KEY = getenv("SECRET_KEY") if IS_THIS_LOCAL else env('SECRET_KEY')
NAME_GOOGLE_TABLE_BD_LIST = "БД (не редактировать)"
NAME_GOOGLE_TABLE_ACCOUNTING_LIST = "Учёт"
CHECKS_PATH = getcwd() + "/misc/images/checks/"
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
ROLES = ['timekeeper']
