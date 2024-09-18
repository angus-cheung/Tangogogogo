import json
import re
import random
import jaconv

def categorize_type(type_str):
    categories = []
    if '名' in type_str:
        categories.append('名')
    if re.search(r'他動|自動|自他動', type_str):
        categories.append('動')
    if '他動' in type_str:
        categories.append('他動')
    if '自動' in type_str:
        categories.append('自動')
    if '自他動' in type_str:
        categories.append('自他動')
    if 'イ形' in type_str:
        categories.append('形')
    if 'イ形' in type_str:
        categories.append('イ形')
    if 'ナ形' in type_str:
        categories.append('ナ形')
    if '副' in type_str:
        categories.append('副')
    if '接' in type_str:
        categories.append('接')
    if '接尾' in type_str:
        categories.append('接尾')
    if '接頭' in type_str:
        categories.append('接頭')
    if '連' in type_str:
        categories.append('連')
    if '連語' in type_str:
        categories.append('連語')
    if '連体' in type_str:
        categories.append('連体')
    if '嘆' in type_str:
        categories.append('嘆')
    return categories

def process_word_data(data):
    for word in data:
        del word["Unnamed: 12"]
        del word["Unnamed: 13"]
        del word["Unnamed: 14"]
        del word["Unnamed: 15"]
        del word["Unnamed: 16"]
        del word["Unnamed: 17"]
        del word["Unnamed: 18"]
        del word["Unnamed: 19"]
        del word["Unnamed: 20"]
        del word["Unnamed: 21"]
        del word["Unnamed: 22"]
        del word["Unnamed: 23"]
        del word["PAGE"]
        del word["L/R"]
        type_str = word.get('TYPE', '')
        word['TYPE1'] = categorize_type(type_str)
        text = word.get('PRONUNCIATION', '')
        if text:
            word['PRONUNCIATION_MATCH'] = text.replace('～', '')
        else:
            word_str = word.get('WORD', '')
            if word_str:
                hiragana_text = jaconv.kata2hira(jaconv.z2h(word_str, kana=True, digit=False, ascii=False))
                word['PRONUNCIATION_MATCH'] = hiragana_text
            else:
                word['PRONUNCIATION_MATCH'] = '*'
    return data

def main():
    with open('data.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    processed_data = process_word_data(data)
    random.shuffle(processed_data)
    with open('processed_data_shuffle.json', 'w', encoding='utf-8') as file:
        # json.dump(processed_data, file, ensure_ascii=False, indent=4)
        json.dump(processed_data, file, ensure_ascii=False, separators=(',', ':'))
if __name__ == '__main__':
    main()
