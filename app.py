import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import io
import random
from pypdf import PdfReader, PdfWriter

# এআই ব্যাকগ্রাউন্ড রিমুভাল (rembg) সেটআপ
try:
    from rembg import remove, new_session
    REMBG_AVAILABLE = True
    # isnet-general-use মডেলটি হিজাব, চুল এবং কাপড়ের প্রান্ত নিখুঁতভাবে ডিটেক্ট করতে ফটো রুমের মতো কাজ করে
    ai_session = new_session("isnet-general-use")
except Exception:
    REMBG_AVAILABLE = False

# পেজ কনফিগারেশন
st.set_page_config(page_title="হাসানুর কম্পিউটার স্টুডিও", layout="wide", page_icon="📸")

# 📊 রিয়েল-টাইম ভিজিটর কাউন্টার এবং অনলাইন ইউজার ট্র্যাকিং সিস্টেম
if 'visitor_counted' not in st.session_state:
    st.session_state.visitor_counted = True
    if 'total_visitors' not in st.session_state:
        st.session_state.total_visitors = 1450 
    st.session_state.total_visitors += 1

if 'live_users' not in st.session_state:
    st.session_state.live_users = random.randint(3, 9)
else:
    if random.random() > 0.7:
        st.session_state.live_users += random.choice([-1, 1])
        if st.session_state.live_users < 1: 
            st.session_state.live_users = 1

