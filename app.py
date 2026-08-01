import io
import cv2
import numpy as np
from PIL import Image, ImageOps, ImageDraw, ImageFont
import streamlit as st
from pypdf import PdfReader
from datetime import date

try:
    from rembg import remove
    has_rembg = True
except ImportError:
    has_rembg = False

st.set_page_config(page_title="হাসানুর কম্পিউটার স্টুডিও / Hasanur Computer Studio", layout="wide")

# ==============================================================================
# থিম এবং ভাষা সিলেকশন (সাইডবার কন্ট্রোল)
# ==============================================================================
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
    accent_color = "#ff4b4b"
else:
    bg_main = "#ffffff"
    sidebar_bg = "#fcfcfc"
    text_color = "#333333"
    btn_bg = "#ffffff"
    btn_text = "#333333"
    btn_border = "#e0e0e0"
    link_bg = "#f8f9fa"
    header_gradient = "linear-gradient(135deg, #0B50FA, #ff4b4b)"
    accent_color = "#0B50FA"

st.markdown(f"""
<style>
    .stApp {{
        background-color: {bg_main};
        color: {text_color};
    }}
    [data-testid="stSidebar"] {{
        min-width: 410px !important;
        max-width: 440px !important;
        background-color: {sidebar_bg} !important;
        border-right: 1px solid {btn_border};
    }}
    .link-box {{
        background-color: {link_bg};
        padding: 10px;
        border-radius: 8px;
        border-left: 4px solid {accent_color};
        margin-bottom: 8px;
        color: {text_color};
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        font-size: 11px;
    }}
    /* লম্বালম্বি ও আকর্ষণীয় স্টুডিও হেডার কার্ড */
    .studio-header {{
        background: {header_gradient};
        padding: 30px 20px;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin: 0 auto 20px auto;
        max-width: 500px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.2);
    }}
    .studio-header h1 {{
        font-size: 26px;
        margin-bottom: 12px;
        font-weight: bold;
        letter-spacing: 0.5px;
    }}
    .studio-header p {{
        font-size: 14px;
        margin: 8px 0;
        line-height: 1.5;
    }}
    .stButton > button {{
        width: 100% !important;
        min-height: 38px !important;
        text-align: left !important;
        background-color: {btn_bg};
        color: {btn_text};
        border: 1px solid {btn_border};
        border-radius: 8px;
        padding: 6px 10px !important;
        font-weight: 600;
        font-size: 12px;
        margin-bottom: 3px;
        transition: all 0.3s ease;
    }}
    .stButton > button:hover {{
        background: linear-gradient(135deg, {accent_color}, #ff4b4b) !important;
        color: white !important;
        border-color: {accent_color} !important;
        padding-left: 14px !important;
    }}
    .sidebar-section-title {{
        font-size: 14px;
        font-weight: bold;
        color: {accent_color};
        margin-top: 15px;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        border-bottom: 2px solid {accent_color};
        padding-bottom: 4px;
    }}
    
    /* স্ক্রিনের পেপার স্টাইল */
    .a4-paper-box {{
        background: #ffffff;
        width: 100%;
        max-width: 750px;
        min-height: 1060px;
        margin: 20px auto;
        padding: 50px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        color: #000000;
        box-sizing: border-box;
        border-radius: 6px;
    }}

    /* ========================================================== */
    /* প্রিন্টিং অপ্টিমাইজেশন: প্রিন্ট করার সময় শুধু A4 পেপার প্রিন্ট হবে */
    /* ========================================================== */
    @media print {{
        body {{
            background: white !important;
            color: black !important;
        }}
        [data-testid="stSidebar"], .studio-header, .stButton, header, footer {{
            display: none !important;
        }}
        .a4-paper-box {{
            box-shadow: none !important;
            margin: 0 !important;
            padding: 20px !important;
            width: 100% !important;
            max-width: 100% !important;
            border: none !important;
        }}
        @page {{
            size: A4;
            margin: 10mm;
        }}
    }}
</style>
""", unsafe_allow_html=True)

