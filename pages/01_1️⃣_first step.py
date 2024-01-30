import streamlit as st
import urllib.parse
import pandas as pd
import tkinter as tk
from tkinter import filedialog
import requests
from bs4 import BeautifulSoup
import time
import re
import os
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from datetime import datetime
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
from io import StringIO
from st_pages import add_page_title

add_page_title()

def delList(L):
    for i in L:
        if L.count(i) != 1:
            for x in range((L.count(i) - 1)):
                L.remove(i)
    for i in L:
        if ',' in i:
            L.remove(i)
    return L

def leafly_store(chrome_path,output_path):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'}
    baseurl ='https://www.leafly.com/dispensaries'
    s = Service('chromedriver.exe')
    option = webdriver.ChromeOptions()
    # option.add_argument(r'--user-data-dir=C:\Users\40425\AppData\Local\Google\Chrome\User Data')
    option.add_argument(r'--user-data-dir='+chrome_path)
    driver = webdriver.Chrome(service=s,options=option)
    driver.maximize_window()

    Name=[];Distance=[];Category=[];Rating=[];Reviewnum=[];Opentime=[];Pick_delivery=[];Link=[];Location=[];Has_deals=[];Total_product=[];Status=[]
    driver.get(baseurl)
    driver.implicitly_wait(900)
    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    
    pages=soup.find("div",{"class":"flex gap-2"}).find_all("a",{"class":"rounded-sm h-10 flex items-center justify-center underline text-green"})
   
    # pages=soup.find("div",{"class":"flex gap-2"}).find_all("button",{"class":"rounded-sm h-full underline text-green"})
    page=pages[-1].text
    state=soup.find("div",{"class":"jsx-9336165732779550 font-bold lg:font-normal text-green lg:text-default underline lg:no-underline truncate"}).text
    # print('have:',page,'pages')
    # print(state)
    for i in range(1,eval(page)+1):
            pageurl='https://www.leafly.com/dispensaries?page='+str(i)
            driver.get(pageurl)
            driver.implicitly_wait(1200)
            
            time.sleep(3)
            
            # action = ActionChains(driver)
            # try:
            #     scroll= WebDriverWait(driver, 10).until(
            #         EC.presence_of_element_located((By.CSS_SELECTOR, "div.flex.flex-shrink-0.relative.mr-lg.header__menu"))
            #     )
            #     action.move_to_element_with_offset(scroll, -93, 234).click().move_by_offset(0, 500).click().perform()
            #     for _ in range(20):
            #         action.move_by_offset(0, 20).click().perform()

            # except Exception as e:
            #     st.write("Reached the end of the scrollable area or element is out of bounds.")
                

            soup = BeautifulSoup(driver.page_source, "html.parser")
            
            cards=soup.find_all("div",{"flex flex-col items-start justify-between relative h-full w-full rounded overflow-hidden bg-white elevation-low p-lg border border-light-grey my-sm shadow-none"})
            for item in cards:
                try:
                    store=item.find("div",{"class":"font-bold truncate-lines truncate-2-lines w-60"}).text
                except:
                    store=item.find("div",{"class":"font-bold truncate-lines w-60"}).text
                Name.append(store)
                try:
                    distance=item.find("div",{"class":"overflow-hidden mt-xs"}).find("div",{"class":"flex-shrink-0 text-xs"}).text
                except:
                    distance=''
                Distance.append(distance)

                category_temp=[]
                try:
                    category=item.find("div",{"class":"flex flex-col absolute top-0 right-0"}).find("div",{"class":"text-xs font-bold bg-white border border-light-grey rounded px-xs m-sm"}).text
                except:
                    try:
                        category=item.find("div",{"class":"flex flex-col absolute top-0 right-0"}).find("div",{"class":"text-xs font-bold bg-white border border-light-grey rounded px-xs"}).text
                    except:
                        category=''
                category_temp.append(category)   
                Category.append(category_temp)

                try:
                    rating=item.find("div",{"class":"text-xs mt-xs"}).find("span",{"class":"pr-xs"}).text
                except:
                    rating=''
                Rating.append(rating)
                try:
                    reviewnum=item.find("div",{"class":"text-xs mt-xs"}).find("span",{"class":"underline"}).text
                except:
                    reviewnum=''
                Reviewnum.append(reviewnum)
                try:
                    optentime=item.find("div",{"class":"overflow-hidden mt-xs"}).find("div",{"class":"jsx-24d45b056a4a1aa9 flex"}).text
                except:
                    optentime=''
                Opentime.append(optentime)

                pick_delivery=[]
                try:
                    delivery_infos=item.find("div",{"class":"flex flex-wrap"}).find_all("span")
                    for type in delivery_infos:
                        if type.text!='Loading...':
                            temp=type.text.replace('\xa0',' ')
                            pick_delivery.append(temp)
                except:
                    delivery_infos=[]
                Pick_delivery.append(pick_delivery)

                try:
                    infolink=item.find("div",{"class":"w-full"}).find("a",{"class":""}).get('href')
                    link='https://www.leafly.com/'+infolink
                except:
                    link=''
                Link.append(link)
                status='N'
                Status.append(status)
                time.sleep(2)

    
    for j in range(len(Link)):
        menulink=Link[j]+'/menu'
        try:
            driver.get(Link[j])
            time.sleep(1)
            driver.implicitly_wait(900)
            soup = BeautifulSoup(driver.page_source, "html.parser")
        except:
            time.sleep(300)
            driver.get(Link[j])
            time.sleep(1)
            driver.implicitly_wait(900)
            soup = BeautifulSoup(driver.page_source, "html.parser")
        try:
            location=soup.find("div",{"class":"text-sm mb-sm"}).text
        except:
            location=''
        Location.append(location)
        
        time.sleep(1.5)
        try:
            driver.get(menulink)
            time.sleep(1.5)
            driver.implicitly_wait(900)
            soup = BeautifulSoup(driver.page_source, "html.parser")
        except:
            time.sleep(300)
            driver.get(menulink)
            time.sleep(1.5)
            driver.implicitly_wait(900)
            soup = BeautifulSoup(driver.page_source, "html.parser")
        try:
            total_product=soup.find("div",{"class":"flex-shrink-0 font-bold mr-xxl"}).text
        except:
            total_product=''
        Total_product.append(total_product)

        try:
            pickup=soup.find("div",{"data-testid":"dispensary-header-fulfillment"}).text.replace('\xa0',' ')
        except:
            pickup=''
        Pick_delivery[j].append(pickup)
        Pick_delivery[j]=delList(Pick_delivery[j])
        Pick_delivery[j] = [item for item in Pick_delivery[j] if item != '']
       

        try:
            labels=soup.find_all("div",{"class":"uppercase text-xs font-bold border border-light-grey rounded px-sm"})
            for label in labels:
                label_info=label.text
                Category[j].append(label_info)
                
        except:
            label_info=''
        
        Category[j]=delList(Category[j])
        Category[j] = [item for item in Category[j] if item != '']


        try:
            weed_deals=[]
            deals=soup.find_all("div",{"class":"jsx-4e8d3358a540eece p-lg flex justify-between flex-col h-full"})   
            for deal in deals:
                temp1=deal.find("div",{"class":"jsx-4e8d3358a540eece bg-notification rounded text-xs text-white font-bold"}).text
                temp2=deal.find("div",{"class":"jsx-4e8d3358a540eece font-bold mb-sm"}).text
                temp3=deal.find("div",{"class":"jsx-4e8d3358a540eece text-grey text-xs mb-xs"}).text
                final=temp1+','+temp2+','+temp3
                weed_deals.append(final)
                
        except:
            weed_deals=''
        
        Has_deals.append(weed_deals)
        
        time.sleep(1)

    currentDateAndTime = datetime.now()
    currentTime = currentDateAndTime.strftime("%Y.%m.%d")
    driver.close()
    driver.quit()   

    df = pd.DataFrame({
        'Name':Name, 'Distance':Distance,'Category':Category,'Rating':Rating,'Reviewnum':Reviewnum, 'Open time':Opentime,'Pickup or delivery':Pick_delivery,'Link':Link,'Location':Location,'Has deals':Has_deals,'Total product':Total_product,'Finish_scraping':Status})
    df.index.name = 'Index'
    df.to_csv(output_path+state+' '+currentTime+'.csv',encoding='utf-8-sig')

