import os
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

def add_text_to_image(image, text, position, font_name, font_size, text_color):
    """画像にテキストを挿入する関数"""
    draw = ImageDraw.Draw(image)
    try:
        # .ttcと.ttfのファイルパスを構築
        font_path_ttc = f"C:\\Windows\\Fonts\\{font_name}.ttc"
        font_path_ttf = f"C:\\Windows\\Fonts\\{font_name}.ttf"
        
        # .ttcファイルが存在するか確認
        if os.path.exists(font_path_ttc):
            font = ImageFont.truetype(font_path_ttc, font_size, index=0)  # .ttcファイル用
        # .ttfファイルが存在するか確認
        elif os.path.exists(font_path_ttf):
            font = ImageFont.truetype(font_path_ttf, font_size)  # .ttfファイル用
        else:
            # ファイルが存在しない場合、デフォルトフォントを使用
            raise IOError
        
    except IOError:
        # フォントファイルが見つからなかった場合、デフォルトフォントを使用
        font = ImageFont.load_default()
        st.warning(f"フォント '{font_name}' を読み込めませんでした。デフォルトフォントを使用します。")
    
    draw.text(position, text, font=font, fill=text_color)
    return image

def edited_image():
    st.title('画像編集アプリ')

    uploaded_file = st.file_uploader("画像をアップロードしてください", type=['png', 'jpg', 'jpeg'], key="image_uploader")

    if uploaded_file is not None:
        if 'uploaded_file_name' not in st.session_state or st.session_state.uploaded_file_name != uploaded_file.name:
            st.session_state.uploaded_file_name = uploaded_file.name
            image = Image.open(uploaded_file)
            st.session_state.image = image
            st.session_state.text_added = False  # 初回テキスト追加のためのフラグ

        else:
            image = st.session_state.image
        
        with st.form("text_form"):
            available_fonts = ["HGRPP1", "meiryo", "BIZ-UDGothicR", "YuGothR"]
            font_name = st.selectbox("フォントを選択してください", available_fonts, index=3)  # Yu Gothic UI Lightをデフォルト選択
            text = st.text_input("画像に挿入するテキストを入力してください", "Streamlitで挿入した文字列")
            position_x = st.number_input("テキストのX座標を入力", value=100)
            position_y = st.number_input("テキストのY座標を入力", value=100)
            font_size = st.number_input("フォントサイズを入力してください", value=100, min_value=1)
            text_color = st.color_picker("テキストの色を選択してください", "#EA0D0D")
            
            submitted = st.form_submit_button("テキストを更新")

        if not st.session_state.text_added or submitted:
            # テキスト情報を更新し編集後の画像を表示
            image_with_text = add_text_to_image(image.copy(), text, (position_x, position_y), font_name, font_size, text_color)
            st.session_state.image_with_text = image_with_text
            st.session_state.text_added = True
            st.image(st.session_state.image_with_text, caption='編集後の画像')

edited_image()
