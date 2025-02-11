import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv
import os
from functions import *
from analysis import *
from datetime import datetime, timedelta

# Load the data from the Airtable database
st.set_page_config(
    page_title="Music Events Analysis",  # Optional title
    layout="wide",        # Choose between "wide" or "centered"
    initial_sidebar_state="auto"  # "expanded", "collapsed", or "auto"
)
@st.cache_data
def load_data():
    return pd.read_csv('Data/airtable_preprocessed_data.csv')

# Load the data
df = load_data()

df['starting_time'] = pd.to_datetime(df['starting_time'])

df['finishing_time'] = pd.to_datetime(df['finishing_time'])

# Streamlit App Title and Description
st.title("Event Data Analysis Dashboard")

df1 = df.copy()
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

menu = ["Overview", "Analysis and Conclusions"]
choice = st.sidebar.selectbox("Menu", menu)

# Now you can apply the filtering based on the conditions
if choice == "Overview":
    
    # Overview of the project   
    st.markdown(
    """
    ### Overview  
    
    Welcome to the **Music Events Data Analysis Dashboard**!  
    This dashboard provides comprehensive insights into music events across **Valencia**, **Madrid**, and **Barcelona**, 
    leveraging data sourced from **Xceed** and stored in an Airtable database. By analyzing event trends, ticket pricing, and genre preferences, 
    it offers actionable insights for event planners, marketers, and music enthusiasts.
    
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

    This project analyzes music events in three major Spanish cities to uncover patterns, trends, and insights that can guide strategic decision-making. 
    Key objectives include:  

    - **City-Wide Event Distribution**: Understanding how events are spread across cities and identifying regional hotspots for cultural activities.  
    - **Genre Preferences**: Analyzing the popularity of genres to identify opportunities for niche event planning or marketing strategies.  
    - **Ticket Price Analysis**: Examining pricing strategies, including free and sold-out events, to understand audience demand and affordability trends.  
    - **Temporal Trends**: Exploring how event timing (weekdays vs. weekends) impacts attendance and pricing.  

    #### Highlights:
    - Visualizations include pie charts, sunburst charts, and treemaps that showcase event distributions, genre preferences, and geographic densities.
    - Interactive heatmaps and event timelines allow for a detailed exploration of event locations and scheduling patterns.
    - Analysis spans from free events to sold-out scenarios, offering insights into different segments of the market.

    ### Conclusions  

    The analysis reveals several actionable insights:  

    - **Madrid Dominance**: Madrid hosts the highest number of events, reflecting its vibrant cultural scene. This makes it a focal point for diverse event offerings.  
    - **Genre Specialization**: Barcelona shows a strong preference for Electronic and House music, suggesting a niche market ripe for targeted event planning.  
    - **Accessibility in Valencia**: Events in Valencia tend to have lower ticket prices, making it a more accessible market for budget-conscious audiences.  
    - **Peak Demand Days**: Fridays and Saturdays show the highest ticket prices, correlating with increased demand and suggesting opportunities for premium pricing strategies.  
    - **Geographic Opportunities**: Heatmap analysis highlights high-density areas for events, providing guidance for venue selection and urban event planning.  

    This dashboard equips users with the insights needed to optimize event planning, enhance audience engagement, and capitalize on emerging trends in the vibrant Spanish music scene.  
        """
    )
    
