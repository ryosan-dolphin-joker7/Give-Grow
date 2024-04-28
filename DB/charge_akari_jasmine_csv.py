import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from PIL import Image
from googleapiclient.discovery import build
import os

# 以下は別ファイルに関数を記載して実行するためのfrom,import文です
# fromにディレクトリ名、importにファイル名を記載します
# 関数を使うときは、ファイル名.関数名()でOK

from services import meigen_gpt,text_to_slack,meigen_scraping,meigen_source

# meigen_gpt        ：テキストをGPTに送る関数です
# text_to_slack     ：slackにテキストを送る関数です
# meigen_scraping   ：ページから名言を抽出する関数です



st.set_page_config(layout="wide")
st.title('名言を検索')
keyword = st.text_input('ここにキーワードを入力してください')

# CSVファイルのパスを指定します。
csv_file_path = 'C:/Users/jiebing/Desktop/Give-Grow/DB/output.csv'
data = pd.read_csv(csv_file_path)

# ユーザーが入力したキーワードに一致する名言を検索します
matched_quotes = data[(data['title'].str.contains(keyword, case=False)) | (data['quote'].str.contains(keyword, case=False))]

if not matched_quotes.empty:
    st.dataframe(matched_quotes, use_container_width=True)
    
    # プルダウンで名言を選択できるようにします
    quote_options = matched_quotes['quote'].tolist()
    selected_quote = st.selectbox('プルダウンで名言を1つ選択してください', quote_options)
    st.write(f"選択した名言:\n{selected_quote}")
else:
    st.write("一致する名言が見つかりませんでした。")