<h1 align="center">GitHub API Key Scraper</h1>

<p align="center">
  A powerful tool designed to identify and collect exposed Google API keys across GitHub repositories, leveraging the robust Scrapy framework for efficient data extraction.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Project%20Status-Active-green" alt="Project Status: Active">
</p>

## 🚀 Project Structure

The project is organized as follows to ensure easy navigation and management:

```plaintext
project_root/
├── .gitignore                # Files to ignore
├── bad_api_keys.txt          # Invalid API keys storage
├── cookies.txt               # GitHub authentication cookies
├── good_api_keys.txt         # Valid API keys storage
├── requirements.txt          # Python dependencies
├── run.py                    # Script to run spiders
├── scrapy.cfg                # Scrapy configuration
├── settings.py               # Project settings
├── show_files.py             # Display project structure
└── spiders/                  # Spiders directory
    ├── git_hub_crawler.py    # GitHub crawling spider
    └── git_hub_parser.py     # HTML page parser for API keys
```

## 🛠 Setup

To set up the scraper, follow these steps:

1. **Install Python dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

2. Ensure **Scrapy** is installed in your environment.

3. **Update `cookies.txt`** with your GitHub cookies for authentication.

### 🚀 Running the Scraper

To initiate the scraping process:

- Navigate to the project's root directory.
- Execute:
  ```bash
  scrapy crawl git_hub_crawler
  ```
  or
  ```bash
  python run.py
  ```

## 📝 Notes

- Utilize this tool responsibly and ethically, adhering to GitHub's robots.txt and terms of service.
- The scraper's performance relies on updated `cookies.txt` for effective GitHub authentication.
- Intended solely for educational and security research purposes. The developers are not liable for misuse or damage.

---

<p align="center">
  <b>✨ Contributions are welcome! ✨</b>
</p>
```