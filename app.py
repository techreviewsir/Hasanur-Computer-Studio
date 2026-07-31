import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import io
from pypdf import PdfReader, PdfWriter

# rembg এরর হ্যান্ডেল করার জন্য নিরাপদ ইম্পোর্ট
try:
    from rembg import remove
    REMBG_AVAILABLE = True
except Exception:
    REMBG_AVAILABLE = False

# পেজ কনফিগারেশন
st.set_page_config(page_title="হাসানুর কম্পিউটার স্টুডিও", layout="wide", page_icon="📸")

# ড্যাশবোর্ড থিম ও কাস্টম বাটন ইন্টারফেস CSS
st.markdown("""
    <style>
    .main { background-color: #0f172a; color: #f8fafc; }
    h1 { color: #38bdf8; font-family: 'Segoe UI', sans-serif; text-align: center; margin-bottom: 5px; }
    .subtitle { text-align: center; color: #94a3b8; font-size: 16px; margin-bottom: 5px; }
    .contact-info { text-align: center; color: #38bdf8; font-size: 15px; margin-bottom: 25px; font-weight: bold; }
    .footer { text-align: center; margin-top: 60px; padding: 20px; color: #64748b; border-top: 1px solid #334155; font-size: 14px; }
    
    /* 🔴 মডিউল বাটনগুলোর উপর মাউস রাখলে লাল কালার ও আন্ডারলাইন ইফেক্ট */
    div.stButton > button {
        transition: all 0.2s ease-in-out;
    }
    div.stButton > button:hover {
        background-color: #ef4444 !important; /* উজ্জ্বল লাল ব্যাকগ্রাউন্ড */
        color: #ffffff !important;           /* সাদা টেক্সট */
        border-color: #dc2626 !important;     /* লাল বর্ডার */
        text-decoration: underline !important; /* লেখার নিচে আন্ডারলাইন */
    }
    
    /* কুইক কালার চেঞ্জার বাটন স্টাইল */
    .color-btn {
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        font-weight: bold;
        color: white;
        margin-bottom: 10px;
    }
    
    /* সার্ভিস লিঙ্কের জন্য কাস্টম বাটন স্টাইল */
    .link-box {
        display: inline-block;
        background-color: #1e293b;
        color: #38bdf8 !important;
        padding: 8px 16px;
        margin: 5px;
        border-radius: 20px;
        text-decoration: none;
        font-weight: 500;
        border: 1px solid #334155;
        transition: all 0.3s ease;
    }
    .link-box:hover {
        background-color: #38bdf8;
        color: #0f172a !important;
        border-color: #38bdf8;
    }
    .header-link {
        background-color: #22c55e;
        color: white !important;
        padding: 10px 20px;
        border-radius: 8px;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 15px;
    }
    .form-preview {
        background-color: #1e293b;
        padding: 30px;
        border-radius: 8px;
        border: 2px dashed #334155;
        color: #f8fafc;
        font-family: 'Courier New', Courier, monospace;
    }
    </style>
""", unsafe_allow_html=True)

# 🛠️ সাইডবার ড্যাশবোর্ড কন্ট্রোল ও ল্যাঙ্গুয়েজ সিলেকশন
st.sidebar.markdown("## 📊 Project Structure")
lang_mode = st.sidebar.radio("🌐 Select Language / ভাষা নির্বাচন করুন:", ("🇧🇩 বাংলা UI", "🇬🇧 English UI"))
st.sidebar.markdown("---")

