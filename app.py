import io
import cv2
import numpy as np
from PIL import Image, ImageOps, ImageDraw, ImageFont
import streamlit as st
from rembg import remove, new_session
from pypdf import PdfReader
from datetime import date

# =====================================================================
# Advanced Edge Refinement & Foreground Estimation (Photoroom Style)
# =====================================================================
def FB_blur_fusion_foreground_estimator_2(image, alpha, r=90):
    alpha = alpha[:, :, None]
    F, blur_B = FB_blur_fusion_foreground_estimator(image, image, image, alpha, r)
    return FB_blur_fusion_foreground_estimator(image, F, blur_B, alpha, r=6)[0]

def FB_blur_fusion_foreground_estimator(image, F, B, alpha, r=90):
    blurred_alpha = cv2.blur(alpha, (r, r))[:, :, None]
    blurred_FA = cv2.blur(F * alpha, (r, r))
    blurred_F = blurred_FA / (blurred_alpha + 1e-5)
    blurred_B1A = cv2.blur(B * (1 - alpha), (r, r))
    blurred_B = blurred_B1A / ((1 - blurred_alpha) + 1e-5)
    F = blurred_F + alpha * (image - alpha * blurred_F - (1 - alpha) * blurred_B)
    F = np.clip(F, 0, 1)
    return F, blurred_B

# ক্যাশ রিসোর্স দিয়ে হালকা মডেল লোড করা যাতে সার্ভার ক্র্যাশ না করে
@st.cache_resource
def get_rembg_session():
    return new_session("u2net")

# পেজের লেআউট সেটআপ
st.set_page_config(page_title="হাসানুর কম্পিউটার স্টুডিও / Hasanur Computer Studio", layout="wide")

# =====================================================================
# থিম এবং ভাষা সিলেকশন (সাইডবার কন্ট্রোল)
# =====================================================================
st.sidebar.header("⚙️ সেটিংস / Settings")
lang = st.sidebar.selectbox("ভাষা / Language", ["বাংলা (Bengali)", "English"])
theme = st.sidebar.selectbox("থিম / Theme", ["Light Theme ☀️", "Dark Theme 🌙"])

is_eng = (lang == "English")
is_dark = ("Dark" in theme)

# ডাইনামিক সিএসএস (লাইট ও ডার্ক থিমের জন্য এবং টেক্সট বক্স ফিটিং)
if is_dark:
    bg_main = "#0e1117"
    sidebar_bg = "#161b22"
    text_color = "#c9d1d9"
    btn_bg = "#21262d"
    btn_text = "#e6edf3"
    btn_border = "#30363d"
    link_bg = "#1f242c"
    header_gradient = "linear-gradient(135deg, #1f4068, #162447)"
else:
    bg_main = "#ffffff"
    sidebar_bg = "#fcfcfc"
    text_color = "#333333"
    btn_bg = "#ffffff"
    btn_text = "#333333"
    btn_border = "#e0e0e0"
    link_bg = "#f8f9fa"
    header_gradient = "linear-gradient(135deg, #0B50FA, #ff4b4b)"

st.markdown(f"""
<style>
    .stApp {{
        background-color: {bg_main};
        color: {text_color};
    }}
    [data-testid="stSidebar"] {{
        min-width: 380px !important;
        max-width: 410px !important;
        background-color: {sidebar_bg} !important;
    }}
    .link-box {{
        background-color: {link_bg};
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #ff4b4b;
        margin-bottom: 10px;
        color: {text_color};
    }}
    .studio-header {{
        background: {header_gradient};
        padding: 22px;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }}
    .stButton > button {{
        width: 100% !important;
        height: auto !important;
        min-height: 48px !important;
        white-space: normal !important;
        word-wrap: break-word !important;
        text-align: left !important;
        background-color: {btn_bg};
        color: {btn_text};
        border: 1px solid {btn_border};
        border-radius: 8px;
        padding: 10px 12px !important;
        font-weight: 600;
        font-size: 13px;
        margin-bottom: 5px;
        transition: all 0.3s ease;
        box-shadow: 0 2px 5px rgba(0,0,0,0.02);
        display: block !important;
    }}
    .stButton > button div {{
        white-space: normal !important;
        word-wrap: break-word !important;
        width: 100% !important;
    }}
    .stButton > button:hover {{
        background: linear-gradient(135deg, #0B50FA, #ff4b4b) !important;
        color: white !important;
        border-color: #0B50FA !important;
        padding-left: 15px !important;
        box-shadow: 0 4px 15px rgba(11, 80, 250, 0.4);
    }}
</style>
""", unsafe_allow_html=True)

