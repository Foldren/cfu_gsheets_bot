from models import ReportRequest


class ReportRequestExtend:
    __slots__ = {}

    @staticmethod
    async def get(id_rq: list):
        await ReportRequest.get(id=id_rq)

