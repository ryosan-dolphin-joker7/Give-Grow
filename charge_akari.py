import streamlit as st
import pandas as pd
import requests
from PIL import Image
from googleapiclient.discovery import build
import sqlite3
import os

# 画像が保存されているフォルダのパスを指定します。
# この例では、カレントディレクトリの下にある `images` フォルダ内にあると仮定しています。
image_folder_path = 'img'  # または適切なパスに変更してください

# `os.path.join` を使用して、プラットフォームに依存しない形で画像へのパスを構築します。
favicon_path = os.path.join(image_folder_path, 'favicon.ico')

# 画像を開きます。
im = Image.open(favicon_path)

# Streamlitのページ設定を行います。
st.set_page_config(
    page_title="C_Akari", 
    page_icon=im,
    layout="wide", 
    initial_sidebar_state="auto", 
    )

# 以下は別ファイルに関数を記載して実行するためのfrom,import文です
# fromにディレクトリ名、importにファイル名を記載します
# 関数を使うときは、ファイル名.関数名()でOK

from services import meigen_gpt,text_to_slack,meigen_scraping,meigen_source
from services.edited_image import edited_image

# meigen_gpt        ：テキストをGPTに送る関数です
# text_to_slack     ：slackにテキストを送る関数です
# meigen_source     :名言から画像を取得する関数です
# edited_image   　 ：画像を編集する関数です

# DBからランダムに20件の名言を読み込む関数
def load_quotes_from_db():
    with sqlite3.connect("services/quotes_20240417_135122_加工用.db") as conn:
        return pd.read_sql_query("SELECT quote, author, url FROM quotes ORDER BY RANDOM() LIMIT 20", conn)

# Streamlitアプリケーションの初期設定
st.title('★名言の泉★')

# 説明文の設定
st.write("""
心に響く名言があなたを待っています。名言の泉は、あなたが必要とする元気とインスピレーションを提供します。このアプリは、世界中の有名な人々の名言を集め、あなたに合わせて提供します。
""")

st.subheader("機能1:名言データベース")
st.write("""
この機能は３万件以上の名言を検索し、あなたが必要とする名言を見つけるための強力なツールです。誰かを励ますための完璧な名言を見つけることができます。これは、あなたが他人に影響を与え、ポジティブなエネルギーを広めるのに役立つ機能です。
""")

st.subheader("機能2:元気チャージャーあかりちゃん")
st.write("""
あかりちゃんは、あなたの悩みに対応する名言を提供するための人工知能ボットです。あなたが現在直面している問題や悩みをあかりちゃんに伝えると、あかりちゃんはあなたが元気になる言葉を見つけてくれます。これは、あなたが困難な状況を乗り越えるための支援を提供する機能です。
""")



# タブの設定
tab1, tab2 = st.tabs(["名言データベース", "元気チャージャーあかりちゃん"])


with tab1:
    st.image('img/image_template/sample.png', caption='名言を使って元気チャージ！')

    if st.button("ランダムに名言を表示"):
        random_quotes = load_quotes_from_db()
        st.session_state.random_quotes = random_quotes
        if not random_quotes.empty:
            st.dataframe(random_quotes[['quote', 'author', 'url']])

    # 名言の選択
    if 'random_quotes' in st.session_state and not st.session_state.random_quotes.empty:
        selected_quote = st.selectbox('名言を選択してください', st.session_state.random_quotes['quote'])
        if selected_quote:
            quote_details = st.session_state.random_quotes[st.session_state.random_quotes['quote'] == selected_quote].iloc[0]
            st.write('選択された名言:', selected_quote)
            st.write('by:', quote_details['author'])
            image_url = meigen_source.fetch_image_url(selected_quote, quote_details['author'])
            if image_url:
                st.image(image_url, caption=f"名言「{selected_quote}」に関連する画像", width=300)
            else:
                st.error("関連する画像が見つかりませんでした。")
            # 画像編集機能を呼び出す
            edited_image(selected_quote, quote_details['author'])


with tab2:
    st.image('img/akari_icon.png', caption='名言を使って元気チャージ！')
    st.header("元気チャージャーあかりちゃん")
    st.sidebar.header('あかりちゃんの設定')

    # モード選択
    mode = {'自動モード': 'Auto', '手動モード': 'Manual'}
    selected_mode = st.sidebar.selectbox('手動・自動モードを選択してください', list(mode.keys()))
    st.session_state.selected_mode = mode[selected_mode]

    # スタイル選択
    types = {
        'Tech先生': 'ITテクノロジーを活用するビジネスパーソン風でウィットにとんだ文章',
        '優しい先生': '私が元気になるように優しい先生が喋りかけるような文章',
        'スパルタ先生': '私が頑張らざるを得ないように、スパルタ先生が怒るような文章',
        'わんこ先生': '語尾に「ワン」とつく文章',
        'にゃんこ先生': '「にゃんにゃん」だけで表現した文章'
    }
    selected_type = st.sidebar.selectbox('どんなスタイルにするか選択してください', list(types.keys()), index=0)
    st.session_state.selected_type = types[selected_type]


    user_msg = st.text_input("あなたの心配事やお悩みをお聞かせください。")
    if user_msg:
        st.session_state.content_text_to_gpt = user_msg
        response = f"あなたの悩み「{user_msg}」をもとに励ましメッセージを生成します。"
        st.write(response)

    if st.sidebar.button('あかりちゃんからメッセージをもらう'):
        output_text = meigen_gpt.make_meigen(st.session_state.content_text_to_gpt, "", st.session_state.selected_type)
        st.write("あかりちゃんからのメッセージ:", output_text)
        text_to_slack.send_slack_message(output_text)

    if st.sidebar.button('加工した名言をSlackに投稿'):
        text_to_slack.send_slack_message(output_text)

# アバターの設定
img_ASSISTANT = Image.open("img/akari_icon.png")
img_USER = Image.open("img/Give&Grow.png")
avatar_img_dict = {"あなた": img_USER, "あかりちゃん": img_ASSISTANT}