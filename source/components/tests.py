from cryptography.fernet import Fernet
from environs import Env

env = Env()
env.read_env('../.env')

f = Fernet(env('SECRET_KEY'))
# print('NTU1OTY4ZDMtN2EyYi00ZTM0LWI1ZmQtOTVlNWFlMDcwNDUwMzNhYmU0YTgtNjUxZi00MTNjLTlkNjAtOWU0ODMwMGMyNjM3'.encode())
encr_text = f.encrypt(b"https://drive.google.com/drive/folders/1-7TyEnnrnHLIisGr1A6RgI4djVHzSFgu")
print(encr_text)

# decr_text = f.decrypt(encr_text)
# print(decr_text.decode('utf-8'))

# tinkoff t.qCm87E5ocCY4ziCoXaHQQMQ-NPLdmYmWueSTdPranxqPp4YbnJnFKtmGh7rYKoGmJxHIqP9yJMB9NLqxvTHe6A
# module  NTU1OTY4ZDMtN2EyYi00ZTM0LWI1ZmQtOTVlNWFlMDcwNDUwMzNhYmU0YTgtNjUxZi00MTNjLTlkNjAtOWU0ODMwMGMyNjM3



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