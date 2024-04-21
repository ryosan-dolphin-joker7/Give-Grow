import streamlit as st
import pandas as pd
import requests
from PIL import Image
from googleapiclient.discovery import build
import sqlite3
import time
import threading
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
from services.meigen_gpt import make_meigen
from services.text_to_slack import send_slack_message
from services.meigen_search import search_quotes

# meigen_gpt        ：テキストをGPTに送る関数です
# text_to_slack     ：slackにテキストを送る関数です
# meigen_source     :名言から画像を取得する関数です
# edited_image   　 ：画像を編集する関数です

# DBからランダムに20件の名言を読み込む関数
def load_quotes_from_db():
    with sqlite3.connect("services/quotes_20240417_135122_加工用.db") as conn:
        return pd.read_sql_query("SELECT quote, author, url FROM quotes ORDER BY RANDOM() LIMIT 20", conn)

# Streamlitアプリケーションの初期設定
st.title('⛲名言の泉⛲')

# 説明文の設定
st.write("""
心に響く名言があなたを待っています。名言の泉は、あなたが必要とする元気とインスピレーションを提供します。このアプリは、世界中の有名な人々の名言を集め、あなたに合わせて提供します。
""")
st.markdown('##')

st.header("アプリ概要")
st.write("名言の泉は以下の2つの機能で構成されています。")
st.subheader("🐉名言元気玉")
st.write("""
３万件の名言から、あなたが必要とする名言を見つけるための強力なツールです。あなたの大切な組織を励ますための完璧な名言を見つけることができます。元気玉によって、あなたのコミュニティにポジティブなエネルギーを広めるのに役立ちます。
""")

st.subheader("🧚元気チャージャーあかりちゃん")
st.write("""
あなたが直面している課題や悩みに対して名言のメタファーを取り入れて励ましてくれるAIです。あかりちゃんは、あなたが困難な状況を乗り越えるための頼もしいパートナーです。
""")
st.markdown('##')



# タブの設定
tab1, tab2 = st.tabs(["🐉名言元気玉", "🧚元気チャージャーあかりちゃん"])


with tab1:
    st.image('img/genkidama2.png')
    st.subheader("① 名言を抽出してください")

    # 初期化
    if 'quote_options' not in st.session_state:
        st.session_state.quote_options = []
    if 'selected_quote' not in st.session_state:
        st.session_state.selected_quote = ""
    if 'matched_quotes' not in st.session_state:
        st.session_state.matched_quotes = ""

    # ユーザー入力
    keyword = st.text_input('ここにキーワードを入力してください', key="keyword")

    # 検索ボタンが押されたときの処理
    if st.button("名言を検索", key="search"):
        if keyword:  # キーワードが入力されているか確認
            matched_quotes = search_quotes('DB/output.csv', keyword)
            if matched_quotes is not None and not matched_quotes.empty:
                # 検索結果をセッションステートに保存（quote）
                # st.session_state.quote_options = matched_quotes['quote'].tolist()

                # 検索結果をセッションステートに保存（quote, author）
                st.session_state.quote_options = [(quote, author) for quote, author in zip(matched_quotes['quote'], matched_quotes['author'])]
                # 最初の選択肢をデフォルトとして選択された名言に設定
                st.session_state.selected_quote = st.session_state.quote_options[0]
                # 一致した名言をデータフレームとして表示
                st.dataframe(matched_quotes, use_container_width=True)
            else:
                st.write("一致する名言が見つかりませんでした。")
        else:
            st.write("キーワードを入力してください。")

        # quoteをキーとし、対応するauthorを値とする辞書をセッションステートに保存
        st.session_state.quote_author_mapping = {quote: author for quote, author in zip(matched_quotes['quote'], matched_quotes['author'])}
        
        # プルダウンの選択肢としてquoteのみを表示
        st.session_state.quote_options = list(st.session_state.quote_author_mapping.keys())
        st.session_state.selected_quote = st.session_state.quote_options[0]

    # 検索結果がある場合にのみプルダウンを表示
    if st.session_state.quote_options:
        selected_quote_text = st.selectbox(
            'プルダウンで名言を1つ選択してください',
            st.session_state.quote_options,
            index=st.session_state.quote_options.index(st.session_state.selected_quote) if st.session_state.selected_quote in st.session_state.quote_options else 0,
            key="selected_quote_dyn"
        )
        # 選択されたquoteに基づいて、対応するauthorを取得
        selected_author = st.session_state.quote_author_mapping[selected_quote_text]
        # 選択されたquoteとauthorを保存
        st.session_state.selected_quote = (selected_quote_text, selected_author)
        # 選択された名言を表示
        st.write(f"選択した名言:\n{st.session_state.selected_quote[0]}")

    # 選択した名言の画像を検索します
    if st.button("選択した名言を使う"):
        # 名言の選択
        if st.session_state.selected_quote:
            st.write('選択された名言:', st.session_state.selected_quote[0])
            image_url = meigen_source.fetch_image_url(st.session_state.selected_quote[0], st.session_state.selected_quote[1])
            if image_url:
                st.image(image_url, caption=f"名言「{st.session_state.selected_quote[0]}」に関連する画像", width=300)
            else:
                st.error("関連する画像が見つかりませんでした。")
            # 画像編集機能を呼び出す
            edited_image(st.session_state.selected_quote[0], st.session_state.selected_quote[1])


    # 名言をDBからランダムで抽出する
    if st.button("ランダムに名言を抽出"):
        random_quotes = load_quotes_from_db()
        st.session_state.random_quotes = random_quotes
        if not random_quotes.empty:
            st.dataframe(random_quotes[['quote', 'author', 'url']])

    # 名言の選択
    if 'random_quotes' in st.session_state and not st.session_state.random_quotes.empty:
        st.markdown('##')
        st.subheader("② 名言を選択してください")
        selected_quote = st.selectbox('', st.session_state.random_quotes['quote'])
        if selected_quote:
            quote_details = st.session_state.random_quotes[st.session_state.random_quotes['quote'] == selected_quote].iloc[0]
            st.write('選択された名言:', "『" + selected_quote + "』 by:" + quote_details['author'])
            image_url = meigen_source.fetch_image_url(selected_quote, quote_details['author'])
            if image_url:
                st.image(image_url, width=300, caption="参考画像")  # 画像を表示
            else:
                st.error("関連する画像が見つかりませんでした。")
            # 画像編集機能を呼び出す
            edited_image(selected_quote, quote_details['author'])

