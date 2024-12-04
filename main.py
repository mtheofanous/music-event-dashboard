import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv
import os
from functions import *
from analysis import *
from datetime import datetime, timedelta

# df = load_airtable_data()

# Load the data from the Airtable database
df = pd.read_csv('Data/airtable_data.csv')

# Preprocessing
df['city'] = [city.split(',')[-2].strip() for city in df['location_address']]
df = df[df['city'].isin(['Valencia', 'Madrid', 'Barcelona'])].reset_index(drop=True)
df['starting_time'] = pd.to_datetime(df['starting_time'])
df['starting_day'] = df['starting_time'].dt.day_name()
df['finishing_time'] = pd.to_datetime(df['finishing_time'])
df['free_entrance'] = df['remain_prices'].str.contains(r'\b0\.0\b', na=False)

st.set_page_config(
    page_title="Event Analysis",  # Optional title
    layout="centered",        # Choose between "wide" or "centered"
    initial_sidebar_state="auto"  # "expanded", "collapsed", or "auto"
)

# Streamlit App Title and Description
st.title("Event Data Analysis Dashboard")

st.sidebar.header("Filters")

# User inputs for filtering
choose_starting_date = st.sidebar.date_input(
    "**Choose a starting date:**",
    min_value=df["starting_time"].dt.date.min(),
    max_value=df["finishing_time"].dt.date.max(),
    value=df["starting_time"].dt.date.min()
)

choose_finishing_date = st.sidebar.date_input(
    "**Choose a finishing date:**",
    min_value=choose_starting_date + timedelta(days=1),
    max_value=df["finishing_time"].dt.date.max(),
    value=df["finishing_time"].dt.date.max())  # Default to 7 days after the start date

choose_price_filter = st.sidebar.selectbox("**Price filter:**", ["All", "Free", "Sold Out"], index=0)

df1 = df.copy()

df = df[(df['starting_time'] >= choose_starting_date.strftime('%Y-%m-%d')) 
                 & (df['finishing_time'] <= choose_finishing_date.strftime('%Y-%m-%d'))]

# total number of events
total_events = df1.shape[0]
# number of events per city
events_per_city = df1['city'].value_counts()
# Madrid events
madrid_events = events_per_city['Madrid']   
# Barcelona events
barcelona_events = events_per_city['Barcelona']
# Valencia events
valencia_events = events_per_city['Valencia']

