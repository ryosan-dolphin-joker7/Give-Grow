import pandas as pd
import requests
from bs4 import BeautifulSoup

# スクレイピング関数の定義
def scrape_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    articles = soup.find_all('a', href=True)
    urls_titles = []
    for a_tag in articles:
        h2_tag = a_tag.find('h2')
        if h2_tag:
            urls_titles.append({
                "Title": h2_tag.text,
                "URL": a_tag['href']
            })
    return urls_titles

# スクレイピング開始処理
def start_scraping(base_url, max_pages):
    all_data = []
    for page_num in range(1, max_pages + 1):
        current_url = f"{base_url}/page/{page_num}/"
        data = scrape_page(current_url)
        all_data.extend(data)
    return all_data

# ページから名言を抽出する関数
def extract_additional_info(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    div_elements = soup.find_all('div', class_='blank-box bb-green')
    div_texts = [' '.join(div.stripped_strings) for div in div_elements]
    df = pd.DataFrame(div_texts, columns=['Text'])
    
    if len(df) > 2:
        df = df.iloc[:-2]
    if len(df) > 5:
        df = df.sample(n=5)
    else:
        df = df.sample(n=len(df))

    return df
