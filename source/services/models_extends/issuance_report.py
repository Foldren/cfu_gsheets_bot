from models import IssuanceReport


class IssuanceReportApi:
    @staticmethod
    async def add_new_issuance_report(user_id: int, ip: str, selected_user_nickname: str, volume: int,
                                      payment_method: str, selected_notify_group_id: int):
        return await IssuanceReport.create(user_id=user_id, ip=ip, selected_user_nickname=selected_user_nickname,
                                           volume=volume, payment_method=payment_method,
                                           notify_group_id=selected_notify_group_id)

    @staticmethod
    async def get_issuance_reports_by_user(user_id):
        return await IssuanceReport.filter(user_id=user_id).all().values("ip", "selected_user_nickname",
                                                                         "volume", "payment_method")

    @staticmethod
    async def check_issuance_report_by_nickname_and_id(recipient_nickname: str, id_issuance_report: int):
        issuance_reports = IssuanceReport.filter(selected_user_nickname=recipient_nickname, id=id_issuance_report)
        return True if issuance_reports is not None else False

    @staticmethod
    async def get_issuance_report_by_id(id_report):
        return await IssuanceReport.get(id=id_report)

    @staticmethod
    async def remove_issuance_report_by_id(id_report):
        await IssuanceReport.filter(id=id_report).delete()