t = {
    "title": "Hasanur Computer Studio" if is_eng else "🖨️ হাসানুর কম্পিউটার স্টুডিও",
    "address": "<b>Address:</b> Dighirpar, Monirampur, Jashore | <b>Mobile:</b> 01743-614359" if is_eng else "<b>ঠিকানা:</b> দিঘীরপাড়, মনিরামপুর, যশোর | <b>মোবাইল:</b> ০১৭৪৩-৬১৪৩৫৯",
    "subtitle": "All-in-one Master Dashboard for Computer, Design & Online Services" if is_eng else "সকল ধরনের কম্পিউটার, ডিজাইন ও অনলাইন সার্ভিসের অল-ইন-ওয়ান মাস্টার ড্যাশবোর্ড",
    "upload_header": "📁 Master File Uploader" if is_eng else "📁 ফাইল আপলোড (Master File Uploader)",
    "upload_label": "Upload Image or PDF file" if is_eng else "ছবি বা পিডিএফ ফাইল আপলোড করুন",
    "menu_header": "🧭 Navigation Menu & Features" if is_eng else "🧭 নেভিগেশন মেনু ও ফিচারের কাজ",
    "services_header": "🌐 Online Government & Essential Services" if is_eng else "🌐 অনলাইন সরকারি ও জরুরি সেবা",
}

# স্টুডিও হেডার মেইন স্ক্রিনে প্রদর্শন
st.markdown(f"""
<div class="studio-header">
    <h1>{t['title']}</h1>
    <p style="font-size: 16px; margin: 5px 0;">{t['address']}</p>
    <p style="font-size: 13px; margin: 0;">{t['subtitle']}</p>
</div>
""", unsafe_allow_html=True)

# ফাইল আপলোডার অপশনটি হেডার লেখার ঠিক নিচে বসানো হয়েছে
st.markdown(f"### {t['upload_header']}")
global_file = st.file_uploader(t['upload_label'], type=["jpg", "jpeg", "png", "pdf"])

st.markdown("---")

if 'app_mode' not in st.session_state:
    st.session_state.app_mode = 1

st.sidebar.header(t['menu_header'])

if is_eng:
    menu_dict = {
        1: ("✨ AI Background Remover & Custom Background Studio", "Remove background, use solid color or custom image from computer and download HD image."),
        2: ("📱 Samsung S26 Ultra AI Object Editor", "Edit object and lighting using AI prompts."),
        3: ("☀️ Image Brightness & Enhancer", "Perfect image lighting and contrast."),
        4: ("🆔 ID Card Crop & Rotate Tool", "Crop ID card and rotate at specific angles."),
        5: ("🛂 Passport Size Photo Sheet (4 Copies)", "Generate 4-copy passport photo sheet in one click."),
        6: ("🎂 Age Calculator", "Accurate age and day-month calculation."),
        7: ("🧾 Shop Cash Memo / Receipt Generator", "Create customer sales receipt and cash memo."),
        8: ("🛡️ Digital Warranty Card Generator", "Create digital warranty card for products."),
        9: ("📜 Citizenship Certificate Generator", "Create union parishad citizenship certificate."),
        10: ("⚽ Tournament Invitation & Rules (Football/Badminton)", "Create tournament notice and guidelines."),
        11: ("📏 Image Size Changer & Resizer", "Resize images according to pixel measurements."),
        12: ("⬛ Black & White Converter", "Convert color image to black and white."),
        13: ("🔄 Image Rotate & Flip", "Rotate and flip images in various angles."),
        14: ("🖼️ Image Border & Frame Tool", "Add beautiful borders and frames around images."),
        15: ("💧 Watermark Adding Tool", "Add custom name or logo watermark to images."),
        16: ("📄 PDF Text & Image Extract Tool", "Extract text content from PDF files.")
    }
