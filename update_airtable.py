{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "import pandas as pd\n",
    "import numpy as np\n",
    "import plotly.express as px\n",
    "import streamlit as st\n",
    "from dotenv import load_dotenv\n",
    "import os\n",
    "from functions import fetch_airtable_data, airtable_to_dataframe\n",
    "from analysis import top10_genres_by_city, genres_by_city_sunburst, average_ticket_prices_by_city_and_day_of_the_week, event_timeline\n",
    "\n",
    "# Load environment variables\n",
    "load_dotenv()\n",
    "\n",
    "TOKEN = os.getenv('XCEED_TOKEN')\n",
    "BASE_ID = os.getenv('BASE_ID')\n",
    "TABLE_ID = os.getenv('TABLE_ID')\n",
    "\n",
    "# Define Airtable API details\n",
    "airtable_base_url = \"https://api.airtable.com/v0\"\n",
    "headers = {\"Authorization\": f\"Bearer {TOKEN}\"}\n",
    "endpoint = f\"{airtable_base_url}/{BASE_ID}/{TABLE_ID}\"\n",
    "view_name = \"Grid view\"\n",
    "\n",
    "# Fetch and process data\n",
    "records = fetch_airtable_data(view_name=view_name, endpoint=endpoint, headers=headers)\n",
    "df = airtable_to_dataframe(records)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "name": "python",
   "version": "3.12.0"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}