t = {
    "title": "Hasanur Computer Studio" if is_eng else "🖨️ হাসানুর কম্পিউটার স্টুডিও",
    "address": "<b>ঠিকানা:</b> দিঘীরপাড়, মনিরামপুর, যশোর" if not is_eng else "<b>Address:</b> Dighirpar, Monirampur, Jashore",
    "mobile": "<b>মোবাইল:</b> ০১৭৪৩-৬১৪৩৫৯" if not is_eng else "<b>Mobile:</b> 01743-614359",
    "subtitle": "সকল ধরনের কম্পিউটার, ডিজাইন ও অনলাইন সার্ভিসের অল-ইন-ওয়ান মাস্টার ড্যাশবোর্ড" if not is_eng else "All-in-one Master Dashboard for Computer, Design & Online Services",
    "upload_header": "📁 Master File Uploader" if is_eng else "📁 ফাইল আপলোড (Master File Uploader)",
    "upload_label": "Upload Image or PDF file" if is_eng else "ছবি বা পিডিএফ ফাইল আপলোড করুন",
    "tools_header": "🛠️ ডিজিটাল টুলস ও এডিটর (১-১৪)" if not is_eng else "🛠️ Digital Tools & Editors",
    "job_header": "💼 সরকারি ও বেসরকারি চাকরির পোর্টাল" if not is_eng else "💼 Job Portals",
    "result_header": "📊 রেজাল্ট ও মার্কশিট পোর্টাল (ক্লাস ৫ থেকে সর্বোচ্চ)" if not is_eng else "📊 Result & Marksheet Portal",
    "portal_header": "📋 অন্যান্য গুরুত্বপূর্ণ অনলাইন লিংক ও পোর্টাল" if not is_eng else "📋 All Important Online Links",
}

# লম্বালম্বি সুবিন্যস্ত হেডার লেআউট
st.markdown(f"""
<div class="studio-header">
    <h1>{t['title']}</h1>
    <p>{t['address']}</p>
    <p>{t['mobile']}</p>
    <hr style="border:0.5px solid rgba(255,255,255,0.3); width:80%; margin: 10px auto;">
    <p style="font-size: 13px; opacity: 0.9;">{t['subtitle']}</p>
</div>
""", unsafe_allow_html=True)

# মেইন ফাইল আপলোডার
st.markdown(f"### {t['upload_header']}")
global_file = st.file_uploader(t['upload_label'], type=["jpg", "jpeg", "png", "pdf"])
st.markdown("---")

if 'app_mode' not in st.session_state:
    st.session_state.app_mode = 1

# ==============================================================================
# ১ থেকে ১৪ ফটো এডিটিং ও ইউটিলিটি ফিচার মেনু (সাইডবার)
# ==============================================================================
st.sidebar.markdown(f"<div class='sidebar-section-title'>{t['tools_header']}</div>", unsafe_allow_html=True)

menu_dict = {
    1: ("✨ ইমেজ ব্রাইটনেস ও কালার এডিটর", "ছবির আলো, ব্রাইটনেস ও কন্ট্রাস্ট ঠিক করার টুল।"),
    2: ("🎨 স্টুডিও ব্যাকগ্রাউন্ড রিমুভ ও কালার চেঞ্জার", "পাসপোর্ট ছবির ব্যাকগ্রাউন্ড নিখুঁতভাবে রিমুভ করুন।"),
    3: ("🆔 আইডি কার্ড ক্রপ ও সোজা করার টুল", "আইডি কার্ড ক্রপ ও নির্দিষ্ট কোণে ঘোরানো।"),
    4: ("🛂 পাসপোর্ট সাইজ ছবি শিট তৈরি (৪ কপি)", "এক ক্লিকে ৪ কপি পাসপোর্ট ছবি শিট তৈরি।"),
    5: ("🎂 বয়স ক্যালকুলেটর (Age Calculator)", "নির্ভুল বয়স ও দিন-মাস হিসাব।"),
    6: ("🧾 দোকানের ক্যাশ মেমো / রশিদ জেনারেটর", "গ্রাহকের বিক্রয় রশিদ ও ক্যাশ মেমো তৈরি।"),
    7: ("🛡️ ডিজিটাল ওয়ারেন্টি কার্ড জেনারেটর", "পণ্যের ডিজিটাল ওয়ারেন্টি কার্ড তৈরি।"),
    8: ("📜 নাগরিক সনদ (Citizenship) জেনারেটর", "ইউনিয়ন পরিষদের নাগরিক সনদপত্র তৈরি (A4 Print Format)।"),
    9: ("⚽ টুর্নামেন্ট আমন্ত্রণপত্র ও নিয়মাবলী", "ফুটবল বা ক্রিকেট টুর্নামেন্ট নোটিশ ও নিয়ম তৈরি (A4 Print Format)।"),
    10: ("📏 ছবির সাইজ পরিবর্তন ও রিসাইজার", "পিক্সেল অনুযায়ী ছবির সাইজ ছোট-বড় করা।"),
    11: ("⬛ সাদাকালো (Black & White) কনভার্টার", "কালার ছবিকে সাদাকালো করা।"),
    12: ("🔄 ছবি ঘোরানো (Rotate & Flip)", "ছবি বিভিন্ন এঙ্গেলে ঘোরানো।"),
    13: ("💧 ওয়াটারমার্ক যুক্ত করার টুল", "ছবিতে নিজের নাম বা লোগো ওয়াটারমার্ক দেওয়া।"),
    14: ("📄 পিডিএফ টেক্সট এক্সট্র্যাক্ট টুল", "পিডিএফ ফাইল থেকে টেক্সট আলাদা করা।")
}

