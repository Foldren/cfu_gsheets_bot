from models import PeriodStat, User


class PeriodStatExtend:
    __slots__ = {}

    @staticmethod
    async def get_period_stat_users_with_flag_observer(name_stat, admin_id):
        period_stat = await PeriodStat.get(name=name_stat)
        users = await User.filter(admin_id=admin_id).all().values("chat_id", "fullname", "profession")
        observers = await period_stat.observers

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
    async def update_observers_by_name(admin_id: int, ps_name: int, observers_id_list: list):
        period_stat = await PeriodStat.get(name=ps_name)
        new_observers = await User.filter(chat_id__in=observers_id_list)
        admin_users = await User.filter(admin_id=admin_id)
        old_observers = await period_stat.observers
        for o in old_observers:
            if o in admin_users:
                await period_stat.observers.remove(o)
        await period_stat.observers.add(*new_observers)  # Добавляем новых наблюдателей
        await period_stat.save()