# Now you can apply the filtering based on the conditions
if choose_price_filter == "All":
    
    # Overview of the project   
    st.markdown(
    """
    ### Overview  
    Welcome to the Music Events Data Analysis Dashboard!  
    This dashboard provides insights into music events across **Valencia**, **Madrid**, and **Barcelona**.  
    The data was sourced from **Xceed** and stored in an Airtable database.  
    """
    )

    st.write(f"**Data Range:** {df1['starting_time'].dt.date.min()} to {df1['finishing_time'].dt.date.max()}")
    st.write(f"**Total Events:** {total_events}")
    st.write(f"**Events in Madrid:** {madrid_events}")
    st.write(f"**Events in Barcelona:** {barcelona_events}")
    st.write(f"**Events in Valencia:** {valencia_events}")
    st.write('**Data collected and analyzed by:** Marios Theofanous')

    # description of the project
    st.markdown(
        """
        ### Project Description
        
        This project presents a data analysis of events in Valencia, Madrid, and Barcelona. The data was collected from 
        Xceed and stored in an Airtable database. This analysis includes:
        - A pie chart showing the percentage of events by city.
        - Visualization of the top 10 genres by city.
        - A sunburst chart showcasing genre distribution by city.
        - Average ticket prices by city and day of the week.
        - A timeline of events filtered by date range.
        
        This analysis aims to help event organizers, planners, and marketers better understand the event landscape 
        and make data-driven decisions.
        """
    )
    
    # New Visualization pie chart of percentage of events per city
    st.subheader("Percentage of Events by City")
    labels = df['city'].value_counts().index
    values = df['city'].value_counts().values
    fig_pie = px.pie(
        names=labels,
        values=values,
        template='plotly_dark'
    )
    fig_pie.update_layout(
        margin=dict(t=20, l=20, r=20, b=20))
    
    st.plotly_chart(fig_pie)

    # Visualization 1: Top 10 Genres by City
    st.subheader("Top 10 Genres by City")
    top10_genres_by_city(df)
    
    st.markdown(
        """
        ### Analysis and Conclusions: Top 10 Genres by City
    
        **Analysis**:
        - This chart visualizes the most popular event genres across Valencia, Madrid, and Barcelona.
        - It highlights genre preferences in different cities, offering insights into local cultural trends.
        
        **Conclusions**:
        - Cities like Barcelona may show a preference for genres like Electronic, suggesting potential opportunities 
        for event planners to focus on specific genres.
        - Madrid's diversity in genres could indicate a broader appeal across different types of music and events.
        """
    )

    # Visualization 2: Sunburst Chart of Genres by City
    st.subheader("Genres by City (Sunburst)")
    genres_by_city_sunburst(df)
    st.markdown(
        """
        ### Analysis and Conclusions: Genres by City (Sunburst)
        
        **Analysis**:
        - The hierarchical view highlights the dominance of certain genres in specific cities.
        - This provides a clear breakdown of how each genre contributes to the event landscape.

        **Conclusions**:
        - Event organizers can identify niche markets and plan targeted marketing strategies to maximize audience engagement.
        """
    )

    # Visualization 3: Average Ticket Prices by City and Day of the Week
    st.subheader("Average Ticket Prices by City and Day of Week")
    average_ticket_prices_by_city_and_day_of_the_week(df)
    
    st.markdown(
        """
        ### Analysis and Conclusions: Ticket Prices
    
        **Analysis**:
        - Variations in ticket prices across cities and days of the week are evident.
        - Higher prices during weekends suggest increased demand and potential revenue maximization opportunities.
        
        **Conclusions**:
        - Dynamic pricing strategies could help optimize revenue for event organizers.
        - Understanding price sensitivities by day and city can guide event scheduling and promotions.
        """
    )

    # Visualization 4: Event Timeline (by City) 3 days range
    st.subheader(f"Events Timeline by City, 3 days range from {choose_starting_date} to {choose_finishing_date}")
    # 3 days range from the selected date
    choose_date = st.date_input("**Choose a starting date:**", min_value=df['starting_time'].dt.date.min(), max_value=df['finishing_time'].dt.date.max() - timedelta(days=3), value=df['starting_time'].dt.date.min())    

    all_cities = df['city'].unique()
    
    selected_city = st.selectbox("Select a city to display the timeline", options=all_cities)
    
    df_cities = df[df['city'] == selected_city]
    
    if df_cities.empty:
        st.info("No events are selected.")
    else:
        event_timeline(df_cities, choose_date)
        event_timeline_clubs(df_cities, choose_date)
    # Analysis and Conclusions for Event Timeline 3 days range
    
    st.markdown(
        """
        ### Analysis and Conclusions: Event Timeline
    
        **Analysis**:
        - The timeline displays event distribution across cities, helping organizers avoid overlaps and optimize schedules.
        - The comparison of event frequency by city provides a deeper understanding of activity levels.

        **Conclusions**:
        - Event planners can identify optimal time slots for hosting events.
        - Understanding periods of high activity ensures better resource allocation and avoids audience fatigue.
        """
    )