if choice == "Analysis and Conclusions":
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

    # Filter the data based on the selected date range
    df = df[(df['starting_time'] >= choose_starting_date.strftime('%Y-%m-%d')) 
                    & (df['finishing_time'] <= choose_finishing_date.strftime('%Y-%m-%d'))]

    choose_price_filter = st.sidebar.selectbox("**Price filter:**", ["All", "Free", "Sold Out"], index=0)
    
    if choose_price_filter == "All":
        st.markdown(
            """
            ### Analysis and Conclusions: All Price Filter

            **Analysis**:
            - The **All Price Filter** includes all events in the dataset, regardless of ticket prices or availability.
            - It provides a comprehensive view of the event landscape, highlighting genre preferences, city distribution, and ticket pricing.
            - This filter serves as the baseline for understanding event trends and audience preferences across Valencia, Madrid, and Barcelona.

            **Conclusions**:
            - **For attendees**: 
            - The filter offers a broad selection of events, catering to diverse interests and preferences.
            - Attendees can explore a wide range of genres, venues, and ticket prices to find events that match their preferences.
            - **For event organizers**: 
            - Analyzing all events helps identify genre popularity, pricing strategies, and audience engagement levels.
            - Event planners can leverage insights to optimize marketing campaigns, venue selection, and ticket pricing.
            - **Strategic Value**: 
            - Understanding the overall event landscape enables organizers to plan future events, identify market gaps, and capitalize on emerging trends.
            - Tracking genre preferences, city distribution, and ticket pricing can guide data-driven decision-making and enhance event planning strategies.
            """
        )
        choice = st.sidebar.selectbox("Choose a visualization", ["Percentage of Events by City", 
                                                                 "Top 10 Genres by City", 
                                                                 "Genres by City (Sunburst)", 
                                                                 "Average Ticket Prices by City and Day of the Week", 
                                                                 "Event Timeline by City",
                                                                 "Distribution of Events by District",
                                                                 "Heatmap", "Event Map"])
    
        # New Visualization pie chart of percentage of events per city
        if choice == "Percentage of Events by City":
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
            
            st.markdown(
                """
                ### Analysis and Conclusions: Percentage of Events by City
            
                **Analysis**:
                - The pie chart illustrates the distribution of events across Valencia, Madrid, and Barcelona.
                - It provides a visual representation of event density in each city, highlighting potential market opportunities.
                
                **Conclusions**:
                - Madrid has the highest number of events, indicating a vibrant event scene with diverse offerings.
                - Valencia and Barcelona show comparable event frequencies, suggesting a balanced market landscape.
                """
            )


        # Visualization 1: Top 10 Genres by City
        if choice == "Top 10 Genres by City":
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
        if choice == "Genres by City (Sunburst)":
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
            
        if choice == "Average Ticket Prices by City and Day of the Week":
            st.subheader("Average Ticket Prices by City and Day of the Week")
            average_ticket_prices_by_city_and_day_of_the_week(df)
            
            st.markdown(
                """
                ### Analysis and Conclusions: Average Ticket Prices by City and Day of Week
            
                **Analysis**:
                - Variations in ticket prices across cities and days of the week are evident.
                - Higher prices during weekends suggest increased demand and potential revenue maximization opportunities.
                
                **Conclusions**:
                - Dynamic pricing strategies could help optimize revenue for event organizers.
                - Understanding price sensitivities by day and city can guide event scheduling and promotions.
                """
            )

        # Visualization 4: Event Timeline (by City) 3 days range
        if choice == "Event Timeline by City":
            st.subheader(f"Events Timeline by City, 3 days range from {choose_starting_date} to {choose_finishing_date}")
            # 3 days range from the selected date
            choose_date = st.sidebar.date_input("**Choose a starting date:**", min_value=df['starting_time'].dt.date.min(), max_value=df['finishing_time'].dt.date.max() - timedelta(days=3), value=df['starting_time'].dt.date.min() + timedelta(days=4))    

            all_cities = df['city'].unique()
            
            selected_city = st.sidebar.selectbox("Select a city to display the timeline", options=all_cities)
            
            df_cities = df[df['city'] == selected_city]
            
            if df_cities.empty:
                st.info("No events are selected.")
            else:
                event_timeline(df_cities, choose_date)
                # event_timeline_clubs(df_cities, choose_date)
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
        if choice == "Distribution of Events by District":
            st.subheader("Distribution of Events by District")
            treemap_data(df)
            
            st.markdown(
                """
                ### Analysis and Conclusions: Distribution of Events by District
                
                **Analysis**:
                - The treemap visualization showcases the distribution of events by district within each city.
                - It provides a detailed view of event density and venue popularity across different districts.
                
                **Conclusions**:
                - Event planners can identify high-traffic districts and popular venues for hosting events.
                - Understanding the distribution of events by district can guide venue selection and marketing strategies
                
                """
            )
        if choice == "Heatmap":
            st.subheader("Heatmap of Events by City")
            city = st.sidebar.selectbox("Select a city", df['city'].unique())
            
            heatmap_data(df, city)
            
            st.markdown(
                """
                ### Analysis and Conclusions: Heatmap of Events by City
                
                **Analysis**:
                - The heatmap visualization provides a geographic overview of event distribution across cities.
                - It highlights event density and venue locations, offering insights into popular event areas.
                
                **Conclusions**:
                - Event planners can identify high-traffic regions and popular venues for hosting events.
                - Understanding the geographic distribution of events can guide venue selection and marketing strategies.
                """
            )
        if choice == "Event Map":
                
                st.subheader("Event Map")
                city = st.sidebar.selectbox("Select a city", df['city'].unique())
                
                event_map_data(df, city)
                
                st.markdown(
                    """
                    ### Analysis and Conclusions: Event Map
                    
                    **Analysis**:
                    - The interactive map displays event locations within the selected city.
                    - It provides a visual representation of event distribution and venue density.
                    
                    **Conclusions**:
                    - Event planners can identify popular event areas and venue clusters for hosting events.
                    - Understanding the geographic distribution of events can guide venue selection and marketing strategies.
                    """
                )

    if choose_price_filter == "Free":
        
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
        choice = st.sidebar.selectbox("Choose a visualization", ["Percentage of Events by City", 
                                                                 "Top 10 Genres by City", 
                                                                 "Genres by City (Sunburst)", 
                                                                 "Average Ticket Prices by City and Day of the Week",
                                                                 "Event Timeline by City",
                                                                 "Distribution of Events by District",
                                                                 "Heatmap", "Event Map"])
    
    # New Visualization pie chart of percentage of free events out of all events
        if choice == "Percentage of Events by City":
            st.subheader("Percentage of Free Events by City")
            labels = ['Free Events', 'Paid Events']
            values = [df_free.shape[0], df.shape[0] - df_free.shape[0]]
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
        if choice == "Top 10 Genres by City":
            st.subheader("Top 10 Genres by City - Free Events")
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
        if choice == "Genres by City (Sunburst)":
            
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
        
        if choice == "Average Ticket Prices by City and Day of the Week":
            st.subheader("Average Ticket Prices by City and Day of the Week")
            average_ticket_prices_by_city_and_day_of_the_week(df_free)
            
            st.markdown(
                """
                ### Analysis and Conclusions: Average Ticket Prices by City and Day of the Week - Free Events
            
                **Analysis**:
                - Variations in ticket prices across cities and days of the week are evident for free events.
                - Understanding price sensitivities by day and city can guide event scheduling and promotions.
                
                **Conclusions**:
                - Event planners can leverage insights into average ticket prices to optimize revenue and attendance for free events.
                - Dynamic pricing strategies could help attract a broader audience and enhance event visibility.
                """
            )


