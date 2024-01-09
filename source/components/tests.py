from cryptography.fernet import Fernet
from config import SECRET_KEY

f = Fernet(SECRET_KEY)
# print('NTU1OTY4ZDMtN2EyYi00ZTM0LWI1ZmQtOTVlNWFlMDcwNDUwMzNhYmU0YTgtNjUxZi00MTNjLTlkNjAtOWU0ODMwMGMyNjM3'.encode())
# encr_text = f.encrypt(b"https://drive.google.com/drive/folders/1-7TyEnnrnHLIisGr1A6RgI4djVHzSFgu")
# print(encr_text)

# decr_text = f.decrypt(encr_text)
# print(decr_text.decode('utf-8'))

# tinkoff t.qCm87E5ocCY4ziCoXaHQQMQ-NPLdmYmWueSTdPranxqPp4YbnJnFKtmGh7rYKoGmJxHIqP9yJMB9NLqxvTHe6A
# module  NTU1OTY4ZDMtN2EyYi00ZTM0LWI1ZmQtOTVlNWFlMDcwNDUwMzNhYmU0YTgtNjUxZi00MTNjLTlkNjAtOWU0ODMwMGMyNjM3

# print("google_table_url ", f.encrypt(b"https://docs.google.com/spreadsheets/d/1uRn27OI41Yh3lBvoETN3w4WlpG6E2V8__GPwe8tr7q8/edit#gid=0"),
#       "google_drive_dir_url ", f.encrypt(b"https://drive.google.com/drive/u/2/folders/1WuD9uOOAyQ1Cufmjvjmsefw6cbkkDvIa"),
#       "gt_dashboard_url ", f.encrypt(b"https://docs.google.com/spreadsheets/d/1uRn27OI41Yh3lBvoETN3w4WlpG6E2V8__GPwe8tr7q8/edit#gid=613510444"),
#       "gt_day_stat_url ", f.encrypt(b"https://docs.google.com/spreadsheets/d/1uRn27OI41Yh3lBvoETN3w4WlpG6E2V8__GPwe8tr7q8/edit#gid=1628011414"),
#       "gt_week_stat_url ", f.encrypt(b"https://docs.google.com/spreadsheets/d/1uRn27OI41Yh3lBvoETN3w4WlpG6E2V8__GPwe8tr7q8/edit#gid=310902894"),
#       "gt_month_stat_url ", f.encrypt(b"https://docs.google.com/spreadsheets/d/1uRn27OI41Yh3lBvoETN3w4WlpG6E2V8__GPwe8tr7q8/edit#gid=324990355"),
#       )


# async def test():
#     gt = GoogleTable()
#     await gt.distribute_statement_operations(
#         table_url="https://docs.google.com/spreadsheets/d/1uRn27OI41Yh3lBvoETN3w4WlpG6E2V8__GPwe8tr7q8/edit#gid=0",
#         inn_partner="7710140679",
#         queue_category="Тестовый рк  → Тестовый рк 1.0",
#         name_partner="Тестовое распределение")
#
#
# if __name__ == "__main__":
#     run(test())