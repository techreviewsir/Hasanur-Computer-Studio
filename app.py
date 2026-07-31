import io
import cv2
import numpy as np
from PIL import Image, ImageOps
import streamlit as st
from rembg import remove, new_session
from pypdf import PdfReader

# পেজের লেআউট এবং স্টাইলিশ বক্স ও আইকন সেটআপ
st.set_page_config(page_title="Hasanur Computer Studio", layout="wide")

st.markdown("""
<style>
    /* সাইডবারের রেডিও অপশনগুলোকে আকর্ষণীয় বক্স এবং হভার ইফেক্ট দেওয়া */
    .stRadio > label {
        background-color: #f8f9fa;
        border: 1px solid #e0e0e0;
        padding: 12px 18px;
        border-radius: 10px;
        margin-bottom: 8px;
        transition: all 0.3s ease;
        font-weight: 600;
        color: #333333;
    }
    .stRadio > label:hover {
        background-color: #ff4b4b;
        color: white;
        border-color: #ff4b4b;
        padding-left: 22px;
        box-shadow: 0 4px 12px rgba(255, 75, 75, 0.3);
    }
</style>
""", unsafe_allow_html=True)

st.title("🖨️ Hasanur Computer Studio - Professional Dashboard")
st.markdown("---")

# --- গ্লোবাল ফাইল আপলোডার (একবার আপলোড করলেই সব মডিউলে কাজ করবে) ---
st.sidebar.header("📁 Master File Uploader")
global_file = st.sidebar.file_uploader("Upload Image or PDF once", type=["jpg", "jpeg", "png", "pdf"])

# সাইডবার মেনু (বক্স এবং আইকন সহ নির্দিষ্ট মডিউলসমূহ)
st.sidebar.header("Navigation Menu")
app_mode = st.sidebar.radio("Choose a Tool", [
    "✨ 1. Smart AI Background Remover",
    "🎨 2. Custom Background Color Studio",
    "☀️ 3. Image Enhancer & Brightness",
    "🎨 4. B&W to Colorful Image Fixer",
    "🆔 5. ID Card Cropper & Straightener",
    "📄 6. PDF to Image Converter"
])

