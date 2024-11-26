# Import necessary libraries
import pandas as pd  # For data manipulation and analysis
import numpy as np  # For working with arrays and numerical data
import time  # For adding delays (e.g., sleep)
from bs4 import BeautifulSoup  # For parsing HTML
import requests  # For making HTTP requests
import re  # For regular expressions
import os  # For interacting with the operating system (e.g., environment variables)
from selenium import webdriver  # For web scraping using Selenium
from selenium.webdriver.chrome.options import Options  # For configuring the Chrome browser for Selenium
import random  # For generating random numbers
from time import sleep  # For pausing execution of the code for a specified time
from datetime import datetime, timedelta  # For working with date and time
from tqdm import tqdm  # For displaying progress bars
from functions import *  # Import custom functions from another file
from dotenv import load_dotenv  # For loading environment variables from a .env file
import airtable  # For interacting with Airtable API

# Load environment variables from the .env file
load_dotenv()

# Fetch API token and Airtable details from the environment variables
TOKEN = os.getenv('XCEED_TOKEN')  # API token for Airtable
BASE_ID = os.getenv('BASE_ID')  # Base ID for Airtable
TABLE_ID = os.getenv('TABLE_ID')  # Table ID for Airtable

# Set Airtable base URL for API access
airtable_base_url = "https://api.airtable.com/v0"

# Define the headers for API requests to Airtable
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Set the endpoint for Airtable API with the specific base and table ID
endpoint = f"{airtable_base_url}/{BASE_ID}/{TABLE_ID}"
view_name = "Grid view"  # The view name in Airtable to fetch data from

# Fetch existing event data from Airtable using a custom function `fetch_airtable_data`
records = fetch_airtable_data(view_name=view_name, endpoint=endpoint, headers=headers)

# Convert the fetched data into a pandas DataFrame
df_airtable_events = airtable_to_dataframe(records)

# Define the list of cities to scrape event data from
ciudades = ['Valencia', 'Barcelona', 'Madrid']

# Define the finish date for event scraping (current date + 10 days)
finish_date = datetime.now() + timedelta(days=10)

# Update event URLs using a custom scraping function `scraping_xceed_urls`
df_urls = scraping_xceed_urls(ciudades, finish_date)

# Update event data by passing the URLs to another custom function `update_xceed_data`
df_updated = update_xceed_data(df_urls)

# Filter the updated event data to get only the events that already exist in Airtable
df_updated_airtable = df_updated[df_updated['url'].isin(df_airtable_events['url']) == True]

# Reorder the columns of the updated events to match Airtable's column structure
df_updated_airtable = airtable_columns_order(df_updated_airtable)

# Merge the updated event data with the existing data from Airtable to preserve Airtable IDs
df_updated_airtable = df_updated_airtable.merge(df_airtable_events[['url', 'id']], on='url', how='left')

# Try to update the events in Airtable
try:
    update_airtable_events(df_updated_airtable, TOKEN, BASE_ID, TABLE_ID)
    print('Events updated in Airtable')
except Exception as e:
    print('Error updating events in Airtable')
    print(e)

# Identify new events by checking which URLs are not already in Airtable
df_new_events = df_updated[df_updated['url'].isin(df_airtable_events['url']) == False]

# If no new events are found, print a message
if df_new_events.empty:
    print('No new events to add')
else:
    # Reorder columns of the new events to match Airtable's column structure
    df_new_events = airtable_columns_order(df_new_events)
    
    # Replace NaN values with 'NaN' to handle missing data
    df_new_events.replace({np.nan: 'NaN'}, inplace=True)
    
    # Try to add the new events to Airtable
    try:
        upload_to_airtable(df_new_events, TOKEN, BASE_ID, TABLE_ID)
        print('New events added to Airtable')
    except Exception as e:
        print('Error adding new events to Airtable')
        print(e)

# Print the number of events that were updated and the number of new events added
print(f"{len(df_updated_airtable)} events have been updated")
print(f"{len(df_new_events)} new events have been added")

# Prepare a report showing the number of events updated and added, along with the current date
report = pd.DataFrame({
    'date': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
    'updated_events': df_updated_airtable.shape[0],
    'new_events': df_new_events.shape[0]
})

# Append the report to a CSV file for future reference
if os.path.exists('data/report.csv'):
    report.to_csv('data/report.csv', mode='a', header=False, index=False)
else:
    report.to_csv('data/report.csv', mode='w', header=True, index=False)
    
# Description: This script updates event data in Airtable by fetching new event URLs from Xceed and updating the event details. 
# It also adds new events to Airtable if any are found. Finally, it generates a report with the number of events updated and added, along with the current date and time.            