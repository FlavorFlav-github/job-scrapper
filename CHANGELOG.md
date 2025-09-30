# Changelog

## 🚀 Version 1.0.0 - Initial Modular Release (2025-09-30)
This release marks the initial public version of the JobSearchNotifier project, focused on a complete refactoring and restructuring of the codebase from a single procedural script into a highly modular, maintainable, and testable application.

### ✨ New Features
- **Modular Architecture**: The pipeline is now broken into separate, decoupled modules for Scraping, Data Handling, Business Logic, and Orchestration.

- **Centralized Configuration**: All constants and external dependencies are now managed via the dedicated config.py file.

- **Explicit Job Persistence**: Implemented a robust JobRepository to manage reading, merging new jobs, and pruning old entries from the JSON file.

- **Dedicated Filtering Logic**: Introduced the JobFilter class to handle filtering based on recency, required keywords, excluded keywords, and language.

### ♻️ Refactoring and Improvements
- Decoupled Dependencies: Eliminated direct, hard-coded dependencies on global const variables throughout the core logic by passing configuration parameters to classes and functions (Dependency Injection).

- Improved Scraping:

  - Moved the Selenium browser management and initial token extraction into the GlassdoorScraper class.

  - Extracted the GraphQL API interaction and large query string into the dedicated GlassdoorAPIClient for clean, reusable network calls.

- Implemented proper driver cleanup using driver.quit() within the Scraper class.

- Enhanced Error Handling: Replaced generic except Exception blocks with specific exception catching (FileNotFoundError, JSONDecodeError, IOError) and integrated Python's standard logging module instead of using print() for warnings and errors.

- Data Mapping: Extracted raw JSON-to-standardized-dictionary transformation into the reusable map_raw_glassdoor_job function in data_handling.py.

- Clean Orchestration: Moved the procedural script flow into a clean main.py entry point.

### 🗑️ Removals
- Removed the original monolithic script file.

- Removed all hardcoded file paths and constants from application logic files.