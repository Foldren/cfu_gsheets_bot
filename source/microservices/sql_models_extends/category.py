from models import User, Category


class CategoryExtend:
    __slots__ = {}

    @staticmethod
    async def get_admin_users_with_flag_observer(admin_id, category_id):
        users = await User.filter(admin_id=admin_id).all().values("nickname", "fullname", "profession", "chat_id")
        category = await Category.get(id=category_id)
        observers = await category.observers

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
    async def get_parent_categories_names(category_id: int):
        parent = await Category.get(id=category_id).prefetch_related()
        categories_names_list = []

        while parent is not None:
            categories_names_list.append(parent.name)
            parent = await parent.parent

        categories_names_list.reverse()

        return categories_names_list

    @staticmethod
    async def update_by_id(category_id: int, name: str = None, observers_id_list: list = None):
        category = await Category.get(id=category_id)

        if name is not None:
            category.name = name

        if observers_id_list is not None:
            users = await User.filter(chat_id__in=observers_id_list)
            await category.observers.clear()  # Удаляем текущих наблюдателей
            await category.observers.add(*users)  # Добавляем новых наблюдателей

        await category.save()

    @staticmethod
    async def add(name_category: str, lvl_item: int,
                  parent_category_id: Category, observers_id_list: list):
        users = await User.filter(chat_id__in=observers_id_list)

        # Создаем категорию
        category = await Category.create(
            name=name_category,
            level=lvl_item,
            parent_id=parent_category_id,
        )

        await category.observers.add(*users)

    @staticmethod
    async def get_by_id(category_id):
        return await Category.filter(id=category_id).first()

    @staticmethod
    async def get_user_upper_categories(user_id):
        user = await User.filter(chat_id=user_id).first()
        return await user.categories.filter(level=1).all().values("id", "name", "status", "level")

    @staticmethod
    async def get_user_categories_by_parent_id(user_id, parent_id):
        user = await User.filter(chat_id=user_id).first()
        return await user.categories.filter(parent_id=parent_id).all().values("id", "name", "status", "level")

    @staticmethod
    async def get_parent_items(category_id):
        parent = await Category.filter(id=category_id).first().values("parent_id")
        return await Category.filter(parent_id=parent['parent_id']).all().\
            values("id", "name", "parent_id", "status", "level")

    @staticmethod
    async def get_parent_categories_by_chat_id(category_id, user_id):
        parent = await Category.filter(id=category_id).first().values("parent_id")
        return await Category.filter(parent_id=parent['parent_id'], observers__chat_id__contains=user_id).all().\
            values("id", "name", "parent_id", "status", "level")

    @staticmethod
    async def invert_status(category: Category):
        category.status = 0 if category.status == 1 else 1
        await category.save()

    @staticmethod
    async def delete_categories_by_ids(ids_categories_list: list):
        await Category.filter(id__in=ids_categories_list).delete()

    @staticmethod
    async def get_admin_lower_categories_by_id(admin_id):
        return await Category.filter(observers__chat_id__contains=admin_id, child_categories=None).all()

