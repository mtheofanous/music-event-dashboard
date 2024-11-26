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

print(endpoint)

chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

browser = webdriver.Chrome(options=chrome_options)


ciudades = ['Valencia', 'Barcelona', 'Madrid']

finish_date = datetime.now() + timedelta(days=45)

for ciudad in ciudades:

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

    # Start time for execution time calculation
    start_time = time.time()


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
        'place': places,
        'date': date,
        'venue_information': venue_information,
        'event_location_details': event_location_details,
        'event_ticket_types': event_ticket_types,
        'ticket_price': ticket_price,
        'location_identifier': location_identifier,
        'location_address': location_address,
        'remain_prices': remain_prices,
        'image': image,
        'url': urls
    }

    df = pd.DataFrame(data)
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
    
    df.to_csv(f'data/xceed_{ciudad}_starting_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}_finishing_{finish_date.strftime("%Y-%m-%d")}.csv', index=False)
    
    # Upload data to Airtable
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
            
    df_url = pd.DataFrame({'url': urls, 'date': date})
    if ciudad == 'Lisboa':
        df_urls = df_url
    else:
        df_urls = pd.concat([df_urls, df_url], axis=0)
    # Save urls to a csv file
df_urls.to_csv(f'data/xceed__urls.csv', index=False)
