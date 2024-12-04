from datetime import datetime, timedelta
from collections import Counter
import pandas as pd
import requests
import os
import numpy as np
import re
import random
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from tqdm import tqdm
from dotenv import load_dotenv
from time import sleep
import time
import airtable


def start_finish_times(date):

    date_str = date.split('|')[0].strip()
    time_str = date.split('|')[1].strip()

    print(date_str)

    base_date = datetime.strptime(date_str.strip(), "%a, %d %b %Y")

    print(base_date.date())

    # Parse start and finish times
    start_time_str, finish_time_str = time_str.split(" - ")
    start_time = datetime.strptime(start_time_str.strip(), "%H:%M")
    finish_time = datetime.strptime(finish_time_str.strip(), "%H:%M")

    # Combine date with start time
    start_datetime = base_date.replace(hour=start_time.hour, minute=start_time.minute)

    # If finish time is earlier than start time, add one day to the date
    if finish_time < start_time:
        finish_datetime = (base_date + timedelta(days=1)).replace(hour=finish_time.hour, minute=finish_time.minute)
    else:
        finish_datetime = base_date.replace(hour=finish_time.hour, minute=finish_time.minute)
        
    return start_datetime, finish_datetime

def clean_sorted_prices(x):
    clean = x.replace('€', '').replace('Free', '0').replace(',', '')
    sorted_float = sorted([float(i) for i in clean.split(' ')])
    sorted_str = ', '.join([str(i).replace('0.11', 'SOLD OUT').replace('1.11', 'No information available') for i in sorted_float])
    return sorted_str

def clean_sorted_last_prices(x):
    clean = x.replace('€', '').replace('Free', '0').replace(',', '')
    sorted_float = sorted([float(i) for i in clean.split(' ')])
    smallest_value = str(sorted_float[0]).replace('0.11', 'SOLD OUT')
    return smallest_value

def top10_generos(df):
    # Initialize an empty list to store results
    result = []

    # Iterate over each city in the DataFrame
    for city in df['city'].unique():
        # Get the list of genres for the current city
        city_genres = df[df['city'] == city]['event_genres']
        
        # Split genres for each event in the city
        lista_generos = [x.split(', ') for x in city_genres]
        
        # Flatten the list of lists into a single list for the city
        nueva_lista = []
        for l in lista_generos:
            nueva_lista.extend(l)

        # Count the occurrences of each genre in the city
        conteo = Counter(nueva_lista)
        
        # Convert the count into a DataFrame for the current city
        df_gener = pd.DataFrame({'genero': list(conteo.keys()), 'frecuencia': list(conteo.values())})
        
        # Sort by frequency and get the top 10 genres
        df_gener = df_gener.sort_values('frecuencia', ascending=False, ignore_index=True).head(10)
        
        # Add the city column to the result
        df_gener['city'] = city
        
        # Append the city result to the main list
        result.append(df_gener)
        
        # if there is only one city, return the DataFrame
        if len(df['city'].unique()) == 1:
            return df_gener
        
        else:
            continue
    # Concatenate all results into one DataFrame
    df_result = pd.concat(result, ignore_index=True)
    
    return df_result

def fetch_airtable_data(view_name = None, endpoint = None, headers = None):
    all_records = []
    offset = None

    while True:
        params = {"offset": offset} if offset else {}
        if view_name:
            params["view"] = view_name
        response = requests.get(endpoint, headers=headers, params=params)
        response.raise_for_status()  # Raise exception for errors
        data = response.json()
        
        # Add records to the list
        all_records.extend(data.get("records", []))
        
        # Check if there's more data
        offset = data.get("offset")
        if not offset:
            break

    return all_records

# Convert Airtable data to DataFrame
def airtable_to_dataframe(records):
    
    rows = []
    for record in records:
        row = record.get("fields", {})
        row["id"] = record.get("id")  # Add the record ID if needed
        rows.append(row)
    return pd.DataFrame(rows)