if global_file is not None:
    file_extension = global_file.name.split('.')[-1].lower()

    # =====================================================================
    # 1. Smart AI Background Remover (Transparent)
    # =====================================================================
    if app_mode == "✨ 1. Smart AI Background Remover":
        st.header("✨ Smart AI Background Remover")
        if file_extension in ['jpg', 'jpeg', 'png']:
            col1, col2 = st.columns(2)
            with col1:
                st.image(Image.open(global_file), use_container_width=True, caption="Original Image")
            with col2:
                if st.button("Remove Background"):
                    with st.spinner("Processing with AI (HD)..."):
                        session = new_session("u2net")
                        output_bytes = remove(global_file.getvalue(), session=session)
                        out_img = Image.open(io.BytesIO(output_bytes))
                        st.image(out_img, use_container_width=True, caption="Transparent Output")
                        
                        buf = io.BytesIO()
                        out_img.save(buf, format="PNG")
                        st.download_button("Download HD Transparent PNG", buf.getvalue(), "transparent_hd.png", "image/png")
        else:
            st.warning("Please upload an image file (JPG/PNG).")

    # =====================================================================
    # 2. Custom Background Color Studio (অটো কালার চেঞ্জ)
    # =====================================================================
    elif app_mode == "🎨 2. Custom Background Color Studio":
        st.header("🎨 Custom Background Color Studio")
        if file_extension in ['jpg', 'jpeg', 'png']:
            bg_color = st.color_picker("Pick Background Color (Applies Instantly)", "#FFFFFF")

            col1, col2 = st.columns(2)
            with col1:
                st.image(Image.open(global_file), use_container_width=True, caption="Original Image")
            with col2:
                with st.spinner("Applying background and generating HD..."):
                    session = new_session("u2net")
                    output_bytes = remove(global_file.getvalue(), session=session)
                    foreground = Image.open(io.BytesIO(output_bytes)).convert("RGBA")
                    
                    hex_code = bg_color.lstrip('#')
                    bg_rgb = tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))
                    
                    background = Image.new("RGBA", foreground.size, bg_rgb + (255,))
                    final_image = Image.alpha_composite(background, foreground).convert("RGB")
                    
                    st.image(final_image, use_container_width=True, caption=f"Background Color: {bg_color}")
                    
                    buf = io.BytesIO()
                    final_image.save(buf, format="JPEG", quality=95)
                    st.download_button("Download HD Studio Image", buf.getvalue(), "custom_bg_hd.jpg", "image/jpeg")
        else:
            st.warning("Please upload an image file (JPG/PNG).")

    # =====================================================================
    # 3. Image Enhancer & Brightness
    # =====================================================================
    elif app_mode == "☀️ 3. Image Enhancer & Brightness":
        st.header("☀️ Image Enhancer & Brightness Adjuster")
        if file_extension in ['jpg', 'jpeg', 'png']:
            image = Image.open(global_file)
            col1, col2 = st.columns(2)
            with col1:
                brightness = st.slider("Brightness", 0.5, 3.0, 1.0, 0.1)
                contrast = st.slider("Contrast", 0.5, 3.0, 1.0, 0.1)
                st.image(image, use_container_width=True, caption="Original Image")
            with col2:
                img_np = np.array(image)
                enhanced_np = cv2.convertScaleAbs(img_np, alpha=contrast, beta=int((brightness - 1) * 50))
                enhanced_image = Image.fromarray(enhanced_np)
                
                st.image(enhanced_image, use_container_width=True, caption="Enhanced HD Image")
                buf = io.BytesIO()
                enhanced_image.save(buf, format="JPEG", quality=95)
                st.download_button("Download HD Enhanced Image", buf.getvalue(), "enhanced_hd.jpg", "image/jpeg")
        else:
            st.warning("Please upload an image file.")

    # =====================================================================
    # 4. B&W to Colorful Image Fixer (সাদা-কালো ছবিকে রঙিন ও প্রাণবন্ত করা)
    # =====================================================================
    elif app_mode == "🎨 4. B&W to Colorful Image Fixer":
        st.header("🎨 B&W to Colorful Image & Tone Fixer")
        st.write("सাদা-কালো বা মলিন ছবিকে কালার ব্যালেন্স ও স্যাচুরেশন বাড়িয়ে রঙিন ও প্রাণবন্ত করুন।")
        if file_extension in ['jpg', 'jpeg', 'png']:
            image = Image.open(global_file)
            col1, col2 = st.columns(2)
            with col1:
                saturation = st.slider("Color Saturation (রঙের মাত্রা)", 0.0, 3.0, 1.5, 0.1)
                sharpness = st.slider("Sharpness (নিখুঁত ভাব)", 0.0, 3.0, 1.2, 0.1)
                st.image(image, use_container_width=True, caption="Original Image")
            with col2:
                # কালার স্যাচুরেশন এবং শার্পনেস বৃদ্ধি করার প্রসেসিং
                img_cv = np.array(image)
                hsv = cv2.cvtColor(img_cv, cv2.COLOR_RGB2HSV)
                hsv[:, :, 1] = np.clip(hsv[:, :, 1] * saturation, 0, 255)
                colored_rgb = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
                
                # শার্পনেস যোগ করা
                kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]]) * (sharpness / 1.2)
                sharpened = cv2.filter2D(colored_rgb, -1, kernel)
                
                final_colored = Image.fromarray(np.clip(sharpened, 0, 255).astype(np.uint8))
                
                st.image(final_colored, use_container_width=True, caption="Colorful & Enhanced Output")
                buf = io.BytesIO()
                final_colored.save(buf, format="JPEG", quality=95)
                st.download_button("Download HD Colorful Image", buf.getvalue(), "colorful_hd.jpg", "image/jpeg")
        else:
            st.warning("Please upload an image file.")

    # =====================================================================
    # 5. ID Card Cropper & Straightener
    # =====================================================================
    elif app_mode == "🆔 5. ID Card Cropper & Straightener":
        st.header("🆔 ID Card Cropper & Straightener")
        if file_extension in ['jpg', 'jpeg', 'png']:
            img = Image.open(global_file)
            w, h = img.size
            rotation = st.slider("Rotate", -180, 180, 0)
            if rotation != 0:
                img = img.rotate(rotation, expand=True)
                w, h = img.size
                
            cropped = img.crop((0, 0, w, h))
            st.image(cropped, use_container_width=True, caption="ID Card HD Preview")
            buf = io.BytesIO()
            cropped.save(buf, format="JPEG", quality=95)
            st.download_button("Download HD ID Card", buf.getvalue(), "id_card_hd.jpg", "image/jpeg")
        else:
            st.warning("Please upload an image file.")

    # =====================================================================
    # 6. PDF to Image Converter
    # =====================================================================
    elif app_mode == "📄 6. PDF to Image Converter":
        st.header("📄 PDF to Image Converter")
        if file_extension == 'pdf':
            try:
                reader = PdfReader(global_file)
                for i, page in enumerate(reader.pages):
                    for j, img_obj in enumerate(page.images):
                        img = Image.open(io.BytesIO(img_obj.data))
                        st.image(img, width=400, caption=f"Page {i+1} HD")
                        buf = io.BytesIO()
                        img.save(buf, format="PNG")
                        st.download_button(f"Download HD P{i+1} Img{j+1}", buf.getvalue(), f"pdf_p{i+1}_img{j+1}_hd.png", "image/png", key=f"pdf_{i}_{j}")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Please upload a PDF file for this module.")
else:
    st.info("👈 দয়া করে বাম পাশের সাইডবার থেকে প্রথমে একটি ছবি বা পিডিএফ (Master File Uploader) আপলোড করুন। এরপর যেকোনো মডিউলে ক্লিক করলেই সেই ফাইল দিয়ে কাজ করতে পারবেন!")
