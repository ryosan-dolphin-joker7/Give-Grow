import streamlit as st # フロントエンドを扱うstreamlitの機能をインポート
from openai import OpenAI # openAIのchatGPTのAIを活用するための機能をインポート

# OSが持つ環境変数OPENAI_API_KEYにAPIを入力するためにosにアクセスするためのライブラリをインポート
import os 
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む（ローカル環境のみ）
if not os.getenv("CI"):
    load_dotenv()
# 環境変数を使用
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def make_meigen(content_meigen_to_gpt):

    # openAIの機能をclientに代入
    client = OpenAI()

    # chatGPTにリクエストするためのメソッドを設定。引数には書いてほしい内容と文章のテイストと最大文字数を指定
    def run_gpt(content_text_to_gpt,content_kind_of_to_gpt,content_maxStr_to_gpt,role_gpt,user_gpt):
        # リクエスト内容を決める
        request_to_gpt = user_gpt + " 悩みは" + content_text_to_gpt + content_meigen_to_gpt + "という名言を" + content_kind_of_to_gpt + "にしてください。" + content_maxStr_to_gpt + "文字以内で出力してください。"
        st.write('GPTに投げるプロンプト')# タイトル
        st.write(request_to_gpt)
        
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
        return output_content # 返って来たレスポンスの内容を返す

    # ロール
    role_gpt = "あなたはITテクノロジーを学ぶ人に対して、名言を使って励ます人です。"

    # ユーザー
    user_gpt = "私はプログラミング学習に悩んでいる人です。"

    # 悩みについて
    content_text_to_gpt = "環境構築が難しくてツライことです。"

    # 書かせたい構成
    content_contents_to_gpt = "私が元気になるように励ましてください。"

    # 書かせたい内容のテイストを選択肢として表示する
    # content_meigen_to_gpt = "神は人間によって創りあげられた 人の手によるものにすぎん ならば我々に鉄槌を下しに来るのは 神ではなくあくまで 〝人間〟だろうな"

    # 書かせたい内容のテイストを選択肢として表示する
    content_kind_of_to_gpt = "ITテクノロジーを活用するビジネスパーソン風の文章"

    # chatGPTに出力させる文字数
    content_maxStr_to_gpt = "100"

    # GPTで生成する関数を実行
    output_content_text = run_gpt(content_text_to_gpt,content_kind_of_to_gpt,content_maxStr_to_gpt,role_gpt,user_gpt)

    # 結果を表示
    st.write("GPTで生成した名言")
    st.write(output_content_text)

    return output_content_text