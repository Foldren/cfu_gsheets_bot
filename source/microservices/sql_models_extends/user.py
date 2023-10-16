from typing import List, Any, Tuple

from aiogram.types import Message
from cryptography.fernet import Fernet
from tortoise.expressions import Q
from datetime import datetime, timedelta
from components.texts.users.show_user_stats import text_fst_load_dashboard
from config import SECRET_KEY
from microservices.google_api.google_table import GoogleTable
from models import User, AdminInfo, WorkerRoleForReports, ReportRequest, ConfirmNotification


class UserExtend:
    __slots__ = {}

    @staticmethod
    async def get_user_role(chat_id) -> str:
        role_obj = await WorkerRoleForReports.filter(worker_id=chat_id).values_list('role', flat=True)
        return role_obj[0]

    @staticmethod
    async def get_notifications(chat_id):
        return await ConfirmNotification.filter(user_id=chat_id).all()

    @staticmethod
    async def send_confirm_notify_to_users_by_role(admin_id, role_recipients, volume, comment, nickname_sender):
        expr = Q(admin_id=admin_id) | Q(chat_id=admin_id)
        recipients = await User.filter(expr, role_for_reports__role=role_recipients).all()

        match role_recipients:
            case 'conciliator':
                stage = 'conciliate'
            case 'approver':
                stage = 'approve'
            case _:
                stage = 'treasure'

        report_request = await ReportRequest.create(
            stage=stage,
            volume=volume,
            comment=comment,
            nickname_sender=nickname_sender,
            time_delete=datetime.now() + timedelta(hours=24)
        )

        list_notifications = []
        for r in recipients:
            confirm_notification = ConfirmNotification(
                report_request=report_request,
                type='report_request',
                user=r
            )
            list_notifications.append(confirm_notification)

        await ConfirmNotification.bulk_create(list_notifications)

    @staticmethod
    async def get_users_by_role(admin_id: int, role: str) -> list[User]:
        return await User.filter(Q(admin_id=admin_id) | Q(chat_id=admin_id), role_for_reports__role=role).all()

    @staticmethod
    async def change_roles_for_admin_users(admin_id: int, users_chat_id_list: list[int], role: str):
        user_new_roles = []
        expression = Q(worker__admin_id=admin_id) | Q(worker_id=admin_id)
        id_roles_objs = await WorkerRoleForReports.filter(expression, role=role).values_list("id", flat=True)
        await WorkerRoleForReports.filter(id__in=id_roles_objs).delete()
        for user_chat_id in users_chat_id_list:
            user_new_roles.append(WorkerRoleForReports(worker_id=user_chat_id, role=role))
        await WorkerRoleForReports.bulk_create(user_new_roles)

    @staticmethod
    async def get_user_periods_stats_list(user_chat_id):
        user = await User.get(chat_id=user_chat_id)
        p_stats = await user.periods_stats.all().values_list("name", flat=True)
        return p_stats

    @staticmethod
    async def get_admin_stats_urls_by_names(admin_chat_id, stats_names_list, gt_object: GoogleTable, message: Message):
        admin = await User.get(chat_id=admin_chat_id)
        admin_info = await admin.admin_info
        dashboard_url, s_day_url, s_week_url, s_month_url = admin_info.gt_dashboard_url, admin_info.gt_day_stat_url, \
                                                            admin_info.gt_week_stat_url, admin_info.gt_month_stat_url

        if (dashboard_url in [None, b""]) or (s_day_url in [None, b""]) \
                or (s_week_url in [None, b""]) or (s_month_url in [None, b""]):
            await message.answer(text_fst_load_dashboard, parse_mode="html")
            dict_urls = await gt_object.get_stats_dict_encr_urls(admin_info.google_table_url)
            admin_info.gt_dashboard_url = dict_urls["Dashboard"]
            admin_info.gt_day_stat_url = dict_urls["Ежедневный"]
            admin_info.gt_week_stat_url = dict_urls["Еженедельный"]
            admin_info.gt_month_stat_url = dict_urls["Ежемесячный"]
            await admin_info.save()

        list_urls = []
        f = Fernet(SECRET_KEY)
        for st_name in stats_names_list:
            url_for_stat = ""
            if st_name == "Dashboard":
                url_for_stat = f.decrypt(admin_info.gt_dashboard_url).decode('utf-8')
            elif st_name == "Ежедневный":
                url_for_stat = f.decrypt(admin_info.gt_day_stat_url).decode('utf-8')
            elif st_name == "Еженедельный":
                url_for_stat = f.decrypt(admin_info.gt_week_stat_url).decode('utf-8')
            elif st_name == "Ежемесячный":
                url_for_stat = f.decrypt(admin_info.gt_month_stat_url).decode('utf-8')
            list_urls.append(url_for_stat)

        return list_urls

    @staticmethod
    async def get_table_url(admin_chat_id):
        admin = await User.get(chat_id=admin_chat_id)
        admin_info = await admin.admin_info
        return admin_info.google_table_url

    @staticmethod
    async def get_notify_groups(admin_id):
        admin = await User.get(chat_id=admin_id)
        return await admin.notify_groups.all().values("chat_id", "name")

    @staticmethod
    async def invert_mode(admin_id):
        admin_info = await AdminInfo.get(admin_id=admin_id)
        admin_info.admin_mode = not admin_info.admin_mode
        await admin_info.save()

    @staticmethod
    async def get_admin_info(admin_id):
        return await AdminInfo.get(admin_id=admin_id)

    @staticmethod
    async def get_admins_id_list():
        return await User.filter(admin_id=None).all().values_list("chat_id", flat=True)

    @staticmethod
    async def get_users_id_list():
        return await User.exclude(admin_id=None).all().values_list("chat_id", flat=True)

    @staticmethod
    async def get_members_id_list():
        return await User.all().values_list("chat_id", flat=True)

    @staticmethod
    async def get_by_id(id_user: int) -> User:
        return await User.filter(chat_id=id_user).first()

    @staticmethod
    async def get_by_nickname(nickname: str) -> User:
        return await User.filter(nickname=nickname).first()

    @staticmethod
    async def get_user_admin_id(id_user: int) -> int:
        user = await User.get(chat_id=id_user)
        return user.admin_id if user.admin_id else id_user

    @staticmethod
    async def get_admin_users(id_admin: int, include_admin: bool = False, only_none_and_role: str = None):
        values_list = ["nickname", "fullname", "profession", "chat_id"]
        expression = Q(role_for_reports__role=None) | Q(role_for_reports__role=only_none_and_role)
        if only_none_and_role is not None:
            values_list.append("role_for_reports__role")
            admin_users = await User.filter(expression, admin_id=id_admin).all().values(*values_list)
            if include_admin:
                admin_user = await User.filter(expression, chat_id=id_admin).first().values(*values_list)
                if admin_user is not None:
                    admin_users.insert(0, admin_user)
        else:
            admin_users = await User.filter(admin_id=id_admin).all().values(*values_list)
            if include_admin:
                admin_users.insert(0, await User.get(chat_id=id_admin).values(*values_list))
        return admin_users

    @staticmethod
    async def add(chat_id: int, nickname: str, fullname: str, profession: str, id_admin: int):
        await User.create(chat_id=chat_id, nickname=nickname, fullname=fullname, profession=profession,
                          admin_id=id_admin)

    @staticmethod
    async def update_by_id(chat_id: int, nickname: str = None, fullname: str = None, profession: str = None,
                           id_admin: int = None, new_chat_id: int = None):
        user = await User.get(chat_id=chat_id)

        user.chat_id = chat_id if new_chat_id is None else new_chat_id

        if nickname is not None:
            user.nickname = nickname
        if fullname is not None:
            user.fullname = fullname
        if profession is not None:
            user.profession = profession
        if id_admin is not None:
            user.id_admin = id_admin

        await user.save()

    @staticmethod
    async def delete_users_by_chat_ids(chat_ids_users_list: list):
        await User.filter(chat_id__in=chat_ids_users_list).delete()
