
from file_utils import load_data, save_data
from filters import filter_words_lv, filter_words_type, filter_words_kango, filter_words_katakana
from process import load_data_index, process_exe
from utils import clear_console
import filters

import random
import math
import uuid
import os
from datetime import datetime, timedelta

def ask_select(select_arr, text):
    res = []
    while True:
        print(text)
        print("選択肢：")
        for i, option in enumerate(select_arr, 1):
            print(f"{i}. {option}")
        user_input = input("追加する選択肢の番号を入力してください。終了するには N を入力してください: ")
        if user_input.strip().upper() == 'N' or user_input.strip().upper() == 'n':
            break
        if user_input.isdigit() and 1 <= int(user_input) <= len(select_arr):
            print(f"追加されました：{select_arr[int(user_input) - 1]}")
            selected_option = select_arr.pop(int(user_input) - 1)
            res.append(selected_option)  # 選択肢を結果に追加
        else:
            print("無効な入力です。もう一度入力してください。")
        if len(select_arr) == 0:
            break
    return res

def show_plan(plan):
    create_date = plan["create_date"]
    total = 0
    finish_count = 0
    data_index_now = None
    for obj in plan["data_indexs"]:
        data_len = obj["data_len"]
        start_index = obj["start_index"]
        total += data_len
        if start_index > 0:
            finish_count += min(data_len, start_index + 1)
        if start_index + 1 < data_len and data_index_now is None:
            data_index_now = obj
    if not data_index_now:
        data_index_now = plan["data_indexs"][0]
    rate = (finish_count / total) * 100 if total > 0 else 0
    target_words_per_day = plan["target_words_per_day"]
    print(f"練習の総数　{total}")
    print(f"練習したは　{finish_count}")
    print(f"進捗パーセント　{rate:.2f}%")
    print(f"毎日練習数　{target_words_per_day}")
    level = data_index_now["level"]
    type_s = data_index_now["type_s"]
    isKatakana = data_index_now["isKatakana"] 
    isKango = data_index_now["isKango"] 
    isKango_str = "" if isKango == filters.KANGO_FILTER_OPT_EXCLUDES else "漢語"
    isKatakana_str = "" if isKatakana == filters.KATAKANA_FILTER_OPT_EXCLUDES else "カタカタ"
    print(f"現在練習中のコースは　{level} {type_s} {isKango_str}{isKatakana_str}\n")
    return

