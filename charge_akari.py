import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

# 以下は別ファイルに関数を記載して実行するためのfrom,import文です
# fromにディレクトリ名、importにファイル名を記載します
# 関数を使うときは、ファイル名.関数名()でOK

from services import meigen_gpt,text_to_slack,meigen_scraping

# meigen_gpt        ：テキストをGPTに送る関数です
# text_to_slack     ：slackにテキストを送る関数です
# meigen_scraping   ：ページから名言を抽出する関数です


st.set_page_config(layout="wide")
st.title('漫画の名言スクレイピング')

st.header('1.スクレイピングする名言のページを選択します')
# どのページから名言を取得するかを選択します。
urls = {
    '登場人物の名言': 'https://bontoku.com/category/meigen-bonpu/chara-meigen',
    '漫画の名言': 'https://bontoku.com/category/meigen-bonpu/manga-meigen',
    'アニメの名言': 'https://bontoku.com/category/meigen-bonpu/anime-meigen',
    '偉人の名言': 'https://bontoku.com/category/meigen-bonpu/ijin',
    '映画の名言': 'https://bontoku.com/category/meigen-bonpu/movie-meigen'
}
selected_key = st.selectbox('どの名言を取得するか選択してください', list(urls.keys()))
selected_url = urls[selected_key]

# 「〇〇の名言」は複数ページで構成されているので、スクレイピングをする最大ページ数を選択します。
# 最大ページ数を設定しているのは、webサイトへの負荷低減と処理を簡素化してテストをしやすくするためです。
max_pages = st.number_input('取得する最大ページ数を入力してください:', min_value=1, value=1, step=1)


# ボタンを押してスクレイピングを開始します
# start_scraping関数の引数にurlと最大ページ数を指定するとスクレイピングを実行します
# スクレイピングした結果をデータフレームに格納して表示します
st.header('2.スクレイピングを実行します')
st.write('取得する名言と最大ページ数を選択したらボタンを押してください')
if st.button('スクレイピング開始'):
    scraped_data = meigen_scraping.start_scraping(selected_url, int(max_pages))
    if scraped_data:
        # スクレイピング結果をデータフレームに変換して表示
        st.session_state.scraped_data = pd.DataFrame(scraped_data)
        st.dataframe(st.session_state.scraped_data, use_container_width=True)
    else:
        st.write("データが見つかりませんでした。")

# 名言を取得するページを選択してスクレイピングを実行します
if 'scraped_data' in st.session_state and not st.session_state.scraped_data.empty:
    title_options = st.session_state.scraped_data['Title'].tolist()
    selected_title = st.selectbox('名言を取得するページを選択してください', options=title_options)

# 選択したページから名言のテキスト情報を取得します
if 'scraped_data' in st.session_state and 'selected_title' in locals():
    if st.button('ページから名言を抽出'):
        selected_url = st.session_state.scraped_data[st.session_state.scraped_data['Title'] == selected_title]['URL'].iloc[0]
        st.session_state.df_additional = meigen_scraping.extract_additional_info(selected_url)

# 選択したページから名言を抽出して表示します
st.write('選択したページにある名言を表示します')
if 'df_additional' in st.session_state and not st.session_state.df_additional.empty:
    st.dataframe(st.session_state.df_additional, use_container_width=True)

    # 名言の選択と表示
    if 'selected_meigen' not in st.session_state:
        st.session_state.selected_meigen = st.session_state.df_additional['Text'].iloc[0]

    meigen_options = st.session_state.df_additional['Text'].tolist()
    selected_meigen = st.selectbox('名言を選択してください', meigen_options, index=meigen_options.index(st.session_state.selected_meigen) if st.session_state.selected_meigen in meigen_options else 0)
    st.session_state.selected_meigen = selected_meigen  # 選択された名言を更新


# ボタンを押下したら名言のテキスト情報を取得して変数に格納します
st.write('取得した名言を変数に格納します')
if st.button('名言のテキスト情報を取得して変数に格納'):         
        st.write(st.session_state.selected_meigen)

# slack関数を使って変数に格納したテキストをslackに送ります
st.header('3.slackにスクレイピングした名言を送ります')
st.write('変数に格納した名言をslackに送ります')
if st.button('名言をslackに投稿'):         
    text_to_slack.send_slack_message(selected_meigen)


# GPTで生成する関数を実行します
st.header('4.OpenAI_APIを使って名言をTech0風にします')
if st.button('名言をGPTで加工'):
    output_content_text = meigen_gpt.make_meigen(st.session_state.selected_meigen)
    st.session_state.output_content_text = output_content_text

# 引数にテキストを入れるとSlackに投稿します
# チャンネルは「@charger_akari」で固定です。（詳細はtext_to_slack.pyを参照してください）
st.header('5.slackにTech0風の名言を送ります')
if st.button('GPTで改編した名言をslackに投稿'):
    # st.session_stateからoutput_content_textを参照して使用
    if 'output_content_text' in st.session_state:
        text_to_slack.send_slack_message(st.session_state.output_content_text)
    else:
        st.write("加工された名言がありません。先に「名言をGPTで加工」ボタンを押してください。")