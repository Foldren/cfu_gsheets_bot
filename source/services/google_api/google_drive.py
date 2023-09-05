from datetime import datetime
from os import getcwd
from google.oauth2.service_account import Credentials
from gspread_asyncio import AsyncioGspreadClientManager


class GoogleDrive:
    agcm: AsyncioGspreadClientManager
    json_creds_path = "upravlyaika-credentials.json"

    def __inti_credentials(self):
        creds = Credentials.from_service_account_file(self.json_creds_path)
        scoped = creds.with_scopes([
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ])
        return scoped

    def __init__(self):
        self.agcm = AsyncioGspreadClientManager(self.__inti_credentials)