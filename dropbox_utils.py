import os
import json
from datetime import datetime
import dropbox
from dropbox.files import WriteMode
from dropbox.exceptions import ApiError, AuthError
from file_utils import load_data, delete_data

APP_CLOUD_FOLER = "/Tangogogo/data/"

class DropboxClient:
    def __init__(self):
        config = load_data('config.json', {})
        access_token = config['DROP_BOX_ACCESS_TOKEN']
        self.dbx = dropbox.Dropbox(access_token)
    
    def upload_file(self, local_path, dropbox_path):
        try:
            with open(local_path, 'rb') as f:
                self.dbx.files_upload(f.read(), dropbox_path, mode=WriteMode('overwrite'))
            print(f"ファイルアップロード成功: {dropbox_path}")
            return True
        except Exception as e:
            print(f"ファイルアップロード失敗: {e}")
            return False

    def download_file(self, dropbox_path, local_path):
        try:
            metadata, res = self.dbx.files_download(dropbox_path)
            with open(local_path, 'wb') as f:
                f.write(res.content)
            print(f"ファイルダウンロード成功: {local_path}")
            return True
        except Exception as e:
            print(f"ファイルダウンロード失敗: {e}")
            return False

    def list_files(self, folder_path=''):
        try:
            result = self.dbx.files_list_folder(folder_path)
            for entry in result.entries:
                print(entry.name)
            return result
        except Exception as e:
            print(f"ファイルリスト失敗: {e}")
            return None

    def delete_file(self, dropbox_path):
        try:
            self.dbx.files_delete_v2(dropbox_path)
            print(f"ファイル削除成功: {dropbox_path}")
            return True
        except Exception as e:
            print(f"ファイル削除失敗: {e}")
            raise

    def create_folder(self, folder_path):
        try:
            self.dbx.files_create_folder_v2(folder_path)
            print(f"ファイルフォルダ作成成功: {folder_path}")
            return True
        except Exception as e:
            print(f"ファイルフォルダ作成失敗: {e}")
            return False
        
    def file_exists_in_dropbox(self, dropbox_path):
        try:
            self.dbx.files_get_metadata(dropbox_path)
            return True
        except ApiError as e:
            if e.error.is_path() and e.error.get_path().is_not_found():
                return False
            else:
                raise e
    
    def download_file_by_lastdate(self, dropbox_path, local_path):
        try:
            if os.path.exists(local_path):
                with open(local_path, 'r', encoding='utf-8') as f:
                    jsonA = json.load(f)
            else:
                jsonA = None
            metadata, res = self.dbx.files_download(dropbox_path)
            jsonB = json.loads(res.content.decode('utf-8'))
            if jsonA is None:
                with open(local_path, 'w', encoding='utf-8') as f:
                    json.dump(jsonB, f, ensure_ascii=False, indent=4)
                print(f"ファイルダウンロード成功: {local_path}")
                return True
            if "last_date" not in jsonA or "last_date" not in jsonB:
                print(f"ファイルに 'last_date' フィールドが存在しません、ダウンロードをスキップします。")
                return False
            date_format = "%Y-%m-%d %H:%M:%S"
            timeA = datetime.strptime(jsonA["last_date"], date_format)
            timeB = datetime.strptime(jsonB["last_date"], date_format)
            if timeB > timeA:
                with open(local_path, 'w', encoding='utf-8') as f:
                    json.dump(jsonB, f, ensure_ascii=False, indent=4)
                print(f"ファイルダウンロード成功: {local_path} (更新されました)")
                return True
            else:
                print(f"ファイルは最新です。更新は行われません。")
                return False
        except Exception as e:
            print(f"ファイルダウンロード失敗: {e}")
            raise

    def upload_data_file(self, file_name):
        local_path = os.path.join('data', file_name)
        dropbox_path = f'{APP_CLOUD_FOLER}{file_name}'
        if not os.path.exists(local_path):
            print(f"ローカルファイルが存在しません: {local_path}")
            return False
        return self.upload_file(local_path, dropbox_path)

    def download_data_file(self, file_name):
        local_path = os.path.join('data', file_name)
        dropbox_path = f'{APP_CLOUD_FOLER}{file_name}'
        try:
            if not self.file_exists_in_dropbox(dropbox_path):
                print(f"Dropbox ファイルが存在しません: {dropbox_path}")
                return False
            return self.download_file_by_lastdate(dropbox_path, local_path)
        except AuthError as e:
            print(f"Dropbox トークンは無効になったんです。")
            return False
        except Exception as e:
            print(f"Dropbox エラーが発生してます。")
            return False
    
    def delete_data_file(self, file_name):
        local_path = os.path.join('data', file_name)
        dropbox_path = f'{APP_CLOUD_FOLER}{file_name}'
        try:
            if not self.file_exists_in_dropbox(dropbox_path):
                print(f"Dropbox ファイルが存在しません: {dropbox_path}")
                return False
            self.delete_file(dropbox_path, local_path)
            return True
        except AuthError as e:
            print(f"Dropbox トークンは無効になったんです。")
            return False
        except Exception as e:
            print(f"Dropbox エラーが発生してます。")
            return False

if __name__ == "__main__":
    client = DropboxClient()
    # client.create_folder('/Tangogogo/data')
    client.list_files('/Tangogogo/data')
    # client.upload_file('data/data_plan_map.json', '/Tangogogo/data/data_plan_map.json')
    # client.download_file('/Apps/YourApp/local_file.json', 'downloaded_file.json')
    # client.list_files('/Apps/YourApp')
    # client.delete_file('/Tangogogo_data')
    client.delete_file('/Tangogogo/data/data_plan_map.json')
    # client.create_folder('/Apps/YourApp/new_folder')
