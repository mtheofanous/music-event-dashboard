Music Event Analysis Dashboard
Overview
This project is an interactive dashboard that provides insights into music events across Barcelona, Madrid, and Valencia. Leveraging data from Xceed and Airtable, it offers dynamic visualizations to assist event organizers, marketers, and attendees in understanding event trends and making data-driven decisions.

Features
City-Based Insights:
Distribution of events by city.
Popular districts and venues.
Genre Analysis:
Top 10 genres per city.
Sunburst visualization of genre distribution.
Ticket Pricing:
Average ticket prices by day of the week.
Analysis of free and sold-out events.
Event Schedules:
Timeline of events filtered by date and city.
Geographical Visualizations:
Heatmaps for event density.
Interactive maps showing event locations.
Tech Stack
Python: Core development
Streamlit: Interactive dashboards
Plotly & Folium: Advanced visualizations and maps
Airtable API: Dynamic data integration
Selenium & BeautifulSoup: Web scraping
How It Works
Data Collection:
Scrapes data from Xceed for events in Barcelona, Madrid, and Valencia.
Updates Airtable with new and modified event data.
Data Processing:
Cleans and preprocesses data for analysis.
Extracts key insights like event genres, ticket prices, and more.
Visualization:
Creates interactive dashboards with Streamlit.
Offers various filtering and exploration options.
Installation
Clone the repository:
git clone https://github.com/yourusername/music-event-dashboard.git

Install dependencies:
pip install -r requirements.txt
Set up the .env file with your Airtable API credentials.

Run the dashboard:
streamlit run main.py

Future Improvements
Adding more cities for broader analysis.
Enhancing visualizations with user-specific recommendations.

Contributing
Feel free to fork the repository and open a pull request. Contributions are welcome!

