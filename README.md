# 🤖 JobSearchNotifier: Automated Scraper and Multi-Channel Notification Pipeline
JobSearchNotifier is a robust, modular Python pipeline designed to scrape job listings (e.g., from Glassdoor), filter them based on recency and keywords, and send personalized notifications via multiple channels (e.g., Telegram, Slack).

The architecture is built on the Strategy Pattern for communication, allowing for easy expansion to new platforms.

## ✨ Features
- **Multi-Channel Notifications**: Send alerts via Telegram, Slack, Email, etc., configurable via a central dispatcher.

- **Decoupled Architecture**: Clean separation of concerns (Scraping, Data Persistence, Business Logic, and Communication).

- **Persistent Data Handling**: Stores historical job listings in a local JSON file, preventing duplicate notifications.

- **Advanced Filtering**: Filters jobs based on publication date, lookback hours, required keywords, and excluded keywords.

- **Headless Scraping**: Utilizes Selenium with headless Chrome options for automated web interaction.

## 🛠️ Installation and Setup
### 1. Requirements
- **Python 3.8+**

- **Google Chrome** (required for Selenium/ChromeDriver)

- **ChromeDriver**: Ensure you have the correct version of ChromeDriver installed and accessible in your system's PATH.

### 2. Project Setup
```bash
# Clone the repository
git clone https://github.com/FlavorFlav-github/job-scrapper
cd job-scrapper

# Create a virtual environment and activate it
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```
### 3. Configuration
All critical settings are managed in the config.py file. You must edit this file before running the pipeline.

- **Job Search URLs** (PAGES_URL): Define the starting URLs for your job searches.

- **Keywords**: Set REQUIRED_KEYWORDS and EXCLUDED_KEYWORDS for job title filtering.

- **Communication Tokens**:
  - **Telegram**: Add your Bot Token and Chat ID to the env variables (.env file)

- **File Paths**: Set GLASSDOOR_JOBS_FILE to your desired storage path (e.g., data/jobs.json).

### 🚀 Usage
Run the main pipeline script from your project root:

```Bash

python main.py
```
#### Scheduling
For continuous monitoring, we recommend scheduling main.py using tools like Cron (Linux/macOS) or Task Scheduler (Windows) to run hourly or daily.

Example Cron Entry (runs every 12 hours):

```Bash
0 */12 * * * /path/to/JobSearchNotifier/venv/bin/python /path/to/JobSearchNotifier/main.py
```
### 🏗️ Architecture Overview
The project follows a Modular Design to ensure scalability and testability.

| Component       | 	Responsibility                                                          |	Relevant Files|
|-----------------|--------------------------------------------------------------------------|---------------|
| **Orchestrator**  | Executes the pipeline steps in order and handles logging.                | 	main.py|
| **Scraping/API**    | Handles Selenium browser control, token extraction, and GraphQL API calls. | 	glassdoor_scraper.py|
| **Data Handling**   | Manages reading/writing the persistent job database (jobs.json).         | 	data_handling.py|
| **Filtering/Logic** | Applies business rules: recency, keywords, language, and merging/pruning. | 	job_filtering.py|
| **Communication**   | Sends filtered messages using the Strategy Pattern to various channels.  | 	communication/ directory|
| **Configuration**   | Centralized constants and environment-specific settings.                 | 	config.py|

### 🔌 Extending Communication Channels
To add a new notification channel (e.g., Discord or Slack):

- Create a new sender class (e.g., SlackSender) in the communication directory that inherits from the MessageSender interface (Strategy Pattern).

- Implement the required send(content, content_type, config) method within your new class.

- Update the SENDER_MAP dictionary in your notification dispatcher to map the channel name ("slack") to your new class (SlackSender).

- Enable the new channel in your config.py.

### 🤝 Contributing
We welcome contributions! If you have suggestions for new features, bug fixes, or improvements to existing channels:

- Fork the repository.

- Create a new feature branch (git checkout -b feature/AmazingFeature).

- Commit your changes (git commit -m 'Add AmazingFeature').

- Push to the branch (git push origin feature/AmazingFeature).

- Open a Pull Request.

Please ensure your code adheres to Python best practices, includes type hints, and passes any existing tests.

**_Developed by Yassine/@FlavorFlav-github_**