with tab2:
    st.image('img/akari_header.png')
    st.subheader('あかりちゃんの設定')

    # モード選択
    mode = {'手動モード': 'Manual','自動モード': 'Auto' }
    st.write("""
            👋手動モードでは、あかりちゃんのメッセージのスタイルやSlackへの投稿をあなた自身がコントロールできます。\n
            💻自動モードでは、あかりちゃんがメッセージのスタイルやSlackへの投稿を全て管理します。
            """)
    
    selected_mode = st.selectbox('手動モード・自動モードを選択してください', list(mode.keys()))
    st.session_state.selected_mode = mode[selected_mode]

    # スタイル選択
    types = {
        'Tech先生': 'ITテクノロジーを活用するビジネスパーソン風でウィットにとんだ文章',
        '優しい先生': '私が元気になるように優しい先生が喋りかけるような文章',
        'スパルタ先生': '私が頑張らざるを得ないように、スパルタ先生が怒るような文章',
        'わんこ先生': '語尾に「ワン」とつく文章',
        'にゃんこ先生': '「にゃんにゃん」だけで表現した文章'
    }
    selected_type = st.selectbox('あかりちゃんのメッセージのスタイルを選択してください', list(types.keys()), index=0)
    st.session_state.selected_type = types[selected_type]


    user_msg = st.text_input("あなたの心配事やお悩みをあかりちゃんに教えてください。")
    if user_msg:
        st.session_state.content_text_to_gpt = user_msg
        response = f"あなたの悩み「{user_msg}」をもとに、私（あかり）は、あなたに励ましのメッセージを贈ります。"
        st.write(response)

    # モード判定
    if st.session_state.selected_mode == "自動モード":
        # 自動モードの場合
        # ユーザーの悩みと選択スタイルを取得
        content_text_to_gpt = st.session_state.content_text_to_gpt
        selected_type = st.session_state.selected_type

        # Initialize session state
        if 'output_text' not in st.session_state:
            st.session_state.output_text = None
        
        #  ユーザーが悩みを入力変更されたときに自動処理をトリガー
        if st.session_state.content_text_to_gpt != user_msg:
            # GPT で励ましのメッセージを生成
            output_text = meigen_gpt.make_meigen(content_text_to_gpt, selected_type)
            st.session_state.output_text = output_text

            # 生成されたメッセージを出力
            if st.session_state.output_text:
                time.sleep(2) # 2秒間待ってからメッセージを表示
                st.write("あかりちゃんからのメッセージ:", st.session_state.output_text)

            # Slackに投稿
            if st.session_state.output_text:
                text_to_slack.send_slack_message(st.session_state.output_text)
              
            # Clear session state after posting to Slack
            st.session_state.output_text = None

        

    else:
      # 手動モードの場合
      if st.button('あかりちゃんからメッセージをもらう'):
        # ユーザーの悩みと選択スタイルを取得
        content_text_to_gpt = st.session_state.content_text_to_gpt
        selected_type = st.session_state.selected_type

        # Initialize session state
        if 'output_text' not in st.session_state:
            st.session_state.output_text = None
           
        # GPT で励ましのメッセージを生成
        output_text = meigen_gpt.make_meigen(content_text_to_gpt, selected_type)
        st.session_state.output_text = output_text

        # 生成されたメッセージを出力
        if st.session_state.output_text:
           time.sleep(2) # 2秒間待ってからメッセージを表示
           st.write("あかりちゃんからのメッセージ:", st.session_state.output_text)

      # Slackに投稿するボタンがクリックされた場合
      if st.button('あかりちゃんからのメッセージをSlackに投稿'):
          # メッセージが存在する場合、それをSlackに投稿
          if st.session_state.output_text:
              text_to_slack.send_slack_message(st.session_state.output_text)
              st.write("メッセージがSlackに投稿されました")

          # Slackに投稿した後でセッション状態をクリア
          st.session_state.output_text = None
