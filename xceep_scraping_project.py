import pandas as pd 
import numpy as np
import time 
from bs4 import BeautifulSoup 
import requests
import re
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import random
from time import sleep
from datetime import datetime, timedelta
from tqdm import tqdm
from functions import start_finish_times, clean_sorted_prices
from dotenv import load_dotenv

# Load environment variables from a .env file (for sensitive data like API keys)
load_dotenv()

# Retrieve API credentials from environment variables
TOKEN = os.getenv('XCEED_TOKEN')  # Airtable API Token
BASE_ID = os.getenv('BASE_ID')  # Airtable Base ID
TABLE_ID = os.getenv('TABLE_ID')  # Airtable Table ID

# Construct the Airtable API endpoint URL using the credentials
airtable_base_url = "https://api.airtable.com/v0"
headers = {"Authorization" : f"Bearer {TOKEN}", "Content-Type"  : "application/json"}
endpoint = f"{airtable_base_url}/{BASE_ID}/{TABLE_ID}"

# Print the API endpoint for verification (this will help debug if needed)
print(endpoint)

# Set up the Chrome options to run the browser in headless mode (no GUI)
chrome_options = Options()
chrome_options.add_argument("--headless")  # Runs the browser without a UI (headless)
chrome_options.add_argument("--no-sandbox")  # Used for Docker compatibility
chrome_options.add_argument("--disable-dev-shm-usage")  # Avoids issues with shared memory in some environments

# Initialize a new Chrome browser instance with the specified options
browser = webdriver.Chrome(options=chrome_options)

# List of cities we will be scraping event data from
ciudades = ['Valencia', 'Barcelona', 'Madrid']

# Define the finish date for the scraping period (45 days from today)
finish_date = datetime.now() + timedelta(days=45)

