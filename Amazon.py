from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import re
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from textblob import TextBlob
import spacy

# Downloads necessary NLTK resources
nltk.download('stopwords')
nltk.download('punkt')

# Loads spaCy model
nlp = spacy.load("en_core_web_sm")

# Initializing Chrome options
chrome_options = Options()
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--headless')

# Initializing Chrome driver with WebDriver Manager
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Function to get URL of review page
def get_url_review_page(product_url, page_number):
    return product_url.replace('dp','product-reviews') + f'?pageNumber={page_number}'

# Function to get product rating
def get_rating(product_url):
    driver.get(get_url_review_page(product_url, 1))
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    rating = soup.select_one("#cm_cr-product_info > div > div.a-text-left.a-fixed-left-grid-col.reviewNumericalSummary.celwidget.a-col-left > div.a-row.a-spacing-small.averageStarRatingIconAndCount > div > div > div.a-fixed-left-grid-col.aok-align-center.a-col-right > div > span")
    if rating:
        return rating.text.strip()
    else:
        return "N/A"

# Function to get product name
def get_product_name(product_url):
    driver.get(get_url_review_page(product_url, 1))
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    product_name = soup.find('a',{'data-hook':"product-link"})
    if product_name:
        return product_name.text.strip()
    else:
        return "N/A"

# Function to get global rating
def get_global_rating(product_url):
    driver.get(get_url_review_page(product_url, 1))
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    global_rating = soup.find('span',{'class':'a-color-secondary'})
    if global_rating:
        return global_rating.text.strip()
    else:
        return "N/A"

# Function to get image URL
def get_image_url(product_url):
    driver.get(product_url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    image_of_product = soup.select_one('#landingImage')
    if image_of_product:
        return image_of_product['src']
    else:
        return "N/A"

# Function to extract reviews
def extract_reviews(product_url):
    driver.get(get_url_review_page(product_url, 1))
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    review_spans = soup.find_all('span', class_='review-text-content')
    reviews = [review.get_text(strip=True) for review in review_spans]
    return reviews

# Function to extract all reviews
def extract_all_reviews(product_url, num_pages=10):
    all_reviews = []
    for i in range(1, num_pages+1):
        reviews = extract_reviews(product_url)
        all_reviews.extend(reviews)
    return all_reviews

# Function to clean comment
def clean_comment(comment):
    comment = comment.lower()
    comment = re.sub(r'[^a-zA-Z\s]', '', comment)
    tokens = word_tokenize(comment)
    tokens = [token for token in tokens if token not in stop_words]
    cleaned_comment = ' '.join(tokens)
    return cleaned_comment

# Function for sentiment analysis using TextBlob
def sentiment_analysis_textblob(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0:
        return "Positive"
    elif polarity < 0:
        return "Negative"
    else:
        return "Neutral"

# Function to create DataFrame with comments and sentiment
def comment_dataFrame(product_url):
    reviews = extract_all_reviews(product_url)
    reviews_cleaned = [clean_comment(review) for review in reviews]
    df = pd.DataFrame({'comment': reviews_cleaned})
    df['sentiment'] = df['comment'].apply(sentiment_analysis_textblob)
    return df

# Function to get sentiment count by comment
def sentiment_by_comment(df):
    return df['sentiment'].value_counts().reset_index()