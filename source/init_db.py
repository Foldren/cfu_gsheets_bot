from tortoise import Tortoise
from config import MYSQL_URL


async def init_db():
    # Here we create a SQLite DB using file "db.sqlite3"
    #  also specify the app name of "models"
    #  which contain models from "app.models"
    await Tortoise.init(
        db_url=MYSQL_URL,  # 'sqlite://upravlyaika.db'
        modules={'models': ["models"]},
    )

    # Generate the schema
    # await Tortoise.generate_schemas(safe=True)
