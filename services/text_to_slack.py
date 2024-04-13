import requests
import os
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む（ローカル環境のみ）
if not os.getenv("CI"):
    load_dotenv()
# 環境変数を使用
SLACK_API_KEY = os.getenv("SLACK_API_KEY")

# SLACK_API_KEYを取得できているかを確認したいときは、以下のコードを有効にして表示させます
# st.write(SLACK_API_KEY)

# slackにメッセージを飛ばす関数
def send_slack_message(output_content_text, token=SLACK_API_KEY, channel='#charger_akari'):
    """
    Slackの指定されたチャンネルにメッセージを送信します。

    Parameters:
        output_content_text (str): 送信するメッセージの内容。
        token (str): Slack APIの認証トークン。デフォルトは'xxx'。
        channel (str): メッセージを送信するチャンネル。デフォルトは'#charger_akari'。
    """
    url = "https://slack.com/api/chat.postMessage"
    headers = {"Authorization": "Bearer " + token}
    data = {
        'channel': channel,
        'text': output_content_text
    }
    response = requests.post(url, headers=headers, data=data)
    print("Return: ", response.json())