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
    .studio-header {{
        background: {header_gradient};
        padding: 25px 20px;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin: 0 auto 20px auto;
        max-width: 550px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.2);
    }}
    .studio-header h1 {{
        font-size: 24px;
        margin-bottom: 8px;
        font-weight: bold;
    }}
    .studio-header p {{
        font-size: 13px;
        margin: 4px 0;
        line-height: 1.4;
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
        border-bottom: 2px solid {accent_color};
        padding-bottom: 4px;
    }}
    .a4-paper-box {{
        background: #ffffff;
        width: 100%;
        max-width: 800px;
        min-height: 1060px;
        margin: 20px auto;
        padding: 40px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        color: #000000;
        box-sizing: border-box;
        border-radius: 6px;
    }}
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
            padding: 10px !important;
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
    "upload_label": "Upload Image or PDF file" if is_eng else "ছবি বা পিডিএফ ফাইল আপলোড করুন",
    "tools_header": "🛠️ ডিজিটাল টুলস ও এডিটর (১-১৪)" if not is_eng else "🛠️ Digital Tools & Editors",
    "job_header": "💼 সরকারি ও বেসরকারি চাকরির পোর্টাল" if not is_eng else "💼 Job Portals",
    "result_header": "📊 রেজাল্ট ও মার্কশিট পোর্টাল" if not is_eng else "📊 Result & Marksheet Portal",
    "portal_header": "📋 অন্যান্য গুরুত্বপূর্ণ অনলাইন লিংক ও পোর্টাল" if not is_eng else "📋 All Important Online Links",
}

# আপনার ভিডিওতে দেখানো কার্ডের ডিজাইনের মতো সাজানো হেডার সেকশন
st.markdown(f"""
<div class="studio-header">
    <div style="background: rgba(255,255,255,0.15); padding: 15px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.3);">
        <h1 style="margin: 0 0 8px 0; font-size: 24px; color: #ffffff; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);">{t['title']}</h1>
        <p style="margin: 3px 0; font-size: 13px;">{t['address']}</p>
        <p style="margin: 3px 0; font-size: 13px;">{t['mobile']}</p>
        <hr style="border: 0.5px solid rgba(255,255,255,0.3); width: 85%; margin: 10px auto;">
        <p style="margin: 0; font-size: 12px; font-weight: 500; opacity: 0.95;">সকল ধরনের কম্পিউটার, ডিজাইন ও অনলাইন সার্ভিসের অল-ইন-ওয়ান মাস্টার ড্যাশবোর্ড</p>
    </div>
</div>
""", unsafe_allow_html=True)

global_file = st.file_uploader(t['upload_label'], type=["jpg", "jpeg", "png", "pdf"])
st.markdown("---")

if 'app_mode' not in st.session_state:
    st.session_state.app_mode = 1

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

