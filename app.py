import streamlit as st
import replicate
from PIL import Image, ImageDraw, ImageFont
import requests
import io

st.set_page_config(page_title="AI Meme Generator", layout="centered")

st.title("😂 AI Meme Generator")
st.write("Type a prompt, let AI generate an image, then add your own meme text.")

# Load Replicate client (API token from Streamlit secrets)
@st.cache_resource
def get_client():
    return replicate.Client(api_token=st.secrets["REPLICATE_API_TOKEN"])

prompt = st.text_input("🧠 Image prompt (what should the AI draw?)")
top_text = st.text_input("⬆️ Top text (optional):")
bottom_text = st.text_input("⬇️ Bottom text (optional):")

if st.button("Generate Meme"):
    if not prompt.strip():
        st.warning("Please enter a prompt first.")
    else:
        client = get_client()
        with st.spinner("Generating image with AI... this may take a moment."):
            # Run Stable Diffusion XL on Replicate
            output = client.run(
                "stability-ai/stable-diffusion-xl:latest",
                input={
                    "prompt": prompt,
                    "width": 1024,
                    "height": 1024
                }
            )

        image_url = output[0]
        image_bytes = requests.get(image_url).content
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        draw = ImageDraw.Draw(img)

        # Use a basic font (works everywhere)
        font = ImageFont.load_default()

        def draw_centered_text(text, y_pos):
            if not text:
                return
            text = text.upper()
            text_width, text_height = draw.textsize(text, font=font)
            x = (img.width - text_width) / 2
            # simple white text with black background rectangle for contrast
            padding = 10
            rect_x0 = x - padding
            rect_y0 = y_pos - padding
            rect_x1 = x + text_width + padding
            rect_y1 = y_pos + text_height + padding
            draw.rectangle([rect_x0, rect_y0, rect_x1, rect_y1], fill="black")
            draw.text((x, y_pos), text, font=font, fill="white")

        # Draw top and bottom text
        if top_text:
            draw_centered_text(top_text, 20)
        if bottom_text:
            draw_centered_text(bottom_text, img.height - 60)

        # Show the meme
        st.image(img, caption="Generated Meme", use_column_width=True)

        # Prepare download
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)

        st.download_button(
            label="📥 Download Meme as PNG",
            data=buf,
            file_name="meme.png",
            mime="image/png"
        )
