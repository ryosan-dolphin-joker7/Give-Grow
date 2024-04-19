import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# スプレッドシートにアクセス
def access_spreadsheet():
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('chargeakari-key.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open("quotes_GAS").sheet1
    data = sheet.get_all_records()
    return pd.DataFrame(data)

# Streamlitアプリ
def main():
    st.title('Streamlit App')

    if st.button('Load Quotes'):
        df = access_spreadsheet()
        st.write(df)

if __name__ == "__main__":
    main()
