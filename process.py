from file_utils import load_data
from datetime import datetime
from pydub import AudioSegment
from pydub.playback import play
import os
import random

Forgetting_Intervals = [1,7,30]

MODE_MISTAKE = 'M'
MODE_NEW = 'A'
MODE_REVIEW = 'R'

PLAY_SOUND_FLAG = 1

class Process:
    def __init__(self):
        pass

    def refresh_dict(self, dict):
        self.dict = dict

    def refresh_modes(self, modes):
        self.process_modes = modes
    
    # 訓練のデータ読み込み
    def load_data_index(self, level, type_s, isKango, isKatakana, data_len):
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
    def get_today_words(self, data, start_index, target_words_per_day):
        end_index = min(start_index + target_words_per_day, len(data))
        return data[start_index:end_index]

    # 単語表示
    def display_tango_question(self, word):
        print(f"\n中国語: {word['CHINESE']}")
        if len(word['TYPE1']) > 0:
            print(f"\n{word['TYPE1']} ")
        else:
            print(f"\n{word['TYPE']} ")
        if word['KATAKANA'] and "★" in word['KATAKANA']:
            print("カタカナ　⚪︎\t")
        if word['KANGO'] and "★" in word['KANGO']:
            print("漢語　⚪︎\t")
        return

    # 単語テスト関数（単語をテストし、正誤を判断）
    def spelling_test(self, word, review_words, mode):
        word_id = word["ID"]
        orgin_word = self.dict[word_id]
        self.display_tango_question(orgin_word)
        correct = False
        while not correct:
            user_input = input("単語の発音を入力してください：")
            find_index = -1
            for index, item in enumerate(review_words):
                if word['ID'] == item['ID']:
                    find_index = index
                    break
            print(f"find_index = {find_index} word id = {word['ID']}")
            match_res = orgin_word['PRONUNCIATION_MATCH'].replace("～", '').split('/')
            match_res = match_res + orgin_word['WORD'].replace("～", '').split('/')
            if user_input in match_res or user_input == 'pass':
                if user_input == 'pass':
                    print(f"\nスキップしました。")
                else:
                    self.play_sound(orgin_word["MP3"])
                print(f"\n正解です！ {orgin_word['WORD']} {orgin_word['CHINESE']}｜{orgin_word['PRONUNCIATION_MATCH']}")
                if mode == MODE_MISTAKE:
                    if find_index > -1:
                        word['mistakes'] -= 1
                        review_words[find_index] = word
                        print(f"{orgin_word['WORD']} findID = {find_index} wordID = {word['ID']} mistakes -> \n{word['mistakes']}")
                elif mode == MODE_NEW:
                    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    word["last_review"] = current_date
                    word["times_review"] = 0
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
                self.play_sound(orgin_word["MP3"])
                print(f"\n不正解です！ {orgin_word['WORD']} {orgin_word['CHINESE']}｜{orgin_word['PRONUNCIATION_MATCH']}")
                if mode == MODE_NEW or mode == MODE_REVIEW:
                    if 'mistakes' not in word:
                        word['mistakes'] = 1
                    else:
                        word['mistakes'] += 1
                    if 'total_mistakes' not in word:
                        word['total_mistakes'] = 1
                    else:
                        word['total_mistakes'] += 1
                    if find_index > -1:
                        print("word id = {word['ID']} refresh")
                        review_words[find_index] = word
                    else:
                        print("word id = {word['ID']} append")
                        review_words.append(word)
        return review_words

    def play_sound(self, mp3_path):
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
    def test_words(self, words_to_test, review_words):
        for item in words_to_test:
            word = {"ID": item}
            review_words = self.spelling_test(word, review_words, MODE_NEW)
        return review_words

    # 覚えてる単語を再テスト
    def remind_test(self, review_words):
        now = datetime.now()
        review_words_updated = [] 
        words_to_review = [word for word in review_words if 'last_review' in word]
        for word in words_to_review:
            last_review = word.get('last_review')
            time_since_review = (now - datetime.strptime(last_review, '%Y-%m-%d %H:%M:%S')).total_seconds()
            seconds_in_a_day = 86400
            times_review = word.get('times_review')
            if isinstance(times_review, int) and 0 <= times_review < len(Forgetting_Intervals):
                interval_in_seconds = Forgetting_Intervals[times_review] * seconds_in_a_day
                if interval_in_seconds <= time_since_review:
                    review_words_updated.append(word)
            else:
                raise ValueError("Invalid times_review or Forgetting_Intervals index.")
        if len(review_words_updated) > 0:
            print("\n覚えてる単語を再テスト")
        else:
            print("\n覚えてる単語がない、再テスト不要")
        random.shuffle(review_words_updated)
        for word in review_words_updated:
            review_words = self.spelling_test(word, review_words, MODE_REVIEW)
        return review_words

    # 覚えられない単語を再テスト
    def re_mistake_test(self, review_words):
        words_to_review = [word for word in review_words if 'mistakes' in word and word['mistakes'] > 0]
        if len(words_to_review) > 0:
            print(f"\n覚えられない単語を再テスト...　数：{len(words_to_review)}")
        else:
            print("\n覚えられない単語がない、再テスト不要")
        random.shuffle(words_to_review)
        for word in words_to_review:
            review_words = self.spelling_test(word, review_words, MODE_MISTAKE)
        return review_words

    # 練習プロセス
    def process_exe(self, process_data, start_index, target_words_per_day, review_words):
        re_review_words = []
        if MODE_NEW in self.process_modes:
            # 今日の新しい単語を取得
            words_to_learn = self.get_today_words(process_data, start_index, target_words_per_day)
            if len(words_to_learn) > 0:
                # 学習インデックスを更新
                start_index += len(words_to_learn)    
                # 新しい単語をテスト（学習）
                print("\n新しい単語の学習を始めます.")
                res = self.test_words(words_to_learn, review_words)
                re_review_words = res
            else:
                print("\n新しい単語がありません.")
        if MODE_REVIEW in self.process_modes or MODE_MISTAKE in self.process_modes:
            if MODE_REVIEW in self.process_modes:
                remind_test_res = self.remind_test(review_words)
                re_review_words = remind_test_res
            if MODE_MISTAKE in self.process_modes:
                re_mistake_res = self.re_mistake_test(re_review_words or review_words)
                re_review_words = re_mistake_res
        return start_index, re_review_words


