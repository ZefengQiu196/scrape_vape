import streamlit as st
import pandas as pd
import os
import urllib.request
import shutil
import logging
import re
from datetime import datetime
import tkinter as tk
from tkinter import filedialog
from st_pages import add_page_title


# st.set_page_config(
#     page_title="Scrape images in muultiple files in a folder",
#     page_icon=":books:",
#     initial_sidebar_state="expanded", 
# )
add_page_title()
# http client configuration
user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/63.0.3239.84 Chrome/63.0.3239.84 Safari/537.36'

# logging configuration
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

# configure headers
opener = urllib.request.build_opener()
opener.addheaders = [('User-agent', user_agent)]
urllib.request.install_opener(opener)

def fix_url(url):
    url = urllib.parse.quote(url, safe="%/:=&?~#+!$,;'@()*[]")
    return url

def download_image(image_url, dest_dir, image_filename,img_index,log):
    image_filename = re.sub(r'[\<\>\:\"\/\\\|\?\*]', '_', image_filename)
    image_filename=re.sub('\u200b', '', image_filename)
    image_filename=re.sub('\t', '', image_filename)
    image_url = fix_url(image_url)
    try:
        if log==1:
            with st.status("Downloading image %s" % image_url, expanded=True) as status:
            # st.info("Downloading image %s" % image_url)
                tmp_file_name, headers = urllib.request.urlretrieve(image_url)
                content_type = headers.get("Content-Type")

                if content_type == 'image/jpeg' or content_type == 'image/jpg':
                    ext = 'jpg'
                elif content_type == 'image/png':
                    ext = 'png'
                elif content_type == 'image/gif':
                    ext = 'gif'
                elif content_type == 'image/webp':
                    ext = 'webp'
                else:
                    st.warning("unknown image content type:sweat: %s" % content_type)
                    return

                image_path = os.path.join(dest_dir, image_filename + "." + ext)
                shutil.move(tmp_file_name, image_path)
                st.write("The image of No.",img_index,'completed',':smile:')
        else:
                tmp_file_name, headers = urllib.request.urlretrieve(image_url)
                content_type = headers.get("Content-Type")
                if content_type == 'image/jpeg' or content_type == 'image/jpg':
                    ext = 'jpg'
                elif content_type == 'image/png':
                    ext = 'png'
                elif content_type == 'image/gif':
                    ext = 'gif'
                elif content_type == 'image/webp':
                    ext = 'webp'
                else:
                    st.warning("unknown image content type:sweat: %s" % content_type)
                    return
                image_path = os.path.join(dest_dir, image_filename + "." + ext)
                shutil.move(tmp_file_name, image_path)
                # st.write("The image of No.",img_index,'completed',':smile:')
    except Exception as e:
        st.warning("Image download error:cry:. %s" % e)

def get_csv_image_dir(pathname):
    if not os.path.exists(pathname):
        os.makedirs(pathname)
    return pathname


def download_csv_file_images(folder_path, df, storename,log):
    dest_dir = get_csv_image_dir(folder_path)
    for index, row in df.iterrows():
        image_url = row.get("Image")
        currentDateAndTime = datetime.now()
        currentTime = currentDateAndTime.strftime("%Y.%m.%d")
        if pd.notnull(image_url):
            image_filename = storename+'-'+str(row.get("Name"))+'-'+str(row.get("Index"))+'-'+str(currentTime)
            if pd.isnull(image_filename):
                image_filename = row.get("Index")

            download_image(image_url, dest_dir, str(image_filename),index,log)
            

def download_csv_file_images_progressbar(folder_path, df, storename,log):
    dest_dir = get_csv_image_dir(folder_path)
    total_images =len(df)
    for index, row in df.iterrows():
        image_url = row.get("Image")
        currentDateAndTime = datetime.now()
        currentTime = currentDateAndTime.strftime("%Y.%m.%d")
        if pd.notnull(image_url):
            image_filename = storename+'-'+str(row.get("Name"))+'-'+str(row.get("Index"))+'-'+str(currentTime)
            if pd.isnull(image_filename):
                image_filename = row.get("Index")

            download_image(image_url, dest_dir, str(image_filename),index,log)
            st.session_state['progress'] = (index + 1) / total_images
            progress_text = "The image of No."+str(index)+' completed'+':smile:'
            progress_bar.progress(st.session_state['progress'], text=progress_text)