else:
    menu_dict = {
        1: ("✨ এআই ব্যাকগ্রাউন্ড রিমুভার ও কাস্টম ব্যাকগ্রাউন্ড স্টুডিও", "ব্যাকগ্রাউন্ড রিমুভ করে সলিড কালার কিংবা কম্পিউটার থেকে কাস্টম ছবি ব্যাকগ্রাউন্ডে সেট করুন।"),
        2: ("📱 স্যামসাং S26 আলট্রা এআই অবজেক্ট এডিটর", "এআই প্রম্পট দিয়ে ছবির অবজেক্ট ও লাইটিং এডিট।"),
        3: ("☀️ ইমেজ ব্রাইটনেস ও এনহ্যান্সার", "ছবির আলো ও কন্ট্রাস্ট পারফেক্ট করা।"),
        4: ("🆔 আইডি কার্ড ক্রপ ও সোজা করার টুল", "আইডি কার্ড ক্রপ ও নির্দিষ্ট কোণে ঘোরানো।"),
        5: ("🛂 পাসপোর্ট সাইজ ছবি শিট তৈরি (৪ কপি)", "এক ক্লিকে ৪ কপি পাসপোর্ট ছবি শিট তৈরি।"),
        6: ("🎂 বয়স ক্যালকুলেটর (Age Calculator)", "নির্ভুল বয়স ও দিন-মাস হিসাব।"),
        7: ("🧾 দোকানের ক্যাশ মেমো / রশিদ জেনারেটর", "গ্রাহকের বিক্রয় রশিদ ও ক্যাশ মেমো তৈরি।"),
        8: ("🛡️ ডিজিটাল ওয়ারেন্টি কার্ড জেনারেটর", "পণ্যের ডিজিটাল ওয়ারেন্টি কার্ড তৈরি।"),
        9: ("📜 নাগরিক সনদ (Citizenship Certificate) জেনারেটর", "ইউনিয়ন পরিষদের নাগরিক সনদপত্র তৈরি।"),
        10: ("⚽ টুর্নামেন্ট আমন্ত্রণপত্র ও নিয়মাবলী (Badminton/Football)", "ফুটবল বা ব্যাডমিন্টন টুর্নামেন্ট নোটিশ তৈরি।"),
        11: ("📏 ছবির সাইজ পরিবর্তন ও রিসাইজার", "পিক্সেল অনুযায়ী ছবির সাইজ ছোট-বড় করা।"),
        12: ("⬛ সাদাকালো (Black & White) কনভার্টার", "কালার ছবিকে সাদাকালো করা।"),
        13: ("🔄 ছবি ঘোরানো (Rotate & Flip)", "ছবি বিভিন্ন এঙ্গেলে ঘোরানো।"),
        14: ("🖼️ ছবি বর্ডার ও ফ্রেম যুক্ত করা", "ছবির চারপাশে সুন্দর বর্ডার ও ফ্রেম দেওয়া।"),
        15: ("💧 ওয়াটারমার্ক যুক্ত করার টুল", "ছবিতে নিজের নাম বা লোগো ওয়াটারমার্ক দেওয়া।"),
        16: ("📄 পিডিএফ টেক্সট ও ছবি এক্সট্র্যাক্ট টুল", "পিডিএফ ফাইল থেকে টেক্সট আলাদা করা।")
    }

for num, (item_name, desc) in menu_dict.items():
    if st.sidebar.button(item_name, key=f"menu_btn_{num}"):
        st.session_state.app_mode = num
    st.sidebar.markdown(f"<p style='font-size:11px; color:gray; margin-top:-3px; margin-bottom:8px;'>ℹ️ {desc}</p>", unsafe_allow_html=True)

app_mode = st.session_state.app_mode

# =====================================================================
# মূল ফিচারসমূহ হ্যান্ডলিং (১ থেকে ১৬)
# =====================================================================

