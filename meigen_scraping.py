import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import urllib.parse

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

# 追加情報を抽出する関数
def extract_additional_info(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    div_elements = soup.find_all('div', class_='blank-box bb-green')
    div_texts = [' '.join(div.stripped_strings) for div in div_elements]
    df = pd.DataFrame(div_texts, columns=['Text'])
    
    # 最後の2行を削除
    if len(df) > 2:
        df = df.iloc[:-2]
    # ランダムに5つを選択
    if len(df) > 5:
        df = df.sample(n=5, random_state=1)
    else:
        df = df.sample(n=len(df), random_state=1) # 行数が5以下の場合、全行を使用

    return df

st.set_page_config(layout="wide")
st.title('漫画の名言スクレイピング')

urls = {
    '漫画の名言': 'https://bontoku.com/category/meigen-bonpu/manga-meigen',
    '偉人の名言': 'https://bontoku.com/category/meigen-bonpu/ijin',
    '登場人物の名言': 'https://bontoku.com/category/meigen-bonpu/chara-meigen'}
selected_key = st.selectbox('選択してください', list(urls.keys()))
selected_url = urls[selected_key]

max_pages = st.number_input('取得する最大ページ数を入力してください:', min_value=1, value=1, step=1)

# スクレイピング開始ボタン
if st.button('スクレイピング開始'):
    # スクレイピング結果をセッション状態で保持
    st.session_state.scraped_data = scrape_page(selected_url + "/page/1/")
    # スクレイピング結果の表示
    if st.session_state.scraped_data:
        st.dataframe(st.session_state.scraped_data, use_container_width=True)
    else:
        st.write("データが見つかりませんでした。")

# 選択されたタイトルに基づく追加情報の表示
if 'scraped_data' in st.session_state and st.session_state.scraped_data:
    title_options = [item['Title'] for item in st.session_state.scraped_data]
    selected_title = st.selectbox('Titleを選択してください', title_options)
    selected_item = next((item for item in st.session_state.scraped_data if item['Title'] == selected_title), None)
    if selected_item and st.button('追加情報を表示'):
        df_additional = extract_additional_info(selected_item['URL'])
        if not df_additional.empty:
            st.dataframe(df_additional, use_container_width=True)
        else:
            st.write("追加情報を抽出できませんでした。")
