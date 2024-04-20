import streamlit as st
import pandas as pd
import requests
from PIL import Image
from googleapiclient.discovery import build
import sqlite3

# Streamlitアプリケーションのページ設定を初期化およびカスタマイズ
st.set_page_config(layout="wide")

# データベースから名言を読み込む関数
def load_quotes_from_db():
    conn = sqlite3.connect('services\quotes_20240417_135122_加工用.db')  # 正しいパスに更新する
    df = pd.read_sql_query("SELECT * FROM quotes", conn)
    conn.close()
    return df


st.title('元気チャージャーあかりちゃん🧚‍♀️')
st.image('img/sample.png', caption='名言を使って元気チャージ！')


# 名言のデータを読み込む
quotes_df = load_quotes_from_db()

# 名言を選択するためのセレクトボックスを作成
selected_quote = st.selectbox('名言を選択してください', quotes_df['quote'])

# 選択された名言の詳細を表示
if selected_quote:
    quote_details = quotes_df[quotes_df['quote'] == selected_quote].iloc[0]
    st.write('選択された名言:', selected_quote)
    st.write('by ', quote_details['author'])

    # 名言に関連する画像を表示する
    from services import meigen_source  # 画像を取得するためのモジュール
    image_url = meigen_source.fetch_image_url(selected_quote)
    if image_url:
        st.image(image_url, caption=f"名言「{selected_quote}」に関連する画像")
    else:
        st.error("関連する画像が見つかりませんでした。")

# タイトルを設定する
st.header("励ましBOT 元気チャージャーあかりちゃん")

# 定数定義
USER_NAME = "あなた"
ASSISTANT_NAME = "あかりちゃん"

# ユーザーとアシスタントのアバターを設定
if "img_ASSISTANT" not in st.session_state:
    st.session_state.img_ASSISTANT = Image.open("img/akari_icon.png")
img_ASSISTANT = st.session_state.img_ASSISTANT

if "img_USER" not in st.session_state:
    st.session_state.img_USER = Image.open("img/Give&Grow.png")
img_USER = st.session_state.img_USER

avatar_img_dict = {
    USER_NAME: img_USER,
    ASSISTANT_NAME: img_ASSISTANT,
}

# チャットログを保存したセッション情報を初期化
if "chat_log" not in st.session_state:
    st.session_state.chat_log = []

# ユーザーの入力が送信された際に実行される処理
user_msg = st.text_input("何に悩んでいますか？")

# チャット履歴を保存するセッションステートの初期化
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# 'selected_meigen'がst.session_stateに存在しない、または空の場合、新たに設定する
if 'selected_meigen' not in st.session_state or not st.session_state.selected_meigen:
    st.session_state.selected_meigen = selected_quote

# ユーザーの入力が送信された際に実行される処理
if user_msg:
    # 'content_text_to_gpt'変数がst.session_state内に存在しない、または空であるかをチェック
    if 'content_text_to_gpt' not in st.session_state or not st.session_state.content_text_to_gpt:
        # 変数が存在しない、または空である場合、ユーザーのメッセージをcontent_text_to_gptに設定
        st.session_state.content_text_to_gpt = user_msg
        bot_response = f"あなたの悩みは「{user_msg}」なんですね。\r\nボタンを押して名言を加工しましょう"
        # ユーザーのメッセージをチャット履歴に追加
        st.session_state.chat_log.append({"name": USER_NAME, "msg": user_msg})
        # アシスタントの応答をチャット履歴に追加
        st.session_state.chat_log.append({"name": ASSISTANT_NAME, "msg": bot_response})

# GPTで生成する関数を実行します
st.sidebar.header('名言を加工してSlackに投稿します')
if st.sidebar.button('GPTで名言を加工'):
    output_content_text = meigen_gpt.make_meigen(st.session_state.selected_meigen,st.session_state.content_text_to_gpt)
    st.session_state.output_content_text = output_content_text
    st.session_state.chat_log.append({"name": ASSISTANT_NAME, "msg": "加工が完了しました。加工した名言をSlackに投稿しましょう。"})

# slack関数を使って変数に格納したテキストをslackに送ります
if st.sidebar.button('加工前の名言をslackに投稿'):
    if 'output_content_text' in st.session_state:
        text_to_slack.send_slack_message(st.session_state.selected_meigen)
        st.session_state.chat_log.append({"name": ASSISTANT_NAME, "msg": "slackに加工前の名言を投稿しました!"})
    else:
        st.session_state.chat_log.append({"name": ASSISTANT_NAME, "msg": "元にする名言が選択されていません。スクレイピングして名言を取得してください。"})

# 引数にテキストを入れるとSlackに投稿します
# チャンネルは「@charger_akari」で固定です。（詳細はtext_to_slack.pyを参照してください）
if st.sidebar.button('GPTで加工した名言をslackに投稿'):
    # st.session_stateからoutput_content_textを参照して使用
    if 'output_content_text' in st.session_state:
        text_to_slack.send_slack_message(st.session_state.output_content_text)
        st.session_state.chat_log.append({"name": ASSISTANT_NAME, "msg": "slackに加工後の名言を投稿しました!"})
    else:
        # アシスタントの応答をチャット履歴に追加
        st.session_state.chat_log.append({"name": ASSISTANT_NAME, "msg": "加工された名言がありません。先に「名言をGPTで加工」ボタンを押してください。"})

# チャット履歴を表示
for chat in st.session_state.chat_log:
    avatar = avatar_img_dict.get(chat["name"], None)
    with st.chat_message(chat["name"], avatar=avatar):
        st.write(chat["msg"])

# 画像を編集する関数を実行する
edited_image.edited_image()