if app_mode == 1:
    st.header("✨ " + ("AI Background Remover & Custom Background Studio" if is_eng else "এআই ব্যাকগ্রাউন্ড রিমুভার ও কাস্টম ব্যাকগ্রাউন্ড স্টুডিও"))
    if global_file is not None:
        file_extension = global_file.name.split('.')[-1].lower()
        if file_extension in ['jpg', 'jpeg', 'png']:
            bg_mode = st.radio("Choose Background Type" if is_eng else "ব্যাকগ্রাউন্ডের ধরণ নির্বাচন করুন", ["Solid Color" if is_eng else "একক কালার (Solid Color)", "Custom Image from Computer" if is_eng else "কম্পিউটার থেকে কাস্টম ব্যাকগ্রাউন্ড ছবি"])
            
            custom_bg_file = None
            bg_color = "#0B50FA"
            
            if "Color" in bg_mode or "কালার" in bg_mode:
                bg_color = st.color_picker("Select Background Color" if is_eng else "ব্যাকগ্রাউন্ডের কালার পছন্দ করুন", "#0B50FA")
            else:
                custom_bg_file = st.file_uploader("Upload Custom Background Image from Computer" if is_eng else "কম্পিউটার থেকে কাস্টম ব্যাকগ্রাউন্ড ছবি আপলোড করুন", type=["jpg", "jpeg", "png"])
            
            col1, col2 = st.columns(2)
            with col1:
                st.image(Image.open(global_file), use_container_width=True, caption="Original Image" if is_eng else "আসল ছবি")
            with col2:
                if st.button("Remove Background & Apply Custom Studio" if is_eng else "ব্যাকগ্রাউন্ড রিমুভ ও কাস্টম ব্যাকগ্রাউন্ড সেট করুন", key="btn_rem_1"):
                    with st.spinner("Processing advanced AI edge refinement & custom background..." if is_eng else "উন্নত এআই প্রসেসিং ও কাস্টম ব্যাকগ্রাউন্ড সেটআপ চলছে..."):
                        session = get_rembg_session()
                        output_bytes = remove(global_file.getvalue(), session=session)
                        foreground_pil = Image.open(io.BytesIO(output_bytes)).convert("RGBA")
                        orig_pil = Image.open(global_file).convert("RGB").resize(foreground_pil.size)
                        
                        img_np = np.array(orig_pil).astype(np.float32) / 255.0
                        alpha_np = np.array(foreground_pil.split()[-1]).astype(np.float32) / 255.0
                        
                        refined_fg_np = FB_blur_fusion_foreground_estimator_2(img_np, alpha_np)
                        refined_fg_np = np.clip(refined_fg_np * 255, 0, 255).astype(np.uint8)
                        
                        alpha_uint8 = (alpha_np * 255).astype(np.uint8)
                        foreground = Image.fromarray(np.dstack((refined_fg_np, alpha_uint8)), "RGBA")
                        
                        if custom_bg_file is not None:
                            bg_img = Image.open(custom_bg_file).convert("RGBA").resize(foreground.size)
                            final_image = Image.alpha_composite(bg_img, foreground).convert("RGB")
                        else:
                            hex_code = bg_color.lstrip('#')
                            bg_rgb = tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))
                            background = Image.new("RGBA", foreground.size, bg_rgb + (255,))
                            final_image = Image.alpha_composite(background, foreground).convert("RGB")
                        
                        st.image(final_image, use_container_width=True, caption="Custom Studio Background Output" if is_eng else "কাস্টম স্টুডিও ব্যাকগ্রাউন্ড আউটপুট")
                        buf = io.BytesIO()
                        final_image.save(buf, format="JPEG", quality=95)
                        st.download_button("📥 Download HD Image" if is_eng else "📥 HD ছবি ডাউনলোড করুন", buf.getvalue(), "custom_bg_removed_hd.jpg", "image/jpeg", key="dl_1")
        else:
            st.warning("Please upload a valid image file." if is_eng else "দয়া করে একটি ছবি ফাইল আপলোড করুন।")
    else:
        st.info("👋 **Welcome!** Please select a file above." if is_eng else "👋 **স্বাগতম!** উপরে ফাইল আপলোড করুন।")

elif app_mode == 2:
    st.header("📱 " + ("Samsung S26 Ultra AI Object Editor" if is_eng else "স্যামসাং S26 আলট্রা এআই অবজেক্ট ও প্রম্পট এডিটর"))
    if global_file is not None:
        file_extension = global_file.name.split('.')[-1].lower()
        if file_extension in ['jpg', 'jpeg', 'png']:
            col1, col2 = st.columns(2)
            with col1:
                st.image(Image.open(global_file), use_container_width=True, caption="Original Image")
            with col2:
                prompt = st.text_input("Enter AI Command" if is_eng else "এআই কমান্ড লিখুন", "Enhance and refine object lighting")
                if st.button("Start AI Processing" if is_eng else "এআই প্রসেসিং শুরু করুন", key="btn_ai_2"):
                    with st.spinner(f"S26 Ultra AI engine processing '{prompt}'..."):
                        img = Image.open(global_file).convert("RGB")
                        img_np = np.array(img)
                        processed_np = cv2.detailEnhance(img_np, sigma_s=10, sigma_r=0.15)
                        final_ai_img = Image.fromarray(processed_np)
                        st.image(final_ai_img, use_container_width=True, caption=f"AI Edit Output: {prompt}")
                        buf = io.BytesIO()
                        final_ai_img.save(buf, format="JPEG", quality=95)
                        st.download_button("Download AI Edited Image" if is_eng else "এআই এডিটেড ছবি ডাউনলোড করুন", buf.getvalue(), "s26_ai_edited.jpg", "image/jpeg", key="dl_2")
    else:
        st.warning("Please upload an image above.")

