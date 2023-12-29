from tortoise import Tortoise
from tortoise.exceptions import OperationalError
from config import MYSQL_URL
from models import PeriodStat


async def init_db():
    # Here we create a SQLite DB using file "db.sqlite3"
    #  also specify the app name of "models"
    #  which contain models from "app.models"
    await Tortoise.init(
        db_url=MYSQL_URL,  # 'sqlite://upravlyaika.db'
        modules={'models': ["models"]},
    )

    try:
        await PeriodStat.all()
    except OperationalError:
        # Generate the schema
        await Tortoise.generate_schemas(safe=True)

        new_ps = [
            PeriodStat(name="Ежедневный"),
            PeriodStat(name="Еженедельный"),
            PeriodStat(name="Ежемесячный"),
            PeriodStat(name="Dashboard"),
            PeriodStat(name="Чеки"),
        ]

        await PeriodStat.bulk_create(new_ps)
