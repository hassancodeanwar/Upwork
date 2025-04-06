import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import json
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent

class RealEstateScraper:
    def __init__(self):
        self.user_agent = UserAgent()
        self.session = requests.Session()
        self.headers = {
            'User-Agent': self.user_agent.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Configure Chrome options for Selenium
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument(f"user-agent={self.user_agent.random}")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--window-size=1920,1080")
        
    def initialize_browser(self):
        """Initialize the Selenium browser for JavaScript-heavy pages"""
        self.driver = webdriver.Chrome(options=self.chrome_options)
        return self.driver
    
    def _random_delay(self, min_seconds=2, max_seconds=5):
        """Add random delay between requests to avoid detection"""
        time.sleep(random.uniform(min_seconds, max_seconds))
    
    def _rotate_user_agent(self):
        """Rotate user agent to avoid detection"""
        self.headers['User-Agent'] = self.user_agent.random
        
    def scrape_centris(self, search_url, max_pages=10):
        """
        Scrape property listings from Centris.ca
        
        Args:
            search_url: URL with search parameters
            max_pages: Maximum number of pages to scrape
        
        Returns:
            List of property dictionaries
        """
        driver = self.initialize_browser()
        all_properties = []
        
        try:
            driver.get(search_url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".property-thumbnail-container"))
            )
            
            # Handle cookie consent if it appears
            try:
                cookie_button = driver.find_element(By.CSS_SELECTOR, ".cookie-consent-button")
                cookie_button.click()
                time.sleep(1)
            except:
                pass
                
            current_page = 1
            
            while current_page <= max_pages:
                # Get listing URLs from search results
                listing_elements = driver.find_elements(By.CSS_SELECTOR, ".property-thumbnail-container")
                listing_urls = []
                
                for element in listing_elements:
                    try:
                        url = element.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                        listing_urls.append(url)
                    except:
                        continue
                
                # Visit each listing page and extract data
                for url in listing_urls:
                    try:
                        property_data = self._extract_centris_listing(url)
                        if property_data:
                            all_properties.append(property_data)
                    except Exception as e:
                        print(f"Error scraping listing {url}: {e}")
                    
                    self._random_delay()
                
                # Try to go to next page if available
                try:
                    next_button = driver.find_element(By.CSS_SELECTOR, ".pagination-next:not(.disabled)")
                    next_button.click()
                    WebDriverWait(driver, 10).until(
                        EC.staleness_of(listing_elements[0])
                    )
                    current_page += 1
                    self._random_delay(3, 6)
                except:
                    # No more pages or element not found
                    break
                    
        except Exception as e:
            print(f"Error during Centris scraping: {e}")
        finally:
            driver.quit()
            
        return all_properties
    
    def _extract_centris_listing(self, url):
        """Extract data from a single Centris listing page"""
        driver = webdriver.Chrome(options=self.chrome_options)
        property_data = {}
        
        try:
            driver.get(url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".property-summary"))
            )
            
            # Basic listing info
            property_data["source"] = "Centris"
            property_data["listing_url"] = url
            property_data["scrape_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Property ID
            try:
                property_id = driver.find_element(By.CSS_SELECTOR, ".property-id").text
                property_data["property_id"] = property_id.replace("MLS:", "").strip()
            except:
                property_data["property_id"] = None
                
            # Title and Address
            try:
                title = driver.find_element(By.CSS_SELECTOR, ".property-title").text
                property_data["title"] = title.strip()
            except:
                property_data["title"] = None
                
            try:
                address = driver.find_element(By.CSS_SELECTOR, ".property-address").text
                property_data["address"] = address.strip()
                
                # Try to extract city, province, postal code
                address_parts = address.split(',')
                if len(address_parts) >= 2:
                    property_data["city"] = address_parts[1].strip()
                    
                # Try to extract postal code
                postal_match = re.search(r'[A-Z]\d[A-Z] \d[A-Z]\d', address)
                if postal_match:
                    property_data["postal_code"] = postal_match.group(0)
            except:
                property_data["address"] = None
            
            # Price Information
            try:
                price = driver.find_element(By.CSS_SELECTOR, ".property-price").text
                property_data["price"] = price.strip().replace("$", "").replace(",", "")
            except:
                property_data["price"] = None
                
            # Property Features
            try:
                # Bedrooms, bathrooms, etc.
                features = driver.find_elements(By.CSS_SELECTOR, ".property-features .feature")
                for feature in features:
                    feature_text = feature.text
                    if "bed" in feature_text.lower():
                        property_data["bedrooms"] = re.search(r'\d+', feature_text).group(0)
                    elif "bath" in feature_text.lower():
                        property_data["bathrooms"] = re.search(r'\d+', feature_text).group(0)
            except:
                pass
                
            # Detailed specifications
            try:
                specs = driver.find_elements(By.CSS_SELECTOR, ".property-specifications .spec-item")
                for spec in specs:
                    label = spec.find_element(By.CSS_SELECTOR, ".spec-label").text.strip().lower()
                    value = spec.find_element(By.CSS_SELECTOR, ".spec-value").text.strip()
                    
                    if "year built" in label:
                        property_data["year_built"] = value
                    elif "lot size" in label or "land area" in label:
                        property_data["lot_size"] = value
                    elif "living area" in label or "building size" in label:
                        property_data["building_size"] = value
                    elif "stories" in label or "floor" in label:
                        property_data["floors"] = value
                    elif "garage" in label or "parking" in label:
                        property_data["parking"] = value
            except:
                pass
                
            # Get images
            try:
                image_elements = driver.find_elements(By.CSS_SELECTOR, ".property-images img")
                property_data["image_urls"] = [img.get_attribute("src") for img in image_elements]
            except:
                property_data["image_urls"] = []
                
            # Agent info
            try:
                agent_name = driver.find_element(By.CSS_SELECTOR, ".listing-agent-name").text
                property_data["agent_name"] = agent_name.strip()
                
                agency = driver.find_element(By.CSS_SELECTOR, ".listing-agency-name").text
                property_data["agency"] = agency.strip()
            except:
                pass
                
            # Description
            try:
                desc = driver.find_element(By.CSS_SELECTOR, ".property-description").text
                property_data["description"] = desc.strip()
            except:
                property_data["description"] = None
                
            # Get geolocation if available
            try:
                script_elements = driver.find_elements(By.TAG_NAME, "script")
                for script in script_elements:
                    script_content = script.get_attribute("innerHTML")
                    if "latitude" in script_content and "longitude" in script_content:
                        lat_match = re.search(r'latitude":\s*"?(-?\d+\.\d+)"?', script_content)
                        lng_match = re.search(r'longitude":\s*"?(-?\d+\.\d+)"?', script_content)
                        if lat_match and lng_match:
                            property_data["latitude"] = lat_match.group(1)
                            property_data["longitude"] = lng_match.group(1)
            except:
                pass
            
        except Exception as e:
            print(f"Error extracting Centris listing data from {url}: {e}")
        finally:
            driver.quit()
            
        return property_data
    
    def scrape_duproprio(self, search_url, max_pages=10):
        """
        Scrape property listings from DuProprio.com
        
        Args:
            search_url: URL with search parameters
            max_pages: Maximum number of pages to scrape
        
        Returns:
            List of property dictionaries
        """
        driver = self.initialize_browser()
        all_properties = []
        
        try:
            driver.get(search_url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".search-results-listings-list"))
            )
            
            current_page = 1
            
            while current_page <= max_pages:
                # Get listing URLs from search results
                listing_elements = driver.find_elements(By.CSS_SELECTOR, ".search-results-listings-list .listing-thumbnail")
                listing_urls = []
                
                for element in listing_elements:
                    try:
                        url = element.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                        listing_urls.append(url)
                    except:
                        continue
                
                # Visit each listing page and extract data
                for url in listing_urls:
                    try:
                        property_data = self._extract_duproprio_listing(url)
                        if property_data:
                            all_properties.append(property_data)
                    except Exception as e:
                        print(f"Error scraping listing {url}: {e}")
                    
                    self._random_delay()
                
                # Try to go to next page if available
                try:
                    next_button = driver.find_element(By.CSS_SELECTOR, ".pagination-next:not(.disabled)")
                    next_button.click()
                    WebDriverWait(driver, 10).until(
                        EC.staleness_of(listing_elements[0])
                    )
                    current_page += 1
                    self._random_delay(3, 6)
                except:
                    # No more pages or element not found
                    break
                    
        except Exception as e:
            print(f"Error during DuProprio scraping: {e}")
        finally:
            driver.quit()
            
        return all_properties
    
    def _extract_duproprio_listing(self, url):
        """Extract data from a single DuProprio listing page"""
        driver = webdriver.Chrome(options=self.chrome_options)
        property_data = {}
        
        try:
            driver.get(url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".listing-main-info"))
            )
            
            # Basic listing info
            property_data["source"] = "DuProprio"
            property_data["listing_url"] = url
            property_data["scrape_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Property ID
            try:
                property_id = re.search(r'/(\d+)/?', url)
                if property_id:
                    property_data["property_id"] = property_id.group(1)
            except:
                property_data["property_id"] = None
                
            # Title and Address
            try:
                title = driver.find_element(By.CSS_SELECTOR, ".listing-title").text
                property_data["title"] = title.strip()
            except:
                property_data["title"] = None
                
            try:
                address = driver.find_element(By.CSS_SELECTOR, ".listing-address").text
                property_data["address"] = address.strip()
                
                # Try to extract city, province
                address_parts = address.split(',')
                if len(address_parts) >= 2:
                    property_data["city"] = address_parts[0].strip()
                    property_data["province"] = address_parts[1].strip()
            except:
                property_data["address"] = None
            
            # Price Information
            try:
                price = driver.find_element(By.CSS_SELECTOR, ".listing-price").text
                property_data["price"] = price.strip().replace("$", "").replace(",", "")
            except:
                property_data["price"] = None
                
            # Property Features - DuProprio has a different structure
            try:
                features = driver.find_elements(By.CSS_SELECTOR, ".listing-features .feature-item")
                for feature in features:
                    feature_text = feature.text
                    label = feature.find_element(By.CSS_SELECTOR, ".feature-label").text.lower()
                    value = feature.find_element(By.CSS_SELECTOR, ".feature-value").text
                    
                    if "bedroom" in label:
                        property_data["bedrooms"] = value.strip()
                    elif "bathroom" in label:
                        property_data["bathrooms"] = value.strip()
                    elif "year built" in label:
                        property_data["year_built"] = value.strip()
                    elif "lot dimensions" in label or "lot size" in label:
                        property_data["lot_size"] = value.strip()
                    elif "living area" in label or "building size" in label:
                        property_data["building_size"] = value.strip()
                    elif "floor" in label or "level" in label:
                        property_data["floors"] = value.strip()
                    elif "garage" in label or "parking" in label:
                        property_data["parking"] = value.strip()
                    elif "tax" in label:
                        if "municipal" in label:
                            property_data["municipal_tax"] = value.strip()
                        elif "school" in label:
                            property_data["school_tax"] = value.strip()
            except:
                pass
                
            # Get images
            try:
                image_elements = driver.find_elements(By.CSS_SELECTOR, ".listing-images img")
                property_data["image_urls"] = [img.get_attribute("src") for img in image_elements]
            except:
                property_data["image_urls"] = []
                
            # Seller info (DuProprio is direct from owner)
            try:
                seller_name = driver.find_element(By.CSS_SELECTOR, ".seller-info .seller-name").text
                property_data["seller_name"] = seller_name.strip()
                
                # Be careful with contact info - some sites prohibit scraping this
                # This is just an example of what might be available
                seller_phone = driver.find_element(By.CSS_SELECTOR, ".seller-info .seller-phone").text
                property_data["seller_phone"] = seller_phone.strip()
            except:
                pass
                
            # Description
            try:
                desc = driver.find_element(By.CSS_SELECTOR, ".listing-description").text
                property_data["description"] = desc.strip()
            except:
                property_data["description"] = None
                
            # Get geolocation if available
            try:
                script_elements = driver.find_elements(By.TAG_NAME, "script")
                for script in script_elements:
                    script_content = script.get_attribute("innerHTML")
                    if "latitude" in script_content and "longitude" in script_content:
                        lat_match = re.search(r'latitude":\s*"?(-?\d+\.\d+)"?', script_content)
                        lng_match = re.search(r'longitude":\s*"?(-?\d+\.\d+)"?', script_content)
                        if lat_match and lng_match:
                            property_data["latitude"] = lat_match.group(1)
                            property_data["longitude"] = lng_match.group(1)
            except:
                pass
            
        except Exception as e:
            print(f"Error extracting DuProprio listing data from {url}: {e}")
        finally:
            driver.quit()
            
        return property_data
    
    def save_to_csv(self, data, filename):
        """Save scraped data to CSV file"""
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        return filename
    
    def save_to_json(self, data, filename):
        """Save scraped data to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return filename
    
    def handle_captcha(self, driver):
        """
        Basic captcha detection - just checks if a captcha might be present
        For real implementation, consider using a captcha solving service
        """
        captcha_terms = ["captcha", "robot", "human verification", "security check"]
        page_source = driver.page_source.lower()
        
        for term in captcha_terms:
            if term in page_source:
                print(f"Potential CAPTCHA detected: '{term}' found on page")
                # In a real implementation, you would handle the captcha here
                # For example, using a service like 2captcha, Anti-Captcha, etc.
                # Or pause and wait for human intervention
                time.sleep(30)  # Wait for manual intervention in this example
                return True
                
        return False
    
    def run_centris_scraper(self, search_params=None):
        """Run the Centris scraper with common search parameters"""
        # Default search for Montreal properties
        if not search_params:
            search_url = "https://www.centris.ca/en/properties~for-sale~montreal"
        else:
            # Format search parameters
            search_url = f"https://www.centris.ca/en/properties~for-sale~{search_params}"
            
        properties = self.scrape_centris(search_url, max_pages=5)
        
        if properties:
            self.save_to_csv(properties, "centris_properties.csv")
            self.save_to_json(properties, "centris_properties.json")
            
        return properties
    
    def run_duproprio_scraper(self, search_params=None):
        """Run the DuProprio scraper with common search parameters"""
        # Default search for Montreal properties
        if not search_params:
            search_url = "https://duproprio.com/en/search/list?search=true&cities%5B0%5D=montreal"
        else:
            # Format search parameters - this would need adjustment based on DuProprio's format
            search_url = f"https://duproprio.com/en/search/list?search=true&{search_params}"
            
        properties = self.scrape_duproprio(search_url, max_pages=5)
        
        if properties:
            self.save_to_csv(properties, "duproprio_properties.csv")
            self.save_to_json(properties, "duproprio_properties.json")
            
        return properties

# Usage example
if __name__ == "__main__":
    scraper = RealEstateScraper()
    
    # Uncomment to run specific scraper
    # centris_properties = scraper.run_centris_scraper()
    # duproprio_properties = scraper.run_duproprio_scraper()
    
    # Or run with specific search parameters
    # centris_properties = scraper.run_centris_scraper("montreal?min-price=300000&max-price=500000")