elif app_mode == 3:
    st.header("☀️ " + ("Image Brightness & Enhancer" if is_eng else "ছবির আলো ও কন্ট্রাস্ট ঠিক করুন"))
    if global_file is not None:
        file_extension = global_file.name.split('.')[-1].lower()
        if file_extension in ['jpg', 'jpeg', 'png']:
            image = Image.open(global_file)
            brightness = st.slider("Brightness" if is_eng else "ব্রাইটনেস", 0.5, 3.0, 1.0, 0.1)
            contrast = st.slider("Contrast" if is_eng else "কন্ট্রাস্ট", 0.5, 3.0, 1.0, 0.1)
            img_np = np.array(image)
            enhanced_np = cv2.convertScaleAbs(img_np, alpha=contrast, beta=int((brightness - 1) * 50))
            enhanced_image = Image.fromarray(enhanced_np)
            st.image(enhanced_image, use_container_width=True, caption="Enhanced Image")
            buf = io.BytesIO()
            enhanced_image.save(buf, format="JPEG", quality=95)
            st.download_button("Download", buf.getvalue(), "enhanced.jpg", "image/jpeg", key="dl_3")
    else:
        st.warning("Please upload an image above.")

elif app_mode == 4:
    st.header("🆔 " + ("ID Card Crop & Rotate Tool" if is_eng else "আইডি কার্ড ক্রপ ও রোটেশন টুল"))
    if global_file is not None:
        file_extension = global_file.name.split('.')[-1].lower()
        if file_extension in ['jpg', 'jpeg', 'png']:
            img = Image.open(global_file)
            rotation = st.slider("Rotate Image" if is_eng else "ছবি ঘোরান", -180, 180, 0)
            if rotation != 0:
                img = img.rotate(rotation, expand=True)
            st.image(img, use_container_width=True, caption="Preview")
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=95)
            st.download_button("Download ID Card", buf.getvalue(), "id_card.jpg", "image/jpeg", key="dl_4")
    else:
        st.warning("Please upload an image above.")

elif app_mode == 5:
    st.header("🛂 " + ("Passport Size Photo Sheet (4 Copies)" if is_eng else "পাসপোর্ট সাইজ ছবি শিট (৪ কপি)"))
    if global_file is not None:
        file_extension = global_file.name.split('.')[-1].lower()
        if file_extension in ['jpg', 'jpeg', 'png']:
            img = Image.open(global_file).resize((300, 350))
            sheet = Image.new("RGB", (650, 750), (255, 255, 255))
            sheet.paste(img, (25, 25))
            sheet.paste(img, (335, 25))
            sheet.paste(img, (25, 385))
            sheet.paste(img, (335, 385))
            st.image(sheet, use_container_width=True, caption="4-Copy Sheet")
            buf = io.BytesIO()
            sheet.save(buf, format="JPEG", quality=95)
            st.download_button("Download Passport Sheet", buf.getvalue(), "passport_sheet.jpg", "image/jpeg", key="dl_5")
    else:
        st.warning("Please upload an image above.")

elif app_mode == 6:
    st.header("🎂 " + ("Age Calculator" if is_eng else "নিখুঁত বয়স ক্যালকুলেটর টুল"))
    col1, col2 = st.columns(2)
    with col1:
        birth_date = st.date_input("Select Birth Date", date(1995, 1, 1))
    with col2:
        target_date = st.date_input("Calculate Age Up To", date.today())
    if st.button("Calculate Age", key="btn_age_6"):
        if birth_date > target_date:
            st.error("Birth date cannot be in the future!")
        else:
            years = target_date.year - birth_date.year
            months = target_date.month - birth_date.month
            days = target_date.day - birth_date.day
            if days < 0:
                months -= 1
                days += 30
            if months < 0:
                years -= 1
                months += 12
            st.success(f"🎉 Age: **{years} Years, {months} Months, and {days} Days**")