# ভাষা অনুযায়ী টেক্সট ভেরিয়েবল সেটআপ
if lang_mode == "🇧🇩 বাংলা UI":
    title_text = "📸 হাসানুর কম্পিউটার স্টুডিও"
    sub_text = "📍 মনিরামপুর, যশোর | অল-ইন-ওয়ান প্রফেশনাল ডিজিটাল ল্যাব ড্যাশবোর্ড"
    hotline_text = "📞 হটলাইন: 01743614359"
    menu_title = "⚙️ কাজের বিভাগসমূহ (বাটন গ্রিড)"
    footer_text = "© ২০২৬ হাসানুর কম্পিউটার স্টুডিও, মনিরামপুর, যশোর। অল রাইটস রিজার্ভড।"
    upload_msg = "এডিট করার জন্য আপনার ছবিটি এখানে আপলোড করুন..."
    apply_txt = "Apply (পরিবর্তন সেভ করুন)"
    
    b1, b2, b3, b4, b5, b6, b7, b8, b9, b10 = (
        "1. 📐 বাঁকা আইডি সোজা", "2. ✂️ ফটো ক্রপ", "3. 🪄 ফটো রুম এআই (PhotoRoom)", "4. 🪄 ছবি উন্নতকরণ",
        "5. 🎨 ব্যাকগ্রাউন্ড ও কালার", "6. 🧽 অবজেক্ট রিমুভ", "7. 📜 প্রত্যয়ন ও ছাড়পত্র", "8. 📝 সিভি/বায়োডাটা মেকার",
        "9. 🔗 পিডিএফ টুলস", "10. 🌐 অনলাইন লিঙ্ক ও সেটিংস"
    )
else:
    title_text = "📸 Hasanur Computer Studio"
    sub_text = "📍 Monirampur, Jashore | All-in-One Professional Digital Lab Dashboard"
    hotline_text = "📞 Hotline: 01743614359"
    menu_title = "⚙️ Work Modules (Button Grid)"
    footer_text = "© 2026 Hasanur Computer Studio, Monirampur, Jashore. All Rights Reserved."
    upload_msg = "Upload your image here to edit..."
    apply_txt = "Apply Changes"
    
    b1, b2, b3, b4, b5, b6, b7, b8, b9, b10 = (
        "1. 📐 ID Card Fixer", "2. ✂️ Crop Tool", "3. 🪄 PhotoRoom AI", "4. 🪄 En-Real AI",
        "5. 🎨 BG & Color Changer", "6. 🧽 Erase Tool", "7. 📜 Forms & TC", "8. 📝 CV Maker",
        "9. 🔗 PDF Tools", "10. 🌐 Online Directory"
    )

# হেডার ও স্টুডিও ব্র্যান্ডিং রেন্ডারিং
st.markdown(f"<h1>{title_text}</h1>", unsafe_allow_html=True)
st.markdown(f"<div class='subtitle'>{sub_text}</div>", unsafe_allow_html=True)
st.markdown(f"<div class='contact-info'>{hotline_text}</div>", unsafe_allow_html=True)

# 🎛️ মূল স্ক্রিনে বাটন সিস্টেমের মেনু গ্রিড তৈরি
if 'active_module' not in st.session_state:
    st.session_state.active_module = "1"

st.markdown(f"### {menu_title}")
row1_col1, row1_col2, row1_col3, row1_col4, row1_col5 = st.columns(5)
row2_col1, row2_col2, row2_col3, row2_col4, row2_col5 = st.columns(5)

with row1_col1:
    if st.button(b1, use_container_width=True, type="primary" if st.session_state.active_module == "1" else "secondary"):
        st.session_state.active_module = "1"
with row1_col2:
    if st.button(b2, use_container_width=True, type="primary" if st.session_state.active_module == "2" else "secondary"):
        st.session_state.active_module = "2"
with row1_col3:
    if st.button(b3, use_container_width=True, type="primary" if st.session_state.active_module == "3" else "secondary"):
        st.session_state.active_module = "3"
with row1_col4:
    if st.button(b4, use_container_width=True, type="primary" if st.session_state.active_module == "4" else "secondary"):
        st.session_state.active_module = "4"
with row1_col5:
    if st.button(b5, use_container_width=True, type="primary" if st.session_state.active_module == "5" else "secondary"):
        st.session_state.active_module = "5"

with row2_col1:
    if st.button(b6, use_container_width=True, type="primary" if st.session_state.active_module == "6" else "secondary"):
        st.session_state.active_module = "6"
with row2_col2:
    if st.button(b7, use_container_width=True, type="primary" if st.session_state.active_module == "7" else "secondary"):
        st.session_state.active_module = "7"
with row2_col3:
    if st.button(b8, use_container_width=True, type="primary" if st.session_state.active_module == "8" else "secondary"):
        st.session_state.active_module = "8"
