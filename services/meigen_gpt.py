import streamlit as st
from openai import OpenAI # openAIのchatGPTのAIを活用するための機能をインポート

# OSが持つ環境変数OPENAI_API_KEYにAPIを入力するためにosにアクセスするためのライブラリをインポート
import os 
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む（ローカル環境のみ）
if not os.getenv("CI"):
    load_dotenv()
# 環境変数を使用
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def make_meigen(content_meigen_to_gpt,content_text_to_gpt,selected_type):

    # openAIの機能をclientに代入
    client = OpenAI()

    # ロール
    role_gpt = "あなたはITテクノロジーを学ぶ人に対して、名言を使って励ます人です。"

    # ユーザー
    user_gpt = "私はプログラミング学習に悩んでいる人です。"

    # 名言について
    if content_meigen_to_gpt == "":
        content_meigen_to_gpt = "でも、もしオレがここであきらめたら一生会えない気がする、だから退かない"

    # 悩みについて
    if content_text_to_gpt == "":
        content_text_to_gpt = "環境構築が難しくてツライことです。"

    # 書かせたい文章スタイル
    if selected_type == "":
        selected_type = "論理的に淡々と喋りかける風"

    # chatGPTに出力させる文字数
    content_maxStr_to_gpt = "100"

    # chatGPTにリクエストするためのメソッドを設定。引数には書いてほしい内容と文章のテイストと最大文字数を指定
    def run_gpt(content_meigen_to_gpt,content_text_to_gpt,selected_type,content_maxStr_to_gpt,role_gpt,user_gpt):
        # リクエスト内容を決める
        request_to_gpt = user_gpt + " 悩みは『" + content_text_to_gpt + "』です。『" + content_meigen_to_gpt + "』という名言を『" + selected_type + "』にして励ましてください。文章は" + content_maxStr_to_gpt + "文字以内で出力してください。"

        
        # 決めた内容を元にclient.chat.completions.createでchatGPTにリクエスト。オプションとしてmodelにAIモデル、messagesに内容を指定
        response =  client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role":"system", "content": role_gpt },
                {"role":"user", "content": request_to_gpt },
            ],
        )

        # 返って来たレスポンスの内容はresponse.choices[0].message.content.strip()に格納されているので、これをoutput_contentに代入
        output_content = response.choices[0].message.content.strip()
        return request_to_gpt,output_content # 返って来たレスポンスの内容を返す

    # GPTで生成する関数を実行
    request_content_text,output_content_text = run_gpt(content_meigen_to_gpt,content_text_to_gpt,selected_type,content_maxStr_to_gpt,role_gpt,user_gpt)

    return request_content_text,output_content_text