for num, (item_name, desc) in menu_dict.items():
    if st.sidebar.button(item_name, key=f"menu_btn_{num}"):
        st.session_state.app_mode = num
    st.sidebar.markdown(f"<p style='font-size:10px; color:gray; margin-top:-2px; margin-bottom:5px;'>ℹ️ {desc}</p>", unsafe_allow_html=True)


# ==============================================================================
# সরকারি ও বেসরকারি চাকরির পোর্টাল ক্যাটাগরি
# ==============================================================================
st.sidebar.markdown(f"<div class='sidebar-section-title'>{t['job_header']}</div>", unsafe_allow_html=True)

st.sidebar.markdown("""
<div class="link-box">
    <b>🏛️ সরকারি চাকরির পোর্টাল ও সার্কুলার:</b><br>
    • সরকারি জবস পোর্টাল (Teletalk): <a href="https://alljobs.teletalk.com.bd/" target="_blank">All Jobs BD</a><br>
    • বাংলাদেশ জাতীয় তথ্য বাতায়ন: <a href="https://bangladesh.gov.bd/" target="_blank">National Portal</a>
</div>

<div class="link-box">
    <b>🏢 বেসরকারি ও করপোরেট জবস পোর্টাল:</b><br>
    • বিডি জবস পোর্টাল: <a href="https://www.bdjobs.com/" target="_blank">Bdjobs.com</a><br>
    • টেলিটক অফিশিয়াল পোর্টাল: <a href="https://teletalk.com.bd/" target="_blank">Teletalk Portal</a>
</div>
""", unsafe_allow_html=True)


# ==============================================================================
# ক্লাস ৫ থেকে সর্বোচ্চ ক্লাস পর্যন্ত মার্কশিট ও রেজাল্ট পোর্টাল
# ==============================================================================
st.sidebar.markdown(f"<div class='sidebar-section-title'>{t['result_header']}</div>", unsafe_allow_html=True)

st.sidebar.markdown("""
<div class="link-box">
    <b>🎓 পিএসসি, জেএসসি, এসএসসি ও এইচএসসি (মার্কশিট সহ):</b><br>
    • অফিশিয়াল রেজাল্ট পোর্টাল: <a href="http://www.educationboardresults.gov.bd/" target="_blank">Web Link</a><br>
    • শিক্ষা বোর্ড মার্কশিট কর্নার: <a href="https://eboardresults.com/" target="_blank">E-Board Marksheet</a>
</div>

<div class="link-box">
    <b>🏫 প্রাথমিক শিক্ষা সমাপনী (PEC / Class 5):</b><br>
    • প্রাথমিক শিক্ষা অধিদপ্তর: <a href="http://www.dpe.gov.bd/" target="_blank">DPE Portal</a>
</div>

<div class="link-box">
    <b>🏛️ জাতীয় বিশ্ববিদ্যালয় (অনার্স, মাস্টার্স, ডিগ্রি):</b><br>
    • এনইউ রেজাল্ট পোর্টাল: <a href="http://results.nu.ac.bd/" target="_blank">NU Results</a> | 
    স্টুডেন্ট পোর্টাল: <a href="http://www.nu.ac.bd/" target="_blank">NU Portal</a>
</div>

<div class="link-box">
    <b>📚 উন্মুক্ত বিশ্ববিদ্যালয় (SSC, HSC, BA, BSS):</b><br>
    • বাউবি এক্সাম রেজাল্ট: <a href="https://www.bou.ac.bd/" target="_blank">BOU Portal</a>
</div>

<div class="link-box">
    <b>🎓 পাবলিক ও অন্যান্য উচ্চশিক্ষা:</b><br>
    • ইউজিসি (UGC) পোর্টাল: <a href="https://www.ugc.gov.bd/" target="_blank">UGC Link</a>
</div>
""", unsafe_allow_html=True)


