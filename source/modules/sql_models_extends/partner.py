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
    async def get_by_name(partner_name):
        return await Partner.filter(name=partner_name).first()

    @staticmethod
    async def get_admin_partners(admin_chat_id):
        return await Partner.filter(admin_id=admin_chat_id).all().values("id", "name", "inn", "bank_reload_category__id")

    @staticmethod
    async def delete_partners_by_ids(ids_partners_list: list):
        await Partner.filter(id__in=ids_partners_list).delete()

    @staticmethod
    async def update_bank_rel_cat_by_id(partner_id: int, reload_category_id: int):
        await Partner.filter(id=partner_id).update(bank_reload_category_id=reload_category_id)


