from httpx import AsyncClient


# date format '2023-07-13'
async def get_statement(api_key: str, account_number: str, from_date: str, to_date: str):
    from_date_frmt = f'{from_date}T00:00:00Z'
    to_date_frmt = f'{to_date}T23:59:59Z'
    headers = {'Authorization': 'Bearer ' + api_key}
    url_operation = 'https://business.tinkoff.ru/openapi/api/v1/statement?accountNumber=' + \
                    account_number + '&from=' + from_date_frmt + '&to=' + to_date_frmt

    response = await AsyncClient(verify=False).get(url=url_operation, headers=headers)

    if response.status_code == 200:
        # Обработка ответа
        print(response.text)
    else:
        raise Exception(f"Ошибка по api тинькофф:\n\n {response.text}")