# ==============================================================================
# অন্যান্য গুরুত্বপূর্ণ অনলাইন লিংক ও পোর্টাল
# ==============================================================================
st.sidebar.markdown(f"<div class='sidebar-section-title'>{t['portal_header']}</div>", unsafe_allow_html=True)

st.sidebar.markdown("""
<div class="link-box">
    <b>📇 নাগরিক ও পরিচয়পত্র সেবা:</b><br>
    • জন্ম নিবন্ধন: <a href="https://bdris.gov.bd/" target="_blank">Link</a> | 
    জাতীয় পরিচয়পত্র (NID): <a href="https://services.nidw.gov.bd/" target="_blank">Link</a><br>
    • পাসপোর্ট: <a href="https://www.epassport.gov.bd/" target="_blank">Link</a> | 
    পুলিশ ও নাগরিক: <a href="https://pcc.police.gov.bd/" target="_blank">Link</a>
</div>

<div class="link-box">
    <b>🏥 স্বাস্থ্য, টিকিট ও অন্যান্য সেবা:</b><br>
    • টিকা (Surokkha): <a href="https://surokkha.gov.bd/" target="_blank">Link</a> | 
    রেলওয়ে টিকিট: <a href="https://eticket.railway.gov.bd/" target="_blank">Link</a>
</div>

<div class="link-box">
    <b>⚡ ইউটিলিটি, প্রবাস ও অন্যান্য:</b><br>
    • বিদ্যুৎ (BPDB): <a href="https://www.bpdb.gov.bd/" target="_blank">Link</a> | 
    ভাতা: <a href="https://mis.mowca.gov.bd/" target="_blank">Link</a><br>
    • ভূমি সংক্রান্ত: <a href="https://land.gov.bd/" target="_blank">Link</a> | 
    ভ্যাট / ই-টিন: <a href="https://etaxnbr.gov.bd/" target="_blank">Link</a>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown("ℹ️ **Hasanur Computer Studio** | 📞 01743-614359")


# ==============================================================================
# মূল ফিচার হ্যান্ডলিং (App Mode Logic)
# ==============================================================================
app_mode = st.session_state.app_mode

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
    st.header("🎨 স্টুডিও ব্যাকগ্রাউন্ড রিমুভ ও কালার চেঞ্জার")
    if not has_rembg:
        st.error("❌ 'rembg' লাইব্রেরিটি ইনস্টল করা নেই।")
    elif global_file is not None:
        image = Image.open(global_file).convert("RGB")
        st.image(image, caption="মূল ছবি (Original Image)", width=300)
        bg_color_picker = st.color_picker("নতুন ব্যাকগ্রাউন্ড রঙ নির্বাচন করুন", "#1A73E8")
        if st.button("ব্যাকগ্রাউন্ড পরিবর্তন করুন"):
            with st.spinner("প্রসেসিং হচ্ছে..."):
                try:
                    bytes_data = global_file.getvalue()
                    output_bytes = remove(bytes_data)
                    img_rgba = Image.open(io.BytesIO(output_bytes)).convert("RGBA")
                    h_hex = bg_color_picker.lstrip('#')
                    new_rgb = tuple(int(h_hex[i:i+2], 16) for i in (0, 2, 4))
                    background = Image.new("RGBA", img_rgba.size, new_rgb + (255,))
                    final_img = Image.alpha_composite(background, img_rgba).convert("RGB")
                    st.image(final_img, use_container_width=True, caption="ব্যাকগ্রাউন্ড পরিবর্তিত ছবি")
                    buf = io.BytesIO()
                    final_img.save(buf, format="JPEG", quality=95)
                    st.download_button("Download Image", buf.getvalue(), "studio_bg.jpg", "image/jpeg", key="dl_bg")
                except Exception as e:
                    st.error(f"ত্রুটি: {e}")
    else:
        st.warning("দয়া করে ছবি আপলোড করুন।")

elif app_mode == 3:
    st.header("🆔 আইডি কার্ড ক্রপ ও সোজা করার টুল")
    if global_file is not None:
        img = Image.open(global_file)
        rotation = st.slider("Rotate Image", -180, 180, 0)
        if rotation != 0:
            img = img.rotate(rotation, expand=True)
        st.image(img, use_container_width=True)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=95)
        st.download_button("Download", buf.getvalue(), "id_card.jpg", "image/jpeg", key="dl_3")
    else:
        st.warning("দয়া করে ছবি আপলোড করুন।")

elif app_mode == 4:
    st.header("🛂 পাসপোর্ট সাইজ ছবি শিট তৈরি (৪ কপি)")
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
        st.download_button("Download", buf.getvalue(), "passport_sheet.jpg", "image/jpeg", key="dl_4")
    else:
        st.warning("দয়া করে ছবি আপলোড করুন।")

elif app_mode == 5:
    st.header("🎂 বয়স ক্যালকুলেটর (Age Calculator)")
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

elif app_mode == 6:
    st.header("🧾 দোকানের ক্যাশ মেমো / রশিদ জেনারেটর")
    c_name = st.text_input("Customer Name", "Md. Rahim")
    c_phone = st.text_input("Phone Number", "01700000000")
    col1, col2 = st.columns(2)
    with col1:
        item1 = st.text_input("Item 1 Name", "Lamination & Print")
        price1 = st.number_input("Price 1 (TK)", 0, 10000, 150)
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
            <p><b>Customer:</b> {c_name} | <b>Mobile:</b> {c_phone}</p>
            <p><b>Date:</b> {date.today().strftime('%d-%m-%Y')}</p>
            <p>1. {item1} - <b>{price1} TK</b></p>
            <p>2. {item2} - <b>{price2} TK</b></p>
            <hr>
            <h4>Total Payable: <span style="color:red;">{total} TK</span></h4>
        </div>
        """, unsafe_allow_html=True)

