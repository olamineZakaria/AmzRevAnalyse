from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import re
import csv
import pandas as pd
import re
import nltk
nltk.download('stopwords')
nltk.download('punkt')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import spacy
from textblob import TextBlob
import streamlit as st
import plotly.express as px
import requests
import subprocess
from wordcloud import WordCloud
from webdriver_manager.chrome import ChromeDriverManager

nlp = spacy.load("en_core_web_sm")
#subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
stop_words = set(stopwords.words('english'))
chrome_options = Options()
#chrome_options.add_argument("--headless")
options = Options()
options.add_argument('--disable-gpu')
options.add_argument('--headless')
# chrome_driver_path = "chromedriver.exe" 
# def get_driver():
#     return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
# service = Service(chrome_driver_path)
# driver = webdriver.Chrome(service=service, options=chrome_options)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
def get_url_review_page(UrlProduct,i):
    UrlReview = UrlProduct.replace('dp','product-reviews') + '?pageNumber=' + str(i)
    return UrlReview
def get_rating(UrlProduct):
    driver.get(get_url_review_page(UrlProduct,1))
    soup = BeautifulSoup(driver.page_source,'html.parser')
    rating = soup.select("#cm_cr-product_info > div > div.a-text-left.a-fixed-left-grid-col.reviewNumericalSummary.celwidget.a-col-left > div.a-row.a-spacing-small.averageStarRatingIconAndCount > div > div > div.a-fixed-left-grid-col.aok-align-center.a-col-right > div > span")
    rating = str(rating)
    g=rating[73:-17]
    return g
def get_product_name(UrlProduct):
    driver.get(get_url_review_page(UrlProduct,1))
    soup = BeautifulSoup(driver.page_source,'html.parser')
    Product_name = soup.find('a',{'data-hook':"product-link"})
    # Product_name = str(Product_name.string)
    Product_name = str(Product_name)
    pattern = r'>([^<]+)<'
    Product_name = re.findall(pattern, Product_name)
    return Product_name[0]
def get_global_rating(UrlProduct):
    driver.get(get_url_review_page(UrlProduct,1))
    soup = BeautifulSoup(driver.page_source,'html.parser')
    Global_rating = soup.find('span',{'class':'a-color-secondary'})
    Global_rating = str(Global_rating)
    g = Global_rating[44:-7]
    return g
def get_image_url(UrlProduct):
    driver.get(UrlProduct)
    soup = BeautifulSoup(driver.page_source,'html.parser')
    Image_of_product = soup.select('#landingImage')
    Image_of_product = re.findall(r'src="https.*pg',str(Image_of_product[0]))
    Image_of_product =  str(Image_of_product)
    Image_of_product = Image_of_product[7:-2]
    return Image_of_product
def extract_reviews(UrlProduct):
    driver.get(get_url_review_page(UrlProduct,1))
    soup = BeautifulSoup(driver.page_source,'html.parser')
    review_spans = soup.find_all('span', class_='review-text-content')
    reviews = [review.get_text() for review in review_spans]
    return reviews
def extract_all_reviews(UrlProduct):
    all_reviews = []
    url_review = get_url_review_page(UrlProduct,1)
    numberOfpages = 10
    for i in range(1,numberOfpages+1):
        url_review = get_url_review_page(UrlProduct,1)
        reviews = extract_reviews(url_review)
        all_reviews.extend(reviews)
        # with open("file.txt", "a", encoding="utf-8") as file:
        #     for review in reviews:
        #         file.write(review + "\n")
        # print("Page", i)
    return all_reviews
def clean_comment(comment):
    comment = comment.lower()
    comment = re.sub(r'[^a-zA-Z\s]', '', comment)
    comment = re.sub(r'\d+', '', comment)
    tokens = word_tokenize(comment)
    tokens = [token for token in tokens if token not in stop_words]
    cleaned_comment = ' '.join(tokens)
    return cleaned_comment
def sentiment_analysis_textblob(text):
    doc = nlp(text)
    blob = TextBlob(doc.text)
    polarity = blob.sentiment.polarity
    if polarity > 0:
        sentiment_label = "Positive"
    elif polarity < 0:
        sentiment_label = "Negative"
    else:
        sentiment_label = "Neutral"
    return sentiment_label
def comment_dataFrame(UrlProduct):
    reviews = extract_all_reviews(UrlProduct)
    reviews_cleaned = [clean_comment(review.replace("\n", " ")) for review in reviews]
    df = pd.DataFrame(reviews_cleaned, columns=['comment'])
    df['sentiment'] = df['comment'].apply(sentiment_analysis_textblob)
    return df
def sentiemnt_by_comment(df):
    return df.groupby('sentiment').count()['comment'].reset_index()