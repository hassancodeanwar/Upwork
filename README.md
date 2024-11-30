# NYT Bestsellers Scraper

## Overview

The NYT Bestsellers Scraper is a Python-based web scraping tool designed to extract bestselling book information from the New York Times Best Sellers list. It allows users to retrieve comprehensive book details across multiple dates and save the data in various formats.

## Dependencies

- `beautifulsoup4` (v4.12.3): HTML parsing library
- `pandas` (v2.2.3): Data manipulation and analysis library
- `requests` (v2.32.3): HTTP request library

## Installation

1. Install Python 3.8+
2. Create a virtual environment (recommended)
3. Install dependencies:
   ```bash
   pip install beautifulsoup4==4.12.3 pandas==2.2.3 requests==2.32.3
   ```

## Core Components

### `NYTBestsellersScraper` Class

#### Initialization
- Sets base URL for NYT Best Sellers list
- Configures custom headers to mimic browser request
- Creates a persistent HTTP session

#### Methods

1. `get_bestsellers_for_date(year, month, day)`
   - Scrapes bestseller books for a specific date
   - Returns a list of book dictionaries
   
   **Parameters:**
   - `year` (int): Target year
   - `month` (int): Target month
   - `day` (int): Target day

2. `_extract_book_details(element)`
   - Internal method to parse individual book details
   - Extracts:
     * Title
     * Author
     * Publisher
     * Description
     * "New This Week" status
     * ISBN
     * Image URL
   
3. `scrape_bestsellers_range(start_year=2019, end_year=2024)`
   - Comprehensive scraping across multiple years
   - Generates a DataFrame with all scraped books
   - Implements rate limiting to prevent IP blocking
   
   **Parameters:**
   - `start_year` (int, optional): Starting year for scraping
   - `end_year` (int, optional): Ending year for scraping

4. `save_to_formats(dataframe, base_filename='nyt_bestsellers')`
   - Saves scraped data to multiple file formats
   - Generates:
     * CSV
     * JSON
     * Excel spreadsheet

## Usage Example

```python
from nyt_bestsellers_scraper import NYTBestsellersScraper

# Initialize scraper
scraper = NYTBestsellersScraper()

# Scrape bestsellers from 2019-2024
bestsellers_df = scraper.scrape_bestsellers_range()

# Save to multiple formats
scraper.save_to_formats(bestsellers_df)
```

## Error Handling

- Graceful handling of network errors
- Prints detailed error messages
- Continues scraping even if individual date retrieval fails

## Performance Considerations

- Uses `requests.Session()` for connection pooling
- Implements 1-second delay between requests to avoid rate limiting
- Supports large-scale data extraction across multiple years

## Limitations

- Depends on NYT website's current HTML structure
- May require updates if website design changes
- Limited to specific bestseller categories

## Recommended Improvements

1. Add proxy support for large-scale scraping
2. Implement more robust error retry mechanism
3. Add configuration for different bestseller categories
4. Create option for incremental/resumable scraping

## Legal Considerations

- Ensure compliance with NYT's Terms of Service
- Use responsibly and respect website's robots.txt
- Consider obtaining official API access for large-scale data retrieval

## Logging and Monitoring

- Prints scraping progress and errors to console
- Captures total number of books scraped
- Provides sample book data for quick verification

## Security Notes

- Uses custom User-Agent to mimic browser requests
- Implements basic request headers for improved scraping reliability
