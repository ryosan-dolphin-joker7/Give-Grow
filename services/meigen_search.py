import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from PIL import Image
from googleapiclient.discovery import build
import os


keyword = st.text_input('ここにキーワードを入力してください')

# CSVファイルのパスを指定します。
csv_file_path = '/DB/output.csv'
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