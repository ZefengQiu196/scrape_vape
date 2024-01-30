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
from st_pages import add_page_title

add_page_title()


def leafly(Dispensary,output_path,dispensary_name):    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'}
    baseurl ='https://www.leafly.com'
    start = time.time()
    start_local=time.strftime('%Y-%m-%d %H:%M',time.localtime(time.time()))
    cstart = time.process_time()
    try:
        main = requests.get(Dispensary,headers=headers).text
        soup=BeautifulSoup(main,'html.parser')
        Store=dispensary_name
        # try:
        #     Store=soup.find("h1",{"class":"heading--s font-bold pr-xxl pb-xs"}).text
        # except:
        #     try:
        #         Store=soup.find("h1",{"class":"heading--m font-extrabold pr-xxl pb-xs pt-xs"}).text
        #     except:
        #         try:
        #             Store=soup.find("h1",{"class":"heading--m font-extrabold pr-xxl"}).text
        #         except:
        #             Store=dispensary_name
        
        st.write('Begin scrapping:',Store)
    except:
        st.write('main page,wait...')
        time.sleep(60)
        main = requests.get(Dispensary,headers=headers).text
        soup=BeautifulSoup(main,'html.parser')
        Store=dispensary_name
        # try:
        #     Store=soup.find("h1",{"class":"heading--s font-bold pr-xxl pb-xs"}).text
        # except:
        #     try:
        #         Store=soup.find("h1",{"class":"heading--m font-extrabold pr-xxl pb-xs pt-xs"}).text
        #     except:
        #         try:
        #             Store=soup.find("h1",{"class":"heading--m font-extrabold pr-xxl"}).text
        #         except:
        #             Store=dispensary_name

        st.write('Begin scrapping:',Store)
    categorylist = soup.find_all("li",{"class":"mx-sm flex-shrink-0"})

    Category_link=[]
    Categories=[]
    Link=[];Name=[];Label=[];Unit=[];Price=[];Feature=[];Brand=[];Image=[];Lineage=[];Description=[];Rating=[];
    Reviewnum=[];Alsolike=[];Similar=[];Strain=[];Orgprice=[];Discount=[];THC=[];CBD=[];Category=[];OtherAmount=[]
    for category in categorylist:
        category_link = category.find("a",{"class":"text-center"}).get('href')
        category_name = category.find("a",{"class":"text-center"}).get('data-testid').replace('-products-category','')
        Category_link.append(baseurl+category_link)
        Categories.append(category_name)
    st.write(Store,' ,have those categories:',Categories)  
    Category_page=[]    
    for i in range(len(Category_link)):
        try:
            menu=requests.get(Category_link[i],headers=headers).text
            soup=BeautifulSoup(menu,'html.parser')
            category_product=soup.find("div",{"class":"flex-shrink-0 font-bold mr-xxl"}).text
        except:
            st.write('wait for counting')
            time.sleep(60)
            menu=requests.get(Category_link[i],headers=headers).text
            soup=BeautifulSoup(menu,'html.parser')
            category_product=soup.find("div",{"class":"flex-shrink-0 font-bold mr-xxl"}).text
        try:
            totalpage=soup.find("div",{"class":"flex gap-2"}).find_all("a",{"class":"rounded-sm h-10 flex items-center justify-center underline text-green"})
            page=totalpage[-1].text
        except:
            page='1'
        Category_page.append(page)  
        st.write(Store,' ,category:',Categories[i],'have total: ',category_product,' .It have ',page,' pages')
        time.sleep(random.uniform(1, 1.5))
    st.write(Store,'Finish count page')   
    for j in range(len(Categories)):
        for x in range(1,eval(Category_page[j])+1):
            add='&page={}'.format(x)
            menu_link=Category_link[j]+add
            
            try:
                option = webdriver.ChromeOptions()
                option.add_argument('headless')
                driver = webdriver.Chrome(options=option)
                driver.implicitly_wait(120)
                driver.get(menu_link)
            except:
                st.write('Wait...')
                time.sleep(120)
                option = webdriver.ChromeOptions()
                option.add_argument('headless')
                driver = webdriver.Chrome(options=option)
                driver.implicitly_wait(90)
                driver.get(menu_link)

            soup = BeautifulSoup(driver.page_source, "html.parser")
            
            cards=soup.find_all("div",{"class":"col-1/2 lg:col-1/3 mb-md"})
            if len(cards)==0:
                cards=soup.select('div.relative.h-full.bg-white.elevation-low.rounded.p-lg, div.relative.h-full.bg-white.elevation-low.rounded.p-lg.pt-xl')

            st.write(Categories[j],'page:',x,'has cards:',len(cards))
            if len(cards)>0:
                for card in cards:
                    Category.append(Categories[j])
                    try:
                        card_link=card.find("a",{"class":"block h-full w-full"}).get('href')
                        link=baseurl+card_link
                    except:
                        try:
                            card_link=card.find("a",{"data-testid":"menu-item-card-link"}).get('href')
                            link=baseurl+card_link
                        except:
                            st.write('link error,the card is:',card)
                            link=''

                    try:
                        name=card.find("h3",{"class":"font-bold text-sm break-words underline mt-xs"}).text
                    except:
                        try:
                            name=card.find("h3",{"class":"font-bold text-sm break-words mt-xs"}).text
                        except:
                            try:
                                name=card.find("h3",{"class":"font-bold text-sm break-words mt-xs min-h-[48px]"}).text
                            except:
                                try:
                                    name=card.find("div",{"class":"font-bold text-sm break-words"}).text
                                except:
                                    name=''
                    try:
                        label=card.find("div",{"class":"text-secondary text-xs leading-none"}).text
                    except:
                        try:
                            label=card.find("div",{"class":"text-secondary text-xs"}).text
                        except:
                            label=''
                    try:
                        unit=card.find("div",{"class":"font-bold text-xs"}).text
                    except:
                        unit=''
                    try:
                        price=card.find("div",{"class":"font-bold text-lg"}).text
                    except:
                        try:
                            price=card.find("div",{"class":"font-bold text-lg text-notification"}).text
                        except:
                            try:
                                price=card.find("div",{"class":"font-bold text-lg min-h-[24px]"}).text
                            except:
                                try:
                                    price=card.find("div",{"class":"font-bold text-lg min-h-[24px] text-notification"}).text
                                except:
                                    price=''
                    try:
                        orgprice=card.find("div",{"class":"flex items-center text-xs mt-xs"}).find('span').text
                    except:
                        try:
                            orgprice=card.find("div",{"class":"flex items-center text-xs mt-xs min-h-[24px]"}).find('span').text
                        except:
                            try:
                                orgprice=card.find("div",{"class":"flex items-center text-xs gap-1"}).find('span').text
                            except:
                                orgprice=''
                    try:
                        discount=card.find("div",{"class":"flex items-center text-xs mt-xs"}).find("div",{"class":"bg-notification rounded text-white font-bold mr-sm"}).text
                    except:
                        try:
                            discount=card.find("div",{"class":"flex items-center text-xs mt-xs min-h-[24px]"}).find("div",{"class":"bg-notification rounded text-white font-bold mr-sm"}).text
                        except:
                            try:
                                discount=card.find("div",{"class":"flex items-center text-xs gap-1"}).find("div",{"class":"bg-notification rounded text-white font-bold mr-sm"}).text
                            except:
                                try:
                                    discount=card.find("div",{"class":"flex items-center text-xs gap-1"}).find("div",{"class":"bg-notification rounded text-white font-bold"}).text
                                except:
                                    discount=''
                    try:
                        brand=card.find("h4",{"class":"font-normal text-xs"}).text.replace('by ',"")
                    except:
                        try:
                            brand=card.find("div",{"class":"font-normal text-xs"}).text.replace('by ',"")
                        except:
                            brand=''
                    st.write(name,';',brand,';',orgprice,';',discount)
                    Link.append(link);Name.append(name);Label.append(label);Unit.append(unit);Price.append(price);Brand.append(brand)
                    Orgprice.append(orgprice);Discount.append(discount)
                    try:
                        specific= requests.get(link,headers=headers).text
                        soups=BeautifulSoup(specific,'html.parser')
                    except:
                        print('specific error, link for this:',link)
                        time.sleep(300)
                        specific= requests.get(link,headers=headers).text
                        soups=BeautifulSoup(specific,'html.parser')
                    try:
                        thc=soups.find("div",{"class":"inline-block px-sm py-xs rounded bg-deep-green-20 mr-md"}).text
                    except:
                        thc=''
                    try:
                        cbd=soups.find("div",{"class":"inline-block px-sm py-xs rounded bg-deep-green-20"}).text
                    except:
                        cbd=''    
                    try:
                        im=soups.find("source").get('data-srcset').replace(' 1x',"").replace(' 2x',"")
                        image=re.split(r", ",im)[-1]
                    except:
                        image=''
                    try:
                        lineage=soups.find("div",{"class":"inline-block px-sm py-xs rounded bg-leafly-white mr-md"}).text
                    except:
                        lineage=''
                    try:
                        rating=soups.find("div",{"class":"text-xs text-sm mb-md"}).find("span",{"class":"pr-xs"}).text
                    except:
                        rating=''
                    try:
                        reviewnum=soups.find("div",{"class":"text-xs text-sm mb-md"}).find("span",{"class":"pl-xs"}).text.replace('(',"").replace(')',"")       
                    except:
                        reviewnum=''
                    try:
                        description=soups.find("section",{"class":"jsx-bf312eca109b4ce8 description"}).text.replace('About this product',"") 
                    except:
                        description=''
                    try:
                        Like=soups.find("ul",{"class":"jsx-425042678 inline-flex lg:flex -mr-sm lg:mr-none transition-transform"})
                        relate=Like.find_all("li",{"class":"jsx-425042678 flex-shrink-0 carousel__card mr-md"})
                        tmp=[]
                        for r in relate:
                            alsolike=r.find("h3",{"class":"font-bold text-sm break-words underline mt-xs"}).text
                            tmp.append(alsolike)
                    except:
                        try:
                            Like=soups.find("ul",{"class":"jsx-1462095365 inline-flex lg:flex -mr-sm lg:mr-none transition-transform carousel-list"})
                            relate=Like.find_all("li",{"class":"jsx-1462095365 flex-shrink-0 carousel__card mr-md snap-start"})
                            tmp=[]
                            for r in relate:
                                try:
                                    alsolike=r.find("h3",{"class":"font-bold text-sm break-words mt-xs"}).text
                                except:
                                    alsolike=r.find("h3",{"class":"font-bold text-sm break-words mt-xs min-h-[48px]"}).text
                                tmp.append(alsolike)
                        except:
                            tmp=''
                    Alsolike.append(tmp);THC.append(thc);CBD.append(cbd)
                    Image.append(image);Lineage.append(lineage);Description.append(description);Rating.append(rating);Reviewnum.append(reviewnum)

                    option = webdriver.ChromeOptions()
                    option.add_argument('--headless=new')
                    option.add_argument('--log-level=1')
                    option.add_argument('--log-level=2')
                    option.add_experimental_option('excludeSwitches', ['enable-logging'])
                    driver = webdriver.Chrome(options=option)
                    driver.implicitly_wait(60)
                    try:
                        driver.get(link)
                        time.sleep(1)
                        element = BeautifulSoup(driver.page_source, "html.parser")
                    except gaierror:
                        st.write('gaierror:',link)
                        st.write("wait...")
                        time.sleep(180)
                        option = webdriver.ChromeOptions()
                        option.add_argument('--headless=new')
                        option.add_argument('--log-level=1')
                        option.add_argument('--log-level=2')
                        option.add_experimental_option('excludeSwitches', ['enable-logging'])
                        driver = webdriver.Chrome(options=option)
                        driver.implicitly_wait(30)
                        driver.get(link)
                        element = BeautifulSoup(driver.page_source, "html.parser")
                    except WebDriverException:
                        st.write('WebDriverException:',link)
                        st.write("wait...")
                        time.sleep(180)
                        option = webdriver.ChromeOptions()
                        option.add_argument('--headless=new')
                        option.add_argument('--log-level=1')
                        option.add_argument('--log-level=2')
                        option.add_experimental_option('excludeSwitches', ['enable-logging'])
                        driver = webdriver.Chrome(options=option)
                        driver.implicitly_wait(30)
                        driver.get(link)
                        element = BeautifulSoup(driver.page_source, "html.parser")
                    try:
                        amount=element.find_all("div",{"class":"flex-grow-0 col-auto md:col-1/2 lg:col-1/3 mb-sm"})
                        temp=[]
                        if len(amount)>1: 
                            for other in amount[1:]:
                                others=other.find("div",{"data-testid":"variant-select__card"}).get('aria-label').replace('Select ','')
                                temp.append(others)
                            OtherAmount.append(temp)       
                        else:
                            OtherAmount.append(temp)
                    except:
                        OtherAmount.append([])

                    try:
                        strain=element.find("div",{"class":"flex flex-col gap-md flex-none"}).find("div",{"class":"flex flex-col gap-sm"}).find("a",{"class":"heading--l mb-xs"}).text
                    except:
                        try:
                            strain=element.find("div",{"class":"expandable-container"}).text 
                        except:
                            strain=''
                    Strain.append(strain)
                    
                    try:
                        similar = element.find_all("div",{"class":"jsx-d8321ff0acf99c10 underline overflow-hidden"})
                        if len(similar)==0:
                            similar = element.find_all("div",{"class":"jsx-61ab12a85e76008 underline overflow-hidden"})
                        temp=[]
                        for item in similar:
                            temp.append(item.text)
                    except:
                        temp=[]
                    Similar.append(temp)
                    driver.close()
                    driver.quit()
                    time.sleep(random.uniform(1, 2))


            time.sleep(random.uniform(1, 2))
        print(Store,':',Categories[j],'done')
        time.sleep(2)
    currentDateAndTime = datetime.now()
    currentTime = currentDateAndTime.strftime("%Y.%m.%d")
    Time=[currentTime]*len(Name)
    
    storename=Store.replace('\u200b', '').replace('\t', '')
    storename=re.sub(r'[\\/:*?"<>|]', '_', storename)

    print(Store,'have total:',len(Name),'products')
    df = pd.DataFrame({
    'Link':Link, 'Name':Name,'Label':Label,'Category':Category,'Brand':Brand, 'Image':Image,'Unit':Unit,'Price':Price,'OrginalPrice':Orgprice,'Discount':Discount,'OtherAmount':OtherAmount,'THC':THC,'CBD':CBD, 
    'Lineage':Lineage,'Description':Description,'Rating':Rating,'Reviewnum':Reviewnum,'Alsolike':Alsolike,'Similar':Similar,'Strain':Strain,'ScrapeTime':Time,'Store name':storename})
    df.index.name = 'Index'
    df.to_csv(output_path+storename+' '+currentTime+'.csv',encoding='utf-8-sig')

    st.write('Begin saving HTMLs in:',storename)
    output_html=output_path+'saved_HTML/'+storename+'/'
    if not os.path.exists(output_html):
        os.makedirs(output_html, exist_ok=True)
    for i in range(len(Link)):
        trans_Name=re.sub('\u200b', '', Name[i])
        trans_Name=re.sub('\t', '', trans_Name)
        trans_Name=re.sub('\n', '', trans_Name)
        trans_Name=re.sub(r'[\\/:*?"<>|]', '_', trans_Name)
        output_filename=output_html+trans_Name+'.html'
        save_url_as_html(Link[i], output_filename)
    st.write('Finish scrapping:',storename)