# Initialize session state variables
if 'imgsfolder' not in st.session_state:
    st.session_state['imgsfolder'] = None
if 'tables' not in st.session_state:
    st.session_state['tables'] = None
if 'stores' not in st.session_state:
    st.session_state['stores'] = None
if 'fold_state' not in st.session_state:
    st.session_state['fold_state'] = None
if 'path_state' not in st.session_state:
    st.session_state['path_state'] = None
if 'savpath' not in st.session_state:
    st.session_state['savpath'] = None
if 'logs' not in st.session_state:
    st.session_state['logs'] = None
if 'progress' not in st.session_state:
    st.session_state['progress'] = None

# Set up tkinter
root = tk.Tk()
root.withdraw()
# Make folder picker dialog appear on top of other windows
root.wm_attributes('-topmost', 1)
st.write('Which folder you save tables of image links  :question:')
clicked = st.button('Choose the folder:open_file_folder:')

if clicked:
    select_dirpath=filedialog.askdirectory(master=root)
    st.session_state['imgsfolder'] = select_dirpath
    st.text_input('You Selected:file_folder::', select_dirpath)  

    download_files = []
    files=os.listdir(select_dirpath)
    for file in files:
        if file.endswith(".csv") or file.endswith(".xlsx"):
            download_files.append(file)
    st.write('Find these tables:white_check_mark::',download_files)   
    st.session_state['tables'] = download_files
    download = [] 
    for name in download_files:
    # Extract the date from the name using regular expressions
        date_match = re.search(r'\d{4}\.\d{2}\.\d{2}', name)
        if date_match:
            date = date_match.group()
            # Split the name by the date
            store_name = name.split(date)[0].strip('- ')
            # for char in store_name:
            #     if char == "_":
            #         for special_char in r'[\\/:*?"<>|]':
            #             tempstore_name = store_name.replace(char, special_char)
            #             download.append(tempstore_name)
            download.append(store_name)
    st.session_state['stores'] = download 
    st.session_state['fold_state'] = 1    
st.divider()




if st.session_state['fold_state'] is not None:
    st.write('Please select a folder for saving your images')
    clicked2 = st.button('Select a folder :open_file_folder:')  
    if clicked2:
        select_path=filedialog.askdirectory(master=root)
        st.session_state['savpath'] = select_path
        st.text_input('You Selected:', select_path+ '/') 
        st.session_state['path_state'] = 1
     
    

if st.session_state['path_state'] is not None:
    st.divider()    
    if st.button("Start Scraping with logs:page_with_curl:", type="primary"):
        for i in range(len(st.session_state.tables)):
            tab_path=st.session_state['imgsfolder']+'/'+st.session_state.tables[i] 
            storename=st.session_state['stores'][i]
            storename = re.sub(r'[\<\>\:\"\/\\\|\?\*]', '_', storename)
            if tab_path.endswith(".csv"):
                df = pd.read_csv(tab_path)
            else:
                df = pd.read_excel(tab_path)
            column_name='Name'
            folder_path=st.session_state['savpath']+ '/'+storename+'/'
            st.session_state['logs'] = 1
            with st.spinner("Downloading images in %s" % storename):
                download_csv_file_images(folder_path, df, storename,st.session_state['logs'])
            st.success("Images in %s downloaded successfully!:sparkler:" % storename)
    if st.button("Start Scraping with progress bar:hourglass_flowing_sand:", type="primary"):
        for i in range(len(st.session_state.tables)):
            tab_path=st.session_state['imgsfolder']+'/'+st.session_state.tables[i] 
            storename=st.session_state['stores'][i]
            storename = re.sub(r'[\<\>\:\"\/\\\|\?\*]', '_', storename)
            if tab_path.endswith(".csv"):
                df = pd.read_csv(tab_path)
            else:
                df = pd.read_excel(tab_path)
            column_name='Name'
            folder_path=st.session_state['savpath']+ '/'+storename+'/'
            st.write(folder_path)
            st.session_state['logs'] = 0
            with st.spinner("Downloading images in %s" % storename):
                st.session_state['progress'] = 0
                progress_bar = st.progress(st.session_state['progress'])
                download_csv_file_images_progressbar(folder_path, df, storename,st.session_state['logs'])
            st.success("Images in %s downloaded successfully!:sparkler:" % storename)