from models import PaymentAccount


class PaymentAccountExtend:
    __slots__ = {}

    @staticmethod
    async def add(number: str, first_date_load_statement: int, bank_id: int, organization_id: int):
        await PaymentAccount.create(
            number=number,
            first_date_load_statement=first_date_load_statement,
            bank_id=bank_id,
            organization_id=organization_id
        )

    @staticmethod
    async def get_by_id(payment_account_id):
        return await PaymentAccount.filter(id=payment_account_id).first()

    @staticmethod
    async def get_bank_payment_accounts(bank_id):
        return await PaymentAccount.filter(bank_id=bank_id).all()

    @staticmethod
    async def get_pa_by_ids(ids_pa_list: list):
        return await PaymentAccount.filter(id__in=ids_pa_list).all()

    @staticmethod
    async def delete_payment_accounts_by_ids(ids_payment_accounts_list: list):
        await PaymentAccount.filter(id__in=ids_payment_accounts_list).delete()