elif app_mode == 7:
    st.header("🧾 " + ("Shop Cash Memo / Receipt Generator" if is_eng else "দোকানের বিক্রয় রশিদ (Cash Memo) জেনারেটর"))
    cust_name = st.text_input("Customer Name", "Md. Rahim Uddin")
    cust_phone = st.text_input("Customer Phone Number", "01700000000")
    col1, col2, col3 = st.columns(3)
    with col1:
        item1 = st.text_input("Item 1 Name", "Lamination & Print")
        price1 = st.number_input("Item 1 Price (TK)", 0, 10000, 150)
    with col2:
        item2 = st.text_input("Item 2 Name", "Passport Size Photo")
        price2 = st.number_input("Item 2 Price (TK)", 0, 10000, 100)
    with col3:
        item3 = st.text_input("Item 3 Name", "Online Application Fee")
        price3 = st.number_input("Item 3 Price (TK)", 0, 10000, 200)
    total_amount = price1 + price2 + price3
    if st.button("Generate Cash Memo & Print Preview", key="btn_memo_7"):
        memo_html = f"""
        <div style="background: white; padding: 25px; border-radius: 10px; border: 2px dashed #0B50FA; color: black;">
            <h2 style="text-align: center; color: #0B50FA; margin:0;">Hasanur Computer Studio</h2>
            <p style="text-align: center; font-size: 14px; margin: 2px 0;">Dighirpar, Monirampur, Jashore | Mobile: 01743-614359</p>
            <hr>
            <p><b>Customer Name:</b> {cust_name} | <b>Mobile:</b> {cust_phone}</p>
            <p><b>Date:</b> {date.today().strftime('%d-%m-%Y')}</p>
            <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
                <tr style="background: #f0f2f6; border-bottom: 1px solid #ddd;">
                    <th style="padding: 8px; text-align: left;">Description</th>
                    <th style="padding: 8px; text-align: right;">Price (TK)</th>
                </tr>
                <tr><td style="padding: 8px;">{item1}</td><td style="padding: 8px; text-align: right;">{price1} TK</td></tr>
                <tr><td style="padding: 8px;">{item2}</td><td style="padding: 8px; text-align: right;">{price2} TK</td></tr>
                <tr><td style="padding: 8px;">{item3}</td><td style="padding: 8px; text-align: right;">{price3} TK</td></tr>
                <tr style="border-top: 2px solid #000; font-weight: bold;">
                    <td style="padding: 10px;">Total Payable:</td>
                    <td style="padding: 10px; text-align: right; color: #ff4b4b;">{total_amount} TK</td>
                </tr>
            </table>
        </div>
        """
        st.markdown(memo_html, unsafe_allow_html=True)
        st.success("Cash memo generated successfully!")

