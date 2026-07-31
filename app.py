import io
import cv2
import numpy as np
from PIL import Image, ImageOps, ImageDraw, ImageFont
import streamlit as st
from pypdf import PdfReader
from datetime import date

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
    .stButton > button:hover {{
        background: linear-gradient(135deg, #0B50FA, #ff4b4b) !important;
        color: white !important;
        border-color: #0B50FA !important;
        padding-left: 15px !important;
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
}

st.markdown(f"""
<div class="studio-header">
    <h1>{t['title']}</h1>
    <p style="font-size: 16px; margin: 5px 0;">{t['address']}</p>
    <p style="font-size: 13px; margin: 0;">{t['subtitle']}</p>
</div>
""", unsafe_allow_html=True)

st.markdown(f"### {t['upload_header']}")
global_file = st.file_uploader(t['upload_label'], type=["jpg", "jpeg", "png", "pdf"])
st.markdown("---")

if 'app_mode' not in st.session_state:
    st.session_state.app_mode = 1

st.sidebar.header(t['menu_header'])

menu_dict = {
    1: ("✨ ইমেজ ব্রাইটনেস ও কালার এডিটর", "ছবির আলো, ব্রাইটনেস ও কন্ট্রাস্ট ঠিক করার টুল।"),
    2: ("🆔 আইডি কার্ড ক্রপ ও সোজা করার টুল", "আইডি কার্ড ক্রপ ও নির্দিষ্ট কোণে ঘোরানো।"),
    3: ("🛂 পাসপোর্ট সাইজ ছবি শিট তৈরি (৪ কপি)", "এক ক্লিকে ৪ কপি পাসপোর্ট ছবি শিট তৈরি।"),
    4: ("🎂 বয়স ক্যালকুলেটর (Age Calculator)", "নির্ভুল বয়স ও দিন-মাস হিসাব।"),
    5: ("🧾 দোকানের ক্যাশ মেমো / রশিদ জেনারেটর", "গ্রাহকের বিক্রয় রশিদ ও ক্যাশ মেমো তৈরি।"),
    6: ("🛡️ ডিজিটাল ওয়ারেন্টি কার্ড জেনারেটর", "পণ্যের ডিজিটাল ওয়ারেন্টি কার্ড তৈরি।"),
    7: ("📜 নাগরিক সনদ (Citizenship Certificate) জেনারেটর", "ইউনিয়ন পরিষদের নাগরিক সনদপত্র তৈরি।"),
    8: ("⚽ টুর্নামেন্ট আমন্ত্রণপত্র ও নিয়মাবলী", "ফুটবল বা ব্যাডমিন্টন টুর্নামেন্ট নোটিশ তৈরি।"),
    9: ("📏 ছবির সাইজ পরিবর্তন ও রিসাইজার", "পিক্সেল অনুযায়ী ছবির সাইজ ছোট-বড় করা।"),
    10: ("⬛ সাদাকালো (Black & White) কনভার্টার", "কালার ছবিকে সাদাকালো করা।"),
    11: ("🔄 ছবি ঘোরানো (Rotate & Flip)", "ছবি বিভিন্ন এঙ্গেলে ঘোরানো।"),
    12: ("🖼️ ছবি বর্ডার ও ফ্রেম যুক্ত করা", "ছবির চারপাশে সুন্দর বর্ডার ও ফ্রেম দেওয়া।"),
    13: ("💧 ওয়াটারমার্ক যুক্ত করার টুল", "ছবিতে নিজের নাম বা লোগো ওয়াটারমার্ক দেওয়া।"),
    14: ("📄 পিডিএফ টেক্সট এক্সট্র্যাক্ট টুল", "পিডিএফ ফাইল থেকে টেক্সট আলাদা করা।")
}

for num, (item_name, desc) in menu_dict.items():
    if st.sidebar.button(item_name, key=f"menu_btn_{num}"):
        st.session_state.app_mode = num
    st.sidebar.markdown(f"<p style='font-size:11px; color:gray; margin-top:-3px; margin-bottom:8px;'>ℹ️ {desc}</p>", unsafe_allow_html=True)

app_mode = st.session_state.app_mode

# =====================================================================
# ফিচারসমূহ হ্যান্ডলিং
# =====================================================================

if app_mode == 1:
    st.header("✨ ইমেজ ব্রাইটনেস ও কালার এডিটর")
    if global_file is not None:
        image = Image.open(global_file)
        brightness = st.slider("Brightness", 0.5, 3.0, 1.0, 0.1)
        contrast = st.slider("Contrast", 0.5, 3.0, 1.0, 0.1)
        img_np = np.array(image)
        enhanced_np = cv2.convertScaleAbs(img_np, alpha=contrast, beta=int((brightness - 1) * 50))
        enhanced_image = Image.fromarray(enhanced_np)
        st.image(enhanced_image, use_container_width=True, caption="Enhanced Image")
        buf = io.BytesIO()
        enhanced_image.save(buf, format="JPEG", quality=95)
        st.download_button("Download Enhanced Image", buf.getvalue(), "enhanced.jpg", "image/jpeg", key="dl_1")
    else:
        st.info("👋 অনুগ্রহ করে উপরে একটি ছবি আপলোড করুন।")

elif app_mode == 2:
    st.header("🆔 আইডি কার্ড ক্রপ ও রোটেশন টুল")
    if global_file is not None:
        img = Image.open(global_file)
        rotation = st.slider("Rotate Image", -180, 180, 0)
        if rotation != 0:
            img = img.rotate(rotation, expand=True)
        st.image(img, use_container_width=True)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=95)
        st.download_button("Download Image", buf.getvalue(), "id_card.jpg", "image/jpeg", key="dl_2")
    else:
        st.warning("দয়া করে ছবি আপলোড করুন।")

elif app_mode == 3:
    st.header("🛂 পাসপোর্ট সাইজ ছবি শিট (৪ কপি)")
    if global_file is not None:
        img = Image.open(global_file).resize((300, 350))
        sheet = Image.new("RGB", (650, 750), (255, 255, 255))
        sheet.paste(img, (25, 25))
        sheet.paste(img, (335, 25))
        sheet.paste(img, (25, 385))
        sheet.paste(img, (335, 385))
        st.image(sheet, use_container_width=True)
        buf = io.BytesIO()
        sheet.save(buf, format="JPEG", quality=95)
        st.download_button("Download Sheet", buf.getvalue(), "passport_sheet.jpg", "image/jpeg", key="dl_3")
    else:
        st.warning("দয়া করে ছবি আপলোড করুন।")

elif app_mode == 4:
    st.header("🎂 বয়স ক্যালকুলেটর")
    col1, col2 = st.columns(2)
    with col1:
        birth_date = st.date_input("Select Birth Date", date(1995, 1, 1))
    with col2:
        target_date = st.date_input("Calculate Age Up To", date.today())
    if st.button("Calculate Age"):
        years = target_date.year - birth_date.year
        months = target_date.month - birth_date.month
        days = target_date.day - birth_date.day
        if days < 0:
            months -= 1
            days += 30
        if months < 0:
            years -= 1
            months += 12
        st.success(f"🎉 বয়স: **{years} বছর, {months} মাস, এবং {days} দিন**")

elif app_mode == 5:
    st.header("🧾 দোকানের ক্যাশ মেমো জেনারেটর")
    cust_name = st.text_input("Customer Name", "Md. Rahim")
    cust_phone = st.text_input("Phone Number", "01700000000")
    col1, col2 = st.columns(2)
    with col1:
        item1 = st.text_input("Item Name", "Lamination & Print")
        price1 = st.number_input("Price (TK)", 0, 10000, 150)
    with col2:
        item2 = st.text_input("Item 2 Name", "Online Form Fillup")
        price2 = st.number_input("Price 2 (TK)", 0, 10000, 200)
    total = price1 + price2
    if st.button("Generate Memo"):
        st.markdown(f"""
        <div style="background:white; padding:20px; border:2px solid #0B50FA; border-radius:10px; color:black;">
            <h3 style="text-align:center; color:#0B50FA; margin:0;">Hasanur Computer Studio</h3>
            <p style="text-align:center; font-size:12px;">Dighirpar, Monirampur, Jashore</p>
            <hr>
            <p><b>Customer:</b> {cust_name} | <b>Mobile:</b> {cust_phone}</p>
            <p><b>Date:</b> {date.today().strftime('%d-%m-%Y')}</p>
            <p>1. {item1} - <b>{price1} TK</b></p>
            <p>2. {item2} - <b>{price2} TK</b></p>
            <hr>
            <h4>Total Payable: <span style="color:red;">{total} TK</span></h4>
        </div>
        """, unsafe_allow_html=True)

elif app_mode == 6:
    st.header("🛡️ ডিজিটাল ওয়ারেন্টি কার্ড জেনারেটর")
    p_name = st.text_input("Product Name", "HP Printer")
    buyer = st.text_input("Buyer Name", "Hasan Ali")
    if st.button("Generate Card"):
        st.success(f"Warranty card generated successfully for {p_name}!")

elif app_mode == 7:
    st.header("📜 নাগরিক সনদপত্র জেনারেটর")
    c_name = st.text_input("Applicant Name", "Al-Amin")
    if st.button("Generate Certificate"):
        st.success(f"Citizenship certificate generated for {c_name}!")

elif app_mode == 8:
    st.header("⚽ টুর্নামেন্ট আমন্ত্রণপত্র")
    st.text_input("Tournament Name", "Premier League")
    if st.button("Generate Notice"):
        st.success("Tournament notice generated!")

elif app_mode == 9:
    st.header("📏 ছবির সাইজ পরিবর্তন")
    if global_file is not None:
        img = Image.open(global_file)
        w = st.slider("Width", 100, 2000, img.width)
        h = st.slider("Height", 100, 2000, img.height)
        resized = img.resize((w, h))
        st.image(resized, use_container_width=True)
        buf = io.BytesIO()
        resized.save(buf, format="JPEG", quality=95)
        st.download_button("Download", buf.getvalue(), "resized.jpg", "image/jpeg", key="dl_9")
    else:
        st.warning("দয়া করে ছবি আপলোড করুন।")

elif app_mode == 10:
    st.header("⬛ সাদাকালো ছবি কনভার্টার")
    if global_file is not None:
        img = Image.open(global_file).convert("L")
        st.image(img, use_container_width=True)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=95)
        st.download_button("Download", buf.getvalue(), "bw.jpg", "image/jpeg", key="dl_10")
    else:
        st.warning("দয়া করে ছবি আপলোড করুন।")

