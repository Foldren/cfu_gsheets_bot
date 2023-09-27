from models import Bank


class BankExtend:
    __slots__ = {}

    @staticmethod
    async def add(custom_name: str, bank_name: int, api_key: int, admin_id: int):
        await Bank.create(
            custom_name=custom_name,
            api_key=api_key,
            bank_name=bank_name,
            admin_id=admin_id
        )

    @staticmethod
    async def get_by_id(bank_id):
        return await Bank.filter(id=bank_id).first()

    @staticmethod
    async def get_admin_banks(admin_chat_id):
        return await Bank.filter(admin_id=admin_chat_id).all().values("id", "custom_name", "bank_name")

    @staticmethod
    async def delete_banks_by_ids(ids_banks_list: list):
        await Bank.filter(id__in=ids_banks_list).delete()

