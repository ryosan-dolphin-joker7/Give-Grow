import streamlit as st
import requests
import json
import os
from dotenv import load_dotenv
from googleapiclient.discovery import build
from io import BytesIO
from PIL import Image

# .envファイルから環境変数を読み込む（ローカル環境のみ）
if not os.getenv("CI"):
    load_dotenv()
# 環境変数を使用
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
CUSTOM_SEARCH_ENGINE_ID = os.getenv('CUSTOM_SEARCH_ENGINE_ID')


def fetch_image_url(quote, author, add_terms="画像"):
    # 名言と著者名を組み合わせた検索キーワードを生成
    full_keyword = f"{quote} {author} {add_terms}"
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

def fetch_image_data(image_url):
    """指定されたURLから画像データを取得する"""
    try:
        response = requests.get(image_url)
        response.raise_for_status()  # ステータスコードが200系以外の場合は例外を発生させる
        return BytesIO(response.content)  # バイトデータをBytesIOオブジェクトに変換して返す
    except Exception as e:
        print(f"Error fetching image data: {e}")
        return None