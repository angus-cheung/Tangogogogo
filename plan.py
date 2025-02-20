import math
import uuid
from datetime import datetime
from collections import defaultdict
from date_utils import days_between_create_date
from file_utils import load_data, save_data
from filters import filter_words_lv, filter_words_type, filter_words_kango, filter_words_katakana, filter_word_duplicate
from process import Process, MODE_MISTAKE, MODE_NEW, MODE_REVIEW
# from dropbox_utils import DropboxClient
from utils import clear_console
import filters

PLAN_JSON = "data_plan_map.json"

class PlanManager:

    def __init__(self):
        # self.dropbox = DropboxClient()
        self.process = Process()
        self.plan = load_data(PLAN_JSON, {})
        self.data_dict = {item['ID']: item for item in load_data('processed_data_shuffle.json', [])}
        
        self.MESSEAGE_DICT = {
            MODE_MISTAKE: '間違えた問題の復習',
            MODE_NEW: '新しい単語の暗記',
            MODE_REVIEW: '以前の単語の復習',
        }

    def ask_select(self, select_arr, text, select_message_dict=None):
        res = []
        while True:
            print(text)
            print("選択肢：")
            for i, option in enumerate(select_arr, 1):
                if select_message_dict:
                    print(f"{i}. {select_message_dict[option]}")
                else:
                    print(f"{i}. {option}")
            user_input = input("追加する選択肢の番号を入力してください。終了するには N を入力してください、全部を選ぶには ALL を入力してください ")
            if user_input.strip().upper() == 'N':
                break
            if user_input.strip().upper() == 'ALL':
                res = select_arr
                break
            if user_input.isdigit() and 1 <= int(user_input) <= len(select_arr):
                print(f"追加されました：{select_arr[int(user_input) - 1]}")
                selected_option = select_arr.pop(int(user_input) - 1)
                res.append(selected_option)
            else:
                print("無効な入力です。もう一度入力してください。")
            if len(select_arr) == 0:
                break
        return res
    
    def process_data_by_filters(self, data, select_lvs, select_types, select_kango, select_katakana, duplicate_array, data_plan):
        total = 0
        for level in select_lvs:
            level_res, _ = filter_words_lv(data, level)
            for type_s in select_types:
                type_res, _ = filter_words_type(level_res, type_s)
                for kango in select_kango:
                    kango_res, isKango = filter_words_kango(type_res, kango)
                    if kango_res:
                        total += self.process_katakana_options(level, type_s, isKango, kango_res, select_katakana, duplicate_array, data_plan, kango == filters.TYPE_FILTER_OPT_EXCLUDES)
        return total
    
    def process_katakana_options(self, level, type_s, isKango, kango_res, select_katakana, duplicate_array, data_plan, exclude_katakana):
        count = 0
        for katakana in select_katakana if not exclude_katakana else [filters.KATAKANA_FILTER_OPT_EXCLUDES]:
            ka_res, isKatakana = filter_words_katakana(kango_res, katakana)
            data_index_words = filter_word_duplicate(ka_res, duplicate_array)
            if data_index_words:
                data_index, _, _ = self.process.load_data_index(level, type_s, isKango, isKatakana, len(data_index_words))
                data_index["words"] = data_index_words
                data_plan['data_indexs'].append(data_index)
                count += len(data_index_words)
        return count

    def list_top_mistakes(self, top_n=10):
        review_data = [word for word in self.plan.get("review_words", []) if 'total_mistakes' in word]
        if review_data:
            sorted_words = sorted(review_data, key=lambda x: x['total_mistakes'], reverse=True)
            print(f"\n全体で間違いが最も多い単語トップ {top_n}:")
            for i, word_data in enumerate(sorted_words[:top_n], 1):
                word_info = self.data_dict.get(word_data["ID"], {})
                print(f"{i:02}. 単語: {word_info.get('WORD', 'N/A')}, ｜{word_info.get('CHINESE', 'N/A')}｜{word_info.get('PRONUNCIATION_MATCH', 'N/A')} 間違いの回数: {word_data['total_mistakes']}")

    def show_overall_progress(self):
        progress = defaultdict(lambda: {'total_words': 0, 'learned_words': 0})
        for plan in self.plan.get('data_indexs', []):
            level = plan['level']
            progress[level]['total_words'] += plan['data_len']
            progress[level]['learned_words'] += plan['start_index']
        
        print("\n全体の学習進捗表示:")
        for level, stats in progress.items():
            learned_pct = (stats['learned_words'] / stats['total_words']) * 100 if stats['total_words'] else 0
            print(f"レベル {level}: {learned_pct:.2f}% 完了 ({stats['learned_words']} / {stats['total_words']})")

    def calculate_elapsed_display(self, last_date):
        days_ago = (datetime.now() - last_date).days
        hours_ago = (datetime.now() - last_date).seconds // 3600
        if days_ago >= 3:
            return last_date.strftime("%Y-%m-%d")
        elif days_ago >= 1:
            return f"{days_ago}日前"
        else:
            return f"{hours_ago}時間前"

    def calculate_learned_display(self, days, minutes):
        return f"{days}日間" if days > 1 else f"{minutes}分間"

    def track_study_time(self):
        stats = defaultdict(lambda: {"total_days": 0, "total_minutes": 0, "last_date": None})
        for plan in self.plan.get('data_indexs', []):
            if plan["start_index"] != 0:
                level = plan['level']
                type_s = plan['type_s']
                last_date = datetime.strptime(plan['last_date'], "%Y-%m-%d %H:%M:%S")
                create_date = datetime.strptime(plan['create_date'], "%Y-%m-%d %H:%M:%S")
                elapsed_time = last_date - create_date
                stats[(level, type_s)]['total_days'] += elapsed_time.days
                stats[(level, type_s)]['total_minutes'] += elapsed_time.seconds // 60
                stats[(level, type_s)]['last_date'] = last_date

        print("\n各コースの学習進捗表示:")
        for (level, type_s), data in stats.items():
            last_review_display = self.calculate_elapsed_display(data['last_date'])
            learned_display = self.calculate_learned_display(data['total_days'], data['total_minutes'])
            print(f"レベル {level} - 種類 {type_s}: 最終復習日時 {last_review_display}, 学習時間: {learned_display}")
            
    def show_plan_detail(self):
        self.track_study_time()
        self.show_overall_progress()
        self.list_top_mistakes()
        return
    
    def data_clean(self):
        print(f"review_words --> {len(self.plan['review_words'])}")
        self.plan["review_words"] = []
        save_data(PLAN_JSON, self.plan)
        return
            
    def show_plan(self):
        total = 0
        finish_count = 0
        data_index_now = None
        for obj in self.plan["data_indexs"]:
            data_len = obj["data_len"]
            start_index = obj["start_index"]
            total += data_len
            if start_index > 0:
                finish_count += min(data_len, start_index + 1)
            if start_index + 1 < data_len and data_index_now is None:
                data_index_now = obj
        if not data_index_now:
            data_index_now = self.plan["data_indexs"][0]
        rate = (finish_count / total) * 100 if total > 0 else 0
        target_words_per_day = self.plan["target_words_per_day"]
        days = days_between_create_date(self.plan["create_date"])
        print(f"練習の総数　{total}")
        print(f"練習したは　{finish_count}")
        print(f"進捗パーセント　{rate:.2f}%")
        print(f"毎日練習数　{target_words_per_day}")
        print(f"練習天数　{days}")
        print(f"練習数予定　{days*target_words_per_day}")
        level = data_index_now["level"]
        type_s = data_index_now["type_s"]
        isKatakana = data_index_now["isKatakana"]
        isKango = data_index_now["isKango"]
        isKango_str = "" if isKango == filters.KANGO_FILTER_OPT_EXCLUDES else "漢語"
        isKatakana_str = "" if isKatakana == filters.KATAKANA_FILTER_OPT_EXCLUDES else "カタカタ"
        print(f"予定のコースは　{level} {type_s} {isKango_str}{isKatakana_str}\n")

    def make_plan(self):
        day = input("練習の天数を入力してください。")
        while not (day.isdigit() and int(day) > 0):
            print("無効な入力です。もう一度入力してください。")
            day = input("練習の天数を入力してください。")
        
        select_lvs = self.ask_select(["N5", "N4", "N3", "N2", "N1"], "練習のレベル範囲")
        select_types = self.ask_select(['動', '形', '名', '副', '接', '連', '代', '嘆', '助'], "練習の種類範囲")
        select_kango = [filters.TYPE_FILTER_OPT_EXCLUDES, filters.TYPE_FILTER_OPT_ONLY]
        select_katakana = [filters.TYPE_FILTER_OPT_EXCLUDES, filters.TYPE_FILTER_OPT_ONLY]
        
        data_plan = {
            'id': str(uuid.uuid4()),
            'create_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'data_indexs': []
        }
        
        data = load_data('processed_data_shuffle.json', [])
        clear_console()
        print(f"全部の単語数は{len(data)}\n")
        
        duplicate_array = []
        total = self.process_data_by_filters(data, select_lvs, select_types, select_kango, select_katakana, duplicate_array, data_plan)

        if total == 0:
            print(f"プラン作成失敗　原因:単語数ゼロ\n")
            return
        
        print(f"total ---> {total}")
        target_words_per_day = math.ceil(total / int(day))
        data_plan["target_words_per_day"] = target_words_per_day
        self.plan = data_plan
        self.plan["review_words"] = []
        save_data(PLAN_JSON, self.plan)
    
    def ask_other_options(self):
        cmd = input("レディー ゴー!!!\nNEW -> 計画をやり直す\nSHOW -> 進捗の詳細情報を表示\nCLEAN -> データクリア\nその他のキー -> 練習を続ける ")
        if cmd.upper() == "NEW":
            # self.dropbox.delete_data_file(PLAN_JSON)
            self.make_plan()
            return True
        if cmd.upper() == "SHOW":
            self.show_plan_detail()
            return True
        if cmd.upper() == "CLEAN":
            self.data_clean()
            return True
        return False

    def exec_plan(self):
        self.show_plan()

        if self.ask_other_options():
            return
        data_indexs = self.plan["data_indexs"]
        data_index = {}
        refresh_index = -1
        
        for idx, obj in enumerate(data_indexs):
            if obj["start_index"] != obj["data_len"]:
                data_index = obj
                refresh_index = idx
                break
        
        level = data_index["level"]
        type_s = data_index["type_s"]
        isKango = data_index["isKango"]
        isKatakana = data_index["isKatakana"]
        start_index = data_index["start_index"]
        words = data_index["words"]
        
        select_modes = self.ask_select([MODE_NEW, MODE_REVIEW, MODE_MISTAKE], "練習タイプ選びください", self.MESSEAGE_DICT)
        self.process.refresh_modes(select_modes)
        
        data_len = data_index["data_len"]
        print(f"\n練習コース: {level}|{type_s}|{isKango}|{isKatakana} 単語量:{data_len}")
        
        self.process.refresh_dict(self.data_dict)
        refresh_start_index, re_review_words = self.process.process_exe(words, start_index, self.plan["target_words_per_day"], self.plan["review_words"])
            
        data_index["start_index"] = refresh_start_index
        data_index['last_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.plan["data_indexs"][refresh_index] = data_index
        self.plan["review_words"] = re_review_words
        self.plan["last_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_data(PLAN_JSON, self.plan)
        # self.dropbox.upload_data_file(PLAN_JSON)

    def run_plan_if_need(self):
        # self.dropbox.download_data_file(PLAN_JSON)
        plan_map = load_data(PLAN_JSON, {})
        print("========= TANGO Go go go go =========")
        if plan_map and plan_map.get("id"):
            self.exec_plan()
        else:
            self.make_plan()


