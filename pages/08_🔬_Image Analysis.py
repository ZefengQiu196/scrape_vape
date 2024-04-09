from openai import OpenAI
import streamlit as st
from paddleocr import PaddleOCR, draw_ocr
from PIL import Image
import os
import pandas as pd
import base64
import requests
import cv2 as cv
import numpy as np
from sklearn.cluster import KMeans
from collections import Counter
from io import BytesIO
from rembg import remove
from st_pages import add_page_title

add_page_title()
# Function to feed image to ocr model
def ocr_single_img(imgpath):
        # The ocr model dir must have model and params file
        #English and Chinese mixed mdoel
        ocr = PaddleOCR(det_model_dir='{ch_PP-OCRv4_det_server_infer}',use_angle_cls=True) 
        #English only mdoel
        # ocr = PaddleOCR(use_angle_cls=True, lang="en") 
        img_path = imgpath
        result = ocr.ocr(img_path, cls=True)

        result = result[0]
        if image_path.startswith(('http://', 'https://')):
            response = requests.get(image_path)
            response.raise_for_status()
            image = Image.open(BytesIO(response.content)).convert('RGB')
        else:
            image = Image.open(img_path).convert('RGB')
        if result is not None:
            boxes = [line[0] for line in result]
            txts = [line[1][0] for line in result]
            scores = [line[1][1] for line in result]

            im_show = draw_ocr(image, boxes, txts, scores)
            im_show = Image.fromarray(im_show)
            df = pd.DataFrame({'OCR result':txts,'Score':scores,'Detect box':boxes})
            # st.image(im_show, caption='OCR result of image you upload')
             
        else:
            boxes=[]
            txts=[]
            scores=[]
            df = pd.DataFrame({'OCR result':txts,'Score':scores,'Detect box':boxes})
            st.markdown('''OCR model didn't detect any text! :sob:''')
        return im_show,df

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
    

def palette_perc_lab(k_cluster, cluster_labels, width=300):
    Color_name1=[]
    Color_hex1=[]
    Color_name2=[]
    Color_hex2=[]
    RGB=[]
    # Initialize the palette as a black image
    palette = np.zeros((50, width, 3), np.uint8)

    # Calculate the percentage of each cluster label
    n_pixels = len(cluster_labels)
    counter = Counter(cluster_labels)
    perc = {i: np.round(counter[i] / n_pixels, 2) for i in counter}
    perc = dict(sorted(perc.items()))
    # Draw the palette
    step = 0
    for idx, center in enumerate(k_cluster.cluster_centers_):
        lab_color = np.uint8([[center]])
        bgr_color = cv.cvtColor(lab_color, cv.COLOR_LAB2BGR).flatten()
        rgb_color = bgr_color[::-1] 
        RGB.append(list(rgb_color))
        end = step + int(perc[idx] * width)
        palette[:, step:end, :] = rgb_color
        step = end
    
    palette_image = Image.fromarray(palette)

    lab_center_lists = [list(row) for row in k_cluster.cluster_centers_]    
     
    for lab_center in lab_center_lists:
        
        closest_color_name, closest_hex= find_closest_color(lab_center, color_df)
        Color_name1.append(closest_color_name)
        Color_hex1.append(closest_hex)
        
        closest_color_name2, closest_hex2= find_closest_color(lab_center, color_df2)
        Color_name2.append(closest_color_name2)
        Color_hex2.append(closest_hex2)
    df_main_color= pd.DataFrame({'Color name in wiki dict':Color_name1,'Color hex in wiki dict':Color_hex1,'Color name in human dict':Color_name2,'Color hex in human dict':Color_hex2})

    return palette_image, perc, k_cluster.cluster_centers_,df_main_color

def palette_perc_lab_withbackground(k_cluster):
    Color_name1=[]
    Color_hex1=[]
    Color_name2=[]
    Color_hex2=[]
    width = 300
    palette = np.zeros((50, width, 3), np.uint8)
    
    n_pixels = len(k_cluster.labels_)
    counter = Counter(k_cluster.labels_)
    perc = {i: np.round(counter[i]/n_pixels, 2) for i in counter}
    perc = dict(sorted(perc.items()))
    
    step = 0
    for idx, center in enumerate(k_cluster.cluster_centers_):
        lab_color = np.uint8([[center]])  # LAB 颜色
        rgb_color = cv.cvtColor(lab_color, cv.COLOR_LAB2BGR)  # 转换回 RGB
        palette[:, step:int(step + perc[idx]*width+1), :] = rgb_color
        step += int(perc[idx]*width+1)
        
    palette_rgb = cv.cvtColor(palette, cv.COLOR_BGR2RGB)  # 将 BGR 转换为 RGB
    palette = Image.fromarray(palette_rgb)

    lab_center_lists = [list(row) for row in k_cluster.cluster_centers_]      
    for lab_center in lab_center_lists:
        
        closest_color_name, closest_hex= find_closest_color(lab_center, color_df)
        Color_name1.append(closest_color_name)
        Color_hex1.append(closest_hex)
        
        closest_color_name2, closest_hex2= find_closest_color(lab_center, color_df2)
        Color_name2.append(closest_color_name2)
        Color_hex2.append(closest_hex2)
    df_main_color= pd.DataFrame({'Color name in wiki dict':Color_name1,'Color hex in wiki dict':Color_hex1,'Color name in human dict':Color_name2,'Color hex in human dict':Color_hex2})

    return palette,perc,df_main_color

