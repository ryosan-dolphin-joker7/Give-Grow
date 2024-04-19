import streamlit as st
import pandas as pd
import sqlite3

# データベースファイルへのパス
DATABASE_PATH = "quotes_20240417_135122_加工用.db"

# データベースからデータを読み込む関数
def load_data():
    conn = sqlite3.connect(DATABASE_PATH)
    query = "SELECT * FROM quotes"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def main():
    st.title('名言ビューアー')

    # データ読み込みボタン
    if st.button('名言を読み込む'):
        df = load_data()
        if not df.empty:
            st.write(df)
        else:
            st.write("名言データが見つかりませんでした。")

if __name__ == "__main__":
    main()
