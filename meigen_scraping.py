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

# スクレイピング開始ボタン
if st.button('スクレイピング開始'):
    # 指定されたページ数に基づいてスクレイピングを実行
    scraped_data = start_scraping(selected_url, int(max_pages))
    if scraped_data:
        # スクレイピング結果をデータフレームに変換して表示
        st.session_state.scraped_data = pd.DataFrame(scraped_data)
        st.dataframe(st.session_state.scraped_data, use_container_width=True)
    else:
        st.write("データが見つかりませんでした。")

# Title の選択
if 'scraped_data' in st.session_state and not st.session_state.scraped_data.empty:
    title_options = st.session_state.scraped_data['Title'].tolist()
    selected_title = st.selectbox('Title を選択してください', options=title_options)

# ページ情報の抽出
if 'scraped_data' in st.session_state and 'selected_title' in locals():
    if st.button('ページから名言を抽出'):
        selected_url = st.session_state.scraped_data[st.session_state.scraped_data['Title'] == selected_title]['URL'].iloc[0]
        st.session_state.df_additional = extract_additional_info(selected_url)

# 名言の選択と名言の抽出
if 'df_additional' in st.session_state and not st.session_state.df_additional.empty:
    st.dataframe(st.session_state.df_additional, use_container_width=True)

    # 名言の選択と表示
    if 'selected_meigen' not in st.session_state:
        st.session_state.selected_meigen = st.session_state.df_additional['Text'].iloc[0]

    meigen_options = st.session_state.df_additional['Text'].tolist()
    selected_meigen = st.selectbox('名言を選択してください', meigen_options, index=meigen_options.index(st.session_state.selected_meigen) if st.session_state.selected_meigen in meigen_options else 0)
    st.session_state.selected_meigen = selected_meigen  # 選択された名言を更新

if st.button('名言のテキスト情報を取得して変数に格納'):         
        # 名言の表示
        st.write(st.session_state.selected_meigen)

import os
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む（ローカル環境のみ）
if not os.getenv("CI"):
    load_dotenv()
# 環境変数を使用
SLACK_API_KEY = os.getenv("SLACK_API_KEY")

# SLACK_API_KEYを取得できているかを確認したいときは、以下のコードを有効にして表示させます
# st.write(SLACK_API_KEY)


def send_slack_message(output_content_text, token=SLACK_API_KEY, channel='#charger_akari'):
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

from services import meigen_gpt

# GPTで生成する関数を実行
if st.button('名言をGPTで加工'):
    output_content_text = meigen_gpt.make_meigen(st.session_state.selected_meigen)
    st.session_state.output_content_text = output_content_text

# Slackに投稿
if st.button('GPTで改編した名言をslackに投稿'):
    # st.session_stateからoutput_content_textを参照して使用
    if 'output_content_text' in st.session_state:
        send_slack_message(st.session_state.output_content_text)
    else:
        st.write("加工された名言がありません。先に「名言をGPTで加工」ボタンを押してください。")