def euclidean_distance(lab1, lab2):
    """
    Calculate the Euclidean distance between two LAB colors.

    Args:
    - lab1: A LAB color (list or tuple).
    - lab2: Another LAB color (list or tuple).

    Returns:
    - The Euclidean distance between lab1 and lab2.
    """
    return np.sqrt(sum((a - b) ** 2 for a, b in zip(lab1, lab2)))

def find_closest_color(lab_color, color_df):
    """
    Find the closest color in the dataframe to the given LAB color.

    Args:
    - lab_color: A LAB color (list or tuple).
    - color_df: DataFrame with a column 'LAB' containing LAB colors.

    Returns:
    - A tuple containing the name of the closest color and the corresponding row in the dataframe.
    """
    min_distance = float('inf')
    closest_color = None

    for _, row in color_df.iterrows():
        LAB_dict = [int(num) for num in row['LAB(OpenCV)'].strip("[]").split()]
        distance = euclidean_distance(lab_color, LAB_dict)
        if distance < min_distance:
            min_distance = distance
            closest_color = row['Color_Name_Readable']
            closest_hex = row['Hex']

    return closest_color, closest_hex



# Find the closest color in the dataframe
color_df=pd.read_csv('color dict/Wiki_color.csv')
color_df2=pd.read_csv('color dict/Human_color.csv')

    

with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
    
if 'img_state' not in st.session_state:
    st.session_state['img_state'] = None
if 'ocr_df_result' not in st.session_state:
    st.session_state['ocr_df_result'] = None
if 'ocr_img_result' not in st.session_state:
    st.session_state['ocr_img_result'] = None
if 'palette_img_result' not in st.session_state:
    st.session_state['palette_img_result'] = None
if 'palette_perc_result' not in st.session_state:
    st.session_state['palette_perc_result'] = None
if 'palette_name_result' not in st.session_state:
    st.session_state['palette_name_result'] = None
if 'llm_result' not in st.session_state:
    st.session_state['llm_result'] = None

#Upload image file
image_path = st.text_input("What is your path or URL of image?")

if image_path:
    image_path = image_path.strip('\'"')
    
    if image_path.startswith(('http://', 'https://')):
        try:
            response = requests.get(image_path)
            response.raise_for_status()
            image = Image.open(BytesIO(response.content))
            st.image(image, caption='Image from URL')
        except requests.RequestException as e:
            st.error(f"Something wrong when download image from URL: {e}")

    elif os.path.exists(image_path) and image_path.lower().endswith(('.png', '.jpg', '.jpeg')):
        image = Image.open(image_path)
        st.image(image, caption='Image you choose')
    else:
        st.error("Sorry, you didn't choose a valid image type!")
    st.session_state['img_state'] =1

