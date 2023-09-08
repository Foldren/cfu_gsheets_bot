from tortoise import Model
from tortoise.fields import IntField, TextField, BooleanField, ManyToManyField, ForeignKeyField, OnDelete, \
    ManyToManyRelation, ForeignKeyRelation, OneToOneRelation, ReverseRelation, OneToOneField, BigIntField


class User(Model):
    chat_id = BigIntField(pk=True)
    admin: ForeignKeyRelation['User'] = ForeignKeyField('models.User', on_delete=OnDelete.CASCADE, related_name="workers", null=True)
    menu_items: ManyToManyRelation['MenuItem'] = ManyToManyField('models.MenuItem', on_delete=OnDelete.CASCADE, related_name="observers", through="user_menu_item")
    workers: ReverseRelation["User"]  # Связь один ко многим к самому себе (выводим дочерние элементы)
    notify_groups: ReverseRelation["NotifyGroup"]
    admin_info: ReverseRelation["AdminInfo"]
    nickname = TextField(maxlength=150, null=False)
    fullname = TextField(maxlength=250, null=True)
    profession = TextField(maxlength=250, null=True)
    hints = BooleanField(default=1)

    class Meta:
        table = "users"


class MenuItem(Model):
    id = BigIntField(pk=True)
    parent: ForeignKeyRelation['MenuItem'] = ForeignKeyField('models.MenuItem', on_delete=OnDelete.CASCADE, related_name="child_items", null=True)
    child_items: ReverseRelation["MenuItem"]  # Связь один ко многим к самому себе (выводим дочерние элементы)
    observers: ManyToManyRelation['User']
    name = TextField(maxlength=100, null=False)
    status = BooleanField(default=1)
    level = IntField(default=1, null=False)
    queue = TextField(maxlength=3000, null=True)
    queue_id = TextField(maxlength=3000, null=True)

    class Meta:
        table = "menu_items"


class NotifyGroup(Model):
    chat_id = BigIntField(pk=True)
    admin: ForeignKeyRelation['User'] = ForeignKeyField('models.User', on_delete=OnDelete.CASCADE, related_name="notify_groups", null=True)

    class Meta:
        table = "notification_groups"


class AdminInfo(Model):
    admin: OneToOneRelation['User'] = OneToOneField('models.User', on_delete=OnDelete.CASCADE, related_name="admin_info", pk=True)
    google_table_url = TextField(maxlength=500, null=False)
    google_drive_dir_url = TextField(maxlength=500, null=False)

    class Meta:
        table = "admin_info"
