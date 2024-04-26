import pandas as pd
# スプレッドシートのデータを扱うライブラリをインポート
import gspread
# スプレッドシートの認証機能をインポート
from gspread_dataframe import set_with_dataframe
# スプレッドシートのデータとpandasライブラリのデータを紐づける機能をインポート
from google.oauth2.service_account import Credentials

# .envファイルから環境変数を読み込む（ローカル環境のみ）
if not os.getenv("CI"):
    load_dotenv()
# 環境変数を使用
    # 使用するスプレッドシートのアクセス先をSP_SHEET_KEYに代入
    # https://docs.google.com/spreadsheets/d/「ここの部分がSP_SHEET_KEYに代入される」
SP_SHEET_KEY = os.getenv("SP_SHEET_KEY")

def action_add():
    # その役割の許可をもらうAPIキーをservice_account.jsonから読み込み、credentialsに代入
    # 認証キーを使うアクセス先をscopesに代入
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]

    # その役割の許可をもらうAPIキーをservice_account.jsonから読み込み、credentialsに代入
    credentials = Credentials.from_service_account_file(
        'exalted-bonus.json',
        scopes=scopes
    )

    # 認証情報を格納しているcredentialsを使って、gspread.authorizeでスプレッドシートの使用許可を取り、その認証結果をgcに代入
    gc = gspread.authorize(credentials)

    # 開きたいスプレッドシートを認証結果を格納したgcを使ってgc.open_by_keyで開く
    sh = gc.open_by_key(SP_SHEET_KEY)

    # 参照するシート名をSP_SHEETに代入
    SP_SHEET = 'action'

    # gc.open_by_keyで開いたスプレッドシートのsampleシートをsh.worksheet(SP_SHEET)で情報を得て、worksheetに代入する
    worksheet = sh.worksheet(SP_SHEET)

    # 得られたsampleシートの情報をget_all_values()で値をすべて取得してdataに代入
    data = worksheet.get_all_values()

    # スプレッドシートにある既存のデータをデータフレームに格納し、df_oldに代入
    df_old = pd.DataFrame(data[1:], columns=data[0])

    # データを辞書形式で用意
    data = {
        '名前': ['山田太郎', '鈴木花子', '佐藤一郎'],
        '年齢': [25, 30, 22],
        '都市': ['東京', '大阪', '福岡']
    }
    # 辞書からDataFrameを作成
    df = pd.DataFrame(data)

    # 既存のデータdf_oldと区別するためにdfをdf_newとしておきます
    df_new = df # スクレイピングで取得した新しいデータdfをdf_newに代入
    df_upload = pd.concat([df_old,df_new]) # 既存のdf_oldとdf_newをpd.concatで結合
    df_upload.reset_index(drop=True,inplace=True)

    # シートにアクセス準備が出来たので、set_with_dataframe(どこに,どのデータ,データフレームで自動生成されるindex数字を含むかどうか)
    # を使ってシートにデータフレームのデータを書き込みます。
    set_with_dataframe(sh.worksheet("action"), df_upload, include_index=False)