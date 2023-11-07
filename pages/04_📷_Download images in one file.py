import streamlit as st
import pandas as pd
import os
import urllib.request
import shutil
import logging
import re
import tkinter as tk
from PIL import Image
from tkinter import filedialog
from st_pages import add_page_title


# st.set_page_config(
#     page_title="Scrape images in a table file",
#     page_icon=":notebook_with_decorative_cover:",
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

def download_image(image_url, dest_dir, image_filename,img_index):
    image_filename = re.sub(r'[\<\>\:\"\/\\\|\?\*]', '_', image_filename)
    image_url = fix_url(image_url)
    try:
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
            st.session_state['display_img']=image_path
            st.session_state['display_name'] =image_filename
            # st.write("The image of No.",img_index,'completed',':smile:')
    except Exception as e:
        st.warning("Image download error:cry:. %s" % e)

    

def get_csv_image_dir(pathname):
    if not os.path.exists(pathname):
        os.makedirs(pathname)
    return pathname


def download_csv_file_images(folder_path, df, column_name):
    dest_dir = get_csv_image_dir(folder_path)
    total_images =len(df)
    
                
    for index, row in df.iterrows():
        image_url = row.get("Image")
        if pd.notnull(image_url):
            image_filename = row.get(column_name)
            if pd.isnull(image_filename):
                image_filename = row.get("Index")

            download_image(image_url, dest_dir, str(image_filename),index)
            st.write('You download:')
                
            image = Image.open(st.session_state['display_img'])
            image=image.resize((120,120))
            st.image(image,caption=st.session_state['display_name'])
            st.session_state['progress'] = (index + 1) / total_images
            progress_text = "The image of No."+str(index)+' completed'+':smile:'
            progress_bar.progress(st.session_state['progress'], text=progress_text)
                
    

    

 # Initialize session state variables
if 'imgpath' not in st.session_state:
    st.session_state['imgpath'] = None
if 'path_state' not in st.session_state:
    st.session_state['path_state'] = None    
if 'progress' not in st.session_state:
    st.session_state['progress'] = None
if 'display_img' not in st.session_state:
    st.session_state['display_img'] = None
if 'display_name' not in st.session_state:
    st.session_state['display_name'] = None


# Step 1: File uploader
uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx"])

if uploaded_file is not None:
    # Step 2: Display file content
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    st.write('You upload the following table:')
    if 'Image' in df.columns:
        # st.dataframe(
        #     df.style.applymap(
        #     lambda _: "background-color: pink;", subset=(["Image"])
        #     )
        # )
        st.data_editor(
            df,
            column_config={
                "Image": st.column_config.LinkColumn(
                    help="The URLs of product images",
                    max_chars=1000,
                )
            },
        )

        tran_col=tuple(df.columns)

        # Step 3: Column selection for image filenames
        column_name = st.selectbox("Choose a column for image filenames", tran_col,index=None,placeholder="Which column you want to choose?")
        st.write('You selected:', "'",column_name,"'",'Column')
        st.divider()

        # Step 4: Local folder path input
        # folder_path = st.text_input("Enter local folder path for saving images")
    
        # Set up tkinter
        root = tk.Tk()
        root.withdraw()
        # Make folder picker dialog appear on top of other windows
        root.wm_attributes('-topmost', 1)
        st.write('Please select a folder for saving your images')
        clicked = st.button('Select a folder :open_file_folder:')
        
        if clicked:
            select_dirpath=filedialog.askdirectory(master=root)
            st.session_state['imgpath'] = select_dirpath
            st.text_input('You Selected:', select_dirpath+ '/')  
            st.session_state['path_state'] = 1

        if st.session_state['path_state'] is not None:
        # Step 5: Start scraping button
            st.divider()
            if st.button("Start Scraping:sparkles:", type="primary"):
                folder_path = st.session_state['imgpath'] + '/'
                if not folder_path:
                    st.warning("Please enter a local folder path.")
                else:
                    with st.spinner("Downloading images in %s" % uploaded_file.name):
                        st.session_state['progress'] = 0
                        progress_bar = st.progress(st.session_state['progress'])
                        download_csv_file_images(folder_path, df, column_name)
                    st.success("Images downloaded successfully!:sparkler:")
                    st.balloons()

    else:
        st.dataframe(df)
        st.error('''
                No Image column in this table  
                Please upload another table	:pleading_face:
                ''', icon="🚨")






  