elif choose_price_filter == "Free":
    
    # Analysis and Conclusions for Price Filter
    st.markdown(
        """
        ### Analysis and Conclusions: Free Price Filter

        **Analysis**:
        - The **Free Price Filter** identifies events where a free ticket option was available at the time of data collection. This includes:
        - Completely free events with no paid ticket options.
        - Events offering a **guest list** option for free entry.
        - Events with multiple ticket types, including a free option at the time of collection.
        - This filter is valuable for distinguishing events that cater to a wider audience, offering opportunities for cost-free entertainment or promotional access.
        - It highlights events with varying pricing strategies, emphasizing the flexibility some organizers offer to attract diverse demographics.

        **Conclusions**:
        - **For attendees**: 
        - The filter provides an excellent way to discover budget-friendly or entirely free entertainment options, enabling broader participation in events.
        - Guests can prioritize events that offer value without financial commitment, especially when considering guest list entries or promotional access.
        - **For event organizers**: 
        - Offering free ticket options can be an effective marketing tool to attract new audiences, especially those hesitant to commit financially.
        - It presents a way to boost attendance during initial event hours or for less popular time slots, potentially converting free attendees into paying customers for future events.
        - Analyzing the success of free ticket options can provide insights into audience engagement and event accessibility.
        - **Strategic Value**: 
        - Events with free ticket options may serve as a gateway for building brand awareness, fostering goodwill, and cultivating a loyal attendee base.
        - Tracking trends in free ticket availability across cities and genres can guide organizers in adopting competitive pricing models while balancing profitability and accessibility.
        """
    )
    
    df_free = df[df['free_entrance'] == True].copy()
    
    # New Visualization pie chart of percentage of free events out of all events
    st.subheader("Percentage of Free Events out of All Events")
    free_events = df[df['free_entrance'] == True].shape[0]
    all_events = df.shape[0]
    free_percentage = round((free_events / all_events) * 100, 2)
    labels = ['Free Events', 'Paid Events']
    values = [free_percentage, 100 - free_percentage]
    fig_pie = px.pie(
        names=labels,
        values=values,
        title='Percentage of Free Events out of All Events',
        template='plotly_dark'
    )
    st.plotly_chart(fig_pie)
    
    st.markdown(
        """
        ### Analysis and Conclusions: Percentage of Free Events
    
        **Analysis**:
        - The pie chart illustrates the proportion of free events compared to all events in the dataset.
        - It provides a clear visualization of the availability of cost-free entertainment options for attendees.
        
        **Conclusions**:
        - The percentage of free events indicates the accessibility of budget-friendly entertainment across cities.
        - Event organizers can leverage free events to attract new audiences and build brand loyalty.
        """
    )    
    
    # Visualization 1: Top 10 Genres by City (Free Events)
    st.subheader("Top 10 Genres by City (Free Events)")
    top10_genres_by_city(df_free)
    
    st.markdown(
        """
        ### Analysis and Conclusions: Top 10 Genres by City (Free Events)
    
        **Analysis**:
        - This chart visualizes the most popular genres for free events across Valencia, Madrid, and Barcelona.
        - It highlights genre preferences for cost-free entertainment, offering insights into audience interests and promotional strategies.
        
        **Conclusions**:
        - Genres like Electronic and House may be popular choices for free events, attracting a diverse audience.
        - The availability of free tickets for specific genres can drive attendance and engagement, providing opportunities for event organizers to expand their reach.
        """
    )
    
    # Visualization 2: Sunburst Chart of Genres by City (Free Events)
    st.subheader("Genres by City (Sunburst) - Free Events")
    genres_by_city_sunburst(df_free)
    
    st.markdown(
        """
        ### Analysis and Conclusions: Genres by City (Sunburst) - Free Events
        
        **Analysis**:
        - The hierarchical view highlights the dominance of certain genres in free events across cities.
        - This provides a clear breakdown of how each genre contributes to cost-free entertainment options.

        **Conclusions**:
        - Event organizers can identify genres with high demand for free events and plan targeted marketing strategies to maximize audience engagement.
        """
    )
    
    # Visualization 4: Event Timeline (by City) - Free Events
    st.subheader(f"Events from {choose_starting_date} to {choose_finishing_date} by City (Free Events)")
    
    choose_date = st.date_input("**Choose a starting date:**", min_value=df['starting_time'].dt.date.min(), max_value=df['finishing_time'].dt.date.max() - timedelta(days=3), value=df['starting_time'].dt.date.min())    

    
    all_cities = df_free['city'].unique()
    
    selected_city = st.multiselect("Select cities to include", options=all_cities, default= None)
    
    df_cities = df_free[df_free['city'].isin(selected_city)]
    
    if df_cities.empty:
        st.info("No events are selected.")
    else:
        event_timeline(df_cities, choose_date)
    
    st.markdown(
        """
        ### Analysis and Conclusions: Event Timeline - Free Events
    
        **Analysis**:
        - The timeline displays the distribution of free events across cities, helping organizers avoid overlaps and optimize schedules.
        - The comparison of free event frequency by city provides insights into cost-free entertainment options.

        **Conclusions**:
        - Event planners can identify optimal time slots for hosting free events.
        - Understanding periods of high free event activity ensures better resource allocation and avoids audience fatigue.
        """
    )
    
