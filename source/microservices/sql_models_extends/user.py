from datetime import datetime, timedelta
from sys import maxsize

from aiogram.types import Message
from cryptography.fernet import Fernet
from tortoise.expressions import Q
from components.texts.users.show_user_stats import text_fst_load_dashboard
from config import SECRET_KEY
from microservices.google_api.google_table import GoogleTable
from models import User, AdminInfo, ReportRequest, ConfirmNotification, Role, PeriodStat


class UserExtend:
    __slots__ = {}

    @staticmethod
    async def check_all_users_roles_exist(admin_id):
        expr = Q(admin_id=admin_id) | Q(chat_id=admin_id)
        users_chat_ids = await User.filter(expr).values_list('chat_id', flat=True)
        conciliators = await Role.filter(user_id__in=users_chat_ids, name='conciliator', type='report_request')
        approvers = await Role.filter(user_id__in=users_chat_ids, name='approver', type='report_request')
        treasures = await Role.filter(user_id__in=users_chat_ids, name='treasurer', type='report_request')
        return (conciliators != []) and (approvers != []) and (treasures != [])

    @staticmethod
    async def get_user_role(chat_id: int, role_type: str) -> str:
        role_obj = await Role.filter(user_id=chat_id, type=role_type).values_list('name', flat=True)
        return role_obj[0] if role_obj else None

    @staticmethod
    async def get_notifications(chat_id, type_n: str = None):
        match type_n:
            case 'n_conciliate_report_request':
                expr = Q(report_request__stage='conciliate') & Q(user_id=chat_id)
            case 'n_approve_report_request':
                expr = Q(report_request__stage='approve') & Q(user_id=chat_id)
            case 'n_treasure_report_request':
                expr = Q(report_request__stage='treasure') & Q(user_id=chat_id)
            case _:
                expr = Q(user_id=chat_id)

        return await ConfirmNotification.filter(expr).all()

    @staticmethod
    async def send_confirm_notify_to_users_by_role(admin_id: int, role_recipients: str, volume: int, comment: str,
                                                   nickname_sender: str):
        expr = Q(admin_id=admin_id) | Q(chat_id=admin_id)
        recipients = await User.filter(expr, roles__name=role_recipients).all()

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
    async def change_users_roles(admin_id: int, users_chat_id_list: list[int], role: str, role_type: str):
        expr_u = Q(admin_id=admin_id) | Q(chat_id=admin_id)
        users_with_admin_ids = await User.filter(expr_u).values_list('chat_id', flat=True)

        expr = Q(user_id__in=users_with_admin_ids) & Q(type=role_type)
        users_type_roles = await Role.filter(expr).all()

        for i in range(0, len(users_type_roles)):
            role_user = await users_type_roles[i].user
            if role_user.chat_id in users_chat_id_list:
                users_type_roles[i].name = role
            elif users_type_roles[i].name == role:
                users_type_roles[i].name = None

        await Role.bulk_update(users_type_roles, fields=['name'])

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
            if st_name == "Ежедневный":
                url_for_stat = f.decrypt(admin_info.gt_day_stat_url).decode('utf-8')
            elif st_name == "Еженедельный":
                url_for_stat = f.decrypt(admin_info.gt_week_stat_url).decode('utf-8')
            elif st_name == "Ежемесячный":
                url_for_stat = f.decrypt(admin_info.gt_month_stat_url).decode('utf-8')
            else:
                continue
            list_urls.append(url_for_stat)

        return list_urls

    @staticmethod
    async def get_table_url(admin_chat_id):
        admin = await User.get(chat_id=admin_chat_id)
        admin_info = await admin.admin_info
        return admin_info.google_table_url

    @staticmethod
    async def get_notify_groups(admin_id, only_chat_ids: bool = False):
        admin = await User.get(chat_id=admin_id)
        if only_chat_ids:
            notify_groups = await admin.notify_groups.all().values_list("chat_id", flat=True)
        else:
            notify_groups = await admin.notify_groups.all().values("chat_id", "name")
        return notify_groups

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
    async def get_admin_users(id_admin: int, include_admin: bool = False, only_ids: bool = False):
        values_list = ["nickname", "fullname", "profession", "chat_id"]
        expr = Q(admin_id=id_admin) | Q(chat_id=id_admin) if include_admin else Q(admin_id=id_admin)
        if only_ids:
            admin_users = await User.filter(expr).all().values_list("chat_id", flat=True)
        else:
            admin_users = await User.filter(expr).all().values(*values_list)
        return admin_users

    @staticmethod
    async def get_users_by_role_and_type(id_admin: int, role: str, role_type: str):
        values_list = ["nickname", "fullname", "profession", "chat_id", "roles__name"]
        expr = ((Q(roles__type=role_type) & Q(roles__name=role)) | (Q(roles__type=role_type) & Q(roles__name=None))) & \
               (Q(admin_id=id_admin) | Q(chat_id=id_admin))
        admin_users = await User.filter(expr).all().values(*values_list)
        return admin_users

    @staticmethod
    async def add(chat_id: int, nickname: str, fullname: str, profession: str,
                  bet: int, increased_bet: int, id_admin: int = None, google_table_url: str = None,
                  google_drive_dir_url: str = None):
        user = await User.create(chat_id=chat_id, nickname=nickname, fullname=fullname, profession=profession,
                                 admin_id=id_admin, bet=bet, increased_bet=increased_bet)
        await Role.bulk_create([Role(user_id=chat_id, type='normal'), Role(user_id=chat_id, type='report_request')])

        if id_admin is None:
            await AdminInfo.create(
                admin_id=chat_id,
                google_table_url=Fernet(SECRET_KEY).encrypt(google_table_url.encode('utf-8')),
                google_drive_dir_url=Fernet(SECRET_KEY).encrypt(google_drive_dir_url.encode('utf-8'))
            )
            await user.periods_stats.add(*(await PeriodStat.all()))

    @staticmethod
    async def update_by_id(chat_id: int, nickname: str = None, fullname: str = None, profession: str = None,
                           bet: int = None,
                           increased_bet: int = None, id_admin: int = None, new_chat_id: int = None):
        user = await User.get(chat_id=chat_id)

        user.chat_id = chat_id if new_chat_id is None else new_chat_id

        if bet is not None:
            user.bet = bet
        if increased_bet is not None:
            user.increased_bet = increased_bet
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