# Visualization 4: Event Timeline (by City) - Free Events
        if choice == "Event Timeline by City":
            
            st.subheader(f"Events from {choose_starting_date} to {choose_finishing_date} by City (Free Events)")

            choose_date = st.sidebar.date_input("**Choose a starting date:**", min_value=df['starting_time'].dt.date.min(), max_value=df['finishing_time'].dt.date.max() - timedelta(days=3), value=df['starting_time'].dt.date.min())    

            all_cities = df_free['city'].unique()
            
            selected_city = st.sidebar.multiselect("Select cities to include", options=all_cities, default= None)
            
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
        if choice == "Distribution of Events by District":
            st.subheader("Distribution of Events by District - Free Events")
            treemap_data(df_free)
            
            st.markdown(
                """
                ### Analysis and Conclusions: Distribution of Events by District
                
                **Analysis**:
                - The treemap visualization showcases the distribution of free events by district within each city.
                - It provides a detailed view of event density and venue popularity across different districts.
                
                **Conclusions**:
                - Event planners can identify high-traffic districts and popular venues for hosting free events.
                - Understanding the distribution of free events by district can guide venue selection and marketing strategies
                
                """
            )
            
        if choice == "Heatmap":
            st.subheader("Heatmap of Events by City - Free Events")
            city = st.sidebar.selectbox("Select a city", df['city'].unique())
            
            heatmap_data(df_free, city)
            
            st.markdown(
                """
                ### Analysis and Conclusions: Heatmap of Events by City
                
                **Analysis**:
                - The heatmap visualization provides a geographic overview of event distribution across cities.
                - It highlights event density and venue locations, offering insights into popular event areas.
                
                **Conclusions**:
                - Event planners can identify high-traffic regions and popular venues for hosting events.
                - Understanding the geographic distribution of events can guide venue selection and marketing strategies.
                """
            )
        if choice == "Event Map":
                
                st.subheader("Event Map - Free Events")
                city = st.sidebar.selectbox("Select a city", df['city'].unique())
                
                event_map_data(df_free, city)
                
                st.markdown(
                    """
                    ### Analysis and Conclusions: Event Map
                    
                    **Analysis**:
                    - The interactive map displays event locations within the selected city.
                    - It provides a visual representation of event distribution and venue density.
                    
                    **Conclusions**:
                    - Event planners can identify popular event areas and venue clusters for hosting events.
                    - Understanding the geographic distribution of events can guide venue selection and marketing strategies.
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
        choice = st.sidebar.selectbox("Choose a visualization", ["Percentage of Events by City", 
                                                                 "Top 10 Genres by City", 
                                                                 "Genres by City (Sunburst)", 
                                                                 "Average Ticket Prices by City and Day of the Week", 
                                                                 "Event Timeline by City",
                                                                 "Distribution of Events by District",
                                                                 "Heatmap", "Event Map"])
        
        # New Visualization pie chart of percentage of sold out events out of all events
        if choice == "Percentage of Events by City":
            st.subheader("Percentage of Sold Out Events by City")
            
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
        if choice == "Top 10 Genres by City":
            st.subheader("Top 10 Genres by City - Sold Out Events")
            
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
        if choice == "Genres by City (Sunburst)":
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
        if choice == "Average Ticket Prices by City and Day of the Week":
            st.subheader("Average Ticket Prices by City and Day of the Week")
            average_ticket_prices_by_city_and_day_of_the_week(df_sold_out)
            
            st.markdown(
                """
                ### Analysis and Conclusions: Average Ticket Prices by City and Day of the Week - Sold Out Events
            
                **Analysis**:
                - Variations in ticket prices across cities and days of the week are evident for sold-out events.
                - Understanding price sensitivities by day and city can guide event scheduling and promotions.
                
                **Conclusions**:
                - Event planners can leverage insights into average ticket prices to optimize revenue and attendance for sold-out events.
                - Dynamic pricing strategies could help attract a broader audience and enhance event visibility.
                """
            )
        
        # Visualization 4: Event Timeline (by City) - Sold Out Events 3 days range
        if choice == "Event Timeline by City":
            st.subheader(f"Events from {choose_starting_date} to {choose_finishing_date} by City (Sold Out Events)")
            
            if df_sold_out.empty:
                st.info("No sold-out events are available.")
            else:
                choose_date = st.sidebar.date_input("**Choose a starting date:**", min_value=df['starting_time'].dt.date.min(), max_value=df['finishing_time'].dt.date.max(), value=df['starting_time'].dt.date.min())    

                all_cities = df_sold_out['city'].unique()
                
                selected_city = st.sidebar.multiselect("Select cities to include", options=all_cities, default= None)
                
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
                
        if choice == "Distribution of Events by District":
            st.subheader("Distribution of Events by District - Sold Out Events")
            treemap_data(df_sold_out)
            
            st.markdown(
                """
                ### Analysis and Conclusions: Distribution of Events by District - Sold Out Events
                
                **Analysis**:
                - The treemap visualization showcases the distribution of sold-out events by district within each city.
                - It provides a detailed view of event density and venue popularity across different districts.
                
                **Conclusions**:
                - Event planners can identify high-traffic districts and popular venues for hosting sold-out events.
                - Understanding the distribution of sold-out events by district can guide venue selection and marketing strategies
                
                """
            )
        
        if choice == "Heatmap":
            st.subheader("Heatmap of Events by City")
            city = st.sidebar.selectbox("Select a city", df['city'].unique())
            
            heatmap_data(df, city)
            
            st.markdown(
                """
                ### Analysis and Conclusions: Heatmap of Events by City
                
                **Analysis**:
                - The heatmap visualization provides a geographic overview of event distribution across cities.
                - It highlights event density and venue locations, offering insights into popular event areas.
                
                **Conclusions**:
                - Event planners can identify high-traffic regions and popular venues for hosting events.
                - Understanding the geographic distribution of events can guide venue selection and marketing strategies.
                """
            )
            
        if choice == "Event Map":
            
            st.subheader("Event Map")
            city = st.sidebar.selectbox("Select a city", df['city'].unique())
            
            event_map_data(df, city)
            
            st.markdown(
                """
                ### Analysis and Conclusions: Event Map
                
                **Analysis**:
                - The interactive map displays event locations within the selected city.
                - It provides a visual representation of event distribution and venue density.
                
                **Conclusions**:
                - Event planners can identify popular event areas and venue clusters for hosting events.
                - Understanding the geographic distribution of events can guide venue selection and marketing strategies.
                """
            )
    
        