with row2_col4:
    if st.button(b9, use_container_width=True, type="primary" if st.session_state.active_module == "9" else "secondary"):
        st.session_state.active_module = "9"
with row2_col5:
    if st.button(b10, use_container_width=True, type="primary" if st.session_state.active_module == "10" else "secondary"):
        st.session_state.active_module = "10"

st.markdown("---")

# ইমেজ ফাইল আপলোডার গ্লোবাল হ্যান্ডলিং (ফটো মডিউল ১, ২, ৩, ৪, ৫, 6 এর জন্য)
is_photo_module = st.session_state.active_module in ["1", "2", "3", "4", "5", "6"]
uploaded_file = st.file_uploader(upload_msg, type=["jpg", "jpeg", "png"]) if is_photo_module else None

base_image = None
if uploaded_file is not None:
    base_image = Image.open(uploaded_file)
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        st.image(base_image, caption="Original Image / মূল ছবি", use_container_width=True)

# ====================================================================
# MODULE 1: 📐 বাঁকা আইডি কার্ড ও ডকুমেন্ট সোজা করার টুল
# ====================================================================
if st.session_state.active_module == "1":
    st.markdown("### 📐 1. বাঁকা আইডি কার্ড ও ডকুমেন্ট সোজা করার টুল (Persp-AI)")
    if base_image:
        st.info("💡 মোবাইল থেকে তোলা যেকোনো বাঁকা কার্ডের ৪টি কোণকে সোজা করতে নিচের কন্ট্রোলগুলো এডজাস্ট করুন।")
        
        img_np = np.array(base_image)
        h, w = img_np.shape[:2]
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            top_left_x = st.slider("টপ-লেফট X (উপরের বাম কোণ)", 0, w, int(w*0.05))
            top_left_y = st.slider("টপ-লেফট Y", 0, h, int(h*0.05))
            bottom_left_x = st.slider("বটম-লেফট X (নিচের বাম কোণ)", 0, w, int(w*0.05))
            bottom_left_y = st.slider("বটম-লেফট Y", 0, h, int(h*0.95))
        with col_s2:
            top_right_x = st.slider("টপ-রাইট X (উপরের ডান কোণ)", 0, w, int(w*0.95))
            top_right_y = st.slider("টপ-রাইট Y", 0, h, int(h*0.05))
            bottom_right_x = st.slider("বটম-রাইট X (নিচের ডান কোণ)", 0, w, int(w*0.95))
            bottom_right_y = st.slider("বটম-রাইট Y", 0, h, int(h*0.95))
            
        if st.button("সোজা করুন (Transform ID Card)", type="primary", use_container_width=True):
            pts1 = np.float32([[top_left_x, top_left_y], [top_right_x, top_right_y], 
                               [bottom_left_x, bottom_left_y], [bottom_right_x, bottom_right_y]])
            pts2 = np.float32([[0, 0], [w, 0], [0, h], [w, h]])
            
            matrix = cv2.getPerspectiveTransform(pts1, pts2)
            result_np = cv2.warpPerspective(img_np, matrix, (w, h))
            out = Image.fromarray(result_np)
            
            with col_v2:
                st.image(out, caption="সোজা করা আইডি কার্ড", use_container_width=True)
                buf = io.BytesIO(); out.save(buf, format="JPEG")
                st.download_button("📥 ডাউনলোড করুন", data=buf.getvalue(), file_name="fixed_id_card.jpg", use_container_width=True)

# ====================================================================
# MODULE 2: ✂️ Crop Tool
# ====================================================================
elif st.session_state.active_module == "2":
    st.markdown("### ✂️ 2. Crop Tool")
    if base_image:
        crop_type = st.radio("Select Crop Ratio / ক্রপ রেশিও:", ("Passport Size (413x531 px)", "Stamp Size (236x295 px)", "Custom Auto ID Card"))
        if st.button(apply_txt, type="primary", use_container_width=True):
            if "Passport" in crop_type:
                out = base_image.resize((413, 531), Image.Resampling.LANCZOS)
            elif "Stamp" in crop_type:
                out = base_image.resize((236, 295), Image.Resampling.LANCZOS)
            else:
                out = base_image.resize((600, 400), Image.Resampling.LANCZOS)
            with col_v2:
                st.image(out, caption="Cropped Output", use_container_width=True)
                buf = io.BytesIO(); out.save(buf, format="JPEG")
                st.download_button("📥 Download Result", data=buf.getvalue(), file_name="cropped.jpg", use_container_width=True)

