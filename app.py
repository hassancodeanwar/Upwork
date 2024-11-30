import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import time
import json
import re

class NYTBestsellersScraper:
    def __init__(self):
        self.base_url = "https://www.nytimes.com/books/best-sellers/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.nytimes.com/books/best-sellers/'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def get_bestsellers_for_date(self, year, month, day):
        """
        Scrape bestsellers for a specific date
        
        Args:
            year (int): Year of bestseller list
            month (int): Month of bestseller list
            day (int): Day of bestseller list
        
        Returns:
            list: Bestseller books details
        """
        # Construct full URL with more specific format
        url = f"{self.base_url}{year}/{month:02d}/{day:02d}/combined-print-and-e-book-nonfiction/"
        
        try:
            # Send GET request
            response = self.session.get(url)
            
            # Check if request was successful
            if response.status_code != 200:
                print(f"Failed to retrieve page: {response.status_code}")
                print(f"URL: {url}")
                return []
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all book articles
            book_elements = soup.find_all('article', class_='css-1u6k25n')
            
            # Extract book details
            books = []
            for element in book_elements:
                book_info = self._extract_book_details(element)
                if book_info:
                    books.append(book_info)
            
            return books
        
        except Exception as e:
            print(f"Error scraping {year}-{month}-{day}: {e}")
            return []

    def _extract_book_details(self, element):
        """
        Extract individual book details from a book element
        
        Args:
            element (BeautifulSoup): Beautiful Soup element for a book
        
        Returns:
            dict: Book details
        """
        try:
            # Extract title
            title_elem = element.find('h3', class_='css-5pe77f')
            title = title_elem.text.strip() if title_elem else "Unknown Title"
            
            # Extract author
            author_elem = element.find('p', class_='css-hjukut')
            author = author_elem.text.replace('by ', '').strip() if author_elem else "Unknown Author"
            
            # Extract publisher
            publisher_elem = element.find('p', class_='css-heg334')
            publisher = publisher_elem.text.strip() if publisher_elem else "Unknown Publisher"
            
            # Extract description
            desc_elem = element.find('p', class_='css-14lubdp')
            description = desc_elem.text.strip() if desc_elem else "No description"
            
            # Check if it's new this week
            new_this_week_elem = element.find('p', class_='css-1o26r9v')
            new_this_week = new_this_week_elem is not None
            
            # Extract ISBN - use more robust method
            isbn_elems = element.find_all('meta', itemprop='isbn')
            isbn = isbn_elems[0].get('content', None) if isbn_elems else None
            
            # Extract book image URL
            image_elem = element.find('footer', class_='css-1d36f7m')
            image_url = image_elem.find('img')['src'] if image_elem and image_elem.find('img') else None
            
            return {
                "title": title,
                "author": author,
                "publisher": publisher,
                "description": description,
                "new_this_week": new_this_week,
                "isbn": isbn,
                "image_url": image_url
            }
        except Exception as e:
            print(f"Error extracting book details: {e}")
            return {}

    def scrape_bestsellers_range(self, start_year=2019, end_year=2024):
        """
        Scrape bestsellers across multiple years
        """
        all_bestsellers = []
        
        # Generate dates for scraping
        current_date = datetime(start_year, 1, 1)
        end_date = datetime(end_year, 12, 8)
        
        while current_date <= end_date:
            try:
                # Scrape bestsellers for this date
                bestsellers = self.get_bestsellers_for_date(
                    current_date.year, 
                    current_date.month,
                    current_date.day
                )
                
                # Add scrape date to each book
                for book in bestsellers:
                    book['scrape_date'] = current_date
                
                all_bestsellers.extend(bestsellers)
                
                # Add delay to avoid rate limiting
                time.sleep(1)
                
                # Move to next week
                current_date += timedelta(days=7)
            
            except Exception as e:
                print(f"Error in date {current_date}: {e}")
                # Move to next week even if there's an error
                current_date += timedelta(days=7)
        
        return pd.DataFrame(all_bestsellers)

    def save_to_formats(self, dataframe, base_filename='nyt_bestsellers'):
        """
        Save scraped data to multiple formats
        """
        # Save to CSV
        dataframe.to_csv(f'{base_filename}.csv', index=False)
        
        # Save to JSON
        dataframe.to_json(f'{base_filename}.json', orient='records', indent=2)
        
        # Save to Excel
        dataframe.to_excel(f'{base_filename}.xlsx', index=False)

def main():
    scraper = NYTBestsellersScraper()
    
    try:
        # Scrape bestsellers from 2019-2024
        bestsellers_df = scraper.scrape_bestsellers_range()
        
        # Save to multiple formats
        scraper.save_to_formats(bestsellers_df)
        
        print("Scraping completed successfully!")
        print(f"Total books scraped: {len(bestsellers_df)}")
        
        # Pretty print first few books
        print("\nSample Books:")
        print(json.dumps(bestsellers_df.head().to_dict(orient='records'), indent=2))
    
    except Exception as e:
        print(f"Scraping failed: {e}")

if __name__ == "__main__":
    main()