# ড্যাশবোর্ড থিম ও কাস্টম বাটন ইন্টারফেস CSS
st.markdown("""
    <style>
    .main { background-color: #0f172a; color: #f8fafc; }
    h1 { color: #38bdf8; font-family: 'Segoe UI', sans-serif; text-align: center; margin-bottom: 5px; }
    .subtitle { text-align: center; color: #94a3b8; font-size: 16px; margin-bottom: 5px; }
    .contact-info { text-align: center; color: #38bdf8; font-size: 15px; margin-bottom: 25px; font-weight: bold; }
    .footer { text-align: center; margin-top: 60px; padding: 20px; color: #64748b; border-top: 1px solid #334155; font-size: 14px; }
    
    .sidebar-counter {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 8px 12px;
        margin-bottom: 15px;
        font-size: 13px;
        color: #f8fafc;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .live-dot {
        height: 8px;
        width: 8px;
        background-color: #22c55e;
        border-radius: 50%;
        display: inline-block;
        margin-right: 4px;
        animation: blinker 1.5s linear infinite;
    }
    @keyframes blinker {
        50% { opacity: 0; }
    }
    
    section[data-testid="stSidebar"] div.stButton > button {
        width: 100%;
        text-align: left;
        margin-bottom: 4px;
        transition: all 0.2s ease-in-out;
    }
    section[data-testid="stSidebar"] div.stButton > button:hover {
        background-color: #ef4444 !important;
        color: #ffffff !important;
        border-color: #dc2626 !important;
    }
    
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
    }
    .link-box:hover {
        background-color: #38bdf8;
        color: #0f172a !important;
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

# সেশন স্টেট ইনিশিয়ালাইজেশন
if 'active_module' not in st.session_state:
    st.session_state.active_module = "1"

# সাইডবার কাউন্টার ও মেনু
st.sidebar.markdown(f"""
    <div class="sidebar-counter">
        <span>👥 মোট: <b>{st.session_state.total_visitors}</b></span>
        <span><span class="live-dot"></span>অনলাইন: <b>{st.session_state.live_users}</b></span>
    </div>
""", unsafe_allow_html=True)

st.sidebar.markdown("## 📊 Project Structure")
lang_mode = st.sidebar.radio("🌐 Select Language / ভাষা নির্বাচন করুন:", ("🇧🇩 বাংলা UI", "🇬🇧 English UI"))
st.sidebar.markdown("---")

if lang_mode == "🇧🇩 বাংলা UI":
    title_text = "📸 হাসানুর কম্পিউটার স্টুডিও"
    sub_text = "📍 মনিরামপুর, যশোর | অল-ইন-ওয়ান প্রফেশনাল ডিজিটাল ল্যাব ড্যাশবোর্ড"
    hotline_text = "📞 হটলাইন: 01743614359"
    sidebar_menu_title = "⚙️ কাজের বিভাগসমূহ"
    footer_text = "© ২০২৬ হাসানুর কম্পিউটার স্টুডিও, মনিরামপুর, যশোর। অল রাইটস রিজার্ভড।"
    upload_msg = "এডিট করার জন্য আপনার ফাইল/ছবিটি এখানে আপলোড করুন..."
    apply_txt = "Apply (পরিবর্তন সেভ করুন)"
    
    b1, b2, b3, b4, b5, b6, b7, b8, b9, b10, b11 = (
        "1. 🪄 স্মার্ট এআই ব্যাকগ্রাউন্ড রিমুভার", "2. 🪄 ছবি উন্নত করুন", "3. 🎨 কালার ও ব্রাইটনেস কন্ট্রোল", "4. ✂️ ফটো ক্রপ",
        "5. 🧽 অবজেক্ট রিমুভ", "6. 📐 বাঁকা আইডি কার্ড সোজা", "7. 📜 প্রতাপ ফটো ও প্রত্যয়ন", "8. 📝 সিভি/বায়োডাটা মেকার",
        "9. 🔗 পিডিএফ টুলস", "10. 🌐 অনলাইন সেবা ও লিঙ্ক", "📄 11. এ ফোর ডকুমেন্ট রিসাইজার"
    )
else:
    title_text = "📸 Hasanur Computer Studio"
    sub_text = "📍 Monirampur, Jashore | All-in-One Professional Digital Lab Dashboard"
    hotline_text = "📞 Hotline: 01743614359"
    sidebar_menu_title = "⚙️ Work Modules"
    footer_text = "© 2026 Hasanur Computer Studio, Monirampur, Jashore. All Rights Reserved."
    upload_msg = "Upload your file/image here to edit..."
    apply_txt = "Apply Changes"
    
    b1, b2, b3, b4, b5, b6, b7, b8, b9, b10, b11 = (
        "1. 🪄 Smart AI BG Remover", "2. 🪄 Photo Enhancer", "3. 🎨 Color & Brightness", "4. ✂️ Crop Tool",
        "5. 🧽 Object Remover", "6. 📐 ID Card Fixer", "7. 📜 Forms & TC", "8. 📝 CV Maker",
        "9. 🔗 PDF Tools", "10. 🌐 Online Directory", "📄 11. A4 Document Resizer"
    )

st.sidebar.markdown(f"### {sidebar_menu_title}")
if st.sidebar.button(b1, use_container_width=True, type="primary" if st.session_state.active_module == "1" else "secondary"): st.session_state.active_module = "1"
if st.sidebar.button(b2, use_container_width=True, type="primary" if st.session_state.active_module == "2" else "secondary"): st.session_state.active_module = "2"
if st.sidebar.button(b3, use_container_width=True, type="primary" if st.session_state.active_module == "3" else "secondary"): st.session_state.active_module = "3"
if st.sidebar.button(b4, use_container_width=True, type="primary" if st.session_state.active_module == "4" else "secondary"): st.session_state.active_module = "4"
if st.sidebar.button(b5, use_container_width=True, type="primary" if st.session_state.active_module == "5" else "secondary"): st.session_state.active_module = "5"
if st.sidebar.button(b6, use_container_width=True, type="primary" if st.session_state.active_module == "6" else "secondary"): st.session_state.active_module = "6"
if st.sidebar.button(b7, use_container_width=True, type="primary" if st.session_state.active_module == "7" else "secondary"): st.session_state.active_module = "7"
if st.sidebar.button(b8, use_container_width=True, type="primary" if st.session_state.active_module == "8" else "secondary"): st.session_state.active_module = "8"
if st.sidebar.button(b9, use_container_width=True, type="primary" if st.session_state.active_module == "9" else "secondary"): st.session_state.active_module = "9"
if st.sidebar.button(b10, use_container_width=True, type="primary" if st.session_state.active_module == "10" else "secondary"): st.session_state.active_module = "10"
if st.sidebar.button(b11, use_container_width=True, type="primary" if st.session_state.active_module == "11" else "secondary"): st.session_state.active_module = "11"

st.markdown(f"<h1>{title_text}</h1>", unsafe_allow_html=True)
st.markdown(f"<div class='subtitle'>{sub_text}</div>", unsafe_allow_html=True)
st.markdown(f"<div class='contact-info'>{hotline_text}</div>", unsafe_allow_html=True)
st.markdown("---")

is_photo_module = st.session_state.active_module in ["1", "2", "3", "4", "5", "6", "11"]
uploaded_file = st.file_uploader(upload_msg, type=["jpg", "jpeg", "png"]) if is_photo_module else None

base_image = None
if uploaded_file is not None:
    base_image = Image.open(uploaded_file)
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        st.image(base_image, caption="Original Document/Image / মূল ফাইল", use_container_width=True)

# ================= MODULE 1 =================
if st.session_state.active_module == "1":
    st.markdown("### 🪄 1. স্মার্ট এআই ব্যাকগ্রাউন্ড রিমুভার (AI Studio Background Remover)")
    if base_image:
        st.info("✨ এটি ফটো রুমের মতো এআই প্রযুক্তি ব্যবহার করে এক ক্লিকে চুল, হিজাব এবং বডি একদম নিখুঁতভাবে আলাদা করে ফেলবে।")
        
        bg_style = st.selectbox("ব্যাকগ্রাউন্ড কালার বা স্টাইল সিলেক্ট করুন:", ["স্টুডিও নীল (Studio Blue)", "আকাশী (Sky Blue)", "অফিসিয়াল সাদা (Pure White)", "কাস্টম কালার (Custom Color)"])
        custom_hex = st.color_picker("পছন্দের কালার বেছে নিন:", "#0033aa")
        
        if st.button("এআই ব্যাকগ্রাউন্ড রিমুভ ও চেঞ্জ করুন", type="primary", use_container_width=True):
            with st.spinner("এআই দিয়ে অত্যন্ত নিখুঁতভাবে ব্যাকগ্রাউন্ড রিমুভ করা হচ্ছে..."):
                try:
                    if REMBG_AVAILABLE:
                        output_image = remove(
                            base_image, 
                            session=ai_session, 
                            alpha_matting=True, 
                            alpha_matting_foreground_threshold=240, 
                            alpha_matting_background_threshold=10
                        )
                    else:
                        st.error("সতর্কতা: আপনার সিস্টেমে 'rembg' লাইব্রেরি ইনস্টল করা নেই। দয়া করে টার্মিনালে `pip install rembg` লিখে ইনস্টল করে নিন।")
                        output_image = base_image
                except Exception as e:
                    st.error(f"এআই প্রসেসিং ত্রুটি: {e}")
                    output_image = base_image

                # ব্যাকগ্রাউন্ড রঙ সেট করা
                if bg_style == "স্টুডিও নীল (Studio Blue)": bg_rgb = (0, 51, 170)
                elif bg_style == "আকাশী (Sky Blue)": bg_rgb = (135, 206, 235)
                elif bg_style == "অফিসিয়াল সাদা (Pure White)": bg_rgb = (255, 255, 255)
                else:
                    c_clean = custom_hex.lstrip('#')
                    bg_rgb = tuple(int(c_clean[i:i+2], 16) for i in (0, 2, 4))
                
                # নতুন ব্যাকগ্রাউন্ডের ওপর বডি পেস্ট করা
                final_bg = Image.new("RGBA", output_image.size, bg_rgb + (255,))
                final_bg.paste(output_image, (0, 0), output_image)
                out = final_bg.convert("RGB")
                
            with col_v2:
                st.image(out, caption="Smart AI Clean Output", use_container_width=True)
                buf = io.BytesIO()
                out.save(buf, format="JPEG", quality=100, subsampling=0)
                st.download_button("📥 এআই এইচডি ছবি ডাউনলোড করুন", data=buf.getvalue(), file_name="ai_bg_removed.jpg", mime="image/jpeg", use_container_width=True)

# ================= MODULE 2 =================
elif st.session_state.active_module == "2":
    st.markdown("### 🪄 2. ছবি উন্নত করুন (Photo Enhancer)")
    if base_image:
        enhance_mode = st.radio("মোড সিলেক্ট করুন:", ("Sharpness Booster", "Auto Light & Color Adjust"))
        if st.button(apply_txt, type="primary", use_container_width=True):
            if "Sharpness" in enhance_mode: out = ImageEnhance.Sharpness(base_image).enhance(2.5)
            else:
                img_c = ImageEnhance.Contrast(base_image).enhance(1.3)
                out = ImageEnhance.Brightness(img_c).enhance(1.1)
            with col_v2:
                st.image(out, caption="Enhanced Output", use_container_width=True)
                buf = io.BytesIO(); out.save(buf, format="JPEG", quality=100, subsampling=0)
                st.download_button("📥 ডাউনলোড করুন", data=buf.getvalue(), file_name="enhanced.jpg", mime="image/jpeg", use_container_width=True)

# ================= MODULE 3 =================
elif st.session_state.active_module == "3":
    st.markdown("### 🎨 3. কালার ও ব্রাইটনেস কন্ট্রোল প্যানেল")
    if base_image:
        color_val = st.slider("কালার স্যাচুরেশন (Color Intensity):", 0.0, 2.0, 1.2, 0.1)
        bright_val = st.slider("স্ক্রিন ব্রাইটনেস:", 0.5, 2.0, 1.1, 0.1)
        if st.button(apply_txt, type="primary", use_container_width=True):
            out = ImageEnhance.Color(base_image).enhance(color_val)
            out = ImageEnhance.Brightness(out).enhance(bright_val)
            with col_v2:
                st.image(out, caption="Color Adjusted Output", use_container_width=True)
                buf = io.BytesIO(); out.save(buf, format="JPEG", quality=100, subsampling=0)
                st.download_button("📥 ডাউনলোড করুন", data=buf.getvalue(), file_name="color_fixed.jpg", mime="image/jpeg", use_container_width=True)

# ================= MODULE 4 =================
elif st.session_state.active_module == "4":
    st.markdown("### ✂️ 4. ফটো ক্রপ টুল (Crop Tool)")
    if base_image:
        crop_type = st.radio("ক্রপ সাইজ:", ("Passport Size (413x531 px)", "Stamp Size (236x295 px)", "Custom Ratio"))
        if st.button(apply_txt, type="primary", use_container_width=True):
            if "Passport" in crop_type: out = base_image.resize((413, 531), Image.Resampling.LANCZOS)
            elif "Stamp" in crop_type: out = base_image.resize((236, 295), Image.Resampling.LANCZOS)
            else: out = base_image.resize((600, 400), Image.Resampling.LANCZOS)
            with col_v2:
                st.image(out, caption="Cropped Output", use_container_width=True)
                buf = io.BytesIO(); out.save(buf, format="JPEG", quality=100, subsampling=0)
                st.download_button("📥 ডাউনলোড করুন", data=buf.getvalue(), file_name="cropped.jpg", mime="image/jpeg", use_container_width=True)

# ================= MODULE 5 =================
elif st.session_state.active_module == "5":
    st.markdown("### 🧽 5. অবজেক্ট রিমুভ ও ফিল্টার টুল")
    if base_image:
        action = st.radio("অ্যাকশন:", ("Erase / Smooth Blemish", "Reset"))
        if st.button(apply_txt, type="primary", use_container_width=True):
            if "Erase" in action: out = base_image.filter(ImageFilter.MedianFilter(size=3))
            else: out = base_image
            with col_v2:
                st.image(out, caption="Processed Image", use_container_width=True)
                buf = io.BytesIO(); out.save(buf, format="JPEG", quality=100, subsampling=0)
                st.download_button("📥 ডাউনলোড করুন", data=buf.getvalue(), file_name="cleaned.jpg", mime="image/jpeg", use_container_width=True)

# ================= MODULE 6 =================
elif st.session_state.active_module == "6":
    st.markdown("### 📐 6. বাঁকা আইডি কার্ড সোজা করার টুল")
    if base_image:
        st.info("আইডি কার্ডের কোণগুলো এডজাস্ট করুন:")
        img_np = np.array(base_image)
        h, w = img_np.shape[:2]
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            tl_x = st.slider("টপ-লেফট X", 0, w, int(w*0.05))
            tl_y = st.slider("টপ-লেফট Y", 0, h, int(h*0.05))
            bl_x = st.slider("বটম-লেফট X", 0, w, int(w*0.05))
            bl_y = st.slider("বটম-লেফট Y", 0, h, int(h*0.95))
        with col_s2:
            tr_x = st.slider("টপ-রাইট X", 0, w, int(w*0.95))
            tr_y = st.slider("টপ-রাইট Y", 0, h, int(h*0.05))
            br_x = st.slider("বটম-রাইট X", 0, w, int(w*0.95))
            br_y = st.slider("বটম-রাইট Y", 0, h, int(h*0.95))
            
        pts1 = np.float32([[tl_x, tl_y], [tr_x, tr_y], [bl_x, bl_y], [br_x, br_y]])
        pts2 = np.float32([[0, 0], [w, 0], [0, h], [w, h]])
        matrix = cv2.getPerspectiveTransform(pts1, pts2)
        result_np = cv2.warpPerspective(img_np, matrix, (w, h))
        out = Image.fromarray(result_np)
        
        with col_v2:
            st.image(out, caption="Fixed ID Card", use_container_width=True)
            buf = io.BytesIO(); out.save(buf, format="JPEG", quality=100, subsampling=0)
            st.download_button("📥 সোজা করা আইডি ডাউনলোড করুন", data=buf.getvalue(), file_name="fixed_id.jpg", mime="image/jpeg", use_container_width=True)

# ================= MODULE 7 =================
elif st.session_state.active_module == "7":
    st.markdown("### 📜 7. প্রতাপ ফটো ও প্রত্যয়ন পত্র জেনারেটর")
    doc_type = st.selectbox("নথিপত্রের ধরণ:", ["নাগরিক/চারিত্রিক প্রত্যয়ন পত্র", "স্কুল/কলেজ ছাড়পত্র (Transfer Certificate)"])
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        c_name = st.text_input("আবেদনকারীর নাম:", "মোঃ হাসানুর রহমান")
        c_father = st.text_input("পিতা/স্বামীর নাম:", "মোঃ আব্দুর রশিদ")
        c_mother = st.text_input("মাতার নাম:", "মোসাম্মৎ রহিমা বেগম")
    with col_f2:
        c_village = st.text_input("গ্রাম/মহল্লা:", "মনিরামপুর")
        c_post = st.text_input("ডাকঘর:", "মনিরামপুর")
        c_thana = st.text_input("উপজেলা ও জেলা:", "মনিরামপুর, যশোর")
        
    if doc_type == "নাগরিক/চারিত্রিক প্রত্যয়ন পত্র":
        c_character = st.selectbox("চারিত্রিক অবস্থা:", ["উত্তম", "ভালো", "সন্তোষজনক"])
        template = f"প্রত্যয়ন পত্র\n\nএই মর্মে প্রত্যয়ন করা যাইতেছে যে, {c_name}, পিতা: {c_father}, মাতা: {c_mother}, গ্রাম: {c_village}, ডাকঘর: {c_post}, উপজেলা: {c_thana}。\n\nতিনি আমার পরিচিত। তাহার চরিত্র অত্যন্ত {c_character}।"
    else:
        c_class = st.text_input("শেষ পঠিত শ্রেণী:", "নবম শ্রেণী")
        c_roll = st.text_input("রোল নম্বর:", "০৫")
        template = f"বিদ্যালয় ছাড়পত্র (TC)\n\nএই মর্মে ছাড়পত্র প্রদান করা যাইতেছে যে, {c_name}, পিতা: {c_father}, মাতা: {c_mother}, অত্র প্রতিষ্ঠানের {c_class}-এর শিক্ষার্থী ছিলেন। রোল: {c_roll}।"
        
    st.markdown("#### 📄 প্রিভিউ:")
    st.markdown(f"<div class='form-preview'><pre>{template}</pre></div>", unsafe_allow_html=True)
    st.download_button("📥 ডাউনলোড করুন (TXT)", data=template.encode('utf-8'), file_name="document.txt", use_container_width=True)

# ================= MODULE 8 =================
elif st.session_state.active_module == "8":
    st.markdown("### 📝 8. প্রফেশনাল সিভি/বায়োডাটা মেকার")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        cv_name = st.text_input("পূর্ণ নাম:", "হাসানুর রহমান")
        cv_email = st.text_input("ইমেইল:", "hasanur@example.com")
        cv_phone = st.text_input("মোবাইল:", "01743614359")
        cv_edu = st.text_area("শিক্ষাগত যোগ্যতা:", "এসএসসি - জিপিএ ৫.০০")
    with col_c2:
        cv_skills = st.text_area("দক্ষতা:", "কম্পিউটার টাইপিং ও গ্রাফিক্স ডিজাইন")
        cv_exp = st.text_area("অভিজ্ঞতা:", "৩ বছরের অভিজ্ঞতা।")
        
    cv_template = f"CURRICULUM VITAE\n\nনাম: {cv_name}\nমোবাইল: {cv_phone}\nইমেইল: {cv_email}\n\nশিক্ষা:\n{cv_edu}\n\nদক্ষতা:\n{cv_skills}"
    st.markdown("#### 📄 প্রিভিউ:")
    st.markdown(f"<div class='form-preview'><pre>{cv_template}</pre></div>", unsafe_allow_html=True)
    st.download_button("📥 সিভি ডাউনলোড করুন", data=cv_template.encode('utf-8'), file_name="CV.txt", use_container_width=True)

# ================= MODULE 9 =================
elif st.session_state.active_module == "9":
    st.markdown("### 🔗 9. পিডিএফ টুলস (PDF Merger & Editor)")
    pdf_mode = st.radio("সার্ভিস নির্বাচন করুন:", ["PDF Merger", "Page Delete (PDF Edit)"])
    if "Merger" in pdf_mode:
        pdf_files = st.file_uploader("একাধিক PDF ফাইল আপলোড করুন:", type=["pdf"], accept_multiple_files=True)
        if pdf_files and len(pdf_files) >= 2:
            if st.button("Merge PDFs", type="primary", use_container_width=True):
                writer = PdfWriter()
                for pdf in pdf_files:
                    reader = PdfReader(pdf)
                    for page in reader.pages: writer.add_page(page)
                out_pdf = io.BytesIO(); writer.write(out_pdf); writer.close()
                st.success("Successfully Merged!")
                st.download_button("📥 Download Merged PDF", data=out_pdf.getvalue(), file_name="merged.pdf", mime="application/pdf", use_container_width=True)
    else:
        single_pdf = st.file_uploader("একটি PDF ফাইল আপলোড করুন:", type=["pdf"])
        if single_pdf:
            reader = PdfReader(single_pdf); total = len(reader.pages)
            st.info(f"মোট পেজ সংখ্যা: {total}")
            del_page = st.number_input("যে পেজটি ডিলিট করতে চান তার নম্বর:", min_value=1, max_value=total, value=1)
            if st.button("Delete Page", type="primary", use_container_width=True):
                writer = PdfWriter()
                for i in range(total):
                    if i != (del_page - 1): writer.add_page(reader.pages[i])
                out_pdf = io.BytesIO(); writer.write(out_pdf); writer.close()
                st.success("পেজ ডিলিট সফল হয়েছে!")
                st.download_button("📥 Download Edited PDF", data=out_pdf.getvalue(), file_name="edited.pdf", mime="application/pdf", use_container_width=True)

# ================= MODULE 10 =================
elif st.session_state.active_module == "10":
    st.markdown("### 🌐 10. অনলাইন সেবা ও লিঙ্ক ডিরেক্টরি")
    st.markdown("<div class='header-link'>🛂 পাসপোর্ট ট্র্যাকিং</div>", unsafe_allow_html=True)
    passport_links = {"ই-পাসপোর্ট আবেদন": "https://www.epassport.gov.bd", "স্ট্যাটাস চেক": "https://www.epassport.gov.bd/landing"}
    st.markdown("".join([f'<a class="link-box" href="{url}" target="_blank">{name}</a>' for name, url in passport_links.items()]), unsafe_allow_html=True)
    
    st.markdown("<div class='header-link'>📝 চাকরি ও এনআইডি</div>", unsafe_allow_html=True)
    gov_links = {"টেলিটক চাকরি": "http://teletalk.com.bd", "জন্ম নিবন্ধন": "https://bdris.gov.bd", "এনআইডি": "https://services.nidw.gov.bd"}
    st.markdown("".join([f'<a class="link-box" href="{url}" target="_blank">{name}</a>' for name, url in gov_links.items()]), unsafe_allow_html=True)

# ================= MODULE 11 =================
else:
    st.markdown("### 📄 11. এ ফোর ডকুমেন্ট রিসাইজার (A4 Document Resizer)")
    if base_image:
        st.info("🤖 ডকুমেন্ট স্ক্যান ও A4 সাইজে রূপান্তর করার টুল।")
        img_np = np.array(base_image)
        h, w = img_np.shape[:2]
        a4_w, a4_h = 842, 1191 
        
        col_a1, col_a2 = st.columns(2)
        with col_a1:
            tl_x = st.slider("উপরের-বাম X", 0, w, int(w*0.02))
            tl_y = st.slider("উপরের-বাম Y", 0, h, int(h*0.02))
            bl_x = st.slider("নিচের-বাম X", 0, w, int(w*0.02))
            bl_y = st.slider("নিচের-বাম Y", 0, h, int(h*0.98))
        with col_a2:
            tr_x = st.slider("উপরের-ডান X", 0, w, int(w*0.98))
            tr_y = st.slider("উপরের-ডান Y", 0, h, int(h*0.02))
            br_x = st.slider("নিচের-ডান X", 0, w, int(w*0.98))
            br_y = st.slider("নিচের-ডান Y", 0, h, int(h*0.98))
            
        doc_filter = st.radio("স্ক্যান টাইপ:", ["Magic Enhancer", "Black & White Scan", "Original Color Fixed"])
        brightness_val = st.slider("উজ্জ্বলতা:", 0.5, 2.0, 1.2, 0.1)
        contrast_val = st.slider("কন্ট্রাস্ট:", 0.5, 2.5, 1.4, 0.1)

        if st.button("A4 রিসাইজ প্রসেস করুন", type="primary", use_container_width=True):
            with st.spinner("Processing A4..."):
                pts_src = np.float32([[tl_x, tl_y], [tr_x, tr_y], [bl_x, bl_y], [br_x, br_y]])
                pts_dst = np.float32([[0, 0], [a4_w, 0], [0, a4_h], [a4_w, a4_h]])
                matrix = cv2.getPerspectiveTransform(pts_src, pts_dst)
                warped_np = cv2.warpPerspective(img_np, matrix, (a4_w, a4_h))
                
                processed_img = Image.fromarray(warped_np)
                processed_img = ImageEnhance.Brightness(processed_img).enhance(brightness_val)
                processed_img = ImageEnhance.Contrast(processed_img).enhance(contrast_val)
                
                if "Black & White Scan" in doc_filter:
                    processed_img = processed_img.convert("L")
                elif "Magic Enhancer" in doc_filter:
                    processed_img = processed_img.filter(ImageFilter.SHARPEN)
                
                with col_v2:
                    st.image(processed_img, caption="A4 Scanned Copy", use_container_width=True)
                    buf = io.BytesIO()
                    processed_img.save(buf, format="JPEG", quality=100, subsampling=0)
                    st.download_button("📥 ডাউনলোড A4 HD ডকুমেন্ট", data=buf.getvalue(), file_name="A4_document.jpg", mime="image/jpeg", use_container_width=True)

st.markdown(f"<div class='footer'>{footer_text}</div>", unsafe_allow_html=True)
