import streamlit as st
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

# 追加情報を抽出する関数
def extract_additional_info(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    div_elements = soup.find_all('div', class_='blank-box bb-green')
    div_texts = [' '.join(div.stripped_strings) for div in div_elements]
    df = pd.DataFrame(div_texts, columns=['Text'])
    
    if len(df) > 2:
        df = df.iloc[:-2]
    if len(df) > 5:
        df = df.sample(n=5, random_state=1)
    else:
        df = df.sample(n=len(df), random_state=1)

    return df

st.set_page_config(layout="wide")
st.title('漫画の名言スクレイピング')

urls = {
    '漫画の名言': 'https://bontoku.com/category/meigen-bonpu/manga-meigen',
    '偉人の名言': 'https://bontoku.com/category/meigen-bonpu/ijin',
    '登場人物の名言': 'https://bontoku.com/category/meigen-bonpu/chara-meigen'
}
selected_key = st.selectbox('選択してください', list(urls.keys()))
selected_url = urls[selected_key]

max_pages = st.number_input('取得する最大ページ数を入力してください:', min_value=1, value=1, step=1)

if st.button('スクレイピング開始'):
    st.session_state.scraped_data = scrape_page(selected_url + "/page/1/")
    if st.session_state.scraped_data:
        st.dataframe(st.session_state.scraped_data, use_container_width=True)
    else:
        st.write("データが見つかりませんでした。")

# Title の選択と追加情報の抽出
if 'scraped_data' in st.session_state and st.session_state.scraped_data:
    title_options = [item['Title'] for item in st.session_state.scraped_data]
    selected_title = st.selectbox('Title を選択してください', options=title_options)
    
if st.button('追加情報を抽出'):
    selected_url = next((item['URL'] for item in st.session_state.scraped_data if item['Title'] == selected_title), None)
    if selected_url:
        st.session_state.df_additional = extract_additional_info(selected_url)

if 'df_additional' in st.session_state and not st.session_state.df_additional.empty:
    st.dataframe(st.session_state.df_additional, use_container_width=True)

    # 名言の選択と表示
    if 'selected_meigen' not in st.session_state:
        st.session_state.selected_meigen = st.session_state.df_additional['Text'].iloc[0]

    meigen_options = st.session_state.df_additional['Text'].tolist()
    selected_meigen = st.selectbox('名言を選択してください', meigen_options, index=meigen_options.index(st.session_state.selected_meigen) if st.session_state.selected_meigen in meigen_options else 0)
    st.session_state.selected_meigen = selected_meigen  # 選択された名言を更新

if st.button('名言を取得'):         
        # 名言の表示
        st.write(st.session_state.selected_meigen)

import os
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む（ローカル環境のみ）
if not os.getenv("CI"):
    load_dotenv()

# 環境変数を使用
Slack_API_KEY = os.getenv("Slack_API_KEY")

import requests

def send_slack_message(output_content_text, token=Slack_API_KEY, channel='#charger_akari'):
    """
    Slackの指定されたチャンネルにメッセージを送信します。

    Parameters:
        output_content_text (str): 送信するメッセージの内容。
        token (str): Slack APIの認証トークン。デフォルトは'xxx'。
        channel (str): メッセージを送信するチャンネル。デフォルトは'#charger_akari'。
    """
    url = "https://slack.com/api/chat.postMessage"
    headers = {"Authorization": "Bearer " + token}
    data = {
        'channel': channel,
        'text': output_content_text
    }
    response = requests.post(url, headers=headers, data=data)
    print("Return: ", response.json())


if st.button('名言をslackに投稿'):         
        # 名言の表示
        send_slack_message(selected_meigen)