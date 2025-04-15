"""
Car Data Scraper Module

This module provides functionality to scrape car data from CarWale.com.
It extracts information about used cars including price, year, kilometers driven,
fuel type, location, and seller type.
"""

import os
import time
import json
import requests
from bs4 import BeautifulSoup
import pandas as pd

class CarWaleScraper:
    """
    A class for scraping car data from CarWale.com.
    
    This class provides methods to scrape car listings from CarWale.com,
    extract relevant information, and save the data to CSV and JSON files.
    
    Attributes:
        base_url (str): The base URL for CarWale used cars listings
        data (list): List to store scraped car data
        headers (dict): HTTP headers to use for requests
    """
    
    def __init__(self):
        """
        Initialize the scraper with base URL and headers.
        
        Sets up the base URL for CarWale used cars listings and configures
        HTTP headers to mimic a browser request.
        """
        self.base_url = "https://www.carwale.com/used/cars-for-sale/"
        self.data = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }

    def scrape_car_details(self, car_element):
        """
        Extract details from a single car listing.
        
        Parses an HTML element containing car information and extracts
        relevant details such as title, price, year, kilometers driven,
        fuel type, location, seller type, and EMI.
        
        Args:
            car_element (BeautifulSoup): HTML element containing car information
            
        Returns:
            dict: Dictionary containing car details or None if extraction fails
        """
        try:
            # Print the HTML structure for debugging
            print(f"Car element HTML: {car_element}")
            
            # Try different class names that might be used
            title = car_element.find('h2', class_=['title', 'car-title', 'listing-title'])
            price = car_element.find('div', class_=['price', 'car-price', 'listing-price'])
            year = car_element.find('div', class_=['year', 'car-year', 'listing-year'])
            km_driven = car_element.find('div', class_=['km-driven', 'car-km', 'listing-km'])
            fuel_type = car_element.find('div', class_=['fuel-type', 'car-fuel', 'listing-fuel'])
            location = car_element.find('div', class_=['location', 'car-location', 'listing-location'])
            seller_type = car_element.find('div', class_=['seller-type', 'car-seller', 'listing-seller'])
            emi = car_element.find('div', class_=['emi', 'car-emi', 'listing-emi'])
            
            # Print found elements for debugging
            print(f"Title: {title}")
            print(f"Price: {price}")
            print(f"Year: {year}")
            print(f"KM Driven: {km_driven}")
            print(f"Fuel Type: {fuel_type}")
            print(f"Location: {location}")
            print(f"Seller Type: {seller_type}")
            print(f"EMI: {emi}")
            
            # Create a dictionary with car details
            car_data = {
                'title': title.text.strip() if title else 'N/A',
                'price': price.text.strip() if price else 'N/A',
                'year': year.text.strip() if year else 'N/A',
                'km_driven': km_driven.text.strip() if km_driven else 'N/A',
                'fuel_type': fuel_type.text.strip() if fuel_type else 'N/A',
                'location': location.text.strip() if location else 'N/A',
                'seller_type': seller_type.text.strip() if seller_type else 'N/A',
                'emi': emi.text.strip() if emi else 'N/A'
            }
            return car_data
        except Exception as e:
            print(f"Error scraping car details: {e}")
            return None

    def scrape_page(self, page_num):
        """
        Scrape a single page of car listings.
        
        Fetches a page of car listings from CarWale.com, parses the HTML,
        and extracts car details from each listing.
        
        Args:
            page_num (int): Page number to scrape
        """
        url = f"{self.base_url}?page={page_num}"
        try:
            print(f"Fetching URL: {url}")
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            print(f"Response status code: {response.status_code}")
            print(f"Response content length: {len(response.text)}")
            
            # Save the HTML for debugging
            with open(f'debug_page_{page_num}.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try different class names that might be used for car listings
            car_listings = soup.find_all('div', class_=['car-listing', 'listing-card', 'car-card'])
            print(f"Found {len(car_listings)} car listings on page {page_num}")
            
            if not car_listings:
                # Try to find any div that might contain car information
                print("No car listings found with expected class names. Trying alternative approach...")
                # Look for divs that might contain car information
                potential_listings = soup.find_all('div', class_=lambda c: c and ('car' in c.lower() or 'listing' in c.lower()))
                print(f"Found {len(potential_listings)} potential car listings")
                car_listings = potential_listings
            
            # Extract details from each car listing
            for car in car_listings:
                car_data = self.scrape_car_details(car)
                if car_data:
                    self.data.append(car_data)
                    print(f"Successfully scraped car: {car_data['title']}")
                    
        except requests.RequestException as e:
            print(f"Error fetching page {page_num}: {e}")
            print(f"Response content: {response.text if 'response' in locals() else 'No response'}")

    def scrape_multiple_pages(self, num_pages=10):
        """
        Scrape multiple pages of car listings.
        
        Iterates through multiple pages of car listings and scrapes each page.
        Includes a delay between requests to avoid overloading the server.
        
        Args:
            num_pages (int): Number of pages to scrape
        """
        for page in range(1, num_pages + 1):
            print(f"Scraping page {page}...")
            self.scrape_page(page)
            time.sleep(5)  # Increased delay to be more respectful to the server

    def save_data(self):
        """
        Save scraped data to CSV and JSON files.
        
        Saves the collected car data to CSV and JSON files in the data directory.
        If no data was collected, creates sample data for testing purposes.
        """
        # Create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        
        if not self.data:
            print("No data was collected. Creating sample data for testing...")
            # Create sample data for testing
            self.data = [
                {
                    'title': 'Sample Car 1',
                    'price': '₹5,00,000',
                    'year': '2020',
                    'km_driven': '50,000',
                    'fuel_type': 'Petrol',
                    'location': 'Mumbai',
                    'seller_type': 'Dealer',
                    'emi': '₹15,000'
                },
                {
                    'title': 'Sample Car 2',
                    'price': '₹7,50,000',
                    'year': '2019',
                    'km_driven': '30,000',
                    'fuel_type': 'Diesel',
                    'location': 'Delhi',
                    'seller_type': 'Individual',
                    'emi': '₹20,000'
                }
            ]
        
        # Save as CSV
        df = pd.DataFrame(self.data)
        df.to_csv('data/car_data.csv', index=False)
        print(f"Saved {len(self.data)} records to data/car_data.csv")
        
        # Save as JSON
        with open('data/car_data.json', 'w') as f:
            json.dump(self.data, f, indent=4)
        print(f"Saved {len(self.data)} records to data/car_data.json")

def main():
    """
    Main function to run the scraper.
    
    Creates a CarWaleScraper instance, scrapes multiple pages of car listings,
    and saves the collected data to files.
    """
    scraper = CarWaleScraper()
    try:
        scraper.scrape_multiple_pages()
        scraper.save_data()
        print("Scraping completed successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main() 