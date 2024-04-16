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


def fetch_image_url(keyword):
    print(f"Fetching image URL for keyword: {keyword}")
    service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
    try:
        result = service.cse().list(
            q=keyword,
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

