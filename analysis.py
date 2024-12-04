import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from functions import top10_generos
from datetime import timedelta
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium

@st.cache_data
def top10_genres_by_city(df):   
    df_genero = df[~df['event_genres'].isnull()] 
    # is not 'NaN
    df_genero = df_genero[df_genero['event_genres'] != 'NaN']
    genero = top10_generos(df_genero)

    # Visualization 1: Top 10 Genres by City

    fig = px.bar(
        genero,
        x='genero',
        y='frecuencia',
        color='city',
        hover_data= 'city',
        barmode='group',
        template='plotly_dark',
        width=1500,
        height=600,
    )

    # make the plot bigger
    fig.update_layout(
        margin=dict(t=0, l=0, r=0, b=0)
    )
    st.plotly_chart(fig)
    
@st.cache_data   
def genres_by_city_sunburst(df):
    
    df_genero = df[~df['event_genres'].isnull()]
    df_genero = df_genero[df_genero['event_genres'] != 'NaN']
    genero = top10_generos(df_genero)
    
    fig_sunburst = px.sunburst(
    genero,
    values="frecuencia",
    path=['city', 'genero'],
    color="genero",
    template='plotly_dark'
    )
    # add percentage labels
    fig_sunburst.update_traces(textinfo='label+percent entry')
    
    fig_sunburst.update_layout(
        margin=dict(t=0, l=0, r=0, b=0)
    )
    st.plotly_chart(fig_sunburst)
    
@st.cache_data
def average_ticket_prices_by_city_and_day_of_the_week(df):

    # Filter out rows where ticket prices are not available
    df_precios = df[df['ticket_price'] != 'No information available'].copy()

    # Convert ticket prices to floats and calculate mean
    # Split the prices, convert to float, and compute the mean in one step
    df_precios['mean_price'] = (
        df_precios['ticket_price']
        .str.split(', ')
        .apply(lambda prices: np.mean(list(map(float, prices))))
    )

    # Create the box plot with Plotly
    fig_box = px.box(
        data_frame=df_precios,
        x="city",
        y="mean_price",
        color="city",
        facet_col="starting_day",
        template="plotly_dark",
        points="suspectedoutliers",
        width=1000,
        height=500
    )

    # Simplify the facet column annotations
    fig_box.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

    # Adjust layout
    fig_box.update_layout(
        margin=dict(t=0, l=0, r=0, b=0)
    )

    # Display the plot
    st.plotly_chart(fig_box)


def event_timeline(df_, choose_date):
    """
    Generates a timeline visualization for events over a 3-day period.

    Args:
    df_ (DataFrame): The input data containing event details.
    choose_date (str or datetime): The starting date for the 3-day period.

    Returns:
    None: Displays the timeline chart in the Streamlit app.
    """
    # Filter the data for the selected 3-day period
    start_date = pd.to_datetime(choose_date)
    end_date = start_date + timedelta(days=3)
    df_filtered = df_[(df_['starting_time'] >= start_date) & (df_['finishing_time'] <= end_date)]
    
    # Create the initial timeline chart
    fig_timeline = px.timeline(
        data_frame=df_filtered,
        x_start="starting_time",
        x_end="finishing_time",
        y="event_title",
        color="place",
        labels={"event_title": "Event Title"},
        width=1800, 
        height=200 + 15*len(df_filtered),
        color_continuous_scale=px.colors.sequential.Viridis
    )

    # Update the appearance of the timeline
    fig_timeline.update_traces(
        marker=dict(line=dict(width=0.2, color='black')),
        opacity=0.9,
        width=0.6,
        
    )
    fig_timeline.update_layout(
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5),
        margin=dict(t=20, l=20, r=20, b=20),
        # plot_bgcolor="rgba(0, 0, 0, 0)",  # Transparent background
        # paper_bgcolor="white",# Chart background
        xaxis = dict(showgrid=True, 
                     zeroline=True, 
                     showticklabels=True, 
                     tickfont=dict(size=14, weight= 'bold'), 
                     tickmode="array",
                     ticktext=pd.date_range(start=start_date, end=end_date, freq="6h").strftime("%H:%M %m-%d").tolist(),
                     ),
        yaxis = dict(showgrid=True, zeroline=False,categoryorder="category ascending", showticklabels=True, tickfont=dict(size=14, weight= 'bold'), tickmode="array", griddash="dot")
    )

    # Render the timeline chart in the Streamlit app
    return st.plotly_chart(fig_timeline)

# Function to generate a treemap visualization for the events per district
def treemap_data(df):
    
    """_summary_
    Generates a treemap visualization for the events per district per city.
    
    _description_
    This function generates a treemap visualization that shows the distribution of events per district per city.
    The size of each rectangle represents the number of events in the corresponding district.
    The color of each rectangle represents the city where the district is located.
    """
    # Group the data by city and district
    df_grouped = df.groupby(['city', 'district']).size().reset_index(name='event_count')
    
    # Create the treemap visualization
    fig_treemap = px.treemap(
        data_frame=df_grouped,
        path=['city', 'district'],
        values='event_count',
        color='city',
        color_discrete_sequence=px.colors.qualitative.Set1,
        template='plotly_dark',
        width=1200,
        height=600
    )
    
    # Adjust the layout of the treemap visualization
    fig_treemap.update_layout(
        margin=dict(t=0, l=0, r=0, b=0),
    )
    fig_treemap.update_traces(textinfo='label+percent entry', hoverinfo='label+percent entry',textfont=dict(size=16, family="Arial", color="white"),  # Adjust size and color
    texttemplate="<b>%{label}</b>")
    
    # Display the treemap visualization
    st.plotly_chart(fig_treemap)
    
def heatmap_data(df, city):
    """_summary_
    Generates a heatmap visualization for the event locations in the selected city.
    
    _description_
    This function generates a heatmap visualization that shows the distribution of event locations in the selected city.
    The heatmap is based on the latitude and longitude coordinates of the event locations.
    """
    # Filter the data for the selected city
    df_city = df[df['city'] == city]
    
    # Create a folium map centered on the selected city
    m = folium.Map(location=[df_city['latitud'].mean(), df_city['longitud'].mean()], zoom_start=11, tiles = 'OpenStreetMap')
    
    # Add a heatmap layer to the map
    HeatMap(data=df_city[['latitud', 'longitud']], radius=10).add_to(m)
    
    # Display the folium map in the Streamlit app
    st_folium(m)
    
def event_map_data(df, city):
    """_summary_
    Generates a map visualization for the event locations in the selected city.
    
    _description_
    This function generates a map visualization that shows the event locations in the selected city.
    The map includes markers for each event location, with additional information displayed on hover.
    """
    # Filter the data for the selected city
    df_city = df[df['city'] == city]
    
    # Create a folium map centered on the selected city
    m = folium.Map(location=[df_city['latitud'].mean(), df_city['longitud'].mean()], zoom_start=12,tiles = 'OpenStreetMap')
    
    # Add markers for each event location to the map
    for index, row in df_city.iterrows():
        folium.Marker([row['latitud'], row['longitud']], popup=row['event_title']).add_to(m)
    
    # Display the folium map in the Streamlit app
    st_folium(m)

