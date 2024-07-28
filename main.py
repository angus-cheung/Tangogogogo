import json
import random
import time

# 定义错题集
incorrect = []

# 函数：询问用户条件
def ask_user_condition():
    level = input("请输入要学习的单词等级（例如：N5）：")
    types = input("请输入要学习的单词类型，多个类型用逗号分隔（例如：[自動1]）：").split(',')
    types = [t.strip('[').strip(']').strip() for t in types]
    num_of_words = int(input("请输入要测试的单词数量："))
    time_limit = int(input("请输入单词拼写的时间（秒）："))
    return level, types, num_of_words, time_limit

# 函数：筛选符合条件的单词
def filter_words(data, level, types, num_of_words):
    # filtered_words = [word for word in data if word['LEVEL'] == level and word['TYPE'] in types]
    filtered_words = [word for word in data if word['LEVEL'] == level]
    random.shuffle(filtered_words)
    return filtered_words[:num_of_words]

# 函数：拼写测试
def spelling_test(words_to_test, time_limit):
    score = 0
    incorrect = []
    for word in words_to_test:
        print(f"\n中文意思：{word['CHINESE']}")
        print("请在规定时间内拼写单词的发音：")
        start_time = time.time()
        user_input = ""
        try:
            while time.time() - start_time < time_limit:
                user_input = input()
                if user_input == word['PRONUNCIATION']:
                    print("拼写正确！")
                    score += 1
                    break
                else:
                    print(f"拼写错误！正确的发音是：{word['PRONUNCIATION']}")
        except KeyboardInterrupt:
            print("\n拼写时间到！")
        if user_input != word['PRONUNCIATION']:
            incorrect.append(word)
            print(f"\n记住哦，{word['WORD']} 的发音是 {word['PRONUNCIATION']}。")
    return score, incorrect

# 函数：保存错题集
def save_incorrect(incorrect):
    with open('incorrect.json', 'w', encoding='utf-8') as f:
        json.dump(incorrect, f, ensure_ascii=False, indent=4)

# 主程序
def main():
    # 读取数据
    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        print(f"\n单词题库：{len(data)}")
        level, types, num_of_words, time_limit = ask_user_condition()
        words_to_test = filter_words(data, level, types, num_of_words)  # 更新这里传递num_of_words
        print(f"\n测试单词数量：{len(words_to_test)}")
        score = spelling_test(words_to_test, time_limit)
        save_incorrect(incorrect)
        print(f"\n测试结束，你拼写正确的单词数量为：{score}/{num_of_words}")

if __name__ == "__main__":
    main()