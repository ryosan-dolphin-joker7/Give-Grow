import os
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

def draw_multiline_text(draw, text, position, font, text_color, max_width):
    """指定した幅でテキストを改行して描画する"""
    lines = []
    words = text.split()
    current_line = ""
    for word in words:
        test_line = current_line + " " + word if current_line else word
        # Check if the width of the line with this word exceeds the max_width
        width = font.getbbox(test_line)[2]  # Get the width from getbbox
        if width > max_width:
            lines.append(current_line)  # Add the current line without this word
            current_line = word  # Start a new line with this word
        else:
            current_line = test_line
    lines.append(current_line)  # Add the last line

    y_text = position[1]
    for line in lines:
        draw.text((position[0], y_text), line, font=font, fill=text_color)
        y_text += font.getbbox(line)[3]  # Move text position for the next line based on height from getbbox

def add_text_to_image(image, text, position, font_name, font_size, text_color, max_width=300):
    """画像にテキストを挿入する関数"""
    draw = ImageDraw.Draw(image)
    font_paths = [
        f"C:\\Windows\\Fonts\\{font_name}.otf",
        f"C:\\Windows\\Fonts\\{font_name}.ttc",
        f"C:\\Windows\\Fonts\\{font_name}.ttf",
        f"./fonts/{font_name}.otf",
        f"./fonts/{font_name}.ttc",
        f"./fonts/{font_name}.ttf"
    ]
    font = None
    for path in font_paths:
        if os.path.exists(path):
            try:
                font = ImageFont.truetype(path, font_size)
                break
            except Exception as e:
                st.error(f"フォント '{path}' の読み込み中にエラーが発生しました: {e}")

    if not font:
        font = ImageFont.load_default()
        st.warning(f"フォント '{font_name}' を読み込めませんでした。デフォルトフォントを使用します。")

    draw_multiline_text(draw, text, position, font, text_color, max_width)
    return image

def edited_image(selected_quote):
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
    if image:
        with st.form("text_form"):
            available_fonts = ["NotoSerifJP-Black", "NotoSerifJP-Bold", "NotoSerifJP-SemiBold","HGRPP1", "meiryo", "meiryob", "BIZ-UDGothicR", "BIZ-UDGothicB", "YuGothR", "YuGothB", ]
            font_name = st.selectbox("フォントを選択してください", available_fonts, index=3)
            text = st.text_input("画像に挿入するテキストを入力してください。スペースで改行できます。", selected_quote)
            position_x = st.slider("テキストのX座標を入力", 0, 500, 70)
            position_y = st.slider("テキストのY座標を入力", 0, 100, 60)
            font_size = st.number_input("フォントサイズを入力してください", value=35, min_value=1)
            text_color = st.color_picker("テキストの色を選択してください", "#141313")
            max_width = st.slider("テキストの最大幅を設定", 5, 30, 12)
            
            submitted = st.form_submit_button("テキストを更新")

        if submitted or not st.session_state.get('text_added', False):
            image_with_text = add_text_to_image(image.copy(), text, (position_x, position_y), font_name, font_size, text_color, max_width)
            st.session_state['image_with_text'] = image_with_text
            st.session_state['text_added'] = True
            st.image(image_with_text, caption='画像が生成されました🧙‍♀️')