col1, col2 = st.columns(2)
if st.session_state['img_state'] is not None:
    with col1:
        
        if st.button('Click me to see OCR result🔍', type="primary"):
            ocr = PaddleOCR(use_angle_cls=True, lang="en")
            st.write('Your Image path:',image_path)
            
            OCR_img,OCR_result=ocr_single_img(image_path)
            st.session_state['ocr_df_result'] = OCR_result
            st.session_state['ocr_img_result'] = OCR_img
           

        if st.session_state['ocr_df_result'] is not None: 
            if image_path.startswith(('http://', 'https://')):  
                response = requests.get(image_path)
                response.raise_for_status()
                image = Image.open(BytesIO(response.content))
            else:
                image = Image.open(image_path)
            st.write('Your Image size:', image.size)
            st.image(st.session_state['ocr_img_result'], caption='OCR result of image you upload')
            st.write('OCR Result:')
            st.dataframe(st.session_state['ocr_df_result'])          

            
            if image_path.startswith(('http://', 'https://')):
                response = requests.get(image_path)
                response.raise_for_status()
                image_np_array = np.array(bytearray(response.content), dtype=np.uint8)
                img_ori = cv.imdecode(image_np_array, cv.IMREAD_UNCHANGED)
                img_pil = Image.fromarray(cv.cvtColor(img_ori, cv.COLOR_BGR2RGB))
                
                output = remove(img_pil)
                if output.mode=='PA':
                    output = output.convert("RGBA")
                img=np.array(output)
                if img.shape[2] == 4:
                    # 从 RGBA 转换为 BGRA
                    img = cv.cvtColor(img, cv.COLOR_RGBA2BGRA)
                else:
                    # 从 RGB 转换为 BGR
                    img = cv.cvtColor(img, cv.COLOR_RGB2BGR)
                
            else:
                img = cv.imread(image_path, cv.IMREAD_UNCHANGED)
            
            if img.shape[2] == 4:
                # Separate BGR and alpha channels
                img_bgr = img[..., :3]
                alpha_channel = img[..., 3]

                # Create a mask where the alpha channel is not zero (non-transparent)
                mask = alpha_channel != 0

                # Create a blank image with the same dimensions as the original
                blank_image = np.zeros(img_bgr.shape, dtype=img_bgr.dtype)

                # Apply mask to copy non-transparent pixels to the blank image
                blank_image[mask] = img_bgr[mask]

                # Convert the non-transparent pixel image to LAB color space
                blank_image_lab = cv.cvtColor(blank_image, cv.COLOR_BGR2LAB)

                # Flatten the LAB image to a 2D array for clustering
                lab_pixels = blank_image_lab[mask].reshape(-1, 3)

                # Perform K-Means clustering on the LAB pixels
                clt_lab = KMeans(n_clusters=5)
                clt_lab.fit(lab_pixels)
                counter = Counter(clt_lab.labels_)
                
                if len(counter)<5:
                    clt_lab = KMeans(n_clusters=len(counter))
                    clt_lab.fit(lab_pixels)
                    counter = Counter(clt_lab.labels_)
                    
                palette_img, perc, palette_centers,df_main_color = palette_perc_lab(clt_lab, clt_lab.labels_)
                st.session_state['palette_img_result'] = palette_img
                st.session_state['palette_perc_result'] = perc

            else:
                img_lab = cv.cvtColor(img, cv.COLOR_BGR2LAB)  # 转换为 LAB 颜色空间
                clt = KMeans(n_clusters=5)
                clt_lab = clt.fit(img_lab.reshape(-1, 3))
                palette_img,perc,df_main_color =palette_perc_lab_withbackground(clt_lab)
                st.session_state['palette_img_result'] = palette_img
                st.session_state['palette_perc_result'] = perc



            st.image(st.session_state['palette_img_result'], caption='Palette of dominant colors of your image')
            perc_value=list(st.session_state['palette_perc_result'].values())
            st.write(perc_value)

           
            st.session_state['palette_name_result'] = df_main_color
            st.dataframe(st.session_state['palette_name_result'])          

    with col2:
        
        if st.button('Click me to see LLM result🤖', type="primary"):
            
            if not openai_api_key:
                st.info("Please add your OpenAI API key to continue.")
                st.stop()
            # Load image from URL
            if image_path.startswith(('http://', 'https://')):
                client = OpenAI(api_key=openai_api_key)

                response = client.chat.completions.create(
                    model="gpt-4-vision-preview",
                    messages=[
                        {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Here is an image of one product sold in online vape shops, just based on this image, can you summarize some features of this product?I'm interested in those feautres:Brand, Flavor, Nicotine Content, Size or Volume, Main colors, Whether has the Warning Label, if has, its specific location. And one feature named 'Others' that contains other features you think is important for this image. Please answer me in the style of dictionary, if you cannot find that feature, just response 'Not found' for that value of dict "},
                            {
                            "type": "image_url",
                            "image_url": {
                                "url": f"{image_path}",
                            },
                            },
                        ],
                        }
                    ],
                    max_tokens=300,
                )
                
                content =response.choices[0].message.content
                st.session_state['llm_result'] = content
              
            else:
                # Getting the base64 string
                base64_image = encode_image(image_path)
                headers = { 
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {openai_api_key}"
                }
                payload = {
                    "model": "gpt-4-vision-preview",
                    "messages": [
                        {
                        "role": "user",
                        "content": [
                            {
                            "type": "text",
                            "text": "Here is an image of one product sold in online vape shops, just based on this image, can you summarize some features of this product?I'm interested in those feautres:Brand, Flavor, Nicotine Content, Size or Volume, Main colors, Whether has the Warning Label, if has, its specific location. And one feature named 'Others' that contains other features you think is important for this image. Please answer me in the style of dictionary, if you cannot find that feature, just response 'Not found' for that value of dict "
                            },
                            {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                            }
                        ]
                        }
                    ],
                    "max_tokens": 300
                }
                response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
                response_json = response.json()
                content = response_json['choices'][0]['message']['content']
                st.session_state['llm_result'] = content
                

        if st.session_state['llm_result'] is not None:       
            st.write('LLM Result:')
            st.write(st.session_state['llm_result'])
            
            