# ====================================================================
# MODULE 3: 🪄 ফটো রুম এআই (PhotoRoom AI Background Changer) - UPDATED
# ====================================================================
elif st.session_state.active_module == "3":
    st.markdown("### 🪄 3. ফটো রুম এআই (PhotoRoom AI Background Changer)")
    if base_image:
        if REMBG_AVAILABLE:
            st.success("⚡ PhotoRoom AI ইঞ্জিন প্রস্তুত! আপলোড করা ছবির ব্যাকগ্রাউন্ড স্বয়ংক্রিয়ভাবে রিমুভ করা হয়েছে।")
            
            # ব্যাকগ্রাউন্ড রিমুভ করা ট্রান্সপারেন্ট ছবি জেনারেট করা
            with st.spinner("Removing background seamlessly..."):
                transparent_img = remove(base_image)
            
            st.markdown("##### 🎨 এক ক্লিকে ব্যাকগ্রাউন্ডের কালার পরিবর্তন করুন (Quick Color Picker):")
            
            # কুইক ব্যাকগ্রাউন্ড চেঞ্জার অপশন
            bg_selection = st.selectbox(
                "জনপ্রিয় স্টুডিও কালার সিলেক্ট করুন:", 
                ["স্বচ্ছ (Transparent/PNG)", "আকাgenerate আকাশী (Sky Blue)", "পাসপোর্ট নীল (Studio Blue)", "অফিসিয়াল সাদা (Pure White)", "কাস্টম কালার (Custom Color)"]
            )
            
            # কাস্টম কালার সিলেক্টর (যদি ইউজার কাস্টম সিলেক্ট করে)
            custom_color = "#ffffff"
            if bg_selection == "কাস্টম কালার (Custom Color)":
                custom_color = st.color_picker("আপনার পছন্দের রঙ সিলেক্ট করুন:", "#ff4b4b")
            
            # বর্ডার মসৃণ করার স্লাইডার
            smoothness = st.slider("বর্ডার বা কিনারার মসৃণতা (Edge Smoothing Level):", min_value=0, max_value=5, value=1)
            
            if st.button("ফটো রুম আউটপুট তৈরি করুন", type="primary", use_container_width=True):
                # এজ স্মুথিং প্রসেসিং
                if smoothness > 0:
                    alpha = transparent_img.split()[-1]
                    smoothed_alpha = alpha.filter(ImageFilter.GaussianBlur(smoothness))
                    transparent_img.putalpha(smoothed_alpha)
                
                # কালার লজিক অ্যাপ্লাই করা
                if bg_selection == "স্বচ্ছ (Transparent/PNG)":
                    out = transparent_img
                    file_ext = "PNG"; mime_type = "image/png"; filename = "photoroom_transparent.png"
                else:
                    if bg_selection == "আকাgenerate আকাশী (Sky Blue)":
                        hex_val = "87CEEB"
                    elif bg_selection == "পাসপোর্ট নীল (Studio Blue)":
                        hex_val = "0033aa"
                    elif bg_selection == "অফিসিয়াল সাদা (Pure White)":
                        hex_val = "ffffff"
                    else:
                        hex_val = custom_color.lstrip('#')
                        
                    bg_rgb = tuple(int(hex_val[i:i+2], 16) for i in (0, 2, 4))
                    bg = Image.new("RGBA", base_image.size, bg_rgb + (255,))
                    bg.paste(transparent_img, (0, 0), transparent_img)
                    out = bg.convert("RGB")
                    file_ext = "JPEG"; mime_type = "image/jpeg"; filename = "photoroom_output.jpg"
                
                with col_v2:
                    st.image(out, caption="PhotoRoom AI Output", use_container_width=True)
                    buf = io.BytesIO(); out.save(buf, format=file_ext)
                    st.download_button("📥 ডাউনলোড ফটো রুম ইমেজ", data=buf.getvalue(), file_name=filename, mime=mime_type, use_container_width=True)
        else:
            st.error("দুঃখিত, আপনার সিস্টেমে rembg AI ইঞ্জিনটি ইনস্টল করা নেই।")

