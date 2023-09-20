text_start_admin_user = f"ВКЛЮЧЕН РЕЖИМ ЮЗЕРА 🙎‍♂️\n\n" \
                        f"<u>Рабочие кнопки бота Управляйки в режиме юзера</u> ⚙️ :\n\n" \
                        f"1️⃣️ <b>Операция с категориями</b> - создайте и добавьте новую запись в отчет (лист БД), " \
                        f"выбирая нужные " \
                        f"категории для позиции в отчете (категория, это статья движения - " \
                        f"приход или расход денежных средств).\n\n" \
                        f"2️⃣ <b>Операция с подотчетами</b> - получение и возврат подотчета\n\n" \
                        f"3️⃣ <b>Кошельки</b> - перевод с одного кошелька на другой по выбранному " \
                        f"ЮР Лицу и изменение " \
                        f"списка ваших кошельков\n\n" \
                        f"4️⃣ <b>Отчеты</b> - вывод отчетов в зависимости от настройки админа."
text_get_list_users = f"<b>ШАГ</b> 1️⃣\n" \
                      f"Здесь вы можете настроить доступы ваших сотрудников к боту Управляйке.\n\n" \
                      f"<u>Кнопки управления</u>:\n\n" \
                      f"➕ - добавить пользователя\n" \
                      f"✏️ - редактировать\n" \
                      f"❌️ - забрать доступ"
text_start_add_user = f"<u>Введите данные пользователя</u>:\n\n" \
                      f"1️⃣ <b>Имя пользователя</b> - в телеграм указан со значком @\n" \
                      f"2️⃣ <b>ФИО</b> - введите через пробел (Фамилия Имя Отчество)\n" \
                      f"3️⃣ <b>Должность сотрудника</b>\n\n" \
                      f"Каждый параметр, начиная со второго вводите с новой строки в формате, " \
                      f"указанном ниже 📋👨‍💼\n\n" \
                      f"Пример:\n<code>@user987\nПочетов Сергей Александрович\nменеджер</code>"
text_get_id_user = "🔵 Перешлите сюда сообщение этого пользователя,\nчтобы я мог взять его chat_id 📨🆔\n" \
                   "(у пользователя в настройках конфиденциальности должна быть разрешена 'пересылка сообщений')\n\n" \
                   "🔵 Либо просто укажите chat_id в формате числа👇"
text_invalid_user_id = "Указан невалидный chat_id ⚠️"
text_end_add_user = f"Отправьте пользователю ссылку на меня - @admfinbot, я добавлю его в систему как только он" \
                    f" запустит бота Управляйку 📩"
text_user_exists = f"Упс, похоже пользователь с этим chat_id уже зарегистрирован в боте 🤷‍♂️"
text_start_change_user = "Нажмите на сотрудника, данные которого нужно изменить 👇"
text_change_user = f"<u>Введите новые данные пользователя</u>:\n\n" \
                   f"1️⃣ <b>Имя пользователя</b> - в телеграм указан со значком @\n" \
                   f"2️⃣ <b>ФИО</b> - введите через пробел (фамилия имя отчество)\n" \
                   f"3️⃣ <b>Должность сотрудника</b>\n\n" \
                   f"Каждый параметр, начиная со второго вводите с новой строки в формате, " \
                   f"указанном ниже 📋👨‍💼 " \
                   f"(также вы просто можете скопировать пример, в нем указаны данные выбранного пользователя)\n\n" \
                   f"Пример:\n"
text_end_change_user = f"Данные пользователя изменены ✅"
text_end_change_id_user = f"id пользователя изменен ✅🆔"
text_get_id_change_user = "🔵 Перешлите сюда сообщение пользователя,\nчтобы я мог взять его chat_id 📨🆔\n" \
                          "(у пользователя в настройках конфиденциальности должна быть разрешена 'пересылка сообщений')\n\n" \
                          "🔵 Либо просто укажите новый chat_id в формате числа👇"
text_start_delete_users = "\nВыберите пользователей, у которых нужно забрать доступ 👉"