from datetime import datetime
from cryptography.fernet import Fernet
from google.oauth2.service_account import Credentials
from gspread_asyncio import AsyncioGspreadClientManager
from config import NAME_GOOGLE_TABLE_ACCOUNTING_LIST, NAME_GOOGLE_TABLE_BD_LIST, STATS_UPRAVLYAIKA, SECRET_KEY, \
    NAME_GOOGLE_TABLE_REPORT_CARD_LIST, NAME_GOOGLE_TABLE_DASHBOARD


class GoogleTable:
    agcm: AsyncioGspreadClientManager
    json_creds_path = "upravlyaika-credentials.json"  # "universe_domain": "googleapis.com"

    def __init_credentials(self):
        creds = Credentials.from_service_account_file(self.json_creds_path)
        scoped = creds.with_scopes([
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ])
        return scoped

    def __init__(self):
        self.agcm = AsyncioGspreadClientManager(self.__init_credentials)

    async def get_dashboard(self, table_encr_url: str):
        table_decr_url = Fernet(SECRET_KEY).decrypt(table_encr_url).decode("utf-8")
        agc = await self.agcm.authorize()
        ss = await agc.open_by_url(table_decr_url)
        ws = await ss.worksheet(NAME_GOOGLE_TABLE_DASHBOARD)

        dashboard_info = await ws.get('D4:K13')

        return {
            "Продажа товара": dashboard_info[0][0],
            "Расходы за период": dashboard_info[0][3],
            "Остатки на расчетном счете ИП": dashboard_info[0][6],
            "К оплате": dashboard_info[4][0],
            "Закупка товара": dashboard_info[4][3],
            "Остатки у физ лиц": dashboard_info[4][6],
            "Общая Прибыль": dashboard_info[8][0],
            "Удержания на МП": dashboard_info[8][3],
        }

    async def write_new_report_card_user(self, table_encr_url: str, chat_id_user: int, name_user: str, status_i: int,
                                         bet: int, increased_bet: int, last_time_come_to_work: str):
        # status_i 1 - приход, 2 - уход
        table_decr_url = Fernet(SECRET_KEY).decrypt(table_encr_url).decode("utf-8")
        agc = await self.agcm.authorize()
        ss = await agc.open_by_url(table_decr_url)
        ws = await ss.worksheet(NAME_GOOGLE_TABLE_REPORT_CARD_LIST)
        frmt_date_time = datetime.now().strftime('%d.%m.%Y %H:%M')
        define_statuses = {1: "Приход", 2: "Уход"}
        time_worked = ""
        if status_i == 2:
            last_time_come_to_work = datetime.strptime(last_time_come_to_work, '%d.%m.%Y-%H:%M')
            td_time_worked = datetime.now() - last_time_come_to_work
            time_worked = str(td_time_worked).split(":")[0] + ":" + str(td_time_worked).split(":")[1]

        await ws.append_row([chat_id_user,
                             name_user,
                             define_statuses[status_i],
                             frmt_date_time,
                             bet,
                             increased_bet,
                             time_worked,
                             ], value_input_option='USER_ENTERED')

    async def distribute_statement_operations(self, table_encr_url: str, inn_partner: str,
                                              name_partner: str, list_queue_category: list):
        """
        Метод распределения операций в листе БД, если инн партнера еще нет в таблице, то возвращает False
        (на месте "Без распределения" ставит очередь категорий, на месте названия контрагента ставит новое)

        :param list_queue_category: очередь категорий
        :param table_encr_url: ссылка на гугл таблицу
        :param inn_partner: инн контрагента
        :param name_partner: наименование контрагента
        :return: bool_partner_in_bd - в случае, если контрагента еще нет в БД
        """

        table_decr_url = Fernet(SECRET_KEY).decrypt(table_encr_url).decode("utf-8")
        agc = await self.agcm.authorize()
        ss = await agc.open_by_url(table_decr_url)
        ws = await ss.worksheet(NAME_GOOGLE_TABLE_BD_LIST)

        bd_values_rows = await ws.get_all_values()
        inns_col = await ws.col_values(13)
        number_rows = len(bd_values_rows)

        bd_values_rows.pop(0)

        if inn_partner in inns_col:
            for i in range(0, 6):
                if i > len(list_queue_category):
                    list_queue_category.append("")

            for i, row in enumerate(bd_values_rows):
                if row[12] == inn_partner:
                    bd_values_rows[i][1] = name_partner

                    # Записываем категорию
                    for k, elem in enumerate(list_queue_category):
                        bd_values_rows[i][7+k] = elem

            await ws.update(range_name=f"A2:M{number_rows}", values=bd_values_rows)
            return True
        else:
            return False

    async def get_stats_dict_encr_urls(self, table_encr_url: str) -> dict:
        """
        Метод для вывода списка ссылок на листы с отчетами (используя ссылку на таблицу)

        :param table_encr_url: ссылка на гугл таблицу
        :return: dict_stats_urls: словарь отчетов со ссылками на листы
        """

        table_decr_url = Fernet(SECRET_KEY).decrypt(table_encr_url).decode("utf-8")
        agc = await self.agcm.authorize()
        ss = await agc.open_by_url(table_decr_url)
        f = Fernet(SECRET_KEY)
        result_stats_urls = {}

        for stat_name in STATS_UPRAVLYAIKA:
            if stat_name == "Чеки":
                continue
            ws = await ss.worksheet(stat_name)
            result_stats_urls[stat_name] = f.encrypt(ws.url.encode())

        return result_stats_urls

    async def add_new_str_to_bd(self, table_encr_url: str, chat_id_worker: int, fullname_worker: str, volume_op: str,
                                org_op: str, queue_op: str, type_op: str, payment_method: str,
                                sender_is_org: bool = False):
        """
        Метод для добавления новой строки (записи) в гугл таблицу в лист БД
        Параметр type_op = profit или cost

        :param org_op: наименование организации
        :param sender_is_org: флаг, что исполнитель - юр лицо
        :param table_encr_url: ссылка на гугл таблицу
        :param chat_id_worker: chat_id сотрудника в телеграм, который производит запись
        :param fullname_worker: полное имя сотрудника
        :param volume_op: сумма операции
        :param queue_op: очередь выбранных категорий для выполнения операции через знак - ' → '
        :param type_op: значения profit или cost (соответственно тип операции доход или расход)
        :param payment_method: тип оплаты, либо банк
        """

        table_decr_url = Fernet(SECRET_KEY).decrypt(table_encr_url).decode("utf-8")
        agc = await self.agcm.authorize()
        ss = await agc.open_by_url(table_decr_url)
        ws = await ss.worksheet(NAME_GOOGLE_TABLE_BD_LIST)
        frmt_date_time = datetime.now().strftime('%d.%m.%Y %H:%M')
        queue_items = queue_op.split(" → ")
        menu_item_lvls = [" ", " ", " ", " ", " ", " "]
        profit_or_cost = type_op == "profit"
        type_op = "Доход" if profit_or_cost else "Расход"
        volume_with_sign = volume_op if profit_or_cost else -int(volume_op)
        surname_fstname = fullname_worker.split(" ")[1] + " " + fullname_worker.split(" ")[0]

        i = 0
        for e in queue_items:
            menu_item_lvls[i] = e
            i += 1

        await ws.append_row([int(chat_id_worker),
                             "ЮР Лицо" if sender_is_org else surname_fstname,
                             frmt_date_time,
                             type_op,
                             payment_method,
                             volume_with_sign,
                             org_op,
                             menu_item_lvls[0],
                             menu_item_lvls[1],
                             menu_item_lvls[2],
                             menu_item_lvls[3],
                             menu_item_lvls[4]
                             ], value_input_option='USER_ENTERED')
        # value_input_option='USER_ENTERED' решает проблему с апострофом который появляется в таблице

    async def add_issuance_report_to_bd(self, table_encr_url: str, chat_id_worker: int, fullname_recipient: str,
                                        volume_op: str, payment_method: str, org_name: str,
                                        return_issuance: bool = False):
        table_decr_url = Fernet(SECRET_KEY).decrypt(table_encr_url).decode("utf-8")
        agc = await self.agcm.authorize()
        ss = await agc.open_by_url(table_decr_url)
        ws = await ss.worksheet(NAME_GOOGLE_TABLE_BD_LIST)

        frmt_date_time = datetime.now().strftime('%d.%m.%Y %H:%M')
        volume_with_sign = -int(volume_op)
        surname_fstname = fullname_recipient.split(" ")[1] + " " + fullname_recipient.split(" ")[0]

        if return_issuance:
            text_operation_str_1 = "Возврат подотчётных средств"
            text_operation_str_2 = "Получение подотчётных средств"
            name_sender = surname_fstname
            name_recipient = "ЮР Лицо"
        else:
            text_operation_str_1 = "Выдача под отчет"
            text_operation_str_2 = "Получение под отчет"
            name_sender = "ЮР Лицо"
            name_recipient = surname_fstname

        row_1 = [int(chat_id_worker), name_sender, str(frmt_date_time), "Расход", payment_method, volume_with_sign,
                 org_name, "Техническая операция", text_operation_str_1]
        row_2 = [int(chat_id_worker), name_recipient, str(frmt_date_time), "Доход", payment_method, volume_op,
                 org_name, "Техническая операция", text_operation_str_2]

        await ws.append_rows([row_1, row_2], value_input_option='USER_ENTERED')

    async def add_transfer_to_bd(self, table_encr_url: str, chat_id_worker: int, volume_op: str,
                                 wallet_sender: str, wallet_recipient: str, org_name: str):
        table_decr_url = Fernet(SECRET_KEY).decrypt(table_encr_url).decode("utf-8")
        agc = await self.agcm.authorize()
        ss = await agc.open_by_url(table_decr_url)
        ws = await ss.worksheet(NAME_GOOGLE_TABLE_BD_LIST)

        frmt_date_time = datetime.now().strftime('%d.%m.%Y %H:%M')
        volume_with_sign = -int(volume_op)

        row_1 = [int(chat_id_worker), "ЮР Лицо", str(frmt_date_time), "Расход", wallet_sender, volume_with_sign,
                 org_name,
                 "Техническая операция", "Перевод"]
        row_2 = [int(chat_id_worker), "ЮР Лицо", str(frmt_date_time), "Доход", wallet_recipient, volume_op, org_name,
                 "Техническая операция", "Перевод"]

        await ws.append_rows([row_1, row_2], value_input_option='USER_ENTERED')

    async def get_balance_in_report_by_fullname(self, table_encr_url: str, chat_id_user: int):
        table_decr_url = Fernet(SECRET_KEY).decrypt(table_encr_url).decode("utf-8")
        agc = await self.agcm.authorize()
        ss = await agc.open_by_url(table_decr_url)
        ws = await ss.worksheet(NAME_GOOGLE_TABLE_ACCOUNTING_LIST)
        user_balances = await ws.get_all_values()
        result = []

        for i in range(0, len(user_balances)):
            if user_balances[i][1] == str(chat_id_user):
                result.append(user_balances[i][2:])

        return result
