from models import User, Category, Organization


class OrganizationExtend:
    __slots__ = {}

    @staticmethod
    async def get_admin_users_with_flag_observer(admin_id, organization_id):
        users = await User.filter(admin_id=admin_id).all().values("nickname", "fullname", "profession", "chat_id")
        organization = await Organization.get(id=organization_id)
        observers = await organization.observers

        # Убираем админа из списка наблюдателей пункта меню
        for i in range(0, len(observers)):
            if observers[i] == admin_id:
                observers.pop(i)
                break

        if observers:
            for i in range(0, len(users)):
                for obs in observers:
                    if users[i]['chat_id'] == obs.chat_id:
                        users[i]['observer'] = True
                        break

        # Меняем статус для пользователей у которых нет пункта observer
        for i in range(0, len(users)):
            if "observer" not in users[i].keys():
                users[i]['observer'] = False

        return users

    @staticmethod
    async def update_by_id(organization_id: int, name: str = None, inn: int = None, observers_id_list: list = None):
        organization = await Organization.get(id=organization_id)

        if name is not None:
            organization.name = name

        if inn is not None:
            organization.inn = inn

        if observers_id_list is not None:
            users = await User.filter(chat_id__in=observers_id_list)
            await organization.observers.clear()  # Удаляем текущих наблюдателей
            await organization.observers.add(*users)  # Добавляем новых наблюдателей

        await organization.save()

    @staticmethod
    async def add(name: str, inn: int, admin_id: int, observers_id_list: list):
        users = await User.filter(chat_id__in=observers_id_list)

        # Создаем категорию
        organization = await Organization.create(
            name=name,
            inn=inn,
            admin_id=admin_id,
        )

        await organization.observers.add(*users)

    @staticmethod
    async def get_by_id(organization_id):
        return await Organization.filter(id=organization_id).first()

    @staticmethod
    async def get_user_organizations(user_chat_id):
        user = await User.filter(chat_id=user_chat_id).first()
        is_admin = user.admin_id is None
        organizations = await user.organizations.all().values("id", "name", "status")
        result_organizations = []

        if is_admin:
            result_organizations = organizations
        else:
            for org in organizations:
                if org['status'] == 1:
                    result_organizations.append(org)

        return result_organizations

    @staticmethod
    async def get_admin_organizations(admin_chat_id):
        return await Organization.filter(admin_id=admin_chat_id).all().values("id", "name", "status")

    @staticmethod
    async def invert_status(organization: Organization):
        organization.status = 0 if organization.status == 1 else 1
        await organization.save()

    @staticmethod
    async def delete_organizations_by_ids(ids_organizations_list: list):
        await Organization.filter(id__in=ids_organizations_list).delete()