# ====================================================================
# MODULE 4: 🪄 En-Real & Enhan-AI
# ====================================================================
elif st.session_state.active_module == "4":
    st.markdown("### 🪄 4. En-Real & Enhan-AI Photo Enhancer")
    if base_image:
        enhance_mode = st.radio("Choose Mode / মোড সিলেক্ট করুন:", ("En-Real (Sharpness Booster)", "Enhan-AI (Auto Light & Color Adjust)"))
        if st.button(apply_txt, type="primary", use_container_width=True):
            if "En-Real" in enhance_mode:
                out = ImageEnhance.Sharpness(base_image).enhance(2.5)
            else:
                img_c = ImageEnhance.Contrast(base_image).enhance(1.3)
                out = ImageEnhance.Brightness(img_c).enhance(1.1)
            with col_v2:
                st.image(out, caption="Enhanced Output", use_container_width=True)
                buf = io.BytesIO(); out.save(buf, format="JPEG")
                st.download_button("📥 Download Result", data=buf.getvalue(), file_name="enhanced.jpg", use_container_width=True)

# ====================================================================
# MODULE 5: 🎨 BG-First & BG-AI
# ====================================================================
elif st.session_state.active_module == "5":
    st.markdown("### 🎨 5. BG-First & BG-AI Background Panel")
    if base_image:
        bg_mode = st.radio("Method / পদ্ধতি:", ("BG-First (Remove BG Transparent)", "BG-AI (Custom Solid Color BG)"))
        bg_color = st.color_picker("পাসপোর্ট ছবির ব্যাকগ্রাউন্ড কালার সিলেক্ট করুন (যেমন: আকাশী):", "#87CEEB")
        
        st.markdown("##### 🛠️ নিখুঁত ফিনিশিং সেটিংস (Edge Smoothness):")
        smoothness = st.slider("বর্ডার বা কিনারার মসৃণতা (Smooth Edge Level):", min_value=0, max_value=5, value=2, step=1)
        
        if st.button(apply_txt, type="primary", use_container_width=True):
            if REMBG_AVAILABLE:
                with st.spinner("Processing AI Background with Edge Smoothing..."):
                    transparent = remove(base_image)
                    
                    if smoothness > 0:
                        alpha = transparent.split()[-1]
                        smoothed_alpha = alpha.filter(ImageFilter.GaussianBlur(smoothness))
                        transparent.putalpha(smoothed_alpha)
                    
                    if "BG-First" in bg_mode:
                        out = transparent
                        file_ext = "PNG"; mime_type = "image/png"; filename = "transparent.png"
                    else:
                        h_val = bg_color.lstrip('#')
                        bg_rgb = tuple(int(h_val[i:i+2], 16) for i in (0, 2, 4))
                        
                        bg = Image.new("RGBA", base_image.size, bg_rgb + (255,))
                        bg.paste(transparent, (0, 0), transparent)
                        out = bg.convert("RGB")
                        file_ext = "JPEG"; mime_type = "image/jpeg"; filename = "passport_photo.jpg"
                        
                    with col_v2:
                        st.image(out, caption="Perfect Finished Passport Photo", use_container_width=True)
                        buf = io.BytesIO(); out.save(buf, format=file_ext)
                        st.download_button("📥 Download Photo", data=buf.getvalue(), file_name="passport_photo.jpg", mime=mime_type, use_container_width=True)
            else:
                st.error("AI engine is unavailable on this system.")

# ====================================================================
# MODULE 6: 🧽 Erase & Restore Tool
# ====================================================================
elif st.session_state.active_module == "6":
    st.markdown("### 🧽 6. Erase & Restore Tool")
    if base_image:
        action = st.radio("Action / কাজ:", ("Erase (Blemish Remover Filter)", "Restore (Reset Layer)"))
        if st.button(apply_txt, type="primary", use_container_width=True):
            if "Erase" in action:
                out = base_image.filter(ImageFilter.MedianFilter(size=3))
            else:
                out = base_image
            with col_v2:
                st.image(out, caption="Processed Image", use_container_width=True)
                buf = io.BytesIO(); out.save(buf, format="JPEG")
                st.download_button("📥 Download Image", data=buf.getvalue(), file_name="edited.jpg", use_container_width=True)

