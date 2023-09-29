from models import User, Partner


class PartnerExtend:
    __slots__ = {}

    @staticmethod
    async def add(name: str, inn: str, bank_reload_category_id: int, admin_id: int):
        await Partner.create(
            name=name,
            inn=inn,
            admin_id=admin_id,
            bank_reload_category_id=bank_reload_category_id,
        )

    @staticmethod
    async def get_by_id(partner_id):
        return await Partner.filter(id=partner_id).first()

    @staticmethod
    async def get_admin_partners(admin_chat_id):
        return await Partner.filter(admin_id=admin_chat_id).all().values("id", "name", "inn")

    @staticmethod
    async def delete_partners_by_ids(ids_partners_list: list):
        await Partner.filter(id__in=ids_partners_list).delete()

