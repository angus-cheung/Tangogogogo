# 单词背诵设计
## 功能介绍
* 通过利用遗忘曲线的方法，有计划和系统地进行拼写日语单词的读音。
* 可以指定级别、词性等范围

## 环境部署
### python 环境
* 3.x
### ffmpeg 安装
#### macOS
```bash
brew install ffmpeg
```
#### Windows
- 访问 [FFmpeg 下载页面](https://ffmpeg.org/download.html)。
- 下载 Windows 版的 ffmpeg，并解压到一个文件夹中。
    - 将 ffmpeg 的 bin 目录添加到系统的环境变量中：
    - 右键点击 “此电脑” 或 “我的电脑”，选择 “属性”。
    - 点击左侧的 “高级系统设置”。
    - 在 “系统属性” 中，点击 “环境变量”。
    - 在 “系统变量” 中找到 Path，点击 “编辑”，然后添加 ffmpeg/bin 的路径。
- 打开命令提示符（按 Win + R，输入 cmd，回车）。
- 输入以下命令：
```bash
ffmpeg -version
```
- 如果输出了版本信息，说明 ffmpeg 安装成功。
- 在某些情况下，你可能需要配置项目依赖的环境变量，特别是 ffmpeg 的路径。如果 pydub 无法找到 ffmpeg，你可以显式地设置 ffmpeg 的路径。
  - 手动设置 ffmpeg 的路径（如果 pydub 无法自动找到）
```python
os.environ["PATH"] += os.pathsep + "path/to/ffmpeg/bin"
```
### 安装依赖库
```bash
pip install -r requirements.txt
```
### 运行项目
```bash
python main.py
```
## 数据模型
### 训练计划的数据
* 含义 用户指定的训练计划
#### 字段
- id -> 
- create_date -> 创建日期
- target_words_per_day -> 一天的训练量
- review_words ->  所有训练的背诵记录，详见下面
- data_indexs -> 单次系统训练的数据，详见下面
### 数据例子
* 如下
```json
{
    "id": "5f36b246-c2f8-4724-a23a-0f49dedbe7d9",
    "create_date": "2024-09-12 11:26:48",
    "target_words_per_day": 18,
    "review_words": [],
    "data_indexs": []
}
```
### 单次系统训练的数据
* 含义 用户选定拼写训练范围 (指定的级别-level 类别-type_s 是否汉词-isKango 是否片假名-isKatakana) 后的训练数据记录
#### 字段
- create_date -> 创建日期
- last_date -> 最后训练时间
- level -> 指定的级别
- type_s -> 指定的种类
- isKatakana -> 是否片假名
- isKango -> 是否汉词
- data_len -> 此次训练的单词数量
- start_index -> 已训练到单词的下标
### 数据例子
* 如下
```json
[
    {
        "uuid": "N5動漢語　×カタカナ　×",
        "create_date": "2024-09-12 11:26:48",
        "level": "N5",
        "type_s": "動",
        "isKatakana": "カタカナ　×",
        "isKango": "漢語　×",
        "last_date": "2024-09-12 11:31:05",
        "start_index": 36,
        "data_len": 133
    },
    {
        "uuid": "N5動漢語　×カタカナのみ",
        "create_date": "2024-09-12 11:26:48",
        "level": "N5",
        "type_s": "動",
        "isKatakana": "カタカナのみ",
        "isKango": "漢語　×",
        "last_date": "2024-09-12 11:26:48",
        "start_index": 0,
        "data_len": 5
    },
    {
        "uuid": "N5動漢語のみカタカナ　×",
        "create_date": "2024-09-12 11:26:48",
        "level": "N5",
        "type_s": "動",
        "isKatakana": "カタカナ　×",
        "isKango": "漢語のみ",
        "last_date": "2024-09-12 11:26:48",
        "start_index": 0,
        "data_len": 33
    }
]
```
### 所有训练的背诵记录
* json名称 review_words.json 
* 含义 记录用户每次训练的后，每个单词的一些数据
#### 字段
- ID -> 唯一键
- WORD -> 单词
- PRONUNCIATION_MATCH -> 发音
- MP3 -> 单词音频的对应文件路径
- TYPE1 -> 词的种类，由于一个单词可以有多个词性，属于数组
- CHINESE -> 单词的中文含义
- KANGO -> 是否属于汉语词
- KATAKANA -> 是否用片假名拼写
- times_review -> 复习次数
- last_review -> 最后复习时间
- mistakes -> 当前错误次数(会递减递增 用于错题复习)
- total_mistakes -> 历史错误次数
### 数据例子
```json
[
    {
        "ID": 4607,
        "WORD": "炊く",
        "PRONUNCIATION": "たく",
        "MP3": "\\voice\\N2\\4607.mp3",
        "LEVEL": "N2",
        "TYPE": "[他動１]",
        "ALTERNATIVE": null,
        "CHINESE": "煮，烧",
        "KANGO": null,
        "KATAKANA": null,
        "TYPE1": [
            "動",
            "他動"
        ],
        "PRONUNCIATION_MATCH": "たく",
        "last_review": "2024-09-05 17:49:25",
        "times_review": -1,
        "mistakes": 0,
        "total_mistakes": 0
    }
]
```
## 流程设计
* 判断是否有计划， 有则按流程1，没有计划 按流程2

### 流程1
* 获取训练模型数组，寻找当前正在训练的数据
* 执行新单词的拼写训练，并在途中记录数据
* 根据遗忘曲线，背诵旧单词
* 背诵错题
* 训练完毕，更新相关数据
* 程序结束

### 流程2
* 询问用户计划训练的天数
* 询问用户训练的等级范围
* 询问用户训练的词性范围
* 计算每天训练的单词量
* 生成计划
* 程序结束

## 代码文件结构
- `/data`：保存应用程序使用的各种数据文件。
  - `data_plan_map.json`：存储单词训练的相关信息
  - `processed_data_shuffle.json`：单词数据库
- `/`：程序根目录
  - `file_utils.py`：文件操作工具类 - 包含文件加载和保存的逻辑
  - `filters.py`：数据过滤 - 包含通过等级各种条件的过滤方法
  - `process.py`：训练 - 单词训练处和数据持久化
  - `plan.py`：学习计划 - 包含生成训练计划、执行计划
  - `date_utils.py`：时间工具类
  - `dropbox_uitils.py`：dropbox工具类
  - `main.py`：应用程序的主入口

## 版本日志
### 0.0.1
* 实现范围筛选
* 实现数据持久化
* 支持错题复习
* 利用遗忘曲线复习旧单词

### 0.0.2
* 实现学习计划定制
* 实现学习计划执行

### 0.0.3
* 支持云同步

### 0.0.4
* 调整学习计划功能中筛选单词的逻辑
* 调整学习计划中单词读取的逻辑

### 0.0.5
* 学习计划实现学习统计功能