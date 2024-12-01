# Technical Documentation for NYT Bestsellers Scraper

---

## Title  
**NYT Bestsellers Scraper**

## Author  
**Hassan Anwar**

## Publisher  
GitHub Repository: [Upwork](https://github.com/hassancodeanwar/Upwork)

---

### **Description**  
This script is designed to scrape book details from the New York Times Bestsellers page for a specified range of dates. It collects detailed information about each bestseller, including its title, author, publisher, description, weeks on the list, and cover image URL. The scraped data can be saved in CSV, JSON, and Excel formats.

---

### **File Structure**  

#### **Requirements**  
- `/workspaces/Upwork/requirements.txt`  
  Lists the dependencies required for the script:
  - `requests`
  - `beautifulsoup4`
  - `pandas`
  - `openpyxl`

#### **Additional Files**  
- `/workspaces/Upwork/google-chrome-stable_current_amd64.deb`  
  The Debian package for installing Google Chrome, used for browser emulation if needed for future enhancements.

#### **Script**  
- `app.py`  
  Contains the main scraper implementation.

---

### **Script Components**

#### **1. Initialization**
```python
class NYTBestsellersScraper:
    def __init__(self):
        self.base_url = "https://www.nytimes.com/books/best-sellers/"
        self.headers = { ... }  # User-agent and headers for web requests
        self.session = requests.Session()
        self.session.headers.update(self.headers)
```
- Initializes a session for HTTP requests with appropriate headers to mimic a real browser.

---

#### **2. Scraping Bestsellers for a Date**
```python
def get_bestsellers_for_date(self, year, month, day):
    ...
```
- **Input:** Date parameters (`year`, `month`, `day`).  
- **Output:** List of dictionaries containing book details.  

---

#### **3. Extracting Book Details**
```python
def _extract_book_details(self, element):
    ...
```
- **Input:** BeautifulSoup element of a book.  
- **Output:** Dictionary with fields:
  - `title`
  - `author`
  - `publisher`
  - `description`
  - `new_this_week`
  - `weeks_on_list`
  - `isbn`
  - `image_url`

---

#### **4. Scraping for a Date Range**
```python
def scrape_bestsellers_range(self, start_year=2019, end_year=2024):
    ...
```
- **Purpose:** Scrapes books across multiple years with a weekly interval.  
- **Output:** A Pandas DataFrame containing all book data.  

---

#### **5. Saving Data to Formats**
```python
def save_to_formats(self, dataframe, base_filename='nyt_bestsellers'):
    ...
```
- Saves the scraped data to:
  - CSV
  - JSON
  - Excel (requires `openpyxl`).

---

### **Usage**  

#### **Run the Script**
```bash
python app.py
```
The script:
1. Scrapes bestsellers from 2019 to 2024.
2. Saves the data as `nyt_bestsellers.csv`, `nyt_bestsellers.json`, and `nyt_bestsellers.xlsx`.

#### **Sample Data Output**  
| Title     | Author         | Publisher | Description                                     | New This Week | Weeks on List | ISBN       | Image URL                                   | Scrape Date |
|-----------|----------------|-----------|------------------------------------------------|---------------|---------------|------------|---------------------------------------------|-------------|
| BECOMING  | Michelle Obama | Crown     | The former first lady describes her journey... | True          | 6             | 1524763136 | [https://storage.googleapis.com/.../978...jpg](https://storage.googleapis.com/du-prd/books/images/9781524763138.jpg) | 2019-01-01  |

---

### **Dependencies**

Install required Python libraries:
```bash
pip install -r requirements.txt
```

---

### **Enhancements**
1. **Debian Package:** The `google-chrome-stable_current_amd64.deb` file is included for future browser automation if BeautifulSoup scraping encounters dynamic content.  
2. **Error Handling:** Graceful error handling ensures continuous scraping even when a date fails.

---

### **Limitations**
- Assumes the website's structure remains consistent.
- Relies on static scraping; dynamic scraping can be incorporated using Selenium or Playwright if required.

--- 

### **Contact**
For further queries or contributions, visit the [GitHub Repository](https://github.com/hassancodeanwar/Upwork). 