def scraping_xceed_urls(ciudades, finish_date):
    for ciudad in ciudades:
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run headlessly
        chrome_options.add_argument("--disable-gpu")  # Disable GPU
        chrome_options.add_argument("--disable-webgl")  # Disable WebGL
        chrome_options.add_argument("--disable-software-rasterizer")  # Disable fallback
        chrome_options.add_argument("--disable-features=WebGPU")  # Disable WebGPU

        browser = webdriver.Chrome(options=chrome_options)

        browser.get(f"https://xceed.me/en/{ciudad.lower()}/events/all/all-events")

        # browser.maximize_window()

        sleep(random.uniform(1, 3))

        datos_date = datetime.now().date()
        

        while datos_date < finish_date.date():
            scroll_increment = random.randint(500, 1000)
            browser.execute_script("window.scrollBy(0, " + str(scroll_increment) + ");")
            
            sleep(random.uniform(1, 3))
            
            browser.page_source
            
            soup = BeautifulSoup(browser.page_source, 'html.parser')
            
            places = []
            urls = []
            image = []
            date = []

            for i in soup.find_all('a'):
                if re.match(r'.*\b\d{6}\b', str(i['href'])):  
                # href
                    try:
                        url = i['href']
                    except:
                        url = np.nan
                # local
                    try:
                        local = i.find('h4').text
                    except:
                        local = np.nan
                # date
                    try:
                        day = i.find('h5').text
                    except:
                        day = i.find('h5')
                # IMAGES
                    try:
                        img = i.find('img',alt=re.compile(r"^Cover for event"), attrs={'loading': 'lazy'})['src']
                    except:
                        img = np.nan

                    d_str = day.split('|')[0].strip()
                    datos_date  = datetime.strptime(d_str.strip(), "%a, %d %b %Y")
                    datos_date  = datos_date.date()
                    
                    urls.append(f'https://xceed.me{url}')
                    places.append(local)
                    date.append(day)
                    image.append(img)
                    
        browser.quit()
        
        return pd.DataFrame({'place': places, 'url': urls, 'image': image, 'date': date})
    
