
# Vocabulary Memorization App - Tangogogo
- A vocabulary memorization application using the forgetting curve method to help users systematically learn and review Japanese words based on levels, parts of speech, and other customizable criteria.
## Feature Introduction
- Structured Learning Plans: Users can create tailored learning plans with daily goals and specified ranges (level, part of speech) to enhance memorization efficiency.
- Forgetting Curve-Based Review: Implements the forgetting curve for scheduled reviews to solidify memory over time.
- Mistake Tracking & Review: Tracks mistakes and provides targeted reviews to improve retention.
- Multi-criteria Filtering: Allows filtering vocabulary by part of speech, whether it is a Sino-Japanese word, and whether it uses Katakana.
- Cloud Sync Support: Provides Dropbox or other cloud sync options for secure data backup and restoration.
Learning Progress Tracking: Monitors user progress, mistake records, and review data for better planning.

## Environment Setup
### Python Environment
* 3.x
* source venv/bin/activate 

### Installing ffmpeg
#### macOS
```shell
brew install ffmpeg
```

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
```shell
pip install -r requirements.txt
```

### Running the Project
```shell
python main.py
```

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
```json
{
    "id": "5f36b246-c2f8-4724-a23a-0f49dedbe7d9",
    "create_date": "2024-09-12 11:26:48",
    "target_words_per_day": 18,
    "review_words": [],
    "data_indexes": []
}
```

## System Training Data

* Meaning: Training data records after the user selects the spelling training range (specified level, type, whether it's Katakana or not, and whether it's a Kango).

### Fields
- create_date -> Creation date
- last_date -> Last training time
- level -> Specified level
- type_s -> Specified category
- isKatakana -> Whether it's Katakana
- isKango -> Whether it's Kango
- data_len -> The number of words trained in this session
- start_index -> Index of the last word trained

## Workflow Design
- The application follows different workflows based on the presence of a training plan.

### Workflow 1: With an Existing Plan
- Retrieve the array of training models and locate the data for the current training session.
- Begin the spelling practice for new words, recording data as the user progresses.
- Review previously studied words based on the forgetting curve method.
- Conduct a mistake-focused review to reinforce weak areas.
- Update relevant data upon completion of the training session.

### Workflow 2: Without an Existing Plan
- Ask the user to specify the number of training days.
- Gather information on the user's preferred levels and parts of speech for training.
- Calculate the daily vocabulary load.
- Generate a personalized study plan based on the user’s preferences.

## Code File Structure
- /data: Contains various data files used by the application.
  - data_plan_map.json: Stores information relevant to vocabulary training.
  - processed_data_shuffle.json: Database of vocabulary words.
- /: Root directory of the application.
  - file_utils.py: File operations utility - includes logic for loading and saving files.
  - filters.py: Data filtering module - includes methods for filtering based on levels and other conditions.
  - process.py: Training module - handles vocabulary training and data persistence.
  - plan.py: Study plan module - includes plan generation and execution.
  - date_utils.py: Time utility functions.
  - dropbox_utils.py: Dropbox utility functions.
  - main.py: Main entry point for the application.

## Version Log
### Version 0.0.1
- Implemented range filtering.
- Enabled data persistence.
- Added mistake-focused review functionality.
- Integrated the forgetting curve for reviewing previously learned words.
### Version 0.0.2
- Enabled customization and execution of study plans.
### Version 0.0.3
- Added cloud sync support.
### Version 0.0.4
- Enhanced word filtering logic within the study plan feature.
- Adjusted word retrieval logic for improved study plan execution.
### Version 0.0.5
- Added learning statistics feature within study plans.