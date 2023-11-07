import streamlit as st
import urllib.parse
import pandas as pd
import tkinter as tk
from tkinter import filedialog
import requests
from bs4 import BeautifulSoup
import time
import re
import random
import csv
import os
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from datetime import datetime
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from socket import gethostbyname, gaierror
from PIL import Image
from st_pages import Page, Section, show_pages, add_page_title

st.set_page_config(
    page_title="Ex-stream-ly Cool App for scraping",
    page_icon="🧊",
    # layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        # 'Get Help': 'https://google.com',
        # 'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "This is an app used for scraping!"
        # 'About': "# This is a header. This is an *extremely* cool app!"
    }
)
add_page_title()

st.title('👋This script is a used for :blue[scrape the data] on the website of the :green[leafly]')
st.divider()
st.header('It contains two pages which correspponding to two steps')
st.divider()
st.subheader('The :red[first step page] is used for scrapping the information of all dispensaries within one state in a csv file')

local_image = Image.open('Screenshot/local dispensaries.png')
st.image(local_image)

csv_image = Image.open('Screenshot/Example info.png')
st.image(csv_image,caption='The scrapped data in the first step will look like this')
st.divider()

st.subheader("The :red[second step page] is used for scrapping the information of all dispensaries'products based on the link you scraped in the first step ")

st.divider()
st.header(':red[Some prerequisites:]')
st.subheader('Download the chromedriver.exe which match you Chrome version :red[in the same folder with this script] ')

link1 = '[Download chromedriver here:](https://chromedriver.chromium.org/downloads)'
st.markdown(link1, unsafe_allow_html=True)

st.subheader ('Check your version of Chrome by go to the following page:')
st.subheader(':red[chrome://version/]')

version_image = Image.open('Screenshot/version.png')
st.image(version_image,caption='For example, this Chrome version is 114')

# st.sidebar.markdown("# Introduction page 🎈")
with st.sidebar:
    st.success("Select a step above!")

# Specify what pages should be shown in the sidebar, and what their titles and icons
# should be
show_pages(
    [
        Page("hello.py", "Introduction", "🏠"),
        Section(name="Leafly", icon="🍀"),
        Page("pages/01_1️⃣_first step.py", icon="1️⃣", in_section=True),
        Page("pages/02_2️⃣_second step.py",icon="2️⃣", in_section=True),   
        Page("pages/03_➕_Add strain info.py",icon="➕", in_section=True),  
        Section(name="Scrape Images", icon="🖼️"),
        Page("pages/04_📷_Download images in one file.py",in_section=True),
        Page("pages/05_📸_Download images in multiple files.py", in_section=True), 
        Section(name="Weedmap", icon="🍁"),
        Page("pages/06_🍁_weedmap_1.py",'Scrape store info',icon="1️⃣",in_section=True), 
        Page("pages/07_🤖_chatbot.py",in_section=False), 
    
    ]
)
