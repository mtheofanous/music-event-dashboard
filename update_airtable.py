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
from functions import *
from dotenv import load_dotenv
import airtable

load_dotenv()

TOKEN = os.getenv('XCEED_TOKEN')

BASE_ID = os.getenv('BASE_ID')

TABLE_ID = os.getenv('TABLE_ID')


airtable_base_url = "https://api.airtable.com/v0"

# Headers
headers = {"Authorization" : f"Bearer {TOKEN}",
           "Content-Type"  : "application/json"}

# Endpoint
endpoint = f"{airtable_base_url}/{BASE_ID}/{TABLE_ID}"
view_name = "Grid view"

records = fetch_airtable_data(view_name=view_name, endpoint=endpoint, headers=headers)
df_airtable_events = airtable_to_dataframe(records)

ciudades = ['Valencia', 'Barcelona', 'Madrid']

finish_date = datetime.now() + timedelta(days=10)

# update xceed urls
df_urls = scraping_xceed_urls(ciudades, finish_date)

# update xceed dates
df_updated = update_xceed_data(df_urls)
df_updated_airtable = df_updated[df_updated['url'].isin(df_airtable_events['url'])== True]# Get old events that have been updated
df_updated_airtable = airtable_columns_order(df_updated_airtable)
df_updated_airtable = df_updated_airtable.merge(df_airtable_events[['url', 'id']], on='url', how='left')
# Update airtable events
try:
    update_airtable_events(df_updated_airtable, TOKEN, BASE_ID, TABLE_ID)
    print('Events updated in airtable')
except Exception as e:
    print('Error updating events in airtable')
    print(e)

# new events
df_new_events = df_updated[df_updated['url'].isin(df_airtable_events['url']) == False] # Get new events
if df_new_events.empty:
    print('No new events to add')
else:
    df_new_events = airtable_columns_order(df_new_events)
    df_new_events.replace({np.nan: 'NaN'}, inplace=True)
    # add new events to airtable
    try:
        upload_to_airtable(df_new_events, TOKEN, BASE_ID, TABLE_ID)
        print('New events added to airtable')
    except Exception as e:
        print('Error adding new events to airtable')
        print(e)


# show me how many events have been updated and how many are new
print(f"{len(df_updated_airtable)} events have been updated")
print(f"{len(df_new_events)} new events have been added")

# save only the len in a csv file with the date of the update
report = pd.DataFrame({
    'date': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')], 
    'updated_events': df_updated_airtable.shape[0], 
    'new_events': df_new_events.shape[0]})

# append the report to the csv file
if os.path.exists('data/report.csv'):
    report.to_csv('data/report.csv', mode='a', header=False, index=False)
else:
    report.to_csv('data/report.csv', mode='w', header=True, index=False)








            