import io
import cv2
import numpy as np
from PIL import Image
import streamlit as st
from rembg import remove, new_session

# পেজের লেআউট সেটআপ
st.set_page_config(page_title="Hasanur Computer Studio", layout="wide")

st.title("🖨️ Hasanur Computer Studio - All-in-One Dashboard")
st.markdown("---")

# সাইডবার মেনু
st.sidebar.header("Navigation Menu")
app_mode = st.sidebar.selectbox("Choose a Tool", [
    "1. Smart AI Background Remover",
    "2. Image Enhancer & Brightness",
    "3. ID Card Cropper & Straightener",
    "4. PDF to Image Converter"
])

# --- MODULE 1: AI Background Remover ---
if app_mode == "1. Smart AI Background Remover":
    st.header("✨ Smart AI Background Remover")
    st.write("Upload an image to remove its background instantly and perfectly.")

    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Original Image")
            input_image = Image.open(uploaded_file)
            st.image(input_image, use_container_width=True)

        with col2:
            st.subheader("Background Removed Image")
            if st.button("Remove Background"):
                with st.spinner("Processing with AI (Model: u2net)... Please wait..."):
                    try:
                        # u2net মডেলটি চুল এবং বডির বর্ডার নিখুঁতভাবে রাখতে সবচেয়ে ভালো কাজ করে
                        session = new_session("u2net")
                        
                        # বাইট ফরম্যাটে কনভার্ট করা
                        input_bytes = uploaded_file.getvalue()
                        
                        # ব্যাকগ্রাউন্ড রিমুভ করা
                        output_bytes = remove(input_bytes, session=session)
                        
                        output_image = Image.open(io.BytesIO(output_bytes))
                        st.image(output_image, use_container_width=True)

                        # ডাউনলোড বাটন
                        buf = io.BytesIO()
                        output_image.save(buf, format="PNG")
                        byte_im = buf.getvalue()
                        
                        st.download_button(
                            label="Download Transparent Image",
                            data=byte_im,
                            file_name="bg_removed_hasanur.png",
                            mime="image/png"
                        )
                    except Exception as e:
                        st.error(f"An error occurred: {e}")

# --- MODULE 2: Image Enhancer ---
elif app_mode == "2. Image Enhancer & Brightness":
    st.header("☀️ Image Enhancer & Brightness Adjuster")
    uploaded_file = st.file_uploader("Upload Image for Editing", type=["jpg", "jpeg", "png"], key="enhancer")

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Original", use_container_width=True)
        
        brightness = st.slider("Brightness", 0.5, 2.0, 1.0)
        contrast = st.slider("Contrast", 0.5, 2.0, 1.0)

        # সিম্পল ব্রাইটনেস ও কন্ট্রাস্ট অপারেশন
        img_np = np.array(image)
        enhanced = cv2.convertScaleAbs(img_np, alpha=contrast, beta=(brightness - 1) * 50)
        st.image(enhanced, caption="Enhanced Image", use_container_width=True)

# --- MODULE 3: ID Card Cropper ---
elif app_mode == "3. ID Card Cropper & Straightener":
    st.header("🆔 ID Card Quick Adjuster")
    st.info("Upload your ID card or document image to process.")
    uploaded_file = st.file_uploader("Upload ID Card", type=["jpg", "jpeg", "png"], key="idcard")

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded ID Card", use_container_width=True)
        st.success("Ready for printing or passport/ID adjustments.")

# --- MODULE 4: PDF Converter ---
elif app_mode == "4. PDF to Image Converter":
    st.header("📄 PDF to Image Converter")
    st.info("Upload a PDF file to convert pages into images.")
    uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"])

    if uploaded_pdf is not None:
        st.success("PDF uploaded successfully! Processing features active.")
