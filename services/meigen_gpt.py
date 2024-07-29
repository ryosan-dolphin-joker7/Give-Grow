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

# GPT クライアントを作成
client = OpenAI()

def make_meigen(content_text_to_gpt, selected_type):
    # ユーザーの悩みと選択したスタイルを受け取る
    content_text_to_gpt = st.session_state.content_text_to_gpt
    selected_type = st.session_state.selected_type

    # ユーザーの悩みと選択したスタイルに基づいてリクエストを生成
    request_to_gpt = f"悩みは『{content_text_to_gpt}』です。{selected_type} で励ましてください。文章は100文字以内で出力してください。"

    # GPT 応答
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": request_to_gpt},
        ],
    )

    # 生成されたテキストを取得
    generated_text = response.choices[0].message.content.strip()

    # 必要に応じて切断
    if len(generated_text) > 100:
        generated_text = generated_text[:100]

    return generated_text