# ====================================================================
# MODULE 7: 📜 প্রত্যয়ন পত্র ও ছাড়পত্র ফরম জেনারেটর
# ====================================================================
elif st.session_state.active_module == "7":
    st.markdown("### 📜 7. চারিত্রিক/নাগরিক প্রত্যয়ন পত্র ও স্কুল ছাড়পত্র (TC) জেনারেটর")
    doc_type = st.selectbox("নথিপত্রের ধরণ সিলেক্ট করুন:", ["নাগরিক/চারিত্রিক প্রত্যয়ন পত্র", "স্কুল/কলেজ ছাড়পত্র (Transfer Certificate)"])
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        c_name = st.text_input("আবেদনকারীর নাম (Name):", "মোঃ হাসানুর রহমান")
        c_father = st.text_input("পিতা/স্বামীর নাম (Father's Name):", "মোঃ আব্দুর রশিদ")
        c_mother = st.text_input("মাতার নাম (Mother's Name):", "মোসাম্মৎ রহিমা বেগম")
    with col_f2:
        c_village = st.text_input("গ্রাম/মহল্লা (Village):", "মনিরামপুর")
        c_post = st.text_input("ডাকঘর (Post Office):", "মনিরামপুর")
        c_thana = st.text_input("উপজেলা ও জেলা (Upazila & District):", "মনিরামপুর, যশোর")
        
    if doc_type == "নাগরিক/চারিত্রিক প্রত্যয়ন পত্র":
        c_character = st.selectbox("চারিত্রিক অবস্থা:", ["উত্তম", "ভালো", "সন্তোষজনক"])
        template = f"""
        ===================================================================
                                প্রত্যয়ন পত্র
        ===================================================================
        এই মর্মে প্রত্যয়ন করা যাইতেছে যে, {c_name}, পিতা: {c_father}, মাতা: {c_mother}, 
        গ্রাম: {c_village}, ডাকঘর: {c_post}, উপজেলা: {c_thana}। 
        
        তিনি আমার পরিচিত। আমার জানামতে তিনি অত্র এলাকার স্থায়ী বাসিন্দা এবং বাংলাদেশের 
        একজন সৎ ও নাগরিক। সমাজ বা রাষ্ট্র বিরোধী কোনো কাজের সাথে তিনি জড়িত নহেন। 
        তাহার নৈতিক চরিত্র অত্যন্ত {c_character}। 
        
        আমি তাহার সর্বাঙ্গীন উন্নতি ও মঙ্গল কামনা করি।
        
                                                   স্বাক্ষর ও সীল 
                                             চেয়ারম্যান / পৌর মেয়র
        """
    else:
        c_class = st.text_input("শেষ পঠিত শ্রেণী (Last Class):", "নবম শ্রেণী")
        c_roll = st.text_input("রোল নম্বর (Roll No):", "০৫")
        template = f"""
        ===================================================================
                        বিদ্যালয় / কলেজ ছাড়পত্র (TC)
        ===================================================================
        এই মর্মে ছাড়পত্র প্রদান করা যাইতেছে যে, {c_name}, পিতা: {c_father}, মাতা: {c_mother}, 
        অত্র প্রতিষ্ঠানের একজন নিয়মিত শিক্ষার্থী ছিলেন। তিনি সর্বশেষ {c_class}-এ অধ্যয়ন করিয়াছেন, 
        যাহার রোল নম্বর ছিল {c_roll}। 
        
        অত্র প্রতিষ্ঠানে অধ্যয়নকালীন তাহার আচরণ সন্তোষজনক ছিল। প্রতিষ্ঠানের নিকট তাহার কোনো 
        বকেয়া পাওনা বা দেনা নাই। 
        
        তাহার ভবিষ্যতের সকল প্রকার সাফল্য ও উন্নতি কামনা করিয়া অত্র ছাড়পত্র ইস্যু করা হইলো।
        
                                                   স্বাক্ষর ও সীল 
                                                   প্রধান শিক্ষক
        """
        
    st.markdown("#### 📄 প্রিন্ট প্রিভিউ (Print Preview):")
    st.markdown(f"<div class='form-preview'><pre>{template}</pre></div>", unsafe_allow_html=True)
    st.download_button("📥 প্রিন্ট করার জন্য ডকুমেন্ট ডাউনলোড করুন (TXT)", data=template.encode('utf-8'), file_name="document_output.txt", use_container_width=True)

