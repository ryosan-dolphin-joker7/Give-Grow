import streamlit as st
import requests
import json
import os
from dotenv import load_dotenv
from googleapiclient.discovery import build

# .envファイルから環境変数を読み込む（ローカル環境のみ）
if not os.getenv("CI"):
    load_dotenv()
# 環境変数を使用
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
CUSTOM_SEARCH_ENGINE_ID = os.getenv('CUSTOM_SEARCH_ENGINE_ID')

st.write(GOOGLE_API_KEY)
st.write(CUSTOM_SEARCH_ENGINE_ID)

def fetch_image_url(keyword, add_terms="画像"):
    # 検索キーワードに追加の用語を組み込む
    full_keyword = f"{keyword} {add_terms}"
    print(f"Fetching image URL for keyword: {full_keyword}")
    service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
    try:
        result = service.cse().list(
            q=full_keyword,  # 更新された検索キーワード
            cx=CUSTOM_SEARCH_ENGINE_ID,
            searchType='image',
            num=1
        ).execute()

        if 'items' in result:
            image_url = result['items'][0]['link']
            print(f"Image URL found: {image_url}")
            return image_url
        else:
            print("No images found.")
            return None
    except Exception as e:
        print(f"Error fetching image URL: {e}")
        return None

