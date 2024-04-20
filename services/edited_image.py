import os
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import uuid

def add_text_to_image(image, text, position, font_name, font_size, text_color):
    """画像にテキストを挿入する関数"""
    draw = ImageDraw.Draw(image)
    try:
        # .ttcと.ttfのファイルパスをシステムフォントフォルダと/fontsフォルダで構築
        font_paths = [
            f"C:\\Windows\\Fonts\\{font_name}.ttc",
            f"C:\\Windows\\Fonts\\{font_name}.ttf",
            f"./fonts/{font_name}.ttc",
            f"./fonts/{font_name}.ttf"
        ]
        
        # 利用可能なフォントファイルを検索
        font_path = next((path for path in font_paths if os.path.exists(path)), None)
        
        if font_path:
            font = ImageFont.truetype(font_path, font_size, index=0 if font_path.endswith(".ttc") else None)
        else:
            # フォントファイルが見つからなかった場合、エラーを発生
            raise IOError
        
    except IOError:
        # フォントファイルが見つからなかった場合、デフォルトフォントを使用
        font = ImageFont.load_default()
        print(f"フォント '{font_name}' を読み込めませんでした。デフォルトフォントを使用します。")  # 例: st.warningをprintに変更していますが、必要に応じて調整してください。
    
    draw.text(position, text, font=font, fill=text_color)
    return image
    
def edited_image(selected_quote):
    # 画像アップローダーのキー生成にUUIDを使用
    unique_key = f"image_uploader_{uuid.uuid4()}"
    uploaded_file = st.file_uploader("画像をアップロードしてください", type=['png', 'jpg', 'jpeg'], key=unique_key)

    # アップロードされたファイルがあるかどうか確認
    if uploaded_file is not None:
        if 'uploaded_file_name' not in st.session_state or st.session_state.uploaded_file_name != uploaded_file.name:
            st.session_state.uploaded_file_name = uploaded_file.name
            image = Image.open(uploaded_file)
            st.session_state.image = image
            st.session_state.text_added = False  # 初回テキスト追加のためのフラグ
    else:
        # /imgフォルダ内のファイルリストを取得
        img_folder_path = './img/image_template'
        available_images = [f for f in os.listdir(img_folder_path) if os.path.isfile(os.path.join(img_folder_path, f))]
        
        # ユーザーがフォルダ内のファイルから選択できるようにする
        selected_image_file = st.selectbox('利用可能な画像を選択してください：', available_images)
        
        if selected_image_file:
            # 選択された画像ファイルを開く
            image_path = os.path.join(img_folder_path, selected_image_file)
            image = Image.open(image_path)
            st.session_state.image = image
            st.session_state.text_added = False  # 初回テキスト追加のためのフラグ

        else:
            image = st.session_state.image
        
        with st.form("text_form"):
            available_fonts = ["HGRPP1", "meiryo", "BIZ-UDGothicR", "YuGothR"]
            font_name = st.selectbox("フォントを選択してください", available_fonts, index=3)  # Yu Gothic UI Lightをデフォルト選択
            text = st.text_input("画像に挿入するテキストを入力してください", selected_quote)
            position_x = st.number_input("テキストのX座標を入力", value=100)
            position_y = st.number_input("テキストのY座標を入力", value=100)
            font_size = st.number_input("フォントサイズを入力してください", value=50, min_value=1)
            text_color = st.color_picker("テキストの色を選択してください", "#EA0D0D")
            
            submitted = st.form_submit_button("テキストを更新")

        if not st.session_state.text_added or submitted:
            # テキスト情報を更新し編集後の画像を表示
            image_with_text = add_text_to_image(image.copy(), text, (position_x, position_y), font_name, font_size, text_color)
            st.session_state.image_with_text = image_with_text
            st.session_state.text_added = True
            st.image(st.session_state.image_with_text, caption='編集後の画像')
