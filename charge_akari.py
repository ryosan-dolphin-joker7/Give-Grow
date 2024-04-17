import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from PIL import Image
from googleapiclient.discovery import build


# 以下は別ファイルに関数を記載して実行するためのfrom,import文です
# fromにディレクトリ名、importにファイル名を記載します
# 関数を使うときは、ファイル名.関数名()でOK

from services import meigen_gpt,text_to_slack,meigen_scraping,meigen_source

# meigen_gpt        ：テキストをGPTに送る関数です
# text_to_slack     ：slackにテキストを送る関数です
# meigen_scraping   ：ページから名言を抽出する関数です



st.set_page_config(layout="wide")
st.title('漫画の名言スクレイピング')

st.header('1.スクレイピングする名言のページを選択します')
# どのページから名言を取得するかを選択します。
urls = {
    '登場人物の名言': 'https://bontoku.com/category/meigen-bonpu/chara-meigen',
    '漫画の名言': 'https://bontoku.com/category/meigen-bonpu/manga-meigen',
    'アニメの名言': 'https://bontoku.com/category/meigen-bonpu/anime-meigen',
    '偉人の名言': 'https://bontoku.com/category/meigen-bonpu/ijin',
    '映画の名言': 'https://bontoku.com/category/meigen-bonpu/movie-meigen'
}
selected_key = st.selectbox('どの名言を取得するか選択してください', list(urls.keys()))
selected_url = urls[selected_key]

# 「〇〇の名言」は複数ページで構成されているので、スクレイピングをする最大ページ数を選択します。
# 最大ページ数を設定しているのは、webサイトへの負荷低減と処理を簡素化してテストをしやすくするためです。
max_pages = st.number_input('取得する最大ページ数を入力してください:', min_value=1, value=1, step=1)


# ボタンを押してスクレイピングを開始します
# start_scraping関数の引数にurlと最大ページ数を指定するとスクレイピングを実行します
# スクレイピングした結果をデータフレームに格納して表示します
st.header('2.スクレイピングを実行します')
st.write('取得する名言と最大ページ数を選択したらボタンを押してください')
if st.button('スクレイピング開始'):
    scraped_data = meigen_scraping.start_scraping(selected_url, int(max_pages))
    if scraped_data:
        # スクレイピング結果をデータフレームに変換して表示
        st.session_state.scraped_data = pd.DataFrame(scraped_data)
        st.dataframe(st.session_state.scraped_data, use_container_width=True)
    else:
        st.write("データが見つかりませんでした。")

# 名言を取得するページを選択してスクレイピングを実行します
if 'scraped_data' in st.session_state and not st.session_state.scraped_data.empty:
    title_options = st.session_state.scraped_data['Title'].tolist()
    selected_title = st.selectbox('名言を取得するページを選択してください', options=title_options)

# 選択したページから名言のテキスト情報を取得します
if 'scraped_data' in st.session_state and 'selected_title' in locals():
    if st.button('ページから名言を抽出'):
        selected_url = st.session_state.scraped_data[st.session_state.scraped_data['Title'] == selected_title]['URL'].iloc[0]
        st.session_state.df_additional = meigen_scraping.extract_additional_info(selected_url)

# 選択したページから名言を抽出して表示します
st.write('選択したページにある名言を表示します')
if 'df_additional' in st.session_state and not st.session_state.df_additional.empty:
    st.dataframe(st.session_state.df_additional, use_container_width=True)

    # 名言の選択と表示
    if 'selected_meigen' not in st.session_state:
        st.session_state.selected_meigen = st.session_state.df_additional['Text'].iloc[0]

    meigen_options = st.session_state.df_additional['Text'].tolist()
    selected_meigen = st.selectbox('名言を選択してください', meigen_options, index=meigen_options.index(st.session_state.selected_meigen) if st.session_state.selected_meigen in meigen_options else 0)
    st.session_state.selected_meigen = selected_meigen  # 選択された名言を更新


# ボタンを押下したら名言のテキスト情報を取得して変数に格納し、画像を検索して表示します
if st.button('名言のテキスト情報から画像を検索'):
    print("Selected quote:", st.session_state.selected_meigen)  # Debug: print the selected quote
    image_url = meigen_source.fetch_image_url(st.session_state.selected_meigen)
    if image_url:
        st.image(image_url, caption=f"名言「{st.session_state.selected_meigen}」に関連する画像")
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

# 定型のメッセージ
response = "分かりました。"
assistant_msg = "続けて入力してください"

# ユーザーの入力が送信された際に実行される処理
user_msg = st.text_input("何に悩んでいますか？")

# チャット履歴を保存するセッションステートの初期化
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# 'selected_meigen'がst.session_stateに存在しない、または空の場合、新たに設定する
if 'selected_meigen' not in st.session_state or not st.session_state.selected_meigen:
    st.session_state.selected_meigen = ""

# ユーザーの入力が送信された際に実行される処理
if user_msg:
    # content_text_to_gpt変数がst.session_state内に存在しない、または空であるかをチェック
    if 'content_text_to_gpt' not in st.session_state or not st.session_state.content_text_to_gpt:
        # 変数が存在しない、または空である場合、ユーザーのメッセージをcontent_text_to_gptに設定
        st.session_state.content_text_to_gpt = user_msg
        bot_response = f"あなたの悩みは「{user_msg}」なんですね。\r\nボタンを押して名言を加工しましょう"
    elif 'content_text_to_gpt' not in st.session_state or not st.session_state.content_text_to_gpt:
        # 変数が存在しない、または空である場合、ユーザーのメッセージを新規に設定
        st.session_state.content_text_to_gpt = user_msg
        bot_response = f"あなたの悩みは「{user_msg}」なんですね。\r\nボタンを押して名言を加工しましょう"
    else:
        # 変数が存在し、ユーザーのメッセージが前回と同じ場合、メッセージを変更せずに既定の応答を行う
        bot_response = "同じ悩みが既に設定されています。\r\nボタンを押して名言を加工しましょう"

# ユーザーの入力が送信された際に実行される処理
if user_msg:
    # 'content_text_to_gpt'変数がst.session_state内に存在しない場合、または新しいメッセージが前回のものと異なる場合
    # ユーザーが何も入力していない場合、または同じメッセージを再度入力した場合は、何も処理しない
    if 'content_text_to_gpt' not in st.session_state or (st.session_state.content_text_to_gpt != user_msg):
        # ユーザーが初めてメッセージを入力した場合
        if 'content_text_to_gpt' not in st.session_state:
            bot_response = f"あなたの悩みは「{user_msg}」なんですね。ボタンを押して名言を加工しましょう"
        # ユーザーが新しいメッセージを入力し、それが前回のメッセージと異なる場合
        else:
            bot_response = f"あなたの悩みを「{user_msg}」に変更しました。ボタンを押して名言を加工しましょう"
        
        # st.session_stateの更新
        st.session_state.content_text_to_gpt = user_msg

        # 応答メッセージの表示
        st.write(bot_response)

    # ユーザーのメッセージをチャット履歴に追加
    st.session_state.chat_log.append({"name": USER_NAME, "msg": user_msg})
    # アシスタントの応答をチャット履歴に追加
    st.session_state.chat_log.append({"name": ASSISTANT_NAME, "msg": bot_response})

else:
    # ユーザーが何も入力していない場合の処理
    bot_response = "何か入力してください。"


# GPTで生成する関数を実行します
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