def save_url_as_html(url, filename, max_retries=5, retry_delay=15):
    try:
        retry_count = 0

        while retry_count < max_retries:
            response = requests.get(url)
            
            if response.status_code == 429:
                st.write("Received 429: Too Many Requests. Retrying after delay...")
                retry_count += 1
                time.sleep(retry_delay)
                continue

            response.raise_for_status()  # Check if the request was successful

            folder_path = os.path.dirname(filename)
            if folder_path:
                os.makedirs(folder_path, exist_ok=True)

            with open(filename, 'wb') as file:
                file.write(response.content)

            # st.write(f"URL has been saved as an HTML file: {filename}")
            break  # Break out of the retry loop if successful

    except requests.RequestException as e:
        st.write(f"Error occurred while saving: {e}")
    time.sleep(3)


# st.title('Test page for scraping tools based on streamlit')
# st.divider()


st.header(':blue[First step:] upload the table')
uploaded_file = st.file_uploader("Upload the file you scrape in the first step page")
if uploaded_file is not None:
    # st.write("filename:", uploaded_file.name)
    if uploaded_file.name.endswith("csv"):
    # Can be used wherever a "file-like" object is accepted:
        df = pd.read_csv(uploaded_file)
        st.write(df)
        try:
            if 'Link' in df.columns:
                Dispensary_list=df['Link'].tolist()
            else:
                Dispensary_list = df['Store link-href'].tolist()
            Name=df['Name'].tolist()
            Status=df['Finish_scraping'].tolist()
        except:
            Dispensary_list='No Store link column in this file, please ensure you upload the correct file'
    elif uploaded_file.name.endswith("xlsx"):
        df = pd.read_excel(uploaded_file)
        st.write(df)
        try:
            if 'Link' in df.columns:
                Dispensary_list=df['Link'].tolist()
            else:
                Dispensary_list = df['Store link-href'].tolist()
            Name=df['Name'].tolist()
            Status=df['Finish_scraping'].tolist()
        except:
            Dispensary_list='No Store link column in this file, please ensure you upload the correct file'

    