st.header(':blue[Fisrt step:]change the location you want to scrape ')
# link = '[Go the the leafly website](http://leafly.com)'
# st.markdown(link, unsafe_allow_html=True)

loc_image = Image.open('./Screenshot/change location.png')
st.image(loc_image, caption='Change the State you want to scrape here(at the upper right corner of the website)')

st.divider()
st.header(':blue[Second step:]click button to open a chrome window to beign scrapping ')
st.subheader(':blue[Make sure you choose other browser to run this script(like edge) and entirely close all the Chrome windows:sunglasses:] ')
st.subheader("Because this fucntion need to use your profile Chrome, so you need to choose the 'User data' folder of your chrome ")
st.subheader("For example, my local path is C:\\Users\\40425\\AppData\\Local\\Google\\Chrome\\User Data, where 40425 is my username")

# Initialize session state variables
if 'chromepath' not in st.session_state:
    st.session_state['chromepath'] = None

if 'dirpath' not in st.session_state:
    st.session_state['dirpath'] = None
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

# Folder picker button
st.header(':blue[Second step:] choose the output folder you want')
st.write('Please select a folder:')
clicked2 = st.button('Folder Picker')
if clicked2:
    select_path=filedialog.askdirectory(master=root)
    st.session_state['dirpath'] = select_path
    st.text_input('Selected folder:', select_path) 

st.divider()
if st.button('Begin button'):
    chrome_path = st.session_state['chromepath']
    output_path = st.session_state['dirpath'] + '/'
    
    st.write('Your profile Chrome path is:',chrome_path)
    st.write('Your output path is:',output_path)
    leafly_store(chrome_path,output_path)
    st.write('Finish scraping')
st.divider()

