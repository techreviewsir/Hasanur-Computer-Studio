import io
import cv2
import numpy as np
from PIL import Image, ImageOps
import streamlit as st
from rembg import remove, new_session
from pypdf import PdfReader

# পেজের লেআউট এবং কাস্টম হভার স্টাইল (CSS) সেটআপ
st.set_page_config(page_title="Hasanur Computer Studio", layout="wide")

st.markdown("""
<style>
    /* সাইডবারের রেডিও বাটন বা অপশনগুলোর জন্য প্রিমিয়াম হভার এবং স্টাইল */
    .stRadio > label {
        background-color: #f0f2f6;
        padding: 10px 15px;
        border-radius: 8px;
        margin-bottom: 5px;
        transition: all 0.3s ease;
        font-weight: 500;
    }
    .stRadio > label:hover {
        background-color: #ff4b4b;
        color: white;
        padding-left: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
</style>
""", unsafe_allow_html=True)

st.title("🖨️ Hasanur Computer Studio - Interactive 11-in-1 Dashboard")
st.markdown("---")

# সাইডবার মেনু (হভার ইফেক্টযুক্ত রেডিও বাটন মোড)
st.sidebar.header("Navigation Menu (11 Modules)")
app_mode = st.sidebar.radio("Choose a Tool", [
    "1. Smart AI Background Remover",
    "2. Custom Background Color Studio",
    "3. Image Enhancer & Brightness",
    "4. ID Card Cropper & Straightener",
    "5. Passport Photo Maker (4-in-1)",
    "6. Image Resizer & Compressor",
    "7. Grayscale & Black-White Converter",
    "8. Image Rotator & Flipper",
    "9. Border & Frame Adder",
    "10. Watermark Adder",
    "11. PDF to Image Converter"
])

# =====================================================================
# 1. Smart AI Background Remover
# =====================================================================
if app_mode == "1. Smart AI Background Remover":
    st.header("✨ Smart AI Background Remover (Transparent)")
    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"], key="m1")

    if uploaded_file is not None:
        col1, col2 = st.columns(2)
        with col1:
            st.image(Image.open(uploaded_file), use_container_width=True, caption="Original")
        with col2:
            if st.button("Remove Background"):
                with st.spinner("Processing with AI..."):
                    session = new_session("u2net")
                    output_bytes = remove(uploaded_file.getvalue(), session=session)
                    out_img = Image.open(io.BytesIO(output_bytes))
                    st.image(out_img, use_container_width=True, caption="Transparent Output")
                    
                    buf = io.BytesIO()
                    out_img.save(buf, format="PNG")
                    st.download_button("Download Transparent PNG", buf.getvalue(), "transparent.png", "image/png")

# =====================================================================
# 2. Custom Background Color Studio
# =====================================================================
elif app_mode == "2. Custom Background Color Studio":
    st.header("🎨 Custom Background Color Studio")
    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"], key="m2")
    bg_color = st.color_picker("Pick Background Color", "#FFFFFF")

    if uploaded_file is not None:
        col1, col2 = st.columns(2)
        with col1:
            st.image(Image.open(uploaded_file), use_container_width=True, caption="Original")
        with col2:
            if st.button("Change Background"):
                with st.spinner("Processing..."):
                    session = new_session("u2net")
                    output_bytes = remove(uploaded_file.getvalue(), session=session)
                    foreground = Image.open(io.BytesIO(output_bytes)).convert("RGBA")
                    
                    hex_code = bg_color.lstrip('#')
                    bg_rgb = tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))
                    
                    background = Image.new("RGBA", foreground.size, bg_rgb + (255,))
                    final_image = Image.alpha_composite(background, foreground).convert("RGB")
                    
                    st.image(final_image, use_container_width=True, caption="Custom Background Output")
                    
                    buf = io.BytesIO()
                    final_image.save(buf, format="JPEG")
                    st.download_button("Download Studio Image", buf.getvalue(), "custom_bg.jpg", "image/jpeg")

# =====================================================================
# 3. Image Enhancer & Brightness
# =====================================================================
elif app_mode == "3. Image Enhancer & Brightness":
    st.header("☀️ Image Enhancer & Brightness Adjuster")
    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"], key="m3")

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        brightness = st.slider("Brightness", 0.5, 3.0, 1.0, 0.1)
        contrast = st.slider("Contrast", 0.5, 3.0, 1.0, 0.1)
        
        img_np = np.array(image)
        enhanced_np = cv2.convertScaleAbs(img_np, alpha=contrast, beta=int((brightness - 1) * 50))
        enhanced_image = Image.fromarray(enhanced_np)
        
        st.image(enhanced_image, use_container_width=True, caption="Enhanced Image")
        buf = io.BytesIO()
        enhanced_image.save(buf, format="JPEG")
        st.download_button("Download Enhanced", buf.getvalue(), "enhanced.jpg", "image/jpeg")