def update_xceed_data(df):  
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run headlessly
    chrome_options.add_argument("--disable-gpu")  # Disable GPU
    chrome_options.add_argument("--disable-webgl")  # Disable WebGL
    chrome_options.add_argument("--disable-software-rasterizer")  # Disable fallback
    chrome_options.add_argument("--disable-features=WebGPU")  # Disable WebGPU
    
    event_genres = []
    line_up = []
    venue_information = []
    event_location_details = []
    event_ticket_types = []
    ticket_price = []
    event_name = []
    location_identifier = []
    location_address = []
    remain_prices = []

    # Start time for execution time calculation
    start_time = time.time()
    
    urls = df['url'].tolist()

    for url in tqdm(urls, desc='Processing events', unit='url'):

        browser = webdriver.Chrome(options=chrome_options)

        browser.get(url)

        # browser.maximize_window()

        browser.page_source
            
        soup2 = BeautifulSoup(browser.page_source, "html.parser")

    #event_name
        try:
            ev_name = soup2.find('h1').text
        except:
            ev_name = np.nan
    # genre     
        try:
            event_genre = ', '.join([x.text for x in soup2.find_all('span', attrs={'name': True})])

        except:
            event_genre = np.nan

    # line up
        try:       
            event_lineup = ', '.join([x.text for x in soup2.find('div', class_ = 'LineUp-sc-1xigslr-0').find_all('h3')])

        except:
            event_lineup = np.nan

    # Venue information
        try:
            v_info = soup2.find_all('div', attrs={'overflow':'hidden'})[0].text
            venue_info = re.sub(r'\s+', ' ', v_info).strip()

        except:
            venue_info = np.nan
            
    # Venue local information
        try:
            v_local_info = soup2.find_all('div', attrs={'overflow':'hidden'})[1].text
            venue_local_info = re.sub(r'\s+', ' ', v_local_info).strip()

        except:
            venue_local_info = np.nan

    # ticket_type
        try:
            unique_ticket_types = {x.text for x in soup2.find_all('h3', class_ = 'Name-sc-17wxn8u-0')}
            ticket_types = ', '.join(unique_ticket_types)

        except:
            ticket_types = np.nan
    # Ticket price
    # Utilizamos {} para quitar los valores duplicados.       
        try:
            unique_ticket_prices = {x.text.strip() for x in soup2.find_all('p', class_='PriceText-sc-17wxn8u-2')}
            ticket_prices = ', '.join(unique_ticket_prices)

        except:
            ticket_prices = np.nan
    # ubicacion
        try:
            location_id = soup2.find('a', class_ ='TertiaryTitle-sc-hrr11b-4')['href'].split('=')[-1]

        except:
            location_id = np.nan
    # direccion
        try:
            location = soup2.find('p', attrs={'color':'#6E7A83'}).text

        except:
            location = np.nan

    # Entradas que quedan
    # Utilizamos {} para quitar los valores duplicados.
        try:
            remaining_prices_set = {x.text.strip() for x in soup2.find_all('p', class_ = 'PriceText-sc-17wxn8u-2') if "inherit" in str(x)}
            remaining_ticket_prices = ', '.join(remaining_prices_set)
        #if "inherit" in str(x): # con 'inherit' nos va a enseñar las entradas que quedan, si lo cambio por 'inherit' nos va a ensañar solo las entradas agotadas si hay

        except:
            remaining_ticket_prices = np.nan

        event_genres.append(event_genre)
        line_up.append(event_lineup)
        venue_information.append(venue_info)
        event_location_details.append(venue_local_info)
        event_ticket_types.append(ticket_types)
        ticket_price.append(ticket_prices)
        event_name.append(ev_name)
        location_identifier.append(location_id)
        location_address.append(location)
        remain_prices.append(remaining_ticket_prices)
        
    end_time = time.time()
    execution_time = end_time - start_time
    # estimate time to finish
    time_to_finish = (execution_time * len(urls)) / 60
    print(f"Execution time: {execution_time:.2f} seconds")

    # Save data to a DataFrame
    data = {
        'event_title': event_name,
        'event_genres': event_genres,
        'line_up': line_up,
        'venue_information': venue_information,
        'event_location_details': event_location_details,
        'event_ticket_types': event_ticket_types,
        'ticket_price': ticket_price,
        'location_identifier': location_identifier,
        'location_address': location_address,
        'remain_prices': remain_prices,
        'url': urls
    }
    df['event_title'] = event_name
    df['event_genres'] = event_genres
    df['line_up'] = line_up
    df['venue_information'] = venue_information
    df['event_location_details'] = event_location_details
    df['event_ticket_types'] = event_ticket_types
    df['ticket_price'] = ticket_price
    df['location_identifier'] = location_identifier
    df['location_address'] = location_address
    df['remain_prices'] = remain_prices
    df['url'] = urls
    
    # Add starting and finishing time columns
    df.insert(df.columns.get_loc('date') + 1, 'starting_time', df['date'].apply(lambda x: start_finish_times(x)[0]))
    df.insert(df.columns.get_loc('starting_time') + 1, 'finishing_time', df['date'].apply(lambda x: start_finish_times(x)[1]))
    del df['date']
    
    # transform date to string
    df['starting_time'] = df['starting_time'].dt.strftime('%Y-%m-%d %H:%M:%S')
    df['finishing_time'] = df['finishing_time'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    df.loc[df['event_ticket_types'] == '', 'event_ticket_types'] = 'No information available'
    # clean ticket price column
    df.loc[df['event_ticket_types'] == 'No information available', ['ticket_price','remain_prices']] = '1.11'
    df['ticket_price'] = df['ticket_price'].apply(lambda x: clean_sorted_prices(x))
    
    # clean remaining ticket price column
    df.loc[df['remain_prices'] == '', 'remain_prices'] = '0.11'
    df['remain_prices'] = df['remain_prices'].apply(lambda x: clean_sorted_prices(x))
    
    # date of creation
    df['data_date'] = datetime.now().strftime("%Y-%m-%d")
    
    df.replace(np.nan, 'NaN', inplace=True)
    
    return df
        
    # # Upload data to Airtable
def upload_to_airtable(df, TOKEN, BASE_ID, TABLE_ID):
    
    airtable_base_url = "https://api.airtable.com/v0"

    # Headers
    headers = {"Authorization" : f"Bearer {TOKEN}",
            "Content-Type"  : "application/json"}

    # Endpoint
    endpoint = f"{airtable_base_url}/{BASE_ID}/{TABLE_ID}"

    print(endpoint)
    
    for i in range(0, df.shape[0], 10):
        try:
            
            batch_data = {"records": [{"fields": df.iloc[j, :].to_dict()} for j in range(i, i + 10)],
                        "typecast": True}
        except:
            
            batch_data = {"records": [{"fields": df.iloc[j, :].to_dict()} for j in range(i, df.shape[0])],
                        "typecast": True}

        
        response = requests.post(url=endpoint, json=batch_data, headers=headers)
        # Log the response for troubleshooting
        if response.status_code == 200:
            print(f"Uploaded row {i+1}: {response.json()}")
        else:
            print(f"Failed to upload row {i+1}: {response.status_code} - {response.text}")
            
def airtable_columns_order(df):
    df = df[['event_title', 'event_genres', 'line_up', 'place', 'starting_time', 'finishing_time',
                 'venue_information', 'event_location_details', 'event_ticket_types', 'ticket_price', 
                 'location_identifier', 'location_address', 'remain_prices', 'image', 'url', 'data_date']]
    return df

# Loop through the DataFrame rows and update each record
def update_airtable_events(df, TOKEN, BASE_ID, TABLE_ID):
    at = airtable.Airtable(BASE_ID, TABLE_ID, TOKEN)
    for index, row in df.iterrows():
        record_id = row['id']
        remain_price = row['remain_prices']
        data_date = row['data_date']
        
        # Prepare the data dictionary for each record
        data = {'remain_prices': remain_price, 'data_date': data_date}
        
        at.update(record_id, data)
        
def load_airtable_data():
    # Load environment variables
    load_dotenv()

    TOKEN = os.getenv('XCEED_TOKEN')
    BASE_ID = os.getenv('BASE_ID')
    TABLE_ID = os.getenv('TABLE_ID')

    # Define Airtable API details
    airtable_base_url = "https://api.airtable.com/v0"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    endpoint = f"{airtable_base_url}/{BASE_ID}/{TABLE_ID}"
    view_name = "Grid view"

    # Fetch and process data
    records = fetch_airtable_data(view_name=view_name, endpoint=endpoint, headers=headers)
    return airtable_to_dataframe(records)