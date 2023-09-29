from tortoise import Model
from tortoise.fields import IntField, TextField, BooleanField, ManyToManyField, ForeignKeyField, OnDelete, \
    ManyToManyRelation, ForeignKeyRelation, OneToOneRelation, ReverseRelation, OneToOneField, BigIntField, DateField


class User(Model):
    chat_id = BigIntField(pk=True)
    admin: ForeignKeyRelation['User'] = ForeignKeyField('models.User', on_delete=OnDelete.CASCADE,
                                                        related_name="workers", null=True)
    categories: ManyToManyRelation['Category'] = ManyToManyField('models.Category', on_delete=OnDelete.CASCADE,
                                                                 related_name="observers", through="category_observers")
    organizations: ManyToManyRelation['Organization'] = ManyToManyField('models.Organization',
                                                                        on_delete=OnDelete.CASCADE,
                                                                        related_name="observers",
                                                                        through="organization_observers")
    periods_stats: ManyToManyRelation['PeriodStat'] = ManyToManyField('models.PeriodStat', on_delete=OnDelete.CASCADE,
                                                                      related_name="observers",
                                                                      through="period_stat_observers")
    admin_banks: ReverseRelation['Bank']
    admin_organizations: ReverseRelation["Organization"]
    admin_partners: ReverseRelation["Partner"]
    workers: ReverseRelation["User"]
    notify_groups: ReverseRelation["NotifyGroup"]
    issuance_reports: ReverseRelation["IssuanceReport"]
    admin_info: ReverseRelation["AdminInfo"]
    nickname = TextField(maxlength=150, null=False)
    fullname = TextField(maxlength=250, null=True)
    profession = TextField(maxlength=250, null=True)
    hints = BooleanField(default=1)

    class Meta:
        table = "users"


class Category(Model):
    id = BigIntField(pk=True)
    parent: ForeignKeyRelation['Category'] = ForeignKeyField('models.Category', on_delete=OnDelete.CASCADE,
                                                             related_name="child_categories", null=True)
    child_categories: ReverseRelation["Category"]  # Связь один ко многим к самому себе (выводим дочерние элементы)
    observers: ManyToManyRelation['User']
    bank_reload_category_partners: ReverseRelation['Partner']
    name = TextField(maxlength=100, null=False)
    status = BooleanField(default=1)
    level = IntField(default=1, null=False)

    class Meta:
        table = "categories"


class Organization(Model):
    id = BigIntField(pk=True)
    admin: ForeignKeyRelation['User'] = ForeignKeyField('models.User', on_delete=OnDelete.CASCADE,
                                                        related_name="admin_organizations", null=False)
    payment_accounts: ReverseRelation['PaymentAccount']
    observers: ManyToManyRelation['User']
    name = TextField(maxlength=100, null=False)
    status = BooleanField(default=1)

    class Meta:
        table = "organizations"


class Partner(Model):
    id = BigIntField(pk=True)
    bank_reload_category: ForeignKeyRelation['Category'] = ForeignKeyField('models.Category',
                                                                           on_delete=OnDelete.SET_NULL,
                                                                           related_name="bank_reload_category_partners",
                                                                           null=True)
    admin: ForeignKeyRelation['User'] = ForeignKeyField('models.User', on_delete=OnDelete.CASCADE,
                                                        related_name="admin_partners", null=False)
    inn = TextField(maxlength=100, null=False)
    name = TextField(maxlength=100, null=False)

    class Meta:
        table = "partners"


class Bank(Model):
    id = BigIntField(pk=True)
    admin: ForeignKeyRelation['User'] = ForeignKeyField('models.User', on_delete=OnDelete.CASCADE,
                                                        related_name="admin_banks", null=False)
    payment_accounts: ReverseRelation['PaymentAccount']
    custom_name = TextField(maxlength=200, null=False)
    bank_name = TextField(maxlength=200, null=False)
    api_key = TextField(maxlength=500, null=False)

    class Meta:
        table = "banks"


class PaymentAccount(Model):
    id = BigIntField(pk=True)
    number = TextField(maxlength=50, null=False)
    bank: ForeignKeyRelation['Bank'] = ForeignKeyField('models.Bank', on_delete=OnDelete.CASCADE,
                                                       related_name="payment_accounts", null=False)
    organization: ForeignKeyRelation['Organization'] = ForeignKeyField('models.Organization',
                                                                       on_delete=OnDelete.CASCADE,
                                                                       related_name="payment_accounts", null=False)
    first_date_load_statement = DateField(null=False)
    last_date_reload_statement = DateField(null=True)
    status = BooleanField(default=1)

    class Meta:
        table = "payment_accounts"


class NotifyGroup(Model):
    chat_id = BigIntField(pk=True)
    name = TextField(maxlength=200, null=False)
    admin: ForeignKeyRelation['User'] = ForeignKeyField('models.User', on_delete=OnDelete.CASCADE,
                                                        related_name="notify_groups", null=False)
    issuance_reports: ReverseRelation['IssuanceReport']

    class Meta:
        table = "notification_groups"


class IssuanceReport(Model):
    id = BigIntField(pk=True)
    org_name = TextField(maxlength=100, null=True)
    selected_user_nickname = TextField(maxlength=150, null=True)
    selected_user_id = BigIntField()
    volume = BigIntField(null=False)
    payment_method = TextField(maxlength=100, null=True)
    message_id = BigIntField(null=True)
    user: ForeignKeyRelation['User'] = ForeignKeyField('models.User', on_delete=OnDelete.CASCADE,
                                                       related_name="issuance_reports", null=False)
    notify_group: ForeignKeyRelation['NotifyGroup'] = ForeignKeyField('models.NotifyGroup', on_delete=OnDelete.CASCADE,
                                                                      related_name="issuance_reports", null=False)

    class Meta:
        table = "issuance_reports"


class AdminInfo(Model):
    admin: OneToOneRelation['User'] = OneToOneField('models.User', on_delete=OnDelete.CASCADE,
                                                    related_name="admin_info", pk=True)
    google_table_url = TextField(maxlength=500, null=False)
    google_drive_dir_url = TextField(maxlength=500, null=False)
    gt_day_stat_url = TextField(maxlength=500, null=False)
    gt_week_stat_url = TextField(maxlength=500, null=False)
    gt_month_stat_url = TextField(maxlength=500, null=False)

    class Meta:
        table = "admin_info"


class PeriodStat(Model):
    id = BigIntField(pk=True)
    name = TextField(maxlength=100, null=False)
    observers: ManyToManyRelation['User']

    class Meta:
        table = "periods_stats"