# ====================================================================
# MODULE 8: 📝 প্রফেশনাল সিভি/বায়োডাটা মেকার ফরম
# ====================================================================
elif st.session_state.active_module == "8":
    st.markdown("### 📝 8. প্রফেশনাল সিভি / বায়োডাটা মেকার ফরম")
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        cv_name = st.text_input("পূর্ণ নাম (Full Name):", "হাসানুর রহমান")
        cv_email = st.text_input("ইমেইল (Email):", "hasanur@example.com")
        cv_phone = st.text_input("মোবাইল (Mobile):", "01743614359")
        cv_edu = st.text_area("শিক্ষাগত যোগ্যতা (Education):", "১. এসএসসি - জিপিএ ৫.০০ (২০১৮)\n২. এইচএসসি - জিপিএ ৪.৮ো (২০২০)")
    with col_c2:
        cv_skills = st.text_area("দক্ষতা (Skills):", "কম্পিউটার টাইপিং, গ্রাফিক্স ডিজাইন, ইন্টারনেট ব্রাউজিং ও অনলাইন অ্যাপ্লিকেশন")
        cv_exp = st.text_area("অভিজ্ঞতা (Experience):", "হাসানুর কম্পিউটার স্টুডিওতে ৩ বছরের ডিজিটাল সার্ভিস প্রদানের অভিজ্ঞতা।")
        
    cv_template = f"""
    =======================================================================
                                 CURRICULUM VITAE
    =======================================================================
    নাম (Name)       : {cv_name}
    মোবাইল (Mobile)  : {cv_phone}
    ইমেইল (Email)    : {cv_email}
    -----------------------------------------------------------------------
    CAREER OBJECTIVE:
    To work in a challenging environment where I can utilize my computer skills 
    and general expertise to contribute effectively to the organization.
    
    EDUCATIONAL QUALIFICATION:
    {cv_edu}
    
    PROFESSIONAL SKILLS:
    {cv_skills}
    
    WORK EXPERIENCE:
    {cv_exp}
    -----------------------------------------------------------------------
    Declaration: I hereby declare that all the information provided above is true 
    to the best of my knowledge.
    
    
    👉 Signature: __________________
    """
    st.markdown("#### 📄 সিভি রেডি প্রিভিউ:")
    st.markdown(f"<div class='form-preview'><pre>{cv_template}</pre></div>", unsafe_allow_html=True)
    st.download_button("📥 সিভি (CV) ফাইল ডাউনলোড করুন", data=cv_template.encode('utf-8'), file_name="Hasanur_Studio_CV.txt", use_container_width=True)

