
# Word Memorization Design
## Feature Introduction
* By using the method of the forgetting curve, the pronunciation spelling of Japanese words is planned and systematically conducted.
* You can specify the range, such as level and part of speech.

## Environment Setup
### Python Environment
* 3.x

### Installing ffmpeg
#### macOS
brew install ffmpeg

#### Windows
- Visit the FFmpeg download page.
- Download the Windows version of ffmpeg and extract it to a folder.
    - Add the bin directory of ffmpeg to the system’s environment variables:
    - Right-click “This PC” or “My Computer” and select “Properties.”
    - Click on “Advanced system settings” on the left side.
    - In the “System Properties” window, click “Environment Variables.”
    - In the “System Variables” section, find Path, click “Edit,” and then add the path to ffmpeg/bin.
- Open the Command Prompt (press Win + R, type cmd, and press Enter).
- Enter the following command:
ffmpeg -version
- If version information is displayed, it means ffmpeg has been successfully installed.
- In some cases, you may need to configure environment variables for project dependencies, especially the ffmpeg path. If pydub cannot find ffmpeg, you can explicitly set the ffmpeg path.
  - Manually set the ffmpeg path (if pydub cannot automatically locate it):
os.environ["PATH"] += os.pathsep + "path/to/ffmpeg/bin"

### Installing Dependencies
pip install -r requirements.txt

### Running the Project
python main.py

## Data Model
### Training Plan Data
* Meaning: The training plan specified by the user.
#### Fields
- id -> 
- create_date -> Creation date
- target_words_per_day -> Daily training volume
- review_words -> All memorization records from training, as detailed below.
- data_indexes -> Data from each system training session, as detailed below.

### Data Example
* As shown:
{
    "id": "5f36b246-c2f8-4724-a23a-0f49dedbe7d9",
    "create_date": "2024-09-12 11:26:48",
    "target_words_per_day": 18,
    "review_words": [],
    "data_indexes": []
}

### System Training Data
* Meaning: Training data records after the user selects the spelling training range (specified level, type, whether it's Katakana or not, and whether it's a Kango).
#### Fields
- create_date -> Creation date
- last_date -> Last training time
- level -> Specified level
- type_s -> Specified category
- isKatakana -> Whether it's Katakana
- isKango -> Whether it's Kango
- data_len -> The number of words trained in this session
- start_index -> Index of the last word trained

