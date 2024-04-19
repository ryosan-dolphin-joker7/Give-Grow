# StreamlitのSecretsを使用して環境変数からクレデンシャルを読み込む場合のCSV読み込み

import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# スプレッドシートにアクセスする関数
def access_spreadsheet():
    # StreamlitのSecretsから認証情報を取得
    creds_dict = {
        'type': st.secrets["type"],
        'project_id': st.secrets["project_id"],
        'private_key_id': st.secrets["private_key_id"],
        'private_key': st.secrets["private_key"],
        'client_email': st.secrets["client_email"],
        'client_id': st.secrets["client_id"],
        'auth_uri': st.secrets["auth_uri"],
        'token_uri': st.secrets["token_uri"],
        'auth_provider_x509_cert_url': st.secrets["auth_provider_x509_cert_url"],
        'client_x509_cert_url': st.secrets["client_x509_cert_url"]
    }
    
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open("quotes_GAS").sheet1
    data = sheet.get_all_records()
    return pd.DataFrame(data)

# Streamlitアプリのメイン関数
def main():
    st.title('Streamlit App with Google Sheets')

    if st.button('Load Quotes'):
        df = access_spreadsheet()
        if not df.empty:
            st.write(df)
        else:
            st.error("No data found in the spreadsheet.")

if __name__ == "__main__":
    main()