# Loop through each city in the list to scrape events
for ciudad in ciudades:
    # Navigate to the events page of the current city on the Xceed website
    browser.get(f"https://xceed.me/en/{ciudad.lower()}/events/all/all-events")
    
    # Sleep to simulate a user waiting before performing another action
    sleep(random.uniform(1, 3))  # Random sleep time between 1 and 3 seconds
    
    # Initialize the current date to check against the finish date
    datos_date = datetime.now().date()

    # Continue scraping while the current date is earlier than the finish date
    while datos_date < finish_date.date():
        # Randomly scroll down the page to load more events (mimics human behavior)
        scroll_increment = random.randint(500, 1000)  # Random scroll value
        browser.execute_script("window.scrollBy(0, " + str(scroll_increment) + ");")
        
        # Wait to simulate realistic page scrolling
        sleep(random.uniform(1, 3))  # Sleep for 1-3 seconds to mimic human scrolling
        
        # Get the page content after scrolling
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        
        # Initialize lists to store scraped data
        places = []
        urls = []
        image = []
        date = []

        # Find all <a> tags and extract event URLs and associated data
        for i in soup.find_all('a'):
            if re.match(r'.*\b\d{6}\b', str(i['href'])):  # Match valid event URLs (they contain a number)
                try:
                    url = i['href']  # Extract event URL
                except:
                    url = np.nan  # Handle missing URL
                
                try:
                    local = i.find('h4').text  # Extract event location (place)
                except:
                    local = np.nan  # Handle missing location
                
                try:
                    day = i.find('h5').text  # Extract event date
                except:
                    day = i.find('h5')  # Handle missing date
                
                try:
                    img = i.find('img', alt=re.compile(r"^Cover for event"), attrs={'loading': 'lazy'})['src']  # Extract event image URL
                except:
                    img = np.nan  # Handle missing image URL

                # Convert event date string to datetime format
                d_str = day.split('|')[0].strip()  # Split and clean date string
                datos_date = datetime.strptime(d_str.strip(), "%a, %d %b %Y")
                datos_date = datos_date.date()  # Convert to date format

                # Append extracted data to the lists
                urls.append(f'https://xceed.me{url}')
                places.append(local)
                date.append(day)
                image.append(img)

    # Close the browser after scrolling and collecting URLs
    browser.quit()

    # Initialize lists for detailed event data collection
    event_genres = []
    line_up = []
    venue_information = []
    event_location_details = []
    event_ticket_types = []
    ticket_price = []
    event_name = []
    location_identifier = []
    location_address = []
    sold_out_prices = []
    remain_prices = []

    # Start measuring time to estimate how long the process will take
    start_time = time.time()

    # Loop through each collected event URL to gather detailed information
    for url in tqdm(urls, desc='Processing events', unit='url'):
        # Reopen the browser for each event URL (as we are scraping individual event pages)
        browser = webdriver.Chrome(options=chrome_options)
        browser.get(url)
        
        # Parse the event page content with BeautifulSoup
        soup2 = BeautifulSoup(browser.page_source, "html.parser")

        # Extract event name
        try:
            ev_name = soup2.find('h1').text  # Get the event name (title)
        except:
            ev_name = np.nan  # Handle missing event name

        # Extract event genres (music genres, etc.)
        try:
            event_genre = ', '.join([x.text for x in soup2.find_all('span', attrs={'name': True})])  # Collect all genre information
        except:
            event_genre = np.nan  # Handle missing genre info
        
        # Extract event lineup (performers or speakers)
        try:
            event_lineup = ', '.join([x.text for x in soup2.find('div', class_='LineUp-sc-1xigslr-0').find_all('h3')])  # Collect lineup details
        except:
            event_lineup = np.nan  # Handle missing lineup info
        
        # Extract venue information (like address, venue capacity)
        try:
            v_info = soup2.find_all('div', attrs={'overflow': 'hidden'})[0].text  # Extract first div for venue info
            venue_info = re.sub(r'\s+', ' ', v_info).strip()  # Clean up the venue information
        except:
            venue_info = np.nan  # Handle missing venue info

        # Extract local venue information (e.g., city or area)
        try:
            v_local_info = soup2.find_all('div', attrs={'overflow': 'hidden'})[1].text  # Extract second div for local venue info
            venue_local_info = re.sub(r'\s+', ' ', v_local_info).strip()  # Clean up local venue info
        except:
            venue_local_info = np.nan  # Handle missing local venue info

        # Extract ticket types (general admission, VIP, etc.)
        try:
            unique_ticket_types = {x.text for x in soup2.find_all('h3', class_='Name-sc-17wxn8u-0')}  # Collect unique ticket types
            ticket_types = ', '.join(unique_ticket_types)  # Join ticket types into a single string
        except:
            ticket_types = np.nan  # Handle missing ticket types

        # Extract ticket prices
        try:
            unique_ticket_prices = {x.text.strip() for x in soup2.find_all('p', class_='PriceText-sc-17wxn8u-2')}  # Collect unique ticket prices
            ticket_prices = ', '.join(unique_ticket_prices)  # Join prices into a single string
        except:
            ticket_prices = np.nan  # Handle missing prices

        # Extract location identifier (ID for the venue)
        try:
            location_id = soup2.find('a', class_='TertiaryTitle-sc-hrr11b-4')['href'].split('=')[-1]  # Extract location ID from the URL
        except:
            location_id = np.nan  # Handle missing location ID

        # Extract the event location (address or city)
        try:
            location = soup2.find('p', attrs={'color': '#6E7A83'}).text  # Extract location address
        except:
            location = np.nan  # Handle missing location address

        # Extract remaining ticket prices (for tickets still available)
        try:
            remaining_prices_set = {x.text.strip() for x in soup2.find_all('p', class_='PriceText-sc-17wxn8u-2') if "inherit" in str(x)}  # Filter for remaining ticket prices
            remaining_ticket_prices = ', '.join(remaining_prices_set)  # Join remaining ticket prices into a single string
        except:
            remaining_ticket_prices = np.nan  # Handle missing remaining ticket prices

        # Append the collected data to the corresponding lists
        event_genres.append(event_genre)
        line_up.append(event_lineup)
        venue_information.append(venue_info)
        event_location_details.append(venue_local_info)
        event_ticket_types.append(ticket_types)
        ticket_price.append(ticket_prices)
        event_name.append(ev_name)
        location_identifier.append(location_id)
        location_address.append(location)
        sold_out_prices.append(ticket_prices)
        remain_prices.append(remaining_ticket_prices)

        # Close the browser after processing the event page
        browser.quit()

    # Create a DataFrame from the collected data
    df = pd.DataFrame({
        'name': event_name,
        'genres': event_genres,
        'line_up': line_up,
        'venue': venue_information,
        'local_venue': event_location_details,
        'ticket_types': event_ticket_types,
        'ticket_prices': ticket_price,
        'location': location_address,
        'location_id': location_identifier,
        'sold_out_prices': sold_out_prices,
        'remaining_prices': remain_prices
    })

    # Clean and format ticket prices using a custom function
    df['ticket_prices'] = df['ticket_prices'].apply(clean_sorted_prices)
    
    # Save the DataFrame to an Excel file for future analysis
    df.to_excel(f"events_{ciudad}.xlsx", index=False)

# Description: This script scrapes event data from the Xceed website for multiple cities and saves the data to Excel files for further analysis.
