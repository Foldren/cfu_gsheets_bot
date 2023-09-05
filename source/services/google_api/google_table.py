from datetime import datetime
from google.oauth2.service_account import Credentials
from gspread_asyncio import AsyncioGspreadClientManager


class GoogleTable:
    agcm: AsyncioGspreadClientManager
    json_creds_path = "upravlyaika-credentials.json"

    def __inti_credentials(self):
        creds = Credentials.from_service_account_file(self.json_creds_path)
        scoped = creds.with_scopes([
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ])
        return scoped

    def __init__(self):
        self.agcm = AsyncioGspreadClientManager(self.__inti_credentials)

    async def add_new_str_to_bd(self, table_url: str, chat_id_worker: int, fullname_worker: str, volume_op: str,
                                queue_op: str, type_op: str, payment_method: str):
        """
        Функция для добавления новой строки (записи) в гугл таблицу в лист БД
        Параметр type_op = profit или cost

        :param table_url: ссылка на гугл таблицу
        :param chat_id_worker: chat_id сотрудника в телеграм, который производит запись
        :param fullname_worker: полное имя сотрудника
        :param volume_op: сумма операции
        :param queue_op: очередь выбранных пунктов меню для выполнения операции через знак - ' → '
        :param type_op: значения profit или cost (соответственно тип операции доход или расход)
        :param payment_method: тип оплаты, либо банк
        """

        agc = await self.agcm.authorize()
        ss = await agc.open_by_url(table_url)
        ws = await ss.worksheet("БД")
        frmt_date_time = datetime.now().strftime('%d.%m.%Y %H:%M')
        frmt_date = datetime.now().strftime('%d.%m.%Y')
        queue_items = queue_op.split(" → ")
        menu_item_lvls = [" ", " ", " ", " ", " "]
        type_op = "Доход" if type_op == "profit" else "Расход"
        volume_with_sign = -int(volume_op) if type_op == "cost" else int(volume_op)
        surname_fstname = fullname_worker.split(" ")[1] + " " + fullname_worker.split(" ")[0]
        current_year = datetime.today().year
        current_month = datetime.today().month
        current_week = datetime.today().isocalendar().week
        current_day = datetime.today().day

        i = 0
        for e in queue_items:
            menu_item_lvls[i] = e
            i += 1

        await ws.append_row([str(chat_id_worker),
                             surname_fstname,
                             str(volume_op),
                             frmt_date_time,
                             type_op,
                             menu_item_lvls[4],
                             menu_item_lvls[3],
                             payment_method,
                             " ",
                             frmt_date,
                             " ",
                             volume_with_sign,
                             current_year,
                             current_month,
                             current_week,
                             current_day,
                             " ",
                             frmt_date,
                             " ",
                             menu_item_lvls[2],
                             menu_item_lvls[1]
                             ])