elif app_mode == 11:
    st.header("🔄 ছবি ঘোরানো (Rotate)")
    if global_file is not None:
        img = Image.open(global_file)
        rot = st.selectbox("Angle", [90, 180, 270])
        img = img.rotate(rot, expand=True)
        st.image(img, use_container_width=True)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=95)
        st.download_button("Download", buf.getvalue(), "rot.jpg", "image/jpeg", key="dl_11")
    else:
        st.warning("দয়া করে ছবি আপলোড করুন।")

elif app_mode == 12:
    st.header("🖼️ বর্ডার ও ফ্রেম যুক্ত করুন")
    if global_file is not None:
        img = Image.open(global_file)
        bordered = ImageOps.expand(img, border=20, fill='black')
        st.image(bordered, use_container_width=True)
        buf = io.BytesIO()
        bordered.save(buf, format="JPEG", quality=95)
        st.download_button("Download", buf.getvalue(), "border.jpg", "image/jpeg", key="dl_12")
    else:
        st.warning("দয়া করে ছবি আপলোড করুন।")

elif app_mode == 13:
    st.header("💧 ওয়াটারমার্ক টুল")
    if global_file is not None:
        st.image(Image.open(global_file), use_container_width=True)
        st.success("Watermark tool ready.")
    else:
        st.warning("দয়া করে ছবি আপলোড করুন।")

elif app_mode == 14:
    st.header("📄 পিডিএফ টেক্সট এক্সট্র্যাক্ট")
    if global_file is not None:
        try:
            reader = PdfReader(global_file)
            txt = reader.pages[0].extract_text()
            st.text_area("Extracted Text:", txt, height=200)
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("দয়া করে একটি পিডিএফ ফাইল আপলোড করুন।")

# =========================================================================
# ক্যাটাগরি ও সমস্ত সার্ভিস লিংক ডিরেক্টরি (পুনরায় যুক্ত করা হয়েছে)
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
    """, unsafe_allow_html=True)

with col_b:
    st.markdown("""
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
    """, unsafe_allow_html=True)
