import streamlit as st
import pandas as pd

def search_and_display_quotes(csv_file_path, keyword):
    try:
        # CSVファイルを読み込む
        data = pd.read_csv(csv_file_path)
        
        # キーワードに一致する名言を検索する
        matched_quotes = data[(data['title'].str.contains(keyword, case=False)) | 
                              (data['quote'].str.contains(keyword, case=False))]
        
        if not matched_quotes.empty:
            # 一致した名言をデータフレームとして表示する
            st.dataframe(matched_quotes, use_container_width=True)
            
            # プルダウンで名言を選択できるようにする
            quote_options = matched_quotes['quote'].tolist()
            # セッション状態を使用して選択された名言を保存する
            if 'selected_quote' not in st.session_state:
                st.session_state['selected_quote'] = quote_options[0]
            selected_quote = st.selectbox('プルダウンで名言を1つ選択してください', 
                                          quote_options, 
                                          index=quote_options.index(st.session_state['selected_quote']))
            st.session_state['selected_quote'] = selected_quote
        else:
            st.write("一致する名言が見つかりませんでした。")
            
    except FileNotFoundError:
        st.write(f"指定されたファイルパス '{csv_file_path}' が見つかりません。")