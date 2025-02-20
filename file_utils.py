import os
import json

# データ読み込み
def load_data(file_name, default_value, suffix="data"):
    full_path = os.path.join(suffix, file_name)
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return default_value
    except json.JSONDecodeError:
        return default_value
    except Exception as e:
        print(f"読み取り中にエラーが発生しました: {e}")
        return default_value

# データ保存
def save_data(file_name, data, suffix="data"):
    full_path = os.path.join(suffix, file_name)
    try:
        # 保存时不添加缩进和多余的空格，减少换行和文件大小
        with open(full_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
        return True
    except Exception as e:
        print(f"データ保存中にエラーが発生しました: {e}")
        return False

# データ削除
def delete_data(file_name, suffix="data"):
    full_path = os.path.join(suffix, file_name)
    try:
        if os.path.exists(full_path):
            os.remove(full_path)
            print(f"{file_name} が正常に削除されました。")
            return True
        else:
            print(f"{file_name} が見つかりません。")
            return False
    except Exception as e:
        print(f"データ削除中にエラーが発生しました: {e}")
        return False