elif choose_price_filter == "Sold Out":
    
    # Analysis and Conclusions for Price Filter
    st.markdown(
        """
        ### Analysis and Conclusions: Sold Out Price Filter

        **Analysis**:
        - The **Sold Out Price Filter** identifies events that were sold out at the time of data collection. This includes:
        - Events where all ticket types were fully booked or unavailable.
        - High-demand activities that reached full capacity before the event date.
        - Popular events with limited seating or exclusive access.
        - This filter is valuable for highlighting events with high audience demand, successful marketing campaigns, or limited availability.
        - It provides insights into the popularity of specific genres, venues, or time slots, guiding future event planning strategies.

        **Conclusions**:
        - **For attendees**: 
        - The filter offers a way to discover sought-after events and trending activities that may require early booking or planning.
        - Sold-out events can indicate high-quality entertainment, exclusive access, or unique experiences that appeal to a broad audience.
        - **For event organizers**: 
        - Understanding sold-out events can help identify successful marketing strategies, pricing models, or promotional tactics.
        - It provides an opportunity to analyze audience preferences, optimize ticket sales, and plan future events based on high-demand genres or activities.
        - **Strategic Value**: 
        - Sold-out events can drive urgency, increase event visibility, and create a sense of exclusivity, enhancing brand reputation and customer loyalty.
        - Tracking trends in sold-out events across cities and genres can guide organizers in creating scarcity, demand, and excitement for future activities.
        """
    )
    
    df_sold_out = df[df['remain_prices'] == 'SOLD OUT']
    
    # New Visualization pie chart of percentage of sold out events out of all events
    st.subheader("Percentage of Sold Out Events out of All Events")
    sold_out_events = df[df['remain_prices'] == 'SOLD OUT'].shape[0]
    all_events = df.shape[0]
    sold_out_percentage = round((sold_out_events / all_events) * 100, 2)
    labels = ['Sold Out Events', 'Available Events']
    values = [sold_out_percentage, 100 - sold_out_percentage]
    fig_pie = px.pie(
        names=labels,
        values=values,
        title='Percentage of Sold Out Events out of All Events',
        template='plotly_dark',
    )
    st.plotly_chart(fig_pie)
    
    st.markdown(
        """
        ### Analysis and Conclusions: Percentage of Sold Out Events
    
        **Analysis**:
        - The pie chart illustrates the proportion of sold-out events compared to all events in the dataset.
        - It provides a clear visualization of high-demand activities that reached full capacity before the event date.
        
        **Conclusions**:
        - The percentage of sold-out events indicates the popularity and exclusivity of certain genres, venues, or time slots.
        - Event organizers can leverage scarcity and demand to create excitement, drive ticket sales, and enhance brand reputation.
        """
    )
    
    # Visualization 1: Top 10 Genres by City (Sold Out Events)
    st.subheader("Top 10 Genres by City (Sold Out Events)")
    try:
        top10_genres_by_city(df_sold_out)
    except:   
        st.warning("No sold-out events in the dataset.")
    
    st.markdown(
        """
        ### Analysis and Conclusions: Top 10 Genres by City (Sold Out Events)
    
        **Analysis**:
        - This chart visualizes the most popular genres for sold-out events across Valencia, Madrid, and Barcelona.
        - It highlights genres with high audience demand, successful marketing campaigns, or limited availability.
        
        **Conclusions**:
        - Genres like Techno and House may be popular choices for sold-out events, attracting a dedicated audience.
        - The availability of sold-out events can drive urgency, increase event visibility, and create a sense of exclusivity.
        """
    )
    
    # Visualization 2: Sunburst Chart of Genres by City (Sold Out Events)
    st.subheader("Genres by City (Sunburst) - Sold Out Events")
    try:
        genres_by_city_sunburst(df_sold_out)
    except:
        st.warning("No sold-out events in the dataset.")
    st.markdown(
        """
        ### Analysis and Conclusions: Genres by City (Sunburst) - Sold Out Events
        
        **Analysis**:
        - The hierarchical view highlights the dominance of certain genres in sold-out events across cities.
        - This provides a clear breakdown of how each genre contributes to high-demand activities.

        **Conclusions**:
        - Event organizers can identify genres with exclusive access, limited availability, or high audience demand for future event planning.
        """
    )
    
    # Visualization 4: Event Timeline (by City) - Sold Out Events 3 days range
    st.subheader(f"Events from {choose_starting_date} to {choose_finishing_date} by City (Sold Out Events)")
    
    if df_sold_out.empty:
        st.info("No sold-out events are available.")
    else:
        choose_date = st.date_input("**Choose a starting date:**", min_value=df['starting_time'].dt.date.min(), max_value=df['finishing_time'].dt.date.max(), value=df['starting_time'].dt.date.min())    

        all_cities = df_sold_out['city'].unique()
        
        selected_city = st.multiselect("Select cities to include", options=all_cities, default= None)
        
        df_cities = df_sold_out[df_sold_out['city'].isin(selected_city)]
        
        if df_cities.empty:
            st.info("No events are selected.")
        else:
            event_timeline(df_cities, choose_date)
    
    st.markdown(
        """
        ### Analysis and Conclusions: Event Timeline - Sold Out Events
    
        **Analysis**:
        - The timeline displays the distribution of sold-out events across cities, helping organizers avoid overlaps and optimize schedules.
        - The comparison of sold-out event frequency by city provides insights into high-demand activities.

        **Conclusions**:
        - Event planners can identify optimal time slots for hosting sold-out events.
        - Understanding periods of high sold-out event activity ensures better resource allocation and avoids audience disappointment.
        """
    )
    
        
    
    
