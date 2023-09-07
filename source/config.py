from pathlib import Path
from os import getcwd, getenv
from aiogram.fsm.storage.memory import MemoryStorage
from environs import Env

env = Env()
env.read_env('.env')

IS_THIS_LOCAL = "Pycharm" in str(Path.cwd())
TOKEN = getenv("LOCAL_TOKEN_BOT") if IS_THIS_LOCAL else env('TOKEN_BOT')
MYSQL_URL = getenv('MYSQL_URL') if IS_THIS_LOCAL else env("MYSQL_URL")  # getenv для терминала Pycharm

# К сожалению для миграций придется указывать ссылку напрямую
AERICH_CONFIG = {
    "connections": {"default": MYSQL_URL},
    "apps": {
        "models": {
            "models": ["source.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}  # "connections": {"default": "sqlite://source/upravlyaika.db"},
MEMORY_STORAGE = MemoryStorage()
BANKS_UPRAVLYAIKA = ["Точка", "Модуль", "Сбер", "Тинькофф", "Альфа", "Наличные"]
CHECKS_PATH = getcwd() + "/misc/images/checks/"
