from file_utils import load_data, save_data
from datetime import datetime, timedelta
from pydub import AudioSegment
from pydub.playback import play
import os

Forgetting_Intervals = [0.1, 0.2, 0.4, 0.7, 1.5, 3.0, 1, 2, 4, 7, 15, 30]

MODE_MISTAKE = 'M'
MODE_ALL = 'A'
MODE_REVIEW = 'R'

PLAY_SOUND_FLAG = 0

# 訓練のデータ読み込み
def load_data_index(level, type_s, isKango, isKatakana, data_len):
    uuid = f"{level}{type_s}{isKango}{isKatakana}"
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data_indexs = load_data('data_indexs.json', [])
    res = [item for item in data_indexs if item['uuid'] in uuid]
    data_index = {}
    if len(res) == 0:
        start_index = 0
        data_index['uuid'] = uuid
        data_index['create_date'] = current_date
        data_index['level'] = level
        data_index['type_s'] = type_s
        data_index['isKatakana'] = isKatakana
        data_index['isKango'] = isKango
        data_index['last_date'] = current_date
        data_index['start_index'] = start_index
        data_index['data_len'] = data_len
        data_indexs.append(data_index)
    else:
        data_index = res[0]
        start_index = data_index['start_index']
    return data_index, data_indexs, start_index

# 今日の新しい単語を取得
def get_today_words(data, start_index, target_words_per_day):
    end_index = min(start_index + target_words_per_day, len(data))
    return data[start_index:end_index]

# 単語表示
def display_tango_question(word):
    print(f"\n中国語: {word['CHINESE']}")
    print(f"\n{word['TYPE1']} ")
    if word['KATAKANA'] and "★" in word['KATAKANA']:
        print("カタカナ　⚪︎\t")
    if word['KANGO'] and "★" in word['KANGO']:
        print("漢語　⚪︎\t")
    return

# 単語テスト関数（単語をテストし、正誤を判断）
def spelling_test(word, review_words, mode):
    display_tango_question(word)
    correct = False
    while not correct:
        user_input = input("単語の発音を入力してください：")
        find_index = -1
        for index, item in enumerate(review_words):
            if word['ID'] == item['ID']:
                find_index = index
                break
        if user_input == word['PRONUNCIATION_MATCH'] or user_input == word['WORD']:
            play_sound(word["MP3"])
            print(f"\n正解です！ {word['WORD']} {word['CHINESE']}｜{word['PRONUNCIATION_MATCH']}")
            if mode == MODE_MISTAKE:
                if find_index > -1:
                    word['mistakes'] -= 1
                    review_words[find_index] = word
            elif mode == MODE_ALL:
                current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                word["last_review"] = current_date
                word["times_review"] = -1
                if 'mistakes' not in word:
                    word['mistakes'] = 0
                if find_index > -1:
                    review_words[find_index] = word
                else:
                    review_words.append(word)
            elif mode == MODE_REVIEW:
                current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                word["last_review"] = current_date
                word["times_review"] += 1
            correct = True
        else:
            play_sound(word["MP3"])
            print(f"\n不正解です！ {word['WORD']} {word['CHINESE']}｜{word['PRONUNCIATION_MATCH']}")
            if mode == MODE_ALL or mode == MODE_REVIEW:
                if 'mistakes' not in word:
                    word['mistakes'] = 1
                else:
                    word['mistakes'] += 1
                if 'total_mistakes' not in word:
                    word['total_mistakes'] = 1
                else:
                    word['total_mistakes'] += 1
                if find_index > -1:
                    review_words[find_index] = word
                else:
                    review_words.append(word)
    return review_words

def play_sound(mp3_path):
    if PLAY_SOUND_FLAG:
        root_dir = os.path.dirname(os.path.abspath(__file__))
        full_mp3_path = os.path.join(root_dir, mp3_path)
        full_mp3_path = full_mp3_path.replace("\\", "/")
        full_mp3_path = full_mp3_path.replace("/voice", "voice")
        if not os.path.exists(full_mp3_path):
            print(f"ファイルはありません {full_mp3_path}")
            return
        sound = AudioSegment.from_mp3(full_mp3_path)
        play(sound)

# テストを実施
def test_words(words_to_test, review_words):
    for word in words_to_test:
        review_words = spelling_test(word, review_words, MODE_ALL)
    return review_words

# 覚えてる単語を再テスト
def remind_test(review_words):
    now = datetime.now()
    review_words_updated = [] 
    words_to_review = [word for word in review_words if 'last_review' in word]
    for word in words_to_review:
        last_review = word.get('last_review')
        time_since_review = (now - datetime.strptime(last_review, '%Y-%m-%d %H:%M:%S')).total_seconds()
        seconds_in_a_day = 86400
        for interval in Forgetting_Intervals:
            interval_in_seconds = interval * seconds_in_a_day
            if time_since_review >= interval_in_seconds:
                review_words_updated.append(word)
                break
    if len(review_words_updated) > 0:
        print("\n覚えてる単語を再テスト")
    else:
        print("\n覚えてる単語がない、再テスト不要")
    for word in review_words_updated:
        review_words = spelling_test(word, review_words, MODE_REVIEW)
    return review_words

# 覚えられない単語を再テスト
def review_test(review_words):
    words_to_review = [word for word in review_words if 'mistakes' in word and word['mistakes'] > 0]
    if len(words_to_review) > 0:
        print("\n覚えられない単語を再テスト...")
    else:
        print("\n覚えられない単語がない、再テスト不要")
    for word in words_to_review:
        review_words = spelling_test(word, review_words, MODE_MISTAKE)
    return review_words

# 練習プロセス
def process_exe(data, start_index, target_words_per_day, review_words):
    # 今日の新しい単語を取得
    words_to_learn = get_today_words(data, start_index, target_words_per_day)
    if len(words_to_learn) > 0:
        # 学習インデックスを更新
        start_index += len(words_to_learn)    
        # 新しい単語をテスト（学習）
        print("\n新しい単語の学習を始めます.")
        review_words = test_words(words_to_learn, review_words)
    else:
        print("\n新しい単語がありません.")
    re_review_words = remind_test(review_words)
    re_review_words = review_test(re_review_words)
    return start_index, re_review_words