# ====================================================================
# MODULE 9: 🔗 PDF Tools (Merger & Delete)
# ====================================================================
elif st.session_state.active_module == "9":
    st.markdown("### 🔗 9. অল-ইন-ওয়ান পিডিএফ টুলবক্স")
    pdf_mode = st.radio("পিডিএফ সার্ভিস সিলেক্ট করুন:", ["PDF Merger (একাধিক পিডিএফ জোড়া দিন)", "Page Delete (পেজ বাদ দিন)"])
    
    if "Merger" in pdf_mode:
        pdf_files = st.file_uploader("Upload 2 or more PDFs:", type=["pdf"], accept_multiple_files=True)
        if pdf_files and len(pdf_files) >= 2:
            if st.button("Merge PDFs", type="primary", use_container_width=True):
                writer = PdfWriter()
                for pdf in pdf_files:
                    reader = PdfReader(pdf)
                    for page in reader.pages:
                        writer.add_page(page)
                out_pdf = io.BytesIO(); writer.write(out_pdf); writer.close()
                st.success("Successfully Merged!")
                st.download_button("📥 Download PDF", data=out_pdf.getvalue(), file_name="merged.pdf", mime="application/pdf", use_container_width=True)
    else:
        single_pdf = st.file_uploader("Upload PDF:", type=["pdf"])
        if single_pdf:
            reader = PdfReader(single_pdf); total = len(reader.pages)
            st.info(f"Total Pages: {total}")
            del_page = st.number_input(f"Enter page number to delete (1 to {total}):", min_value=1, max_value=total, value=1)
            if st.button("Delete Page", type="primary", use_container_width=True):
                writer = PdfWriter()
                for i in range(total):
                    if i != (del_page - 1):
                        writer.add_page(reader.pages[i])
                out_pdf = io.BytesIO(); writer.write(out_pdf); writer.close()
                st.success("Page Deleted Successfully!")
                st.download_button("📥 Download Edited PDF", data=out_pdf.getvalue(), file_name="edited.pdf", mime="application/pdf", use_container_width=True)

# ====================================================================
# MODULE 10: 🌐 অনলাইন সেবা ও লিঙ্কসমূহ
# ====================================================================
else:
    st.markdown("### 🌐 10. অল-ইন-ওয়ান অনলাইন সেবা, অ্যাপ্লিকেশন ও লিঙ্ক ডিরেক্টরি")
    
    st.markdown("<div class='header-link'>🛂 পাসপোর্ট ও ভিসা ট্র্যাকিং পোর্টাল</div>", unsafe_allow_html=True)
    passport_links = {
        "ই-পাসপোর্ট নতুন আবেদন": "https://www.epassport.gov.bd",
        "পাসপোর্ট স্ট্যাটাস চেক": "https://www.epassport.gov.bd/landing",
        "বাংলাদেশ অনলাইন visa (IVAC)": "https://www.visa.gov.bd",
        "भारतीय visa আবেদন (IVAC)": "https://www.ivacbd.com",
        "ভিসা চেকিং পোর্টাল (বিদেশ)": "https://services.mofa.gov.bd"
    }
    html_p = "".join([f'<a class="link-box" href="{url}" target="_blank">{name}</a>' for name, url in passport_links.items()])
    st.markdown(html_p, unsafe_allow_html=True)
    
    st.markdown("<div class='header-link'>📝 চাকরি, এনআইডি ও নাগরিক আবেদন পোর্টাল</div>", unsafe_allow_html=True)
    gov_links = {
        "টেলিটক সরকারি চাকরি আবেদন": "http://teletalk.com.bd",
        "জন্ম ও মৃত্যু নিবন্ধন": "https://bdris.gov.bd",
        "জাতীয় পরিচয় পত্র (NID Correction)": "https://services.nidw.gov.bd",
        "ভূমি খতিয়ান ও পর্চা (e-Porcha)": "https://land.gov.bd",
        "ড্রাইভিং লাইসেন্স (BRTA BSP)": "https://bsp.brta.gov.bd",
        "অনলাইন আয়কর রেজিষ্ট্রেশন (e-TIN)": "https://secure.incometax.gov.bd",
        "করোনা টিকা কার্ড (সুরক্ষা)": "https://surokkha.gov.bd",
        "রেলওয়ে অনলাইন টিকেট": "https://eticket.railway.gov.bd",
        "শিক্ষা বোর্ড রেজাল্ট": "http://www.educationboardresults.gov.bd",
        "জাতীয় বিশ্ববিদ্যালয় (NU) ভর্তি/ফরম": "https://www.nu.ac.bd",
        "উন্মুক্ত বিশ্ববিদ্যালয় (BOU) পোর্টাল": "https://www.bou.ac.bd",
        "প্রবাসী কল্যাণ ও কর্মসংস্থান (BMET)": "https://www.probashi.gov.bd"
    }
    html_g = "".join([f'<a class="link-box" href="{url}" target="_blank">{name}</a>' for name, url in gov_links.items()])
    st.markdown(html_g, unsafe_allow_html=True)

st.markdown(f"<div class='footer'>{footer_text}</div>", unsafe_allow_html=True)
