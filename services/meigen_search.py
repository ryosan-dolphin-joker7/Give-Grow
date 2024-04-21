import streamlit as st
import pandas as pd

def search_quotes(csv_file_path, keyword):
    try:
        data = pd.read_csv(csv_file_path)
        matched_quotes = data[(data['title'].str.contains(keyword, case=False)) | 
                              (data['quote'].str.contains(keyword, case=False))]
        return matched_quotes
    except FileNotFoundError:
        return None
