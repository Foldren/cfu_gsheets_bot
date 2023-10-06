import json
import mimetypes
from aiogoogle import Aiogoogle
from aiogoogle.auth.creds import ServiceAccountCreds
from cryptography.fernet import Fernet

from config import SECRET_KEY


class GoogleDrive:
    credentials: ServiceAccountCreds
    json_creds_path = "upravlyaika-credentials.json"

    def __init__(self):
        service_account_key = json.load(open(self.json_creds_path))
        self.credentials = ServiceAccountCreds(
            scopes=[
                "https://www.googleapis.com/auth/drive",
                "https://www.googleapis.com/auth/drive.file"
            ],
            **service_account_key
        )

    async def upload_check_too_google_drive_dir(self, file_path: str, google_dir_encr_url: str, file_name_on_gd: str):
        async with Aiogoogle(service_account_creds=self.credentials) as aiog_session:
            google_dir_decr_url = Fernet(SECRET_KEY).decrypt(google_dir_encr_url).decode("utf-8")
            index_start_folder_id = google_dir_decr_url.rfind("/") + 1
            folder_id = google_dir_decr_url[index_start_folder_id:]

            drive_v3 = await aiog_session.discover('drive', 'v3')
            meta_data = {
                'name': file_name_on_gd,
                'parents': [folder_id]
            }
            request = drive_v3.files.create(upload_file=file_path, fields="id", json=meta_data)
            request.upload_file_content_type = mimetypes.guess_type(file_path)[0]
            await aiog_session.as_service_account(request)
