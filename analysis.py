import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from functions import top10_generos
from datetime import timedelta

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
    # df_precios = df[df['ticket_price'] != 'No information available']
    # precios = df_precios['ticket_price'].apply(lambda x: x.split(', '))
    # precios_float = precios.apply(lambda x: sorted(map(float, x)))
    # mean_prices = [round(np.mean(x)) for x in precios_float]

    # df_precios.loc[:, 'mean_price'] = mean_prices

    # fig_box = px.box(
    #     data_frame=df_precios,
    #     x="city",
    #     y="mean_price",
    #     color="city",
    #     facet_col='starting_day',
    #     template="plotly_dark",
    #     points="suspectedoutliers",
    #     width=1000,
    #     height=500
    # )
    # fig_box.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    # fig_box.update_layout(
    #     margin=dict(t=0, l=0, r=0, b=0)
    # )
    # st.plotly_chart(fig_box)

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
        template="plotly", # Choose a different template if needed (e.g., "plotly_dark", "ggplot2", "simple_white", "plotly", "presentation")
        width=1800, #700 + 10*len(df_filtered), # Automatically adjusts the width based on the number of events displayed
        height=200 + 15*len(df_filtered), #100 + 12*len(df_filtered), # Automatically adjusts the height based on the number of events displayed
        color_discrete_sequence=["rgb(187,187,187)"]
    )

    # Update the appearance of the timeline
    fig_timeline.update_traces(
        marker=dict(line=dict(width=0.1, color='black')),
        opacity=0.9,
        width=0.5,
        
    )
    fig_timeline.update_layout(
        showlegend=False,
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.1),
        margin=dict(t=20, l=20, r=20, b=20),
        plot_bgcolor="rgba(0, 0, 0, 0)",  # Transparent background
        paper_bgcolor="white",# Chart background
        xaxis = dict(showgrid=True, 
                     zeroline=True, 
                     showticklabels=True, 
                     tickfont=dict(size=14, weight= 'bold'), 
                     tickmode="array",
                     ticktext=pd.date_range(start=start_date, end=end_date, freq="6h").strftime("%H:%M %m-%d").tolist(),
                     ),
        yaxis = dict(showgrid=True, zeroline=False, showticklabels=True, tickfont=dict(size=14, weight= 'bold'), tickmode="array", griddash="dot")
    )
    fig_timeline.update_yaxes(
        title_text='', 
        showgrid=True, 
        categoryorder="category ascending", # more options: "category ascending" or "category descending"
        gridwidth=4
    )
        
    # Add rounded corner markers to the start and end of each event
    for _, row in df_filtered.iterrows():
        fig_timeline.add_trace(go.Scatter(
            x=[row["starting_time"], row["finishing_time"]],
            y=[row["event_title"], row["event_title"]],
            mode="markers",
            marker=dict(
                color="rgb(187,187,187)",  # Default color for markers
                opacity=0.9,
                symbol="circle",
                size = max(4, 20 - round(len(df_filtered) // 2))
            ),
            showlegend=False,
           
        ))

    # Render the timeline chart in the Streamlit app
    return st.plotly_chart(fig_timeline)

def event_timeline_clubs(df_, choose_date):
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
        y="place",
        color="event_title",
        template="plotly", # Choose a different template if needed (e.g., "plotly_dark", "ggplot2", "simple_white", "plotly", "presentation")
        width=800, #600 + 10*len(df_filtered), # Automatically adjusts the width based on the number of events displayed
        height=600, #100 + 10*len(df_filtered),# Automatically adjusts the height based on the number of events displayed
        color_discrete_sequence=px.colors.qualitative.Antique_r,
    )

    # Update the appearance of the timeline
    fig_timeline.update_traces(
        marker=dict(line=dict(width=0.1, color='black')),
        opacity=0.9,
        width=0.3
    )
    fig_timeline.update_layout(
        showlegend=False,
        margin=dict(t=10, l=5, r=5, b=5),
        # legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.1),
        plot_bgcolor="rgba(0, 0, 0, 0)",  # Transparent background
        paper_bgcolor="white",
        xaxis = dict(showgrid=True, zeroline=False, showticklabels=True, tickfont=dict(size=14, weight= 'bold'), tickmode="linear", tick0=0, dtick=1),
        yaxis = dict(showgrid=True, zeroline=False, showticklabels=True, tickfont=dict(size=14, weight= 'bold'), tickmode="auto", griddash="dot")# Chart background
    )
    fig_timeline.update_yaxes(
        title_text='', 
        showgrid=True, 
        categoryorder="category ascending",
        gridwidth=4,
    )
    fig_timeline.update_xaxes(
        title_text='', 
        showgrid=True
    )

    # Add rounded corner markers to the start and end of each event
    for _, row in df_filtered.iterrows():
        fig_timeline.add_trace(go.Scatter(
            x=[row["starting_time"], row["finishing_time"]],
            y=[row["place"], row["place"]],
            mode="markers",
            marker=dict(
                color="black",  # Default color for markers
                opacity=0.8,
                symbol="circle-dot",
                size = max(4, 20 - round(len(df_filtered) // 2))
            ),
            showlegend=True
        ))


    # Render the timeline chart in the Streamlit app
    return st.plotly_chart(fig_timeline)

