import urllib.parse
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from PIL import Image
import os
import tkinter as tk
from tkinter import filedialog
from selenium import webdriver
from datetime import datetime
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
import streamlit as st
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from io import StringIO
from st_pages import add_page_title

add_page_title()
def url_encode(string):
    encoded_string = urllib.parse.quote_plus(string)
    return encoded_string

def delList(L):
    for i in L:
        if L.count(i) != 1:
            for x in range((L.count(i) - 1)):
                L.remove(i)
    return L

def get_strain_name(chrome_path,output_path):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'}
    url ='https://www.leafly.com/dispensaries'
    s = Service('chromedriver.exe')
    option = webdriver.ChromeOptions()
    option.add_argument(r'--user-data-dir='+chrome_path)
    driver = webdriver.Chrome(service=s,options=option)
    driver.get(url)
    driver.implicitly_wait(900)

    # filter_icon = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id=listing-wrapper]/div[2]/div[3]/div/button")))
    filter_icon = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.flex.flex-row.border.bg-white.roundedtext-xs.text-green.font-bold.px-sm.m-xs.button--small.px-md.py-xs.border-light-grey.items-center")))
    filter_icon.click()
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    state=soup.find("div",{"class":"jsx-9336165732779550 font-bold lg:font-normal text-green lg:text-default underline lg:no-underline truncate"}).text
    strains=soup.find("div",{"id":"filter-strain-name"}).find("div",{"id":"accordionsection-strain-name"}).find_all('span')
    Strain=[]
    for strain in strains:
        if strain.text!='':
            Strain.append(strain.text)
    st.write('In',state,'There are following strains:')       
    st.write(Strain)
    Strains=[]
    for strain in Strain:
        if type(strain)==float:
            strain='N/A'
        encoded_string = url_encode(strain)
        Strains.append(encoded_string)
    st.session_state['strain_info']=Strain
    time.sleep(2)

    baseurl ='https://www.leafly.com/dispensaries?strain='
    for i in range(len(Strains)):
        with st.spinner("Scraping dispensaies in: %s" % Strain[i]):
            Name=[]
            url=baseurl+Strains[i]
            
            driver.get(url)
            driver.implicitly_wait(900)
            time.sleep(1)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            result=soup.find("div",{"class":"flex flex-row items-center justify-between my-sm"}).find("div",{"class":"text-xs"})
            if (result.text!='0 results'):
                if (result.text=='Loading results'):
                    time.sleep(5)
                    driver.get(url)
                    driver.implicitly_wait(900)
                    time.sleep(2)
                    soup = BeautifulSoup(driver.page_source, "html.parser")
                    result=soup.find("div",{"class":"flex flex-row items-center justify-between my-sm"}).find("div",{"class":"text-xs"})
                try:
                    # pages=soup.find("div",{"class":"flex gap-2"}).find_all("button",{"class":"rounded-sm h-full underline text-green"})
                    pages=soup.find("div",{"class":"flex gap-2"}).find_all("a",{"class":"rounded-sm h-10 flex items-center justify-center underline text-green"})
                    page=pages[-1].text
                except:
                    page='1'
                cards=soup.find_all("div",{"flex flex-col items-start justify-between relative h-full w-full rounded overflow-hidden bg-white elevation-low p-lg border border-light-grey my-sm shadow-none"})
                for item in cards:
                    try:
                        store=item.find("div",{"class":"font-bold truncate-lines truncate-2-lines w-60"}).text
                    except:
                        store=item.find("div",{"class":"font-bold truncate-lines w-60"}).text
                    Name.append(store)
                time.sleep(1)
                if eval(page)>1:
                    for j in range(2,eval(page)+1):
                        pageurl='https://www.leafly.com/dispensaries?page='+str(j)+'&strain='+Strains[i]
                        driver.get(pageurl)
                        driver.implicitly_wait(900)
                        time.sleep(1)
                        soup = BeautifulSoup(driver.page_source, "html.parser")
                        cards=soup.find_all("div",{"flex flex-col items-start justify-between relative h-full w-full rounded overflow-hidden bg-white elevation-low p-lg border border-light-grey my-sm shadow-none"})
                        for item in cards:
                            try:
                                store=item.find("div",{"class":"font-bold truncate-lines truncate-2-lines w-60"}).text
                            except:
                                store=item.find("div",{"class":"font-bold truncate-lines w-60"}).text
                            # print(store)
                            Name.append(store)
                        time.sleep(1)
                Name=delList(Name)
            
            currentDateAndTime = datetime.now()
            currentTime = currentDateAndTime.strftime("%Y.%m.%d")
            Time=[currentTime]*len(Name)
            if (type(Strain[i])!=float):
                file_name = re.sub(r'[\\/:*?"<>|]', '_', Strain[i]) + '.csv'
            else:
                file_name='N_A.csv'
            output_path2=output_path+'Strains in '+state+'/'
            if not os.path.exists(output_path2):
                os.mkdir(output_path2)
            df = pd.DataFrame({'Dispensary':Name,'ScrapeTime':Time})
            df.index.name = 'Index'
            df.to_csv(output_path2+file_name,encoding='utf-8-sig')
            st.session_state['dirpath2'] = output_path2
            # st.success("Finish scraping dispensaies in: %s :sparkler:" % Strain[i])
            time.sleep(1)

    driver.close()


# Initialize session state variables
if 'chromepath' not in st.session_state:
    st.session_state['chromepath'] = None
if 'dirpath' not in st.session_state:
    st.session_state['dirpath'] = None