st.divider()
# Set up tkinter
root = tk.Tk()
root.withdraw()


# Make folder picker dialog appear on top of other windows
root.wm_attributes('-topmost', 1)

if uploaded_file is not None:
    st.write('Select the folder that you save this table for updating scraping status:')
    choose_table = st.button('Table folder')
    if choose_table:  
        select_tablepath=filedialog.askdirectory(master=root)
        st.session_state['table_path'] = select_tablepath
        st.session_state['table_fullpath']=st.session_state['table_path']+'/'+uploaded_file.name
        st.write('Your local table path is:',st.session_state['table_fullpath'])
    



# Folder picker button
st.header(':blue[Second step:] choose the output folder you want')
st.write('Please select a folder:')
clicked = st.button('Folder Picker')
if clicked:
    select_path=filedialog.askdirectory(master=root)
    dirname = st.text_input('Selected folder:', select_path, key="dirpath")    
    output_path=select_path+'/'

    download=[]
    st.session_state['Status_yes']=0
    for i in range(len(Dispensary_list)):
        if Status[i]=='Y':
            download.append(Name[i])
            st.session_state['Status_yes']+=1
    downloaded = st.text_input('These stores have scraped:', download, key="downloaded") 
    
   
       
    
st.divider()
st.header(':blue[Third step:] click the button')
if st.button('Click me to begin'):
    output_path=st.session_state.dirpath+'/'
    st.session_state['progress'] = st.session_state['Status_yes']/len(Dispensary_list)
    progress_text = str(st.session_state['Status_yes'])+' Dispensaries finished scraping'+':smile:'+'. There are total '+str(len(Dispensary_list))+' Dispensaries'
    progress_bar = st.progress(st.session_state['progress'], text=progress_text)
    
    for i in range(len(Dispensary_list)):
        
        if Name[i] not in st.session_state.downloaded:
            dispensary_name=Name[i]
            try:
                leafly(Dispensary_list[i],output_path,dispensary_name)


                df.at[i, 'Finish_scraping'] = 'Y'
                if uploaded_file is not None:
                    if uploaded_file.name.endswith("csv"):
                        df.to_csv(st.session_state['table_fullpath'],encoding='utf-8-sig', index=False) 
                    elif uploaded_file.name.endswith("xlsx"):
                        df.to_excel(st.session_state['table_fullpath'],encoding='utf-8-sig', index=False)
                st.session_state['Status_yes']+=1        
                st.session_state['progress'] = st.session_state['Status_yes']/len(Dispensary_list)
                progress_text = str(st.session_state['Status_yes'])+' Dispensaries finished scraping'+':smile:'+'. There are total '+str(len(Dispensary_list))+' Dispensaries'
                progress_bar.progress(st.session_state['progress'], text=progress_text)


            except AttributeError as e:
                st.write('Something wrong,repeat step 2 and 3')
                break