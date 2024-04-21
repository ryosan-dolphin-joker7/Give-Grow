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

def edited_image(selected_quote, selected_author,index):
    # index引数を使ってフォームのkeyを一意にする
    form_key = f"text_form_{index}"
    # with st.form(key=form_key)
    img_folder_path = './img/image_template'
    available_images = [f for f in os.listdir(img_folder_path) if os.path.isfile(os.path.join(img_folder_path, f))]
    st.markdown('##')
    st.subheader("③ 名言を入れ込む画像を用意してください")
    uploaded_file = st.file_uploader("③-A アップロード  ⚠️任意の画像がない場合はUP不要", type=['png', 'jpg', 'jpeg'], key=f"file_uploader_{selected_quote}")

    image = None
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.session_state['image'] = image
        st.session_state['text_added'] = False
    else:
        selected_image_file = st.selectbox('③-B テンプレートから選択  ✨オススメ', available_images, key=f"image_{selected_quote}")
        st.markdown('##')
        if selected_image_file:
            image_path = os.path.join(img_folder_path, selected_image_file)
            image = Image.open(image_path)
            st.session_state['image'] = image
            st.session_state['text_added'] = False

    if image:
        with st.form(key=form_key):
            # 共通のフォント選択
            available_fonts = ["NotoSerifJP-Black", "NotoSerifJP-Bold", "NotoSerifJP-SemiBold", "meiryo", "meiryob", "BIZ-UDGothicR", "BIZ-UDGothicB", "YuGothR", "YuGothB", "HGRPP1"]
            st.subheader("""
④必要に応じて文字のフォント・改行・位置を調整してください
""")
            font_name = st.selectbox("フォントを選択", available_fonts, index=3)

            # 名言の入力
            quote_text = st.text_input("名言の調整 ❔スペースを空けると改行できます", selected_quote)
            quote_position_x = st.slider("名言のX座標を入力", 0, 500, 70)
            quote_position_y = st.slider("名言のY座標を入力", 0, 500, 60)
            quote_font_size = st.number_input("名言のフォントサイズを入力", value=35, min_value=1, key='quote_font_size')
            quote_text_color = st.color_picker("名言の色を選択", "#141313")
            quote_max_width = st.slider("名言の最大幅を設定", 200, 1000, 500)

            # 著者の入力
            author_text = st.text_input("元ネタの調整", "by " + selected_author)
            author_position_x = st.slider("著者名のX座標を入力", 0, 500, 200)
            author_position_y = st.slider("著者名のY座標を入力", 0, 500, 200)
            author_font_size = st.number_input("著者名のフォントサイズを入力", value=15, min_value=1, key='author_font_size')
            author_text_color = st.color_picker("著者名の色を選択", "#141313")
            author_max_width = st.slider("著者名の最大幅を設定", 200, 1000, 300)

            submitted = st.form_submit_button("変更を反映")

            if submitted or not st.session_state.get('text_added', False):
                # 名言を画像に追加
                image_with_text = add_text_to_image(image.copy(), quote_text, (quote_position_x, quote_position_y), font_name, quote_font_size, quote_text_color, quote_max_width)
                # 著者を画像に追加
                image_with_text = add_text_to_image(image_with_text, author_text, (author_position_x, author_position_y), font_name, author_font_size, author_text_color, author_max_width)
                st.session_state['image_with_text'] = image_with_text
                st.session_state['text_added'] = True
                st.image(image_with_text, caption='🧙‍♀️画像が生成されました')
