import streamlit as st
import pandas as pd
import sqlite3

def search_quotes(csv_file_path, keyword):
    try:
        data = pd.read_csv(csv_file_path)
        matched_quotes = data[(data['title'].str.contains(keyword, case=False)) | 
                              (data['quote'].str.contains(keyword, case=False))]
        return matched_quotes
    except FileNotFoundError:
        return None

# DBからランダムに20件の名言を読み込む関数
def load_quotes_from_db():
    with sqlite3.connect("services/quotes_20240417_135122_加工用.db") as conn:
        return pd.read_sql_query("SELECT quote, author, url FROM quotes ORDER BY RANDOM() LIMIT 20", conn)
    
# SQLiteデータベースからキーワードに基づいて名言を検索する関数
def search_quotes_from_db(keyword):
    try:
        with sqlite3.connect("services/quotes_20240417_135122_加工用.db") as conn:
            # SQLクエリでtitleとquoteカラム両方を検索
            query = """
            SELECT title, quote, author
            FROM quotes
            WHERE title LIKE ? OR quote LIKE ?
            """
            # キーワードをパーセント記号で囲んで部分一致検索を可能にする
            params = ('%' + keyword + '%', '%' + keyword + '%')
            return pd.read_sql_query(query, conn, params=params)
    except Exception as e:
        st.error(f"データベースエラー: {e}")
        return pd.DataFrame()  # エラーが発生した場合は空のDataFrameを返す