# =====================================================================
# 4. ID Card Cropper & Straightener
# =====================================================================
elif app_mode == "4. ID Card Cropper & Straightener":
    st.header("🆔 ID Card Cropper & Straightener")
    uploaded_file = st.file_uploader("Upload ID Card", type=["jpg", "jpeg", "png"], key="m4")

    if uploaded_file is not None:
        img = Image.open(uploaded_file)
        w, h = img.size
        rotation = st.slider("Rotate", -180, 180, 0)
        if rotation != 0:
            img = img.rotate(rotation, expand=True)
            w, h = img.size
            
        cropped = img.crop((0, 0, w, h))
        st.image(cropped, use_container_width=True, caption="ID Card Preview")
        buf = io.BytesIO()
        cropped.save(buf, format="JPEG")
        st.download_button("Download ID Card", buf.getvalue(), "id_card.jpg", "image/jpeg")

# =====================================================================
# 5. Passport Photo Maker (4-in-1)
# =====================================================================
elif app_mode == "5. Passport Photo Maker (4-in-1)":
    st.header("🛂 Passport Photo Sheet Generator")
    uploaded_file = st.file_uploader("Upload Passport Photo", type=["jpg", "jpeg", "png"], key="m5")

    if uploaded_file is not None:
        img = Image.open(uploaded_file).resize((300, 350))
        sheet = Image.new("RGB", (650, 750), (255, 255, 255))
        sheet.paste(img, (25, 25))
        sheet.paste(img, (335, 25))
        sheet.paste(img, (25, 385))
        sheet.paste(img, (335, 385))
        
        st.image(sheet, use_container_width=True, caption="4-Copy Passport Sheet")
        buf = io.BytesIO()
        sheet.save(buf, format="JPEG")
        st.download_button("Download Passport Sheet", buf.getvalue(), "passport_sheet.jpg", "image/jpeg")

# =====================================================================
# 6. Image Resizer & Compressor
# =====================================================================
elif app_mode == "6. Image Resizer & Compressor":
    st.header("📏 Image Resizer")
    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"], key="m6")

    if uploaded_file is not None:
        img = Image.open(uploaded_file)
        width = st.slider("Width", 100, 2000, img.width)
        height = st.slider("Height", 100, 2000, img.height)
        resized = img.resize((width, height))
        st.image(resized, use_container_width=True)
        buf = io.BytesIO()
        resized.save(buf, format="JPEG")
        st.download_button("Download Resized", buf.getvalue(), "resized.jpg", "image/jpeg")

# =====================================================================
# 7. Grayscale & Black-White Converter
# =====================================================================
elif app_mode == "7. Grayscale & Black-White Converter":
    st.header("⬛ Grayscale / B&W Converter")
    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"], key="m7")

    if uploaded_file is not None:
        img = Image.open(uploaded_file).convert("L")
        st.image(img, use_container_width=True, caption="Grayscale Output")
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        st.download_button("Download B&W", buf.getvalue(), "grayscale.jpg", "image/jpeg")

# =====================================================================
# 8. Image Rotator & Flipper
# =====================================================================
elif app_mode == "8. Image Rotator & Flipper":
    st.header("🔄 Image Rotator & Flipper")
    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"], key="m8")

    if uploaded_file is not None:
        img = Image.open(uploaded_file)
        rot = st.selectbox("Rotation", [0, 90, 180, 270])
        if rot > 0:
            img = img.rotate(rot, expand=True)
        st.image(img, use_container_width=True)
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        st.download_button("Download Rotated", buf.getvalue(), "rotated.jpg", "image/jpeg")

# =====================================================================
# 9. Border & Frame Adder
# =====================================================================
elif app_mode == "9. Border & Frame Adder":
    st.header("🖼️ Border & Frame Adder")
    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"], key="m9")

    if uploaded_file is not None:
        img = Image.open(uploaded_file)
        bordered = ImageOps.expand(img, border=20, fill='black')
        st.image(bordered, use_container_width=True)
        buf = io.BytesIO()
        bordered.save(buf, format="JPEG")
        st.download_button("Download Bordered", buf.getvalue(), "bordered.jpg", "image/jpeg")

# =====================================================================
# 10. Watermark Adder
# =====================================================================
elif app_mode == "10. Watermark Adder":
    st.header("💧 Watermark Adder")
    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"], key="m10")
    text = st.text_input("Watermark Text", "Hasanur Studio")

    if uploaded_file is not None:
        img = Image.open(uploaded_file)
        st.image(img, use_container_width=True, caption="Preview")
        st.success(f"Watermark '{text}' ready to apply.")

# =====================================================================
# 11. PDF to Image Converter
# =====================================================================
elif app_mode == "11. PDF to Image Converter":
    st.header("📄 PDF to Image Converter")
    uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"], key="m11")

    if uploaded_pdf is not None:
        try:
            reader = PdfReader(uploaded_pdf)
            for i, page in enumerate(reader.pages):
                for j, img_obj in enumerate(page.images):
                    img = Image.open(io.BytesIO(img_obj.data))
                    st.image(img, width=400, caption=f"Page {i+1}")
                    buf = io.BytesIO()
                    img.save(buf, format="PNG")
                    st.download_button(f"Download P{i+1} Img{j+1}", buf.getvalue(), f"pdf_p{i+1}_img{j+1}.png", "image/png", key=f"pdf_{i}_{j}")
        except Exception as e:
            st.error(f"Error: {e}")
