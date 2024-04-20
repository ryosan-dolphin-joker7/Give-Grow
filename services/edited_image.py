import os
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

def add_text_to_image(image, text, position, font_name, font_size, text_color):
    """画像にテキストを挿入する関数"""
    draw = ImageDraw.Draw(image)
    try:
        font_paths = [
            f"C:\\Windows\\Fonts\\{font_name}.ttc",
            f"C:\\Windows\\Fonts\\{font_name}.ttf",
            f"./fonts/{font_name}.ttc",
            f"./fonts/{font_name}.ttf"
        ]
        
        font_path = next((path for path in font_paths if os.path.exists(path)), None)
        
        if font_path:
            font = ImageFont.truetype(font_path, font_size, index=0 if font_path.endswith(".ttc") else None)
        else:
            raise IOError
        
    except IOError:
        font = ImageFont.load_default()
        st.warning(f"フォント '{font_name}' を読み込めませんでした。デフォルトフォントを使用します。")
    
    draw.text(position, text, font=font, fill=text_color)
    return image
    
def edited_image(selected_quote):
    # /imgフォルダ内のファイルリストを取得
    img_folder_path = './img/image_template'
    available_images = [f for f in os.listdir(img_folder_path) if os.path.isfile(os.path.join(img_folder_path, f))]
    
    uploaded_file = st.file_uploader("画像をアップロードしてください", type=['png', 'jpg', 'jpeg'], key=f"file_uploader_{selected_quote}")

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.session_state['image'] = image
        st.session_state['text_added'] = False
    else:
        selected_image_file = st.selectbox('利用可能な画像を選択してください：', available_images, key=f"image_{selected_quote}")
        if selected_image_file:
            image_path = os.path.join(img_folder_path, selected_image_file)
            image = Image.open(image_path)
            st.session_state['image'] = image
            st.session_state['text_added'] = False
        else:
            image = st.session_state.get('image', None)

    if image:
        with st.form("text_form"):
            available_fonts = ["HGRPP1", "meiryo", "BIZ-UDGothicR", "YuGothR"]
            font_name = st.selectbox("フォントを選択してください", available_fonts, index=3)
            text = st.text_input("画像に挿入するテキストを入力してください", selected_quote)
            position_x = st.number_input("テキストのX座標を入力", value=100)
            position_y = st.number_input("テキストのY座標を入力", value=100)
            font_size = st.number_input("フォントサイズを入力してください", value=50, min_value=1)
            text_color = st.color_picker("テキストの色を選択してください", "#EA0D0D")
            
            submitted = st.form_submit_button("テキストを更新")

        if submitted or not st.session_state.get('text_added', False):
            image_with_text = add_text_to_image(image.copy(), text, (position_x, position_y), font_name, font_size, text_color)
            st.session_state['image_with_text'] = image_with_text
            st.session_state['text_added'] = True
            st.image(image_with_text, caption='編集後の画像')