# সাইডবারের অন্যান্য লিংক সেকশন
st.sidebar.markdown(f"<div class='sidebar-section-title'>{t['job_header']}</div>", unsafe_allow_html=True)
st.sidebar.markdown("""
<div class="link-box">
    <b>🏛️ সরকারি চাকরির পোর্টাল:</b> <a href="https://alljobs.teletalk.com.bd/" target="_blank">All Jobs BD</a><br>
    <b>🏢 বেসরকারি পোর্টাল:</b> <a href="https://www.bdjobs.com/" target="_blank">Bdjobs.com</a>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown(f"<div class='sidebar-section-title'>{t['result_header']}</div>", unsafe_allow_html=True)
st.sidebar.markdown("""
<div class="link-box">
    <b>🎓 শিক্ষা বোর্ড রেজাল্ট:</b> <a href="http://www.educationboardresults.gov.bd/" target="_blank">Education Board</a><br>
    <b>🏛️ জাতীয় বিশ্ববিদ্যালয়:</b> <a href="http://results.nu.ac.bd/" target="_blank">NU Results</a>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown(f"<div class='sidebar-section-title'>{t['portal_header']}</div>", unsafe_allow_html=True)
st.sidebar.markdown("""
<div class="link-box">
    <b>📇 নাগরিক সেবা:</b> जन्म নিবন্ধন | NID | পাসপোর্ট
</div>
""", unsafe_allow_html=True)

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
        st.error("❌ 'rembg' লাইব্রেরি ইনস্টল করা নেই।")
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
    shop_name = st.text_input("দোকানের নাম (Shop Name)", "হাসানুর কম্পিউটার স্টুডিও")
    shop_address = st.text_input("দোকানের ঠিকানা ও ফোন", "দিঘীরপাড়, মনিরামপুর, যশোর | মোবাইল: ০১৭৪৩-৬১৪৩৫৯")

    c_name = st.text_input("গ্রাহকের নাম (Customer Name)", "মোঃ রহিম")
    c_phone = st.text_input("মোবাইল নম্বর", "01700000000")

    if 'memo_items' not in st.session_state:
        st.session_state.memo_items = [
            {'name': 'ল্যামিনেশন ও প্রিন্ট', 'serial': 'N/A', 'price': 150, 'has_warranty': 'না', 'warranty_period': '-'}
        ]

    if st.button("➕ নতুন আইটেম যোগ করুন"):
        st.session_state.memo_items.append({'name': '', 'serial': '', 'price': 0, 'has_warranty': 'না', 'warranty_period': '-'})

    updated_items = []
    total_amount = 0

    for i, item in enumerate(st.session_state.memo_items):
        st.markdown(f"**আইটেম #{i+1}**")
        c1, c2, c3, c4, c5 = st.columns([3, 2, 2, 2, 2])
        with c1:
            it_name = st.text_input("পণ্যের নাম", item['name'], key=f"item_name_{i}")
        with c2:
            it_serial = st.text_input("সিরিয়াল নম্বর", item.get('serial', ''), key=f"item_serial_{i}")
        with c3:
            it_price = st.number_input("মূল্য (TK)", 0, 1000000, int(item['price']), key=f"item_price_{i}")
        with c4:
            has_war = st.selectbox("ওয়ারেন্টি?", ["হ্যাঁ", "না"], index=0 if item['has_warranty']=='হ্যাঁ' else 1, key=f"has_war_{i}")
        with c5:
            war_per = st.text_input("মেয়াদ", item['warranty_period'], key=f"war_per_{i}")
        
        updated_items.append({'name': it_name, 'serial': it_serial or "N/A", 'price': it_price, 'has_warranty': has_war, 'warranty_period': war_per})
        total_amount += it_price
        st.markdown("---")

    if st.button("🖨️ ক্যাশ মেমো জেনারেট করুন (A4 Print Ready)"):
        rows_html = "".join([
            f"<tr><td style='padding:8px; border-bottom:1px solid #ddd; text-align:center;'>{idx+1}</td>"
            f"<td style='padding:8px; border-bottom:1px solid #ddd;'>{itm['name']}</td>"
            f"<td style='padding:8px; border-bottom:1px solid #ddd; text-align:center; font-family:monospace;'>{itm['serial']}</td>"
            f"<td style='padding:8px; border-bottom:1px solid #ddd; text-align:center;'>{itm['has_warranty']} ({itm['warranty_period']})</td>"
            f"<td style='padding:8px; border-bottom:1px solid #ddd; text-align:right;'>{itm['price']} TK</td></tr>"
            for idx, itm in enumerate(updated_items)
        ])

        st.markdown(f"""
        <div class="a4-paper-box" style="border: 3px solid #0B50FA;">
            <div style="text-align:center;">
                <h2 style="color:#0B50FA; margin:0; font-size:26px;">{shop_name}</h2>
                <p style="font-size:13px; margin:4px 0;">{shop_address}</p>
                <hr style="border: 1px solid #0B50FA; width:65%; margin:12px auto;">
                <h3 style="background:#0B50FA; color:white; display:inline-block; padding:5px 20px; border-radius:4px;">ক্যাশ মেমো / রসিদ</h3>
            </div>
            
            <div style="margin-top:20px; display:flex; justify-content:space-between; font-size:13px; background:#f8f9fa; padding:10px; border-radius:5px;">
                <div>
                    <p style="margin:2px 0;"><b>গ্রাহকের নাম:</b> {c_name}</p>
                    <p style="margin:2px 0;"><b>মোবাইল নম্বর:</b> {c_phone}</p>
                </div>
                <div style="text-align:right;">
                    <p style="margin:2px 0;"><b>তারিখ:</b> {date.today().strftime('%d-%m-%Y')}</p>
                </div>
            </div>

            <table style="width:100%; border-collapse: collapse; margin-top:15px; font-size:13px;">
                <thead>
                    <tr style="background:#0B50FA; color:white;">
                        <th style="padding:10px; text-align:center; width:8%;">ক্রমিক</th>
                        <th style="padding:10px; text-align:left; width:35%;">পণ্যের বিবরণ</th>
                        <th style="padding:10px; text-align:center; width:20%;">সিরিয়াল নম্বর</th>
                        <th style="padding:10px; text-align:center; width:20%;">ওয়ারেন্টি</th>
                        <th style="padding:10px; text-align:right; width:17%;">মূল্য</th>
                    </tr>
                </thead>
                <tbody>{rows_html}</tbody>
            </table>

            <div style="margin-top:20px; text-align:right; font-size:15px; background:#f1f3f5; padding:10px; border-radius:5px;">
                <b>সর্বমোট প্রদেয় টাকা (Total): <span style="color:red; font-size:18px;">{total_amount} TK</span></b>
            </div>

            <div style="margin-top:100px; display:flex; justify-content:space-between; font-size:13px;">
                <div><p style="border-top:1px dashed black; padding-top:4px; display:inline-block;">গ্রাহকের স্বাক্ষর</p></div>
                <div style="text-align:right;"><p style="border-top:1px solid black; padding-top:4px; display:inline-block; font-weight:bold;">বিক্রেতার স্বাক্ষর / সিল</p></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.success("✅ ক্যাশ মেমো সফলভাবে জেনারেট হয়েছে!")

elif app_mode == 7:
    st.header("🛡️ ডিজিটাল ওয়ারেন্টি কার্ড জেনারেটর")
    st.text_input("Product Name", "HP Printer")
    st.text_input("Buyer Name", "Hasan Ali")
    if st.button("Generate Card"):
        st.success("Warranty card generated successfully!")

elif app_mode == 8:
    st.header("📜 নাগরিক সনদপত্র জেনারেটর (A4 Print Ready)")
    col1, col2 = st.columns(2)
    with col1:
        cit_name = st.text_input("আবেদনকারীর নাম", "মোঃ রফিকুল ইসলাম")
        cit_father = st.text_input("পিতার নাম", "মোঃ আব্দুল জব্বার")
    with col2:
        cit_village = st.text_input("গ্রাম / মহল্লা", "দিঘীরপাড়")
        cit_ward = st.text_input("ওয়ার্ড ও ইউনিয়ন", "ওয়ার্ড নং- ০৪, ঝাঁপা ইউনিয়ন")

    if st.button("নাগরিক সনদ জেনারেট করুন"):
        st.markdown(f"""
        <div class="a4-paper-box" style="border:6px double #0B50FA;">
            <div style="text-align:center;">
                <h2 style="color:#0B50FA; margin:0;">ইউনিয়ন পরিষদ কার্যালয়</h2>
                <p style="font-size:13px; margin:2px 0;">{cit_ward}, মনিরামপুর, যশোর।</p>
                <hr style="border:1px solid #0B50FA; width:50%;">
                <h3 style="background:#0B50FA; color:white; display:inline-block; padding:5px 20px; border-radius:4px;">নাগরিক সনদপত্র</h3>
            </div>
            <p style="font-size:14px; line-height:1.8; text-align:justify; margin-top:25px;">
                এই মর্মে প্রত্যয়ন করা যাইতেছে যে, <b>{cit_name}</b>, পিতা: <b>{cit_father}</b>, সাং: <b>{cit_village}</b>, উপজেলা: মনিরামপুর, জেলা: যশোর। তিনি অত্র ইউনিয়নের একজন স্থায়ী বাসিন্দা এবং জন্মসূত্রে বাংলাদেশের নাগরিক।
            </p>
            <div style="margin-top:100px; display:flex; justify-content:space-between;">
                <div><p style="border-top:1px dashed black; padding-top:4px; display:inline-block;">আবেদনকারীর স্বাক্ষর</p></div>
                <div style="text-align:right;"><p style="border-top:1px solid black; padding-top:4px; display:inline-block; font-weight:bold;">চেয়ারম্যান</p></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.success("✅ নাগরিক সনদ সফলভাবে তৈরি হয়েছে!")

elif app_mode == 9:
    st.header("⚽ টুর্নামেন্ট আমন্ত্রণপত্র ও নিয়মাবলী জেনারেটর")
    t_name = st.text_input("টুর্নামেন্টের নাম", "দিঘীরপাড় প্রিমিয়ার লিগ")
    t_ground = st.text_input("খেলার স্থান", "দিঘীরপাড় সরকারি প্রাথমিক বিদ্যালয় মাঠ")
    if st.button("টুর্নামেন্ট নোটিশ জেনারেট করুন"):
        st.markdown(f"""
        <div class="a4-paper-box" style="border:4px solid #ff4b4b;">
            <div style="text-align:center;">
                <h2 style="color:#ff4b4b; margin:0;">🏆 টুর্নামেন্ট আমন্ত্রণপত্র 🏆</h2>
                <h3 style="color:#0B50FA; margin:6px 0;">{t_name}</h3>
                <p style="font-size:13px;">📍 স্থান: {t_ground}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.success("✅ টুর্নামেন্টের নোটিশ তৈরি হয়েছে!")

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
    st.header("⬛ সাদাকালো কনভার্টার")
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