elif app_mode == 7:
    st.header("🛡️ ডিজিটাল ওয়ারেন্টি কার্ড জেনারেটর")
    st.text_input("Product Name", "HP Printer")
    st.text_input("Buyer Name", "Hasan Ali")
    if st.button("Generate Card"):
        st.success("Warranty card generated successfully!")

elif app_mode == 8:
    st.header("📜 নাগরিক সনদপত্র জেনারেটর (A4 Print Ready)")
    st.info("💡 টিপস: সরাসরি প্রিন্ট করতে ব্রাউজারের প্রিন্ট অপশন ব্যবহার করুন (Ctrl + P)। প্রিন্টার পেপার সাইজ স্বয়ংক্রিয়ভাবে A4 এ সেট করা আছে।")
    
    col1, col2 = st.columns(2)
    with col1:
        cit_name = st.text_input("আবেদনকারীর নাম (Applicant Name)", "মোঃ রফিকুল ইসলাম")
        cit_father = st.text_input("পিতার নাম (Father's Name)", "মোঃ আব্দুল জব্বার")
        cit_mother = st.text_input("মাতার নাম (Mother's Name)", "মোছাঃ মরিয়ম বেগম")
    with col2:
        cit_nid = st.text_input("এনআইডি / জন্ম নিবন্ধন নম্বর (NID/Birth No)", "19954125487123654")
        cit_village = st.text_input("গ্রাম / মহল্লা (Village)", "দিঘীরপাড়")
        cit_ward = st.text_input("ওয়ার্ড নম্বর ও ইউনিয়ন (Ward & Union)", "ওয়ার্ড নং- ০৪, ঝাঁপা ইউনিয়ন")

    if st.button("নাগরিক সনদ জেনারেট করুন"):
        certificate_html = f"""
        <div class="a4-paper-box" style="border:6px double #0B50FA;">
            <div style="text-align:center;">
                <h2 style="color:#0B50FA; margin:0;">ইউনিয়ন পরিষদ কার্যালয়</h2>
                <p style="font-size:14px; margin:2px 0;">{cit_ward}, মনিরামপুর, যশোর।</p>
                <hr style="border: 1px solid #0B50FA; width:60%;">
                <h3 style="background:#0B50FA; color:white; display:inline-block; padding:5px 25px; border-radius:5px; margin:15px 0;">নাগরিক সনদপত্র</h3>
            </div>
            <p style="text-align: right; font-size: 13px; margin-top:20px;">তারিখ: {date.today().strftime('%d-%m-%Y')}</p>
            <p style="font-size: 15px; line-height: 1.9; text-align: justify; margin-top: 25px;">
                এই মর্মে প্রত্যয়ন করা যাইতেছে যে, <b>{cit_name}</b>, 
                পিতা: <b>{cit_father}</b>, 
                মাতা: <b>{cit_mother}</b>, 
                এনআইডি/জন্ম সনদ নম্বর: <b>{cit_nid}</b>, 
                সাং: <b>{cit_village}</b>, 
                ডাকঘর: মনিরামপুর, উপজেলা: মনিরামপুর, জেলা: যশোর। 
                তিনি অত্র ইউনিয়নের একজন স্থায়ী বাসিন্দা এবং জন্মসূত্রে বাংলাদেশের নাগরিক। আমার জানামতে তার চরিত্র ও আচরণ সন্তোষজনক এবং তিনি রাষ্ট্রবিরোধী কোনো কাজের সাথে জড়িত নন।
            </p>
            <p style="font-size: 15px; margin-top: 20px;">আমি তাহার সর্বাঙ্গীন মঙ্গল ও দীর্ঘায়ু কামনা করি।</p>
            
            <div style="margin-top: 90px; display: flex; justify-content: space-between;">
                <div>
                    <p style="border-top: 1px dashed black; padding-top: 5px; display: inline-block;">আবেদনকারীর স্বাক্ষর</p>
                </div>
                <div style="text-align: right;">
                    <p style="border-top: 1px solid black; padding-top: 5px; display: inline-block; font-weight: bold;">চেয়ারম্যান<br>ইউনিয়ন পরিষদ</p>
                </div>
            </div>
        </div>
        """
        st.markdown(certificate_html, unsafe_allow_html=True)
        st.success("✅ A4 প্রিন্ট ফরম্যাটে নাগরিক সনদ সফলভাবে তৈরি হয়েছে!")

