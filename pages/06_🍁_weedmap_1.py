import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import json
import csv
import os
from tqdm import tqdm
from selenium import webdriver
from datetime import datetime
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import streamlit as st
from collections import Counter
from st_pages import add_page_title

add_page_title()
def place_scrape():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'}
    baseurl='https://weedmaps.com/dispensaries/in/united-states'
    main = requests.get(baseurl,headers=headers).text
    soup=BeautifulSoup(main,'html.parser')
    try:
        states=soup.find_all("a",{"class":"RegionLink-sc-5ee853d5-2 jDlsHT"})
    except:
        states=''
    State_link=[]
    State_name=[]
    for state in states:
        state_link=state.get('href')
        State_link.append(state_link)
        state_name=state.text
        State_name.append(state_name)
    return State_name,State_link

def place2_scrape(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'}
    baseurl='https://weedmaps.com/'+url
    main = requests.get(baseurl,headers=headers).text
    soup=BeautifulSoup(main,'html.parser')
    try:
        subregions=soup.find_all("a",{"class":"RegionLink-sc-5ee853d5-2 jDlsHT"})
    except:
        subregions=''
    Region_link=[]
    Region_name=[]
    for subregion in subregions:
        region_link=subregion.get('href')
        Region_link.append(region_link)
        region_name=subregion.text
        Region_name.append(region_name)
    return Region_name,Region_link    

def Area_dispensary(url):
    Store=[];Region=[];Link=[];Rating=[];Reviewnum=[];Category=[];Delliveries=[];Promotion=[]
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'}
    region_url='https://weedmaps.com'+url
    main = requests.get(region_url,headers=headers).text
    soup=BeautifulSoup(main,'html.parser')
    st.session_state['progress'] = 0
    progress_bar = st.progress(st.session_state['progress'])
    try:
        region=soup.find("span",{"class":"Text-sc-51fcf911-0 Secondary-sc-c32fcfbf-1 cfwChl ffEptK"}).text
    except:
        time.sleep(1)
        region=soup.find("span",{"class":"Text-sc-51fcf911-0 Secondary-sc-c32fcfbf-1 cfwChl ffEptK"}).text
    # st.write(region)
    try:
        pages=soup.find("a",{"class":"pagination-styles__PaginationButton-sc-1k8dxuw-2 iWtaBX"}).text
        page = pages.split()[-1]
    except:
        pages=soup.find("a",{"class":"PaginationButton-sc-f3af86c4-2 gSkqUh"}).text
        page = pages.split()[-1]
    # st.write(page,' pages')

    stores_list=soup.find_all("div",{"class":"Card-sc-f49b1e31-1 kezPaw"})
    for store in stores_list:
        try:
            name=store.find("div",{"class":"Text-sc-51fcf911-0 Title-sc-f49b1e31-5 dQtSPx ipKkKY"}).text
        except:
            name=''
        Store.append(name)
        try:
            store_link=store.find('a')['href']
        except:
            store_link=''
        Link.append(store_link)
        Region.append(region)
        try:
            rating=store.find("div",{"class":"Text-sc-51fcf911-0 RatingValue-sc-beddb37b-1 kBrurT kqtLEy"}).text
        except:
            rating=''
        Rating.append(rating)
        try:
            review_num=store.find("div",{"class":"Text-sc-51fcf911-0 Count-sc-beddb37b-2 kBrurT jtacXy"}).text
        except:
            review_num=''
        Reviewnum.append(review_num)
        try:
            category=store.find("span",{"class":"Text-sc-51fcf911-0 Helper-sc-f49b1e31-7 qBJOa iHMRmY"}).text
        except:
            category=''
        Category.append(category)
        try:
            Delivery=[]
            delivery=store.find_all("span",{"class":"Chip-sc-5f639846-9 cvaOiC"})
            for item in delivery:
                if item.text!='Closed' and item.text!='Open now':
                    Delivery.append(item.text)
        except:
            Delivery=[]
        Delliveries.append(Delivery)
        try:
            Discount=[]
            discount_label=store.find("div",{"class":"src__Box-sc-1sbtrzs-0 src__Flex-sc-1sbtrzs-1 DealTagsDesktopContainer-sc-5f639846-16 hNEOfd eqdOIn kHzFGe"})
            discount=discount_label.text
            discount_link=store.find('a')['href']
            Discount.append(discount)
            Discount.append(discount_link)
        except:
            Discount=[]
        Promotion.append(Delivery)
    st.session_state['progress'] = 1 / eval(page)
    progress_text = "Page 1 "+region+' completed'+':smile:'
    progress_bar.progress(st.session_state['progress'], text=progress_text)
    time.sleep(1)

    for j in range(2,eval(page)+1):
        option = webdriver.ChromeOptions()
        option.add_argument('--headless=new')
        option.add_argument('--log-level=1')
        option.add_argument('--log-level=2')
        option.add_experimental_option('excludeSwitches', ['enable-logging'])
        driver = webdriver.Chrome(options=option)
        driver.implicitly_wait(600)
        region_url='https://weedmaps.com'+url+'?page='+str(j)
        driver.get(region_url)
        time.sleep(1.5)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        region=soup.find("span",{"class":"Text-sc-51fcf911-0 Secondary-sc-c32fcfbf-1 cfwChl ffEptK"}).text
        stores_list=soup.find_all("div",{"class":"Card-sc-f49b1e31-1 kezPaw"})
        
        for store in stores_list:
            try:
                name=store.find("div",{"class":"Text-sc-51fcf911-0 Title-sc-f49b1e31-5 dQtSPx ipKkKY"}).text
            except:
                name=''
            Store.append(name)
            try:
                store_link=store.find('a')['href']
            except:
                store_link=''
            Link.append(store_link)
            Region.append(region)
            try:
                rating=store.find("div",{"class":"Text-sc-51fcf911-0 RatingValue-sc-beddb37b-1 kBrurT kqtLEy"}).text
            except:
                rating=''
            Rating.append(rating)
            try:
                review_num=store.find("div",{"class":"Text-sc-51fcf911-0 Count-sc-beddb37b-2 kBrurT jtacXy"}).text
                review_num=review_num.replace('-','')
            except:
                review_num=''
            Reviewnum.append(review_num)
            try:
                category=store.find("span",{"class":"Text-sc-51fcf911-0 Helper-sc-f49b1e31-7 qBJOa iHMRmY"}).text
            except:
                category=''
            Category.append(category)
            try:
                Delivery=[]
                delivery=store.find_all("span",{"class":"Chip-sc-5f639846-9 cvaOiC"})
                for item in delivery:
                    if item.text!='Closed' and item.text!='Open now':
                        Delivery.append(item.text)
            except:
                Delivery=[]
            Delliveries.append(Delivery)
            try:
                Discount=[]
                discount_label=store.find("div",{"class":"src__Box-sc-1sbtrzs-0 src__Flex-sc-1sbtrzs-1 DealTagsDesktopContainer-sc-5f639846-16 hNEOfd eqdOIn kHzFGe"})
                discount=discount_label.text
                discount_link=store.find('a')['href']
                Discount.append(discount)
                Discount.append(discount_link)
            except:
                Discount=[]
            Promotion.append(Discount)
        st.session_state['progress'] = j / eval(page)
        progress_text = "Page "+str(j)+' '+region+' completed'+':smile:'
        progress_bar.progress(st.session_state['progress'], text=progress_text)
        time.sleep(2)

    Address=[];Hour=[];Phone=[];Price=[];Description=[];Logo=[];Brand=[]
    
    with st.status("Adding details...", expanded=True) as status:
        option = webdriver.ChromeOptions()
        driver = webdriver.Chrome(options=option)
        driver.maximize_window()
        for k in range(len(Link)):
            
            st.write("Adding details of",Store[k])
            # baseurl='https://weedmaps.com/'+Link[k]+'#details'
            # main = requests.get(baseurl,headers=headers).text
            # soup=BeautifulSoup(main,'html.parser')
            baseurl='https://weedmaps.com/'+Link[k]
            driver.get(baseurl)
            driver.execute_script("window.scrollTo(0, 1000)")
            driver.implicitly_wait(1200)
            time.sleep(1)
            Brand_item=[]
            soup = BeautifulSoup(driver.page_source, "html.parser")

            age_check = soup.find("button",{"class":"Button-sc-3e5c1223-0 heMWcl"})
            if age_check is not None:
                in_icon = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.Button-sc-3e5c1223-0.heMWcl")))
                in_icon.click()
                time.sleep(0.5)

            cookies=soup.find("button",{"class":"Button-sc-3e5c1223-0 NotificationButton-sc-1910fd4c-5 cmhZzw cxfREe"})
            if cookies is not None:
                cookie_icon = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.Button-sc-3e5c1223-0.NotificationButton-sc-1910fd4c-5.cmhZzw.cxfREe")))
                cookie_icon.click()
                
            try:
                no_menu=soup.find("div",{"class":"Card-sc-98f7e9c9-0 NoItems-sc-d70ab7ed-7 kFshjs euHTYs"}).text
            except:
                no_menu=''
            soup = BeautifulSoup(driver.page_source, "html.parser")
            

            if no_menu=='':
                cart_cancel=soup.find("button",{"class":"Text-sc-51fcf911-0 Cancel-sc-5b6441b0-1 kYJsci bMhrDx"})
                if cart_cancel is not None:
                    cancel_icon = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.Text-sc-51fcf911-0.Cancel-sc-5b6441b0-1.kYJsci.bMhrDx")))
                    cancel_icon.click()
                    time.sleep(0.5)
                cart_cancel2=soup.find("button",{"class":"Button-sc-3e5c1223-0 hnCKGr"})
                if cart_cancel2 is not None:
                    cancel_icon2 = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.Button-sc-3e5c1223-0.hnCKGr")))
                    cancel_icon2.click()
                    time.sleep(0.5)

                more_brand = soup.find("button",{"class":"StyledShowMoreButton-sc-e6df4670-2 ifbgrb"})
                if more_brand!=None:
                    more_icon = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.StyledShowMoreButton-sc-e6df4670-2.ifbgrb")))
                    more_icon.click()
                    time.sleep(1)
                soup = BeautifulSoup(driver.page_source, "html.parser")
                
                try:
                    Brands=soup.find("div",{"data-testid":"brand-filter-group"})
                    brands=Brands.find_all("label",{"data-testid":"checkbox"})
                    for brand in brands:
                        Brand_item.append(brand.text)
                except:
                    Brand_item=[]
            Brand.append(Brand_item)

            st.write(len(Brand_item))
            try:
                script_tag = soup.find('script', {'type': 'application/ld+json'})
            except:
                script_tag=''
            if script_tag!='':
                json_text = script_tag.get_text()
                data = json.loads(json_text)
                try:
                    address = data['address']
                except:
                    address=''
                Address.append(address)
                try:
                    hour = data['openingHoursSpecification']
                except:
                    hour=''
                Hour.append(hour)
                try: 
                    tel = data['telephone']
                except:
                    tel=''
                Phone.append(tel)
                try:
                    pricerange = data['priceRange']
                except:
                    pricerange=''
                Price.append(pricerange)
                try:
                    description=data['description']
                except:
                    description=''
                Description.append(description)
                try:
                    logo_img=data['logo']
                except:
                    logo_img=''
                Logo.append(logo_img)
                time.sleep(1)

            status.update(label="Complete!", state="complete", expanded=False)
        driver.close()
        driver.quit()
        

    df = pd.DataFrame({'Name':Store,'Link':Link,'Region':Region,'Rating':Rating,'Reviewnum':Reviewnum,'Category':Category,'Delivery':Delliveries,
                       'Promotion':Promotion,'Address':Address,'OpenHour':Hour,'Phone':Phone,'Price Range':Price,'Description':Description,'Logo':Logo,'Brand':Brand})
    return df

def State_dispensary(url_list):
    Store=[];Region=[];Link=[];Rating=[];Reviewnum=[];Category=[];Delliveries=[];Promotion=[]
    Address=[];Hour=[];Phone=[];Price=[];Description=[];Logo=[];Brand=[]
    for i in range(len(url_list)):
       
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'}
        region_url='https://weedmaps.com'+url_list[i]
        main = requests.get(region_url,headers=headers).text
        soup=BeautifulSoup(main,'html.parser')
        st.session_state['progress'] = 0
        progress_bar = st.progress(st.session_state['progress'])
        try:
            region=soup.find("span",{"class":"Text-sc-51fcf911-0 Secondary-sc-c32fcfbf-1 cfwChl ffEptK"}).text
        except:
            time.sleep(1)
            region=soup.find("span",{"class":"Text-sc-51fcf911-0 Secondary-sc-c32fcfbf-1 cfwChl ffEptK"}).text
        try:
            pages=soup.find("a",{"class":"pagination-styles__PaginationButton-sc-1k8dxuw-2 iWtaBX"}).text
            page = pages.split()[-1]
        except:
            pages=soup.find("a",{"class":"PaginationButton-sc-f3af86c4-2 gSkqUh"}).text
            page = pages.split()[-1]
        stores_list=soup.find_all("div",{"class":"Card-sc-f49b1e31-1 kezPaw"})
        for store in stores_list:
            try:
                name=store.find("div",{"class":"Text-sc-51fcf911-0 Title-sc-f49b1e31-5 dQtSPx ipKkKY"}).text
            except:
                name=''
            Store.append(name)
            try:
                store_link=store.find('a')['href']
            except:
                store_link=''
            Link.append(store_link)
            Region.append(region)
            try:
                rating=store.find("div",{"class":"Text-sc-51fcf911-0 RatingValue-sc-beddb37b-1 kBrurT kqtLEy"}).text
            except:
                rating=''
            Rating.append(rating)
            try:
                review_num=store.find("div",{"class":"Text-sc-51fcf911-0 Count-sc-beddb37b-2 kBrurT jtacXy"}).text
            except:
                review_num=''
            Reviewnum.append(review_num)
            try:
                category=store.find("span",{"class":"Text-sc-51fcf911-0 Helper-sc-f49b1e31-7 qBJOa iHMRmY"}).text
            except:
                category=''
            Category.append(category)
            try:
                Delivery=[]
                delivery=store.find_all("span",{"class":"Chip-sc-5f639846-9 cvaOiC"})
                for item in delivery:
                    if item.text!='Closed' and item.text!='Open now':
                        Delivery.append(item.text)
            except:
                Delivery=[]
            Delliveries.append(Delivery)
            try:
                Discount=[]
                discount_label=store.find("div",{"class":"src__Box-sc-1sbtrzs-0 src__Flex-sc-1sbtrzs-1 DealTagsDesktopContainer-sc-5f639846-16 hNEOfd eqdOIn kHzFGe"})
                discount=discount_label.text
                discount_link=store.find('a')['href']
                Discount.append(discount)
                Discount.append(discount_link)
            except:
                Discount=[]
            Promotion.append(Delivery)
        st.session_state['progress'] = 1 / eval(page)
        progress_text = "Page 1 "+region+' completed'+':smile:'
        progress_bar.progress(st.session_state['progress'], text=progress_text)
        time.sleep(1)

        for j in range(2,eval(page)+1):
            option = webdriver.ChromeOptions()
            option.add_argument('--headless=new')
            option.add_argument('--log-level=1')
            option.add_argument('--log-level=2')
            option.add_experimental_option('excludeSwitches', ['enable-logging'])
            driver = webdriver.Chrome(options=option)
            driver.implicitly_wait(600)
            region_url='https://weedmaps.com'+url_list[i]+'?page='+str(j)
            driver.get(region_url)
            time.sleep(1.5)
            soup = BeautifulSoup(driver.page_source, "html.parser")

            region=soup.find("span",{"class":"Text-sc-51fcf911-0 Secondary-sc-c32fcfbf-1 cfwChl ffEptK"}).text
            stores_list=soup.find_all("div",{"class":"Card-sc-f49b1e31-1 kezPaw"})
            
            for store in stores_list:
                try:
                    name=store.find("div",{"class":"Text-sc-51fcf911-0 Title-sc-f49b1e31-5 dQtSPx ipKkKY"}).text
                except:
                    name=''
                Store.append(name)
                try:
                    store_link=store.find('a')['href']
                except:
                    store_link=''
                Link.append(store_link)
                Region.append(region)
                try:
                    rating=store.find("div",{"class":"Text-sc-51fcf911-0 RatingValue-sc-beddb37b-1 kBrurT kqtLEy"}).text
                except:
                    rating=''
                Rating.append(rating)
                try:
                    review_num=store.find("div",{"class":"Text-sc-51fcf911-0 Count-sc-beddb37b-2 kBrurT jtacXy"}).text
                    review_num=review_num.replace('-','')
                except:
                    review_num=''
                Reviewnum.append(review_num)
                try:
                    category=store.find("span",{"class":"Text-sc-51fcf911-0 Helper-sc-f49b1e31-7 qBJOa iHMRmY"}).text
                except:
                    category=''
                Category.append(category)
                try:
                    Delivery=[]
                    delivery=store.find_all("span",{"class":"Chip-sc-5f639846-9 cvaOiC"})
                    for item in delivery:
                        if item.text!='Closed' and item.text!='Open now':
                            Delivery.append(item.text)
                except:
                    Delivery=[]
                Delliveries.append(Delivery)
                try:
                    Discount=[]
                    discount_label=store.find("div",{"class":"src__Box-sc-1sbtrzs-0 src__Flex-sc-1sbtrzs-1 DealTagsDesktopContainer-sc-5f639846-16 hNEOfd eqdOIn kHzFGe"})
                    discount=discount_label.text
                    discount_link=store.find('a')['href']
                    Discount.append(discount)
                    Discount.append(discount_link)
                except:
                    Discount=[]
                Promotion.append(Delivery)
            st.session_state['progress'] = j / eval(page)
            progress_text = "Page "+str(j)+' '+region+' completed'+':smile:'
            progress_bar.progress(st.session_state['progress'], text=progress_text)
            time.sleep(2)
            
    df = pd.DataFrame({'Name':Store,'Link':Link,'Region':Region,'Rating':Rating,'Reviewnum':Reviewnum,'Category':Category,'Delivery':Delliveries,
                       'Promotion':Promotion})
    df2 = df.drop_duplicates(subset='Name', keep='first')

    Store2=df2['Name'].tolist();Link2=df2['Link'].tolist();Region2=df2['Region'].tolist()
    Region2=df2['Region'].tolist();Rating2=df2['Rating'].tolist();Reviewnum2=df2['Reviewnum'].tolist()
    Category2=df2['Category'].tolist();Delliveries2=df2['Delivery'].tolist();Promotion2=df2['Promotion'].tolist()
    
    with st.status("Adding details...", expanded=True) as status:
        option = webdriver.ChromeOptions()
        driver = webdriver.Chrome(options=option)
        driver.maximize_window()
        for k in range(len(Link2)):
            
            st.write("Adding details of",Store2[k])
            # baseurl='https://weedmaps.com/'+Link[k]+'#details'
            # main = requests.get(baseurl,headers=headers).text
            # soup=BeautifulSoup(main,'html.parser')
            baseurl='https://weedmaps.com/'+Link2[k]
            driver.get(baseurl)
            driver.execute_script("window.scrollTo(0, 1000)")
            driver.implicitly_wait(1200)
            time.sleep(1)
            Brand_item=[]
            soup = BeautifulSoup(driver.page_source, "html.parser")

            age_check = soup.find("button",{"class":"Button-sc-3e5c1223-0 heMWcl"})
            if age_check is not None:
                in_icon = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.Button-sc-3e5c1223-0.heMWcl")))
                in_icon.click()
                time.sleep(0.5)

            cookies=soup.find("button",{"class":"Button-sc-3e5c1223-0 NotificationButton-sc-1910fd4c-5 cmhZzw cxfREe"})
            if cookies is not None:
                cookie_icon = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.Button-sc-3e5c1223-0.NotificationButton-sc-1910fd4c-5.cmhZzw.cxfREe")))
                cookie_icon.click()
                
            try:
                no_menu=soup.find("div",{"class":"Card-sc-98f7e9c9-0 NoItems-sc-d70ab7ed-7 kFshjs euHTYs"}).text
            except:
                no_menu=''
            soup = BeautifulSoup(driver.page_source, "html.parser")
            

            if no_menu=='':
                cart_cancel=soup.find("button",{"class":"Text-sc-51fcf911-0 Cancel-sc-5b6441b0-1 kYJsci bMhrDx"})
                if cart_cancel is not None:
                    cancel_icon = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.Text-sc-51fcf911-0.Cancel-sc-5b6441b0-1.kYJsci.bMhrDx")))
                    cancel_icon.click()
                    time.sleep(0.5)
                cart_cancel2=soup.find("button",{"class":"Button-sc-3e5c1223-0 hnCKGr"})
                if cart_cancel2 is not None:
                    cancel_icon2 = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.Button-sc-3e5c1223-0.hnCKGr")))
                    cancel_icon2.click()
                    time.sleep(0.5)

                more_brand = soup.find("button",{"class":"StyledShowMoreButton-sc-e6df4670-2 ifbgrb"})
                if more_brand!=None:
                    more_icon = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.StyledShowMoreButton-sc-e6df4670-2.ifbgrb")))
                    more_icon.click()
                    time.sleep(1)
                soup = BeautifulSoup(driver.page_source, "html.parser")
                
                try:
                    Brands=soup.find("div",{"data-testid":"brand-filter-group"})
                    brands=Brands.find_all("label",{"data-testid":"checkbox"})
                    for brand in brands:
                        Brand_item.append(brand.text)
                except:
                    Brand_item=[]
            Brand.append(Brand_item)

            st.write(len(Brand_item))
            try:
                script_tag = soup.find('script', {'type': 'application/ld+json'})
            except:
                script_tag=''
            if script_tag!='':
                json_text = script_tag.get_text()
                data = json.loads(json_text)
                try:
                    address = data['address']
                except:
                    address=''
                Address.append(address)
                try:
                    hour = data['openingHoursSpecification']
                except:
                    hour=''
                Hour.append(hour)
                try: 
                    tel = data['telephone']
                except:
                    tel=''
                Phone.append(tel)
                try:
                    pricerange = data['priceRange']
                except:
                    pricerange=''
                Price.append(pricerange)
                try:
                    description=data['description']
                except:
                    description=''
                Description.append(description)
                try:
                    logo_img=data['logo']
                except:
                    logo_img=''
                Logo.append(logo_img)
                time.sleep(1)

            status.update(label="Complete!", state="complete", expanded=False)
        driver.close()
        driver.quit()

    df3 = pd.DataFrame({'Name':Store2,'Link':Link2,'Region':Region2,'Rating':Rating2,'Reviewnum':Reviewnum2,'Category':Category2,'Delivery':Delliveries2,
                       'Promotion':Promotion2,'Address':Address,'OpenHour':Hour,'Phone':Phone,'Price Range':Price,'Description':Description,'Logo':Logo,'Brand':Brand})
    return df3

@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8-sig')

if 'state_lv' not in st.session_state:
    st.session_state['state_lv'] = None
if 'state_state' not in st.session_state:
    st.session_state['state_state'] = None
if 'area_state' not in st.session_state:
    st.session_state['area_state'] = None
if 'progress' not in st.session_state:
    st.session_state['progress'] = None

State_name,State_link=place_scrape()
option = st.selectbox(
   "Which state you want to scrape?",
   State_name,
   index=None,
   placeholder="Select state in U.S...",
)

st.write('You selected:', option)


if option!=None:
    state_agree = st.checkbox('Scrape the whole state',value=True)
    if state_agree:
        st.write('You will scrape all dispensaries in:', option)
        state_index=State_name.index(option)
        Area_name,Area_link=place2_scrape(State_link[state_index])
        clicked = st.button('Scrape dispensaries info in '+option)
        if clicked:
            with st.spinner("Downloading dispensaries info in %s" % option):
                df_state=State_dispensary(Area_link)
            st.success("Successfully!:sparkler:" )
            st.session_state['state_state'] = 1
            if st.session_state['state_state'] is not None:
                csv = convert_df(df_state)
                st.download_button(
                    label="Download data as CSV",
                    data=csv,
                    file_name=option+'.csv',
                    mime='text/csv',
                )
    else:
        state_index=State_name.index(option)
        Area_name,Area_link=place2_scrape(State_link[state_index])
        option2 = st.selectbox(
            "Which area you want to scrape in"+option+'?',
            Area_name,
            index=None,
            placeholder="Select specific area in "+option,
        )
        st.write('You selected:', option2)
        if option2!=None:
            area_index=Area_name.index(option2)
    
            clicked2 = st.button('Scrape dispensaries info in '+option2)
            if clicked2:
                with st.spinner("Downloading dispensaries info in %s" % option2):
                    df_area=Area_dispensary(Area_link[area_index])
                st.success("Successfully!:sparkler:" )
                st.session_state['area_state'] = 1
                if st.session_state['area_state'] is not None:
                    csv = convert_df(df_area)
                    st.download_button(
                        label="Download data as CSV",
                        data=csv,
                        file_name=option2+'.csv',
                        mime='text/csv',
                    )