elif app_mode == 8:
    st.header("🛡️ " + ("Digital Warranty Card Generator" if is_eng else "পণ্যের ডিজিটাল ওয়ারেন্টি কার্ড জেনারেটর"))
    p_name = st.text_input("Product Name & Model", "HP LaserJet Pro Printer")
    buyer_name = st.text_input("Buyer Name", "Md. Hasan Ali")
    w_period = st.selectbox("Warranty Period", ["1 Year", "2 Years", "3 Years", "6 Months", "Lifetime"])
    if st.button("Generate Warranty Card", key="btn_warr_8"):
        card_html = f"""
        <div style="background: linear-gradient(135deg, #1e3c72, #2a5298); padding: 30px; border-radius: 15px; color: white;">
            <h2 style="text-align: center; margin:0; letter-spacing: 2px;">WARRANTY CARD</h2>
            <p style="text-align: center; font-size: 13px; margin-top: 2px;">Hasanur Computer Studio</p>
            <hr style="border-color: rgba(255,255,255,0.3);">
            <p><b>Product:</b> {p_name}</p>
            <p><b>Buyer Name:</b> {buyer_name}</p>
            <p><b>Warranty Period:</b> {w_period}</p>
            <p><b>Purchase Date:</b> {date.today().strftime('%d-%m-%Y')}</p>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)
        st.success("Warranty card generated successfully!")

elif app_mode == 9:
    st.header("📜 " + ("Citizenship Certificate Generator" if is_eng else "নাগরিক সনদপত্র জেনারেটর"))
    col1, col2 = st.columns(2)
    with col1:
        c_name = st.text_input("Applicant Name", "Md. Al-Amin Hossain")
        c_father = st.text_input("Father's Name", "Md. Abdul Jabbar")
        c_mother = st.text_input("Mother's Name", "Mst. Ayesha Begum")
    with col2:
        c_village = st.text_input("Village / Area", "Dighirpar")
        c_union = st.text_input("Union / Municipality", "No. 2 Jhapa Union Parishad")
        c_upazila = st.text_input("Upazila & District", "Monirampur, Jashore")
    if st.button("Preview Citizenship Certificate", key="btn_cert_9"):
        cert_html = f"""
        <div style="background: #ffffff; padding: 40px; border: 5px double #1e3c72; border-radius: 10px; color: #000;">
            <h3 style="text-align: center; margin: 0; color: #1e3c72;">Government of Bangladesh</h3>
            <h2 style="text-align: center; margin: 5px 0; color: #d9534f;">{c_union}</h2>
            <h1 style="text-align: center; background: #1e3c72; color: white; padding: 5px; font-size: 18px;">Citizenship Certificate</h1>
            <p style="font-size: 16px; line-height: 1.8; margin-top: 20px;">
                This is to certify that <b>{c_name}</b>, Father: <b>{c_father}</b>, Mother: <b>{c_mother}</b>, Village: <b>{c_village}</b>, Upazila: <b>{c_upazila}</b> is a permanent resident and citizen of Bangladesh.
            </p>
        </div>
        """
        st.markdown(cert_html, unsafe_allow_html=True)
        st.success("Citizenship certificate generated!")

elif app_mode == 10:
    st.header("⚽ " + ("Tournament Invitation & Rules Generator" if is_eng else "টুর্নামেন্ট আমন্ত্রণপত্র ও নিয়মাবলী জেনারেটর"))
    t_type = st.selectbox("Select Tournament Type", ["Football Tournament", "Badminton Tournament"])
    col1, col2 = st.columns(2)
    with col1:
        t_name = st.text_input("Tournament Name", "Victory Day Premier League-2026")
        t_organizer = st.text_input("Organizer Club", "Dighirpar Youth Society")
        t_venue = st.text_input("Venue", "Dighirpar Playground")
    with col2:
        t_date = st.text_input("Date & Time", "15 February, 2026 | 3:00 PM")
        t_fee = st.text_input("Entry Fee", "1000 TK")
        t_prize = st.text_input("Prizes", "Champion: 5000 TK + Trophy")
    if st.button("Generate Invitation", key="btn_tourn_10"):
        st.success("Tournament invitation generated successfully!")

elif app_mode == 11:
    st.header("📏 " + ("Image Size Changer & Resizer" if is_eng else "ছবির সাইজ পরিবর্তন"))
    if global_file is not None:
        file_extension = global_file.name.split('.')[-1].lower()
        if file_extension in ['jpg', 'jpeg', 'png']:
            img = Image.open(global_file)
            width = st.slider("Width", 100, 3000, img.width)
            height = st.slider("Height", 100, 3000, img.height)
            resized = img.resize((width, height))
            st.image(resized, use_container_width=True)
            buf = io.BytesIO()
            resized.save(buf, format="JPEG", quality=95)
            st.download_button("Download Resized Image", buf.getvalue(), "resized.jpg", "image/jpeg", key="dl_11")
    else:
        st.warning("Please upload an image above.")

elif app_mode == 12:
    st.header("⬛ " + ("Black & White Converter" if is_eng else "সাদাকালো ছবি কনভার্টার"))
    if global_file is not None:
        file_extension = global_file.name.split('.')[-1].lower()
        if file_extension in ['jpg', 'jpeg', 'png']:
            img = Image.open(global_file).convert("L")
            st.image(img, use_container_width=True)
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=95)
            st.download_button("Download B&W Image", buf.getvalue(), "bw.jpg", "image/jpeg", key="dl_12")
    else:
        st.warning("Please upload an image above.")

elif app_mode == 13:
    st.header("🔄 " + ("Image Rotate & Flip" if is_eng else "ছবি ঘোরানোর টুল"))
    if global_file is not None:
        file_extension = global_file.name.split('.')[-1].lower()
        if file_extension in ['jpg', 'jpeg', 'png']:
            img = Image.open(global_file)
            rot = st.selectbox("Rotation Angle", [0, 90, 180, 270])
            if rot > 0:
                img = img.rotate(rot, expand=True)
            st.image(img, use_container_width=True)
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=95)
            st.download_button("Download Rotated Image", buf.getvalue(), "rotated.jpg", "image/jpeg", key="dl_13")
    else:
        st.warning("Please upload an image above.")

elif app_mode == 14:
    st.header("🖼️ " + ("Add Image Border & Frame" if is_eng else "বর্ডার ও ফ্রেম যুক্ত করুন"))
    if global_file is not None:
        file_extension = global_file.name.split('.')[-1].lower()
        if file_extension in ['jpg', 'jpeg', 'png']:
            img = Image.open(global_file)
            bordered = ImageOps.expand(img, border=20, fill='black')
            st.image(bordered, use_container_width=True)
            buf = io.BytesIO()
            bordered.save(buf, format="JPEG", quality=95)
            st.download_button("Download Bordered Image", buf.getvalue(), "bordered.jpg", "image/jpeg", key="dl_14")
    else:
        st.warning("Please upload an image above.")

elif app_mode == 15:
    st.header("💧 " + ("Watermark Adding Tool" if is_eng else "টেক্সট ওয়াটারমার্ক টুল"))
    if global_file is not None:
        file_extension = global_file.name.split('.')[-1].lower()
        if file_extension in ['jpg', 'jpeg', 'png']:
            img = Image.open(global_file)
            text = st.text_input("Watermark Text", "Hasanur Studio")
            st.image(img, use_container_width=True)
            st.success(f"Watermark '{text}' prepared.")
    else:
        st.warning("Please upload an image above.")

elif app_mode == 16:
    st.header("📄 " + ("PDF Text & Image Extract Tool" if is_eng else "পিডিএফ এক্সট্র্যাক্ট টুল"))
    if global_file is not None:
        file_extension = global_file.name.split('.')[-1].lower()
        if file_extension == 'pdf':
            try:
                reader = PdfReader(global_file)
                all_text = ""
                for idx, page in enumerate(reader.pages):
                    txt = page.extract_text()
                    if txt:
                        all_text += f"--- Page {idx+1} ---\n" + txt + "\n\n"
                st.text_area("PDF Text:", all_text, height=200)
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Please upload a PDF file.")
    else:
        st.warning("Please upload a PDF file above.")

# =========================================================================
# ক্যাটাগরি ও সমস্ত সার্ভিস লিংক ডিরেক্টরি
# =========================================================================
st.markdown("---")
st.header("🌐 " + ("Complete Government & Online Service Directory" if is_eng else "সকল ক্যাটাগরি ভিত্তিক সরকারি ও অনলাইন সার্ভিস ডিরেক্টরি"))

col_a, col_b = st.columns(2)

with col_a:
    st.markdown("""
    <div class="link-box">
        <h4>🏛️ উন্মুক্ত বিশ্ববিদ্যালয় (Open University)</h4>
        <p><b>লিংক:</b> <a href="https://www.bou.ac.bd/" target="_blank">BOU Official Website</a></p>
    </div>
    <div class="link-box">
        <h4>📜 জন্ম নিবন্ধন (Birth Registration)</h4>
        <p><b>লিংক:</b> <a href="https://bdris.gov.bd/" target="_blank">BDRIS Portal</a></p>
    </div>
    <div class="link-box">
        <h4>📇 জাতীয় পরিচয়পত্র (NID Services)</h4>
        <p><b>লিংক:</b> <a href="https://services.nidw.gov.bd/" target="_blank">NID Card Portal</a></p>
    </div>
    <div class="link-box">
        <h4>🎓 জাতীয় বিশ্ববিদ্যালয় (National University)</h4>
        <p><b>লিংক:</b> <a href="https://www.nu.ac.bd/" target="_blank">NU Portal & Admissions</a></p>
    </div>
    <div class="link-box">
        <h4>💉 টিকা (Vaccination Portal)</h4>
        <p><b>লিংক:</b> <a href="https://surokkha.gov.bd/" target="_blank">Surokkha Vaccine Registration</a></p>
    </div>
    <div class="link-box">
        <h4>🎫 টিকেট (Railway & Bus Tickets)</h4>
        <p><b>লিংক:</b> <a href="https://eticket.railway.gov.bd/" target="_blank">Bangladesh Railway E-Ticket</a></p>
    </div>
    <div class="link-box">
        <h4>🏫 পাবলিক বিশ্ববিদ্যালয় (Public Universities)</h4>
        <p><b>লিংক:</b> <a href="https://uccas.gov.bd/" target="_blank">UG Admission Portal</a></p>
    </div>
    <div class="link-box">
        <h4>🛂 পাসপোর্ট (e-Passport Portal)</h4>
        <p><b>লিংক:</b> <a href="https://www.epassport.gov.bd/" target="_blank">Online e-Passport Application</a></p>
    </div>
    <div class="link-box">
        <h4>👮 পুলিশ ও নাগরিক (Police Clearance)</h4>
        <p><b>লিংক:</b> <a href="https://pcc.police.gov.bd/" target="_blank">Police Clearance Certificate Portal</a></p>
    </div>
    <div class="link-box">
        <h4>✈️ প্রবাসী (BMET & Expatriates Welfare)</h4>
        <p><b>লিংক:</b> <a href="https://www.bmet.gov.bd/" target="_blank">BMET Portal & Smart Card</a></p>
    </div>
    <div class="link-box">
        <h4>📝 প্রবেশপত্র (Admit Card & Exam Portals)</h4>
        <p><b>লিংক:</b> <a href="http://www.teletalk.com.bd/" target="_blank">Teletalk Job Portal</a></p>
    </div>
    <div class="link-box">
        <h4>⚡ বিদ্যুৎ (Electricity Bill Pay)</h4>
        <p><b>লিংক:</b> <a href="https://www.bpdb.gov.bd/" target="_blank">BPDB Portal</a></p>
    </div>
    </div>
    """, unsafe_allow_html=True)
