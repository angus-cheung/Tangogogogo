DEBUG_M = 0

TYPE_FILTER_OPT_INCLUDES = "1"
TYPE_FILTER_OPT_EXCLUDES = "2"
TYPE_FILTER_OPT_ONLY = "3"

KANGO_FILTER_OPT_INCLUDES = "_KANGO_INCLUDES_"
KANGO_FILTER_OPT_EXCLUDES = "_KANGO_EXCLUDES_"
KANGO_FILTER_OPT_ONLY = "_KANGO_ONLY_"

KATAKANA_FILTER_OPT_INCLUDES = "_KATAKANA_INCLUDES_"
KATAKANA_FILTER_OPT_EXCLUDES = "_KATAKANA_EXCLUDES_"
KATAKANA_FILTER_OPT_ONLY = "_KATAKANA_ONLY_"

WORD_TYPES = ['名', '動', '他動', '自動', '自他動', '形', 'イ形', 'ナ形', '副', '接', '接尾', '接頭', '連', '連語', '連体', '代', '助', '嘆']

# データのレベルフィルター
def filter_words_lv(data, level = ''):
    if level == '':
        level_mapping = {
            '1': 'N1',
            '2': 'N2',
            '3': 'N3',
            '4': 'N4',
            '5': 'N5'
        }
        while True:
            level_num = input("学習する単語のレベルを数字で入力（1: N1, 2: N2, 3: N3, 4: N4, 5: N5）: ")
            if level_num in level_mapping:
                level = level_mapping[level_num]
                break
            else:
                print("無効な入力です。1から5までの数字を入力してください。")
    filtered_data = [word for word in data if word['LEVEL'] == level]
    if DEBUG_M:
        print(f"\nレベル{level}に当てる単語数 -> {len(filtered_data)}")
    return filtered_data, level

# データの種類フィルター
def filter_words_type(data, type_s = ''):
    if type_s == '':
        if not data or len(data) == 0:
            print("データの種類フィルター data is null")
            return data, None
        types = WORD_TYPES
        print("種類学習する単語のレベル一覧：")
        for index, t in enumerate(types):
            print(f"{index}: {t}\t")
        while True:
            try:
                user_input = input("学習する単語の種類の番号を入力してください（数字）。")
                if user_input.strip():
                    selected_index = int(user_input)
                    if 0 <= selected_index < len(types):
                        type_s = types[selected_index]
                        break
                    else:
                        print("無効な番号です。もう一度入力してください。")
                else:
                    break
            except ValueError:
                print("数字を入力してください。")
    res = []
    for word in data:
        if type_s in word['TYPE1']:
            res.append(word)
        elif type_s in word['TYPE']:
            res.append(word)
    if DEBUG_M:
        print(f"\n種類{type_s}に当てる単語数 -> {len(data)}")
    return res, type_s

# データの漢語フィルター
def filter_words_kango(data, res = ''):
    if res == '':
        if not data or len(data) == 0:
            print("データの漢語フィルター data is null")
            return data
        res = input("漢字が含まれる? 1 - YES (Default) 2 - NO 3 - 漢字のみ: ")
    isKango = KANGO_FILTER_OPT_INCLUDES
    flag = "★"
    if res == TYPE_FILTER_OPT_EXCLUDES:
        isKango = KANGO_FILTER_OPT_EXCLUDES
        data = [word for word in data if not word['KANGO'] or flag != word['KANGO']]
    elif res == TYPE_FILTER_OPT_ONLY:
        isKango = KANGO_FILTER_OPT_ONLY
        data = [word for word in data if word['KANGO'] and flag == word['KANGO']]
    if DEBUG_M:
        print(f"\n漢語の選択{res}に関して、当てる単語数 -> {len(data)}")
    return data, isKango

# データのカタカナフィルター
def filter_words_katakana(data, res = ''):
    if res == '':
        if not data or len(data) == 0:
            return data
        res = input("カタカナが含まれる? 1 - YES (Default) 2 - NO 3 - カタカナのみ: ")
    isKatakana = KATAKANA_FILTER_OPT_INCLUDES
    flag = "★"
    if res == TYPE_FILTER_OPT_EXCLUDES:
        isKatakana = KATAKANA_FILTER_OPT_EXCLUDES
        data = [word for word in data if not word['KATAKANA'] or flag != word['KATAKANA']]
    elif res == TYPE_FILTER_OPT_ONLY:
        isKatakana = KATAKANA_FILTER_OPT_ONLY
        data = [word for word in data if word['KATAKANA'] and flag == word['KATAKANA']]
    if DEBUG_M:
        print(f"\nカタカナ{res}の選択に関して、当てる単語数 -> {len(data)}")
    return data, isKatakana

# データの重複除くフィルター
def filter_word_duplicate(data, duplicate_array):
    res = []
    for item in data:
        item_id = item["ID"]
        if item_id not in duplicate_array:
            duplicate_array.append(item_id)
            res.append(item_id)
    return res