def make_plan():
    day = input("練習の天数を入力してください。")
    while True:
        if day.isdigit() and 1 <= int(day):
            print(f"練習の天数 {day}")
            break
        else:
            print("無効な入力です。もう一度入力してください。")
    select_lvs = ask_select(["N5","N4","N3","N2","N1"], "練習のレベル範囲")
    print(select_lvs)
    select_types = ask_select(['動', '形', '名', '副', '接', '連'], "練習の種類範囲")
    print(select_types)
    select_kango = [filters.TYPE_FILTER_OPT_EXCLUDES, filters.TYPE_FILTER_OPT_ONLY]
    select_katakana = [filters.TYPE_FILTER_OPT_EXCLUDES, filters.TYPE_FILTER_OPT_ONLY]
    
    plan = load_data('data_plan_map.json', {})
    uid = str(uuid.uuid4())
    data_plan = {}
    data_plan['id'] = uid
    data_plan['create_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data_plan['data_indexs'] = []
    data = load_data('processed_data_shuffle.json', []) 
    
    clear_console()
    print(f"全部の単語数は{len(data)}\n")
    
    total = 0
    res = []
    duplicate_words = []
    
    for index, l in enumerate(select_lvs):
        res, level = filter_words_lv(data, l)
        for tid, t in enumerate(select_types):
            type_res, type_s = filter_words_type(res, t)
            for kid, k in enumerate(select_kango):
                kango_res, isKango = filter_words_kango(type_res, k)
                if len(kango_res) > 0:
                    if k == filters.TYPE_FILTER_OPT_EXCLUDES:
                        for kaid, ka in enumerate(select_katakana):
                            ka_res, isKatakana = filter_words_katakana(kango_res, ka)
                            if len(ka_res) > 0:
                                data_index, data_indexs, start_index = load_data_index(level, type_s, filters.KANGO_FILTER_OPT_EXCLUDES, isKatakana, len(ka_res))
                                total += len(ka_res)
                                data_plan['data_indexs'].append(data_index)
                    else:
                        data_index, data_indexs, start_index = load_data_index(level, type_s, isKango, filters.KATAKANA_FILTER_OPT_EXCLUDES, len(kango_res))
                        total += len(kango_res)
                        data_plan['data_indexs'].append(data_index)

    print(f"ターゲット単語数は{total}\n")
    if total == 0:
        print(f"プラン作成失敗　原因:単語数ゼロ\n")
        return
    target_words_per_day = math.ceil(total / int(day))
    print(f"一日のターゲット単語数は{target_words_per_day}\n")
    data_plan["target_words_per_day"] = target_words_per_day
    plan = data_plan
    plan["review_words"] = []
    save_data('data_plan_map.json', plan)
    return

def exec_plan():
    plan = load_data('data_plan_map.json', {})
    target_words_per_day = plan["target_words_per_day"]
    show_plan(plan)
    input("レディー　ゴ!!!")
    data_indexs = plan["data_indexs"]
    data_index = {}
    refresh_index = -1
    for idx, obj in enumerate(data_indexs):
        idxs_start_index = obj["start_index"]
        idxs_data_len = obj["data_len"]
        if idxs_start_index != idxs_data_len -1:
            data_index = obj
            refresh_index = idx
            break
    level = data_index["level"]
    type_s = data_index["type_s"]
    isKango = data_index["isKango"]
    isKango_filter = filters.TYPE_FILTER_OPT_ONLY

    if isKango == filters.KANGO_FILTER_OPT_EXCLUDES:
        isKango_filter = filters.TYPE_FILTER_OPT_EXCLUDES
    isKatakana = data_index["isKatakana"]
    isKatakana_filter = filters.TYPE_FILTER_OPT_ONLY
    if isKatakana == filters.KATAKANA_FILTER_OPT_EXCLUDES:
        isKatakana_filter = filters.TYPE_FILTER_OPT_EXCLUDES
    start_index = data_index["start_index"]
    data = load_data('processed_data_shuffle.json', []) 
    
    print(f"全部の単語数は{len(data)}\n")
    # データフィルター
    res = []
    data_lv, level = filter_words_lv(data, level)
    data_types, type_s = filter_words_type(data_lv, type_s)
    data_kango, isKango = filter_words_kango(data_types, isKango_filter)
    if isKango_filter == filters.TYPE_FILTER_OPT_EXCLUDES:
        res, isKatakana = filter_words_katakana(data_kango, isKatakana_filter)
    else:
        res = data_kango
    data_len = data_index["data_len"]
    data_len_match = len(res)
    if data_len != data_len_match:
        print(f"\nフィルター: {level}|{type_s}|{isKango}|{isKatakana} data_len :{data_len} data_len_match:{data_len_match}")
        return        
    print(f"\nフィルター: {level}|{type_s}|{isKango}|{isKatakana} 合計:{data_len}")
    if data_len > 0:
        random.shuffle(res)
        refresh_start_index, re_review_words = process_exe(res, start_index, target_words_per_day, plan["review_words"])
        # データ保存
        data_index["start_index"] = refresh_start_index
        data_index['last_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        plan["data_indexs"][refresh_index] = data_index
        plan["review_words"] = re_review_words
        save_data("data_plan_map.json", plan)
    else:
        print("\nフィルターの結果はゼロです。")

def run_plan_if_need():
    plan_map = load_data('data_plan_map.json', {})
    print("========= TANGO Go go go go =========")
    if plan_map and plan_map["id"]:
        exec_plan()
    else:
        make_plan()