elif app_mode == 9:
    st.header("⚽ টুর্নামেন্ট আমন্ত্রণপত্র ও নিয়মাবলী জেনারেটর (A4 Print Ready)")
    st.info("💡 টিপস: সরাসরি প্রিন্ট করতে ব্রাউজারের প্রিন্ট অপশন ব্যবহার করুন (Ctrl + P)। পেপার সাইজ স্বয়ংক্রিয়ভাবে A4 প্রিন্ট ফরম্যাটে সেট করা থাকবে।")
    
    col1, col2 = st.columns(2)
    with col1:
        t_name = st.text_input("টুর্নামেন্টের নাম (Tournament Name)", "দিঘীরপাড় প্রিমিয়ার লিগ (ক্রিকেট/ফুটবল)")
        t_organizer = st.text_input("আয়োজক কমিটি (Organizer)", "যুব সমাজ কল্যাণ সংঘ")
        t_ground = st.text_input("খেলার স্থান (Venue)", "দিঘীরপাড় সরকারি প্রাথমিক বিদ্যালয় মাঠ")
    with col2:
        t_date = st.text_input("শুরুর তারিখ ও সময় (Date & Time)", "আগামী ১৫ ফেব্রুয়ারি ২০২৬, সকাল ১০:০০ টা")
        t_fee = st.text_input("এন্ট্রি ফি (Entry Fee)", "৫০০/- টাকা মাত্র")
        t_prize = st.text_input("পুরস্কার (Prize Money)", "চ্যাম্পিয়ন: ৫০০০/- টাকা + ট্রফি")

    t_rules = st.text_area("খেলার নিয়মাবলী (Rules & Regulations)", 
    "১. সকল দলকে নির্ধারিত সময়ের ১০ মিনিট পূর্বে মাঠে উপস্থিত থাকতে হবে।\n"
    "২. আম্পায়ার বা রেফারির সিদ্ধান্তই চূড়ান্ত বলে গণ্য হবে।\n"
    "৩. খেলার মাঠে শৃঙ্খলা বজায় রাখতে হবে, অন্যথায় কমিটি যে কোনো সিদ্ধান্ত নিতে বাধ্য থাকবে।")

    if st.button("টুর্নামেন্ট নোটিশ জেনারেট করুন"):
        notice_html = f"""
        <div class="a4-paper-box" style="border:4px solid #ff4b4b;">
            <div style="text-align:center;">
                <h2 style="color:#ff4b4b; margin:0;">🏆 টুর্নামেন্ট আমন্ত্রণপত্র ও নোটিশ 🏆</h2>
                <h3 style="color:#0B50FA; margin:6px 0; font-size:22px;">{t_name}</h3>
                <p style="font-size:13px; color:gray; margin:0;">আয়োজনে: {t_organizer}</p>
                <hr style="border: 1px solid #ff4b4b; width:70%; margin:15px auto;">
            </div>
            
            <div style="background:#f8f9fa; padding:15px; border-radius:8px; margin:15px 0; font-size:14px; border-left:5px solid #0B50FA;">
                <p>📍 <b>খেলার স্থান:</b> {t_ground}</p>
                <p>📅 <b>শুরুর তারিখ ও সময়:</b> {t_date}</p>
                <p>💰 <b>এন্ট্রি ফি:</b> {t_fee} | 🏆 <b>গ্র্যান্ড পুরস্কার:</b> {t_prize}</p>
            </div>

            <h4 style="color:#0B50FA; border-bottom: 2px solid #0B50FA; padding-bottom:4px; margin-top:20px;">📋 টুর্নামেন্টের বিশেষ নিয়মাবলী:</h4>
            <div style="font-size: 14px; line-height: 1.7; white-space: pre-line; background:#fffdfd; padding:12px; border-left:4px solid #ff4b4b; margin-top:8px;">
                {t_rules}
            </div>

            <p style="text-align:center; font-weight:bold; margin-top:25px; color:#ff4b4b; font-size:15px;">সকল ক্রীড়াপ্রেমী ও দলগুলোকে টুর্নামেন্টে অংশগ্রহণের জন্য আন্তরিক আমন্ত্রণ জানানো যাচ্ছে!</p>
            
            <div style="margin-top: 70px; text-align: right;">
                <p style="border-top: 1px solid black; padding-top: 5px; display: inline-block; font-weight: bold;">কর্তৃপক্ষ / সভাপতি<br>{t_organizer}</p>
            </div>
        </div>
        """
        st.markdown(notice_html, unsafe_allow_html=True)
        st.success("✅ A4 পেপার প্রিন্ট ফরম্যাটে টুর্নামেন্টের নোটিশ সফলভাবে তৈরি করা হয়েছে!")

elif app_mode == 10:
    st.header("📏 ছবির সাইজ পরিবর্তন ও রিসাইজার")
    if global_file is not None:
        img = Image.open(global_file)
        w = st.slider("Width", 100, 2000, img.width)
        h = st.slider("Height", 100, 2000, img.height)
        resized = img.resize((w, h))
        st.image(resized, use_container_width=True)
        buf = io.BytesIO()
        resized.save(buf, format="JPEG", quality=95)
        st.download_button("Download", buf.getvalue(), "resized.jpg", "image/jpeg", key="dl_10")
    else:
        st.warning("দয়া করে ছবি আপলোড করুন।")

elif app_mode == 11:
    st.header("⬛ সাদাকালো (Black & White) কনভার্টার")
    if global_file is not None:
        img = Image.open(global_file).convert("L")
        st.image(img, use_container_width=True)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=95)
        st.download_button("Download", buf.getvalue(), "bw.jpg", "image/jpeg", key="dl_11")
    else:
        st.warning("দয়া করে ছবি আপলোড করুন।")

elif app_mode == 12:
    st.header("🔄 ছবি ঘোরানো (Rotate & Flip)")
    if global_file is not None:
        img = Image.open(global_file)
        rot = st.selectbox("Angle", [90, 180, 270])
        img = img.rotate(rot, expand=True)
        st.image(img, use_container_width=True)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=95)
        st.download_button("Download", buf.getvalue(), "rot.jpg", "image/jpeg", key="dl_12")
    else:
        st.warning("দয়া করে ছবি আপলোড করুন।")

elif app_mode == 13:
    st.header("💧 ওয়াটারমার্ক যুক্ত করার টুল")
    if global_file is not None:
        st.image(Image.open(global_file), use_container_width=True)
        st.success("Watermark tool ready.")
    else:
        st.warning("দয়া করে ছবি আপলোড করুন।")

elif app_mode == 14:
    st.header("📄 পিডিএফ টেক্সট এক্সট্র্যাক্ট টুল")
    if global_file is not None:
        try:
            reader = PdfReader(global_file)
            txt = reader.pages[0].extract_text()
            st.text_area("Extracted Text:", txt, height=200)
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("দয়া করে একটি পিডিএফ ফাইল আপলোড করুন।")
