# September-2023-Group-001
This is the Group 001 repository for the WaiPRACTICE September cohort.

## TED Talks NLP Recommender System

### Overview
This project aims to build a recommender system for TED Talks using Natural Language Processing (NLP). The system recommends TED Talks based on the content of the talks and the preferences of the user.

### Data Collection - TED Web Scraper
The data for this project is obtained using a custom-built web scraper (`TED_scraper` found in `DataCollection`). The scraper is built using the Python `requests` library and is designed to scrape data from the official TED Talks website. The scraped data includes details about each talk such as the title, speaker, transcript, and more.

### Data Storage
The raw data scraped from the website is stored in a MongoDB cluster. MongoDB was chosen for its ability to store large amounts of unstructured data, which is ideal for our web scraping needs. An user with read only access is provided to access the data.

## Data Transformation
A Jupyter notebook is used to flatten all JSON files from each talk. This transforms the data into a tabular format which is easier to work with for our NLP tasks. The transformed data includes one row for each talk and columns for each piece of information about the talk (see `Wrangling` notebook)
