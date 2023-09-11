from models import User, MenuItem
from tortoise.expressions import F


class MenuItemApi:
    @staticmethod
    async def get_admin_users_with_flag_observer(admin_id, item_id):
        users = await User.filter(admin_id=admin_id).all().values("nickname", "fullname", "profession", "chat_id")
        menu_item = await MenuItem.get(id=item_id)
        observers = await menu_item.observers

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
    async def get_parent_items_names(item_id: int):
        mi1 = await MenuItem.get(id=item_id).prefetch_related()
        items_names_list = []

        parent = mi1
        while parent is not None:
            items_names_list.append(parent.name)
            parent = await parent.parent

        items_names_list.reverse()

        return items_names_list

    @staticmethod
    async def update_by_id(item_id: int, name: str = None, observers_id_list: list = None):
        menu_item = await MenuItem.get(id=item_id)

        if name is not None:
            menu_item.name = name

        if observers_id_list is not None:
            users = await User.filter(chat_id__in=observers_id_list)
            await menu_item.observers.clear()  # Удаляем текущих наблюдателей
            await menu_item.observers.add(*users)  # Добавляем новых наблюдателей

        await menu_item.save()

    @staticmethod
    async def add(name_item: str, lvl_item: int,
                  parent_menu_item_id: MenuItem, observers_id_list: list):
        users = await User.filter(chat_id__in=observers_id_list)

        # Создаем пункт меню
        menu_item = await MenuItem.create(
            name=name_item,
            level=lvl_item,
            parent_id=parent_menu_item_id,
        )

        await menu_item.observers.add(*users)

    @staticmethod
    async def get_by_id(item_id):
        return await MenuItem.filter(id=item_id).first()

    @staticmethod
    async def get_user_upper_items(user_id):
        user = await User.filter(chat_id=user_id).first()
        return await user.menu_items.filter(level=1).all().values("id", "name", "status", "level")

    @staticmethod
    async def get_user_items_by_parent_id(user_id, parent_id):
        user = await User.filter(chat_id=user_id).first()
        return await user.menu_items.filter(parent_id=parent_id).all().values("id", "name", "status", "level")

    @staticmethod
    async def get_parent_items(item_id):
        parent = await MenuItem.filter(id=item_id).first().values("parent_id")
        return await MenuItem.filter(parent_id=parent['parent_id']).all().values("id", "name", "parent_id", "status", "level")

    @staticmethod
    async def get_parent_items_by_chat_id(item_id, user_id):
        parent = await MenuItem.filter(id=item_id).first().values("parent_id")
        return await MenuItem.filter(parent_id=parent['parent_id'], observers__chat_id__contains=user_id).all().values("id", "name", "parent_id", "status", "level")

    @staticmethod
    async def invert_status(menu: MenuItem):
        menu.status = 0 if menu.status == 1 else 1
        await menu.save()

    @staticmethod
    async def delete_menu_items_by_ids(ids_items_list: list):
        await MenuItem.filter(id__in=ids_items_list).delete()