if 'dirpath2' not in st.session_state:
    st.session_state['dirpath2'] = None
if 'path_state' not in st.session_state:
    st.session_state['path_state'] = None
if 'strain_state' not in st.session_state:
    st.session_state['strain_state'] = None
if 'strain_info' not in st.session_state:
    st.session_state['strain_info'] = None
if 'df_origin' not in st.session_state:
    st.session_state['df_origin'] = None
if 'dispensary' not in st.session_state:
    st.session_state['dispensary'] = None
if 'csv_name' not in st.session_state:
    st.session_state['csv_name'] = None
if 'progress' not in st.session_state:
    st.session_state['progress'] = None

loc_image = Image.open('./Screenshot/change location.png')
st.image(loc_image, caption='Change the State you want to scrape here(at the upper right corner of the website)',use_column_width ="auto")
st.divider()
# Set up tkinter
root = tk.Tk()
root.withdraw()
# Make folder picker dialog appear on top of other windows
root.wm_attributes('-topmost', 1)

profile_on = st.checkbox('Save Profile Path of Chrome before:question:',value=True)
if not profile_on:
    st.write('Your profile Chrome path is:')
    clicked = st.button('Chrome Picker')
    if clicked:
        select_dirpath=filedialog.askdirectory(master=root)
        st.session_state['chromepath'] = select_dirpath
        st.text_input('Selected folder:', select_dirpath)  
        st.download_button('Download it for future use', select_dirpath)
else:
    profile_file = st.file_uploader("Choose your file that save profile Chrome path")
    if profile_file is not None:
        # To convert to a string based IO:
        stringio = StringIO(profile_file.getvalue().decode("utf-8"))
        # To read file as string:
        string_data = stringio.read()
        st.write('Your profile Chrome path is:',string_data)
        st.session_state['chromepath'] = string_data


    
st.divider()

if st.session_state['chromepath'] is not None:
    # Folder picker button
    st.header('Choose the output folder you want')
    st.write('Please select a folder:')
    clicked2 = st.button('Folder Picker')
    if clicked2:
        select_path=filedialog.askdirectory(master=root)
        st.session_state['dirpath'] = select_path
        st.text_input('Selected folder:', select_path)  

if st.session_state['dirpath'] is not None:
    st.divider()
    if st.button('Scrape Strain Information'):
        chrome_path = st.session_state['chromepath']
        output_path = st.session_state['dirpath'] + '/'
        
        st.write('Your profile Chrome path is:',chrome_path)
        st.write('Your output path is:',output_path)
        get_strain_name(chrome_path,output_path)
        st.write('Finish scraping strains')
        st.session_state['path_state']=1
    st.divider()

if st.session_state['path_state'] is not None:
    uploaded_file = st.file_uploader("Upload the file you scrape in the first step page")
    if uploaded_file is not None:
        st.session_state['csv_name'] =uploaded_file.name
        if uploaded_file.name.endswith("csv"):
        # Can be used wherever a "file-like" object is accepted:
            df = pd.read_csv(uploaded_file)
            st.write(df)
            try:
                Dispensaries=df['Name'].tolist()
                st.session_state['strain_state'] =1
            except:
                Dispensaries='No Name column in this file, please ensure you upload the correct file'
                st.write(Dispensaries)
                st.session_state['strain_state'] =0
        elif uploaded_file.name.endswith("xlsx"):
            df = pd.read_excel(uploaded_file)
            st.write(df)
            try:
                Dispensaries=df['Name'].tolist()
                st.session_state['strain_state'] =1
            except:
                Dispensaries='No Name column in this file, please ensure you upload the correct file'
                st.write(Dispensaries)
                st.session_state['strain_state'] =0
        st.session_state['df_origin']=df
        st.session_state['dispensary']=Dispensaries
        

if st.session_state['strain_state'] is not None:
    st.divider()
    if st.button('Add strain column for this file'):
        strain_files = []
        output_path = st.session_state['dirpath2']
        temp=os.listdir(output_path)
        for item in temp:
            path=output_path+item
            strain_files.append(path)
        All_info=[]
        for j in range(len(strain_files)):
            df_strain = pd.read_csv(strain_files[j])
            Filter=df_strain['Dispensary'].tolist()
            temp=[]
            for item in Filter:
                temp.append(item.rstrip())
            All_info.append(temp)
        has_strain=[]
        strain_list=st.session_state['strain_info'] 
        st.session_state['progress'] = 0
        progress_bar = st.progress(st.session_state['progress'])
        for i in range(len(st.session_state['dispensary'])):
            temp_strain=[]
            for j in range(len(All_info)):
                if (st.session_state['dispensary'][i] in All_info[j])or(st.session_state['dispensary'][i].rstrip() in All_info[j]):
                    temp_strain.append(strain_list[j])
            has_strain.append(temp_strain)

            st.session_state['progress'] = (i + 1) / len(st.session_state['dispensary'])
            progress_bar.progress(st.session_state['progress'])


        has_strain_str = [', '.join(str(item) for item in strain_list) for strain_list in has_strain]
        df_origin=st.session_state['df_origin']
        df_origin['Has_Strain'] = has_strain_str
        # df_origin.index.name = 'Index'
        output_path = st.session_state['dirpath']+ '/'
        df_origin.to_csv(output_path+st.session_state['csv_name'][:-5]+'(With strain name).csv',encoding='utf-8-sig')
        st.success("Successfully add the strain column!:sparkler:")
        st.balloons()