import io
import cv2
import numpy as np
from PIL import Image
import streamlit as st
from pypdf import PdfReader
from datetime import date
import streamlit.components.v1.components as components
import base64
from pathlib import Path

st.set_page_config(page_title="হাসানুর কম্পিউটার স্টুডিও", layout="wide")

# ==============================================================================
# মূল স্টাইল, গ্রেডিয়েন্ট ব্যাকগ্রাউন্ড, সাইডবার মেনু হোয়াইট ব্যাকগ্রাউন্ড ও ব্ল্যাক টেক্সট
# ==============================================================================
st.markdown("""
<style>
    /* ডার্ক মোড চিরতরে বন্ধ করার জন্য গ্লোবাল লাইট থিম স্টাইল */
    .stApp {
        background: linear-gradient(135deg, #071952, #0b2f64, #1b032d, #381123) !important;
        background-attachment: fixed !important;
        color: #ffffff !important;
    }
    
    /* সাইডবার ব্যাকগ্রাউন্ড */
    section[data-testid="stSidebar"] {
        background-color: #0b132b !important;
    }
    
    /* সাইডবারের মেনু বাটন এবং তার ভেতরের সব লেখার রঙ কালো ও ব্যাকগ্রাউন্ড সাদা করা */
    section[data-testid="stSidebar"] button,
    section[data-testid="stSidebar"] button p,
    section[data-testid="stSidebar"] button span,
    section[data-testid="stSidebar"] div[data-testid="stBaseButton-secondary"] {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #cccccc !important;
        font-weight: 700 !important;
        border-radius: 6px !important;
        text-align: left !important;
    }
    
    /* বাটনে মাউস নিলে লাল ব্যাকগ্রাউন্ড ও সাদা লেখা হবে */
    section[data-testid="stSidebar"] button:hover,
    section[data-testid="stSidebar"] button:hover p,
    section[data-testid="stSidebar"] button:hover span {
        background-color: #ff4b4b !important;
        color: #ffffff !important;
        border-color: #ff4b4b !important;
    }
    
    /* সাইডবারের অন্যান্য সাধারণ শিরোনাম সাদা রাখা */
    section[data-testid="stSidebar"] .stMarkdown, 
    section[data-testid="stSidebar"] label, 
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3 {
        color: #ffffff !important;
    }
    
    /* লেখার লিঙ্কে মাউস রাখলে লাল রঙ */
    a:hover, .stMarkdown a:hover {
        color: #ff4b4b !important;
    }
    
    /* অ্যাপের ভেতরের সমস্ত সাধারণ লেখা এবং লেবেল সাদা রঙ নিশ্চিত করা */
    h1, h2, h3, h4, h5, h6, p, span, label, div, .stMarkdown, .stText {
        color: #ffffff !important;
    }
    
    /* টেক্সট ইনপুট ও সিলেক্ট বক্সের ভেতরে লেখার রঙ স্পষ্ট রাখা */
    input, textarea, select {
        color: #000000 !important;
    }

    .studio-header {
        background: linear-gradient(135deg, #0B50FA, #ff4b4b);
        padding: 25px 20px;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }
    .studio-header h1 {
        font-size: 26px;
        margin-bottom: 8px;
        font-weight: bold;
        color: white !important;
    }
    .studio-header p {
        font-size: 14px;
        margin: 4px 0;
        line-height: 1.5;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

def get_embedded_image():
    image_path = "hasanur.jpeg"
    if Path(image_path).exists():
        with open(image_path, "rb") as img_file:
            encoded = base64.b64encode(img_file.read()).decode()
            return f'<img src="data:image/jpeg;base64,{encoded}" style="width: 105px; height: 105px; border-radius: 50%; object-fit: contain; background-color: #ffffff; border: 3px solid white; box-shadow: 0 4px 10px rgba(0,0,0,0.3); vertical-align: middle; margin-right: 15px;">'
    return '👤'

img_tag = get_embedded_image()

# হেডার সেকশন
st.markdown(f"""
<div class="studio-header">
    <div style="background: rgba(255,255,255,0.15); padding: 18px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.3);">
        <div style="display: flex; align-items: center; justify-content: center; flex-wrap: wrap; margin-bottom: 8px;">
            {img_tag}
            <h1 style="margin: 0; display: inline-block;">হাসানুর কম্পিউটার স্টুডিও</h1>
        </div>
        <p style="margin: 3px 0;"><b>ঠিকানা:</b> দিঘীরপাড়, মনিরামপুর, যশোর</p>
        <p style="margin: 3px 0;"><b>মোবাইল:</b> ০১৭৪৩-৬১৪৩৫৯</p>
        <hr style="border: 0.5px solid rgba(255,255,255,0.3); width: 80%; margin: 10px auto;">
        <p style="margin: 0; font-size: 13px; font-weight: 500;">সকল ধরনের কম্পিউটার, ডিজাইন ও অনলাইন সার্ভিসের অল-ইন-ওয়ান মাস্টার ড্যাশবোর্ড</p>
    </div>
</div>
""", unsafe_allow_html=True)

global_file = st.file_uploader("ছবি বা পিডিএফ ফাইল আপলোড করুন", type=["jpg", "jpeg", "png", "pdf"])
st.markdown("---")

if 'app_mode' not in st.session_state:
    st.session_state.app_mode = 6

st.sidebar.header("⚙️ টুলস ও মেনুবার")

menu_dict = {
    1: ("✨ ইমেজ ব্রাইটনেস ও কালার এডিটর", "ছবির আলো ও ব্রাইটনেস ঠিক করুন"),
    2: ("🎨 স্টুডিও ব্যাকগ্রাউন্ড রিমুভ ও কালার", "পাসপোর্ট ছবির ব্যাকগ্রাউন্ড পরিবর্তন"),
    3: ("🆔 আইডি কার্ড ক্রপ ও সোজা করার টুল", "আইডি কার্ড ক্রপ করুন"),
    4: ("🛂 পাসপোর্ট সাইজ ছবি শিট তৈরি (৪ কপি)", "এক ক্লিকে ৪ কপি ছবি তৈরি"),
    5: ("🎂 বয়স ক্যালকুলেটর (Age Calculator)", "নির্ভুল বয়স হিসাব"),
    6: ("🧾 দোকানের ক্যাশ মেমো / রশিদ জেনারেটর", "বিক্রয় রশিদ ও ক্যাশ মেমো তৈরি"),
    7: ("🛡️ ডিজিটাল ওয়ারেন্টি কার্ড জেনারেটর", "ওয়ারেন্টি কার্ড তৈরি"),
    8: ("📜 নাগরিক সনদ (Citizenship) জেনারেটর", "নাগরিক সনদপত্র তৈরি"),
    9: ("⚽ টুর্নামেন্ট আমন্ত্রণপত্র ও নিয়মাবলী", "টুর্নামেন্ট নোটিশ তৈরি"),
    10: ("🔗 অনলাইন সরকারি ও প্রয়োজনীয় লিংকসমূহ", "গুরুত্বপূর্ণ অনলাইন সেবা ও পোর্টাল"),
    11: ("📏 ছবির সাইজ পরিবর্তন ও রিসাইজার", "পিক্সেল অনুযায়ী সাইজ পরিবর্তন"),
    12: ("⬛ সাদাকালো (Black & White) কনভার্টার", "সাদাকালো ছবি তৈরি"),
    13: ("🔄 ছবি ঘোরানো (Rotate & Flip)", "ছবি এঙ্গেলে ঘোরানো"),
    14: ("💧 ওয়াটারমার্ক যুক্ত করার টুল", "নাম বা লোগো ওয়াটারমার্ক"),
    15: ("📄 পিডিএফ টেক্সট এক্সট্র্যাক্ট টুল", "পিডিএফ থেকে টেক্সট আলাদা করা")
}

for num, (item_name, desc) in menu_dict.items():
    if st.sidebar.button(item_name, key=f"menu_btn_{num}"):
        st.session_state.app_mode = num

app_mode = st.session_state.app_mode

def print_content_html(html_content, button_text):
    full_html = f"""
    <!DOCTYPE html>
    <html lang="bn">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: 'SolaimanLipi', Arial, sans-serif;
                background: #525659;
                margin: 0;
                padding: 20px;
                display: flex;
                flex-direction: column;
                align-items: center;
            }}
            .a4-page {{
                background: white;
                width: 210mm;
                height: 297mm;
                padding: 12mm 15mm;
                margin: 0 auto 20px auto;
                box-shadow: 0 0 15px rgba(0,0,0,0.4);
                box-sizing: border-box;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                position: relative;
                border: 2px solid #0B50FA;
            }}
            @media print {{
                body {{
                    background: none;
                    padding: 0;
                }}
                .no-print {{
                    display: none !important;
                }}
                .a4-page {{
                    box-shadow: none;
                    margin: 0;
                    width: 210mm;
                    height: 297mm;
                    padding: 12mm 15mm;
                    page-break-after: avoid;
                    page-break-inside: avoid;
                    border: 2px solid #0B50FA !important;
                    -webkit-print-color-adjust: exact;
                }}
                @page {{
                    size: A4;
                    margin: 0;
                }}
            }}
            .print-btn {{
                background-color: #0B50FA;
                color: white;
                padding: 12px 30px;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 20px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.2);
            }}
            .print-btn:hover {{
                background-color: #083cb3;
            }}
        </style>
    </head>
    <body>
        <button class="print-btn no-print" onclick="window.print()">🖨️ {button_text}</button>
        <div class="a4-page">
            {html_content}
        </div>
    </body>
    </html>
    """
    components.html(full_html, height=1150, scrolling=True)

# মোড ১: ব্রাইটনেস ও কালার এডিটর
if app_mode == 1:
    st.header("✨ ইমেজ ব্রাইটনেস ও কালার এডিটর")
    if global_file is not None:
        image = Image.open(global_file)
        img_np = np.array(image)
        
        brightness = st.slider("ব্রাইটনেস (Brightness)", -100, 100, 0)
        contrast = st.slider("কনট্রাস্ট (Contrast)", 0.0, 3.0, 1.0)
        
        adjusted = cv2.convertScaleAbs(img_np, alpha=contrast, beta=brightness)
        st.image(adjusted, caption="এডিট করা ছবি", use_column_width=True)
    else:
        st.info("দয়া করে উপরে ফাইল আপলোড অপশন থেকে একটি ছবি আপলোড করুন।")

# মোড ২: ব্যাকগ্রাউন্ড রিমুভ ও কালার/ছবি পরিবর্তন
elif app_mode == 2:
    st.header("🎨 স্টুডিও ব্যাকগ্রাউন্ড রিমুভ ও কালার/ছবি পরিবর্তন")
    if global_file is not None:
        image = Image.open(global_file).convert("RGB")
        st.image(image, caption="মূল আপলোড করা ছবি", width=300)
        
        bg_type = st.radio("ব্যাকগ্রাউন্ড পরিবর্তনের মাধ্যম বেছে নিন:", ["রঙ (Color Picker)", "কম্পিউটার থেকে ছবি আপলোড (Custom Image)"])
        
        bg_color = "#ffffff"
        bg_custom_file = None
        
        if bg_type == "রঙ (Color Picker)":
            bg_color = st.color_picker("নতুন ব্যাকগ্রাউন্ড কালার সিলেক্ট করুন", "#ffffff")
        else:
            bg_custom_file = st.file_uploader("ব্যাকগ্রাউন্ডের জন্য একটি ছবি আপলোড করুন", type=["jpg", "jpeg", "png"], key="bg_img_upload")
        
        if st.button("🚀 ব্যাকগ্রাউন্ড রিমুভ ও নতুন ব্যাকগ্রাউন্ড সেট করুন"):
            with st.spinner("প্রসেসিং হচ্ছে, দয়া করে অপেক্ষা করুন..."):
                try:
                    img_np = np.array(image)
                    h, w = img_np.shape[:2]
                    
                    mask = np.zeros(img_np.shape[:2], np.uint8)
                    bgdModel = np.zeros((1, 65), np.float64)
                    fgdModel = np.zeros((1, 65), np.float64)
                    
                    rect = (int(w * 0.1), int(h * 0.05), int(w * 0.8), int(h * 0.9))
                    cv2.grabCut(img_np, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)
                    
                    mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
                    result_np = img_np * mask2[:, :, np.newaxis]
                    
                    if bg_type == "রঙ (Color Picker)" or bg_custom_file is None:
                        hex_c = bg_color.lstrip('#')
                        bg_rgb = tuple(int(hex_c[i:i+2], 16) for i in (0, 2, 4))
                        bg_img = np.full(img_np.shape, bg_rgb, dtype=np.uint8)
                    else:
                        bg_img_pil = Image.open(bg_custom_file).convert("RGB").resize((w, h))
                        bg_img = np.array(bg_img_pil)
                        
                    inv_mask2 = 1 - mask2
                    bg_part = bg_img * inv_mask2[:, :, np.newaxis]
                    final_np = result_np + bg_part
                    
                    final_img = Image.fromarray(final_np)
                    st.success("✅ ব্যাকগ্রাউন্ড সফলভাবে পরিবর্তন করা হয়েছে!")
                    st.image(final_img, caption="রিমুভ ও পরিবর্তিত ব্যাকগ্রাউন্ডের ছবি", use_column_width=True)
                except Exception as e:
                    st.error(f"⚠️ ত্রুটি ঘটেছে: {e}")
    else:
        st.info("দয়া করে উপরে ফাইল আপলোড অপশন থেকে একটি পাসপোর্ট বা পোর্ট্রেট ছবি আপলোড করুন।")

# মোড ৩: আইডি কার্ড ক্রপ
elif app_mode == 3:
    st.header("🆔 আইডি কার্ড ক্রপ ও সোজা করার টুল")
    if global_file is not None:
        image = Image.open(global_file)
        st.image(image, caption="মূল আইডি কার্ড", use_column_width=True)
        st.info("আইডি কার্ড প্রসেসিং এবং ক্রপ করার অপশন এখানে কাজ করবে।")
    else:
        st.info("দয়া করে একটি আইডি কার্ডের ছবি আপলোড করুন।")

# মোড ৪: পাসপোর্ট সাইজ ছবি শিট (৪ কপি)
elif app_mode == 4:
    st.header("🛂 পাসপোর্ট সাইজ ছবি শিট তৈরি (৪ কপি)")
    if global_file is not None:
        image = Image.open(global_file)
        st.image(image, width=150, caption="আপনার ছবি")
        if st.button("৪ কপি ছবি শিট তৈরি করুন"):
            st.success("৪ কপি ছবির প্রিন্ট প্রিভিউ প্রস্তুত।")
    else:
        st.info("দয়া করে একটি পাসপোর্ট ছবি আপলোড করুন।")

# মোড ৫: বয়স ক্যালকুলেটর
elif app_mode == 5:
    st.header("🎂 বয়স ক্যালকুলেটর (Age Calculator)")
    b_date = st.date_input("জন্মতারিখ সিলেক্ট করুন", date(2000, 1, 1))
    t_date_val = st.date_input("কাঙ্ক্ষিত তারিখ", date.today())
    if st.button("বয়স হিসাব করুন"):
        age_years = t_date_val.year - b_date.year - ((t_date_val.month, t_date_val.day) < (b_date.month, b_date.day))
        st.success(f"বয়স: প্রায় {age_years} বছর পূর্ণ হয়েছে।")

# মোড ৬: ক্যাশ মেমো
elif app_mode == 6:
    st.header("🧾 দোকানের ক্যাশ মেমো / রশিদ জেনারেটর")
    
    shop_name = st.text_input("দোকানের নাম", "হাসানুর কম্পিউটার স্টুডিও")
    shop_address = st.text_input("দোকানের ঠিকানা ও ফোন", "দিঘীরপাড়, মনিরামপুর, যশোর | মোবাইল: ০১৭৪৩-৬১৪৩৫৯")

    col_c1, col_c2 = st.columns(2)
    with col_c1:
        c_name = st.text_input("গ্রাহকের নাম", "মোঃ রহিম")
    with col_c2:
        c_phone = st.text_input("মোবাইল নম্বর", "01700000000")

    if 'memo_items' not in st.session_state:
        st.session_state.memo_items = [
            {'name': 'ল্যামিনেশন ও প্রিন্ট', 'serial': 'N/A', 'price': 150, 'has_warranty': 'না', 'warranty_period': '-'}
        ]

    if st.button("➕ নতুন আইটেম যোগ করুন"):
        st.session_state.memo_items.append({'name': '', 'serial': '', 'price': 0, 'has_warranty': 'না', 'warranty_period': '-'})

    updated_items = []
    total_amount = 0
    indices_to_delete = []

    for i, item in enumerate(st.session_state.memo_items):
        st.markdown(f"**আইটেম #{i+1}**")
        c1, c2, c3, c4, c5, c6 = st.columns([2.5, 2, 1.5, 1.5, 1.5, 1])
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
        with c6:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            if st.button("❌ বাদ", key=f"del_item_{i}"):
                indices_to_delete.append(i)
        
        updated_items.append({'name': it_name, 'serial': it_serial or "N/A", 'price': it_price, 'has_warranty': has_war, 'warranty_period': war_per})
        total_amount += it_price
        st.markdown("---")

    if indices_to_delete:
        for idx in sorted(indices_to_delete, reverse=True):
            del st.session_state.memo_items[idx]
        st.rerun()

    if st.button("🖨️ ক্যাশ মেমো ফাইনাল প্রিভিউ ও প্রিন্ট দেখুন"):
        st.success("✅ ক্যাশ মেমো সম্পূর্ণ A4 পেজে প্রস্তুত!")
        
        items_html = ""
        for idx, itm in enumerate(updated_items):
            items_html += f"""
            <tr style="border-bottom: 1px solid #ddd;">
                <td style="padding: 10px; text-align: center;">{idx + 1}</td>
                <td style="padding: 10px;">{itm['name']}</td>
                <td style="padding: 10px; text-align: center;">{itm['serial']}</td>
                <td style="padding: 10px; text-align: center;">{itm['has_warranty']} ({itm['warranty_period']})</td>
                <td style="padding: 10px; text-align: right;">{itm['price']} TK</td>
            </tr>
            """

        memo_html_code = f"""
        <div style='padding: 10px; width: 100%; height: 100%; display: flex; flex-direction: column; justify-content: space-between; box-sizing: border-box;'>
            <div>
                <h2 style='text-align: center; color: #0B50FA; margin: 0; font-size: 26px;'>{shop_name}</h2>
                <p style='text-align: center; font-size: 14px; color: #333; margin: 6px 0;'>{shop_address}</p>
                <hr style='border: 1px solid #0B50FA; margin-bottom: 20px;'>
                <h3 style='text-align: center; background-color: #0B50FA; color: white; padding: 8px; border-radius: 4px; margin: 0 0 25px 0; font-size: 18px;'>ক্যাশ মেমো / রসিদ</h3>
                
                <table style="width: 100%; margin-bottom: 25px; font-size: 15px;">
                    <tr>
                        <td><b>গ্রাহকের নাম:</b> {c_name}</td>
                        <td style="text-align: right;"><b>তারিখ:</b> {date.today().strftime('%d-%m-%Y')}</td>
                    </tr>
                    <tr>
                        <td style="padding-top: 8px;"><b>মোবাইল নম্বর:</b> {c_phone}</td>
                        <td></td>
                    </tr>
                </table>
                
                <table style="width: 100%; border-collapse: collapse; font-size: 15px; margin-bottom: 25px;">
                    <thead>
                        <tr style="background-color: #f1f3f5; border-bottom: 2px solid #0B50FA;">
                            <th style="padding: 10px; text-align: center;">ক্রমিক</th>
                            <th style="padding: 10px; text-align: left;">পণ্যের বিবরণ</th>
                            <th style="padding: 10px; text-align: center;">সিরিয়াল নম্বর</th>
                            <th style="padding: 10px; text-align: center;">ওয়ারেন্টি</th>
                            <th style="padding: 10px; text-align: right;">মূল্য</th>
                        </tr>
                    </thead>
                    <tbody>
                        {items_html}
                    </tbody>
                </table>
                
                <div style='text-align: right; font-size: 16px; background-color: #f8f9fa; padding: 12px; border-radius: 5px;'>
                    <b>সর্বমোট প্রদেয় টাকা (Total): <span style='color: red; font-size: 18px;'>{total_amount} TK</span></b>
                </div>
            </div>
            
            <table style="width: 100%; margin-top: 30px; font-size: 15px;">
                <tr>
                    <td><div style='border-top: 1px dashed black; width: 180px; text-align: center; padding-top: 6px;'>গ্রাহকের স্বাক্ষর</div></td>
                    <td style="text-align: right;"><div style='border-top: 1px solid black; width: 200px; text-align: center; padding-top: 6px; font-weight: bold; display: inline-block;'>বিক্রেতার স্বাক্ষর / সিল</div></td>
                </tr>
            </table>
        </div>
        """
        print_content_html(memo_html_code, "ক্যাশ মেমো প্রিন্ট করুন")

# মোড ৭: ওয়ারেন্টি কার্ড
elif app_mode == 7:
    st.header("🛡️ ডিজিটাল ওয়ারেন্টি কার্ড জেনারেটর")
    w_item = st.text_input("পণ্যের নাম", "স্মার্ট এলইডি টিভি")
    w_code = st.text_input("ওয়ারেন্টি কোড / সিরিয়াল", "SN-987654")
    if st.button("ওয়ারেন্টি কার্ড তৈরি করুন"):
        st.success("ওয়ারেন্টি কার্ড প্রস্তুত করা হয়েছে।")

# মোড ৮: নাগরিক সনদপত্র
elif app_mode == 8:
    st.header("📜 নাগরিক সনদপত্র জেনারেটর")
    
    col_u1, col_u2 = st.columns(2)
    with col_u1:
        cit_name = st.text_input("আবেদনকারীর নাম", "মোঃ রফিকুল ইসলাম")
        cit_father = st.text_input("পিতার নাম", "মোঃ আব্দুল জব্বার")
        cit_mother = st.text_input("মাতার নাম", "মাজেদা বেগম")
    with col_u2:
        cit_vill = st.text_input("গ্রাম / পাড়া", "দিঘীরপাড়")
        cit_word = st.text_input("ওয়ার্ড নম্বর", "ওয়ার্ড নং - ০৪")
        cit_union = st.text_input("ইউনিয়ন / পৌরসভা", "মণিরামপুর সদর ইউনিয়ন")

    if st.button("📜 নাগরিক সনদ প্রিভিউ ও প্রিন্ট দেখুন"):
        st.success("✅ নাগরিক সনদপত্র সম্পূর্ণ A4 পেজে প্রস্তুত!")
        
        cert_html_code = f"""
        <div style='padding: 15px; width: 100%; height: 100%; display: flex; flex-direction: column; justify-content: space-between; box-sizing: border-box; background-color: #ffffff;'>
            <div>
                <div style="text-align:center;">
                    <h2 style="color:#0B50FA; margin:0; font-size: 28px; font-weight: bold;">{cit_union} কার্যালয়</h2>
                    <p style="font-size:15px; margin:6px 0; color:#333;">দিঘীরপাড়, মনিরামপুর, যশোর।</p>
                    <hr style="border:1px solid #0B50FA; width:45%; margin: 15px auto;">
                    <h3 style="background:#0B50FA; color:white; display:inline-block; padding:6px 25px; border-radius:5px; margin-top:10px; font-size: 20px;">নাগরিক সনদপত্র</h3>
                </div>
                
                <p style="font-size:17px; line-height:2.4; text-align:justify; margin-top:40px;">
                    এই মর্মে প্রত্যয়ন করা যাইতেছে যে, <b>{cit_name}</b>, পিতা: <b>{cit_father}</b>, মাতা: <b>{cit_mother}</b>, গ্রাম: <b>{cit_vill}</b>, {cit_word}, উপজেলা: মণিরামপুর, জেলা: যশোর এর অত্র ইউনিয়নের একজন স্থায়ী বাসিন্দা এবং জন্মসূত্রে বাংলাদেশের নাগরিক। আমার জানামতে তিনি দেশবিরোধী বা রাষ্ট্রবিরোধী কোনো কাজের সাথে জড়িত নন এবং তার চরিত্র অত্যন্ত ভালো।
                </p>
                
                <p style="font-size:17px; margin-top:30px; line-height: 1.8;">আমি তার সর্বাঙ্গীন সাফল্য ও দীর্ঘায়ু কামনা করি।</p>
            </div>
            
            <table style="width: 100%; margin-top: 40px; font-size: 15px;">
                <tr>
                    <td><div style="border-top:1px dashed black; width: 180px; text-align: center; padding-top:8px;">আবেদনকারীর স্বাক্ষর</div></td>
                    <td style="text-align: right;"><div style="border-top:1px solid black; width: 180px; text-align: center; padding-top:8px; font-weight:bold; display: inline-block;">চেয়ারম্যান</div></td>
                </tr>
            </table>
        </div>
        """
        print_content_html(cert_html_code, "নাগরিক সনদ প্রিন্ট করুন")

# মোড ৯: টুর্নামেন্ট
elif app_mode == 9:
    st.header("⚽ টুর্নামেন্ট আমন্ত্রণপত্র ও নিয়মাবলী জেনারেটর")
    
    t_name = st.text_input("টুর্নামেন্টের নাম", "দিঘীরপাড় প্রিমিয়ার লিগ ক্রিকেট টুর্নামেন্ট - ২০২৬")
    t_date = st.text_input("শুরুর তারিখ ও সময়", "১৫ ই ফেব্রুয়ারি, ২০২৬ খ্রিঃ, সকাল ১০:০০ টা")
    t_prize = st.text_input("পুরস্কারের বিবরণ", "চ্যাম্পিয়ন: ১০,০০০ টাকা + ট্রফি | রানার্সআপ: ৫,০০০ টাকা + ট্রফি")

    if st.button("⚽ টুর্নামেন্ট নোটিশ প্রিভিউ ও প্রিন্ট দেখুন"):
        st.success("✅ টুর্নামেন্ট আমন্ত্রণপত্র সম্পূর্ণ A4 পেজে প্রস্তুত!")
        
        notice_html_code = f"""
        <div style='padding: 15px; width: 100%; height: 100%; display: flex; flex-direction: column; justify-content: space-between; box-sizing: border-box; background-color: #ffffff;'>
            <div>
                <div style="text-align:center;">
                    <h2 style="color:#ff4b4b; margin:0; font-size: 24px;">🏆 টুর্নামেন্ট আমন্ত্রণপত্র ও নোটিশ 🏆</h2>
                    <h3 style="color:#0B50FA; margin:10px 0; font-size:22px;">{t_name}</h3>
                    <hr style="border:1px solid #ff4b4b; width:55%; margin: 12px auto;">
                </div>
                
                <p style="font-size:16px; line-height:2; margin-top:25px; text-align:center;">
                    সকল ক্রীড়াপ্রেমী ও দলের অবগতির জন্য জানানো যাচ্ছে যে, আগামী <b>{t_date}</b> তারিখে স্থানীয় মাঠে জমকালো আয়োজনের মাধ্যমে এই টুর্নামেন্ট শুরু হতে যাচ্ছে। আপনি বা আপনার দল এই প্রতিযোগিতায় স্বতঃস্ফূর্তভাবে অংশগ্রহণ করার জন্য আমন্ত্রিত।
                </p>
                
                <div style="background:#f8f9fa; padding:15px; border-radius:6px; border-left:5px solid #ff4b4b; margin-top:20px;">
                    <h4 style="margin:0 0 8px 0; color:#333; font-size: 16px;">🎁 আকর্ষণীয় পুরস্কারসমূহ:</h4>
                    <p style="margin:0; font-size:15px; font-weight:bold; color:red;">{t_prize}</p>
                </div>
                
                <div style="margin-top:20px;">
                    <h4 style="color:#333; margin-bottom:8px; font-size: 16px;">📋 প্রধান নিয়মাবলী:</h4>
                    <ol style="font-size:14px; line-height:1.8; margin:0; padding-left:20px;">
                        <li>ম্যাচ শুরুর নির্ধারিত সময়ের ১৫ মিনিট পূর্বে মাঠে উপস্থিত থাকতে হবে।</li>
                        <li>আম্পায়ারের সিদ্ধান্তই চূড়ান্ত সিদ্ধান্ত বলে গণ্য হবে।</li>
                        <li>খেলার মাঠে শৃঙ্খলা বজায় রাখা বাধ্যতামূলক। বিশৃঙ্খলা সৃষ্টিকারী দলকে বহিষ্কার করা হবে।</li>
                        <li>এন্ট্রি ফি জমা দিয়ে নির্দিষ্ট সময়ের মধ্যে টিম রেজিস্ট্রেশন সম্পন্ন করতে হবে।</li>
                    </ol>
                </div>
            </div>
            
            <table style="width: 100%; margin-top: 30px; font-size: 15px;">
                <tr>
                    <td><div style="border-top:1px dashed black; width: 180px; text-align: center; padding-top:8px;">আয়োজক কমিটি</div></td>
                    <td style="text-align: right;"><div style="border-top:1px solid black; width: 180px; text-align: center; padding-top:8px; font-weight:bold; display: inline-block;">প্রধান সমন্বয়ক</div></td>
                </tr>
            </table>
        </div>
        """
        print_content_html(notice_html_code, "টুর্নামেন্ট নোটিশ প্রিন্ট করুন")

# মোড ১০: অনলাইন লিংক
elif app_mode == 10:
    st.header("🔗 অনলাইন সরকারি ও প্রয়োজনীয় লিংকসমূহ")
    st.write("আপনার সাজানো ক্যাটাগরি অনুযায়ী গুরুত্বপূর্ণ সরকারি ও অনলাইন সেবার পোর্টালগুলো নিচে দেওয়া হলো:")

    tab1, tab2, tab3, tab4 = st.tabs(["🏛️ জাতীয় ও নাগরিক সেবা", "🛂 পাসপোর্ট ও ইমিগ্রেশন", "🎓 শিক্ষা ও ফলাফল", "💼 চাকরি ও অন্যান্য"])

    with tab1:
        st.subheader("জাতীয় ও নাগরিক সেবা পোর্টাল")
        st.markdown("""
        - [জাতীয় তথ্য বাতায়ন (Bangladesh National Portal)](https://www.bangladesh.gov.bd)
        - [বাংলাদেশ ফরম পোর্টাল (All Forms)](https://forms.gov.bd)
        - [জাতীয় পরিচয়পত্র সেবা (NID Portal)](https://services.nidw.gov.bd)
        - [জন্ম ও মৃত্যু নিবন্ধন (Birth & Death Registration)](https://bdris.gov.bd)
        - [ভূমি মন্ত্রণালয় ও ই-মিউটেশন (Land Services)](https://land.gov.bd)
        """)

    with tab2:
        st.subheader("পাসপোর্ট ও ইমিগ্রেশন সেবা")
        st.markdown("""
        - [ই-পাসপোর্ট অনলাইন আবেদন (E-Passport Portal)](https://www.epassport.gov.bd)
        - [অনলাইন পুলিশ ক্লিয়ারেন্স সার্টিফিকেট (Police Clearance)](https://pcc.police.gov.bd)
        - [ভিসা ভেরিফিকেশন ও তথ্য (Visa Verification)](https://www.immigrate.gov.bd)
        """)

    with tab3:
        st.subheader("শিক্ষা ও বোর্ড ফলাফল")
        st.markdown("""
        - [শিক্ষা বোর্ড ফলাফল (Education Board Results)](http://www.educationboardresults.gov.bd)
        - [জাতীয় বিশ্ববিদ্যালয় পোর্টাল (National University)](https://www.nu.ac.bd)
        - [মাধ্যমিক ও উচ্চশিক্ষা অধিদপ্তর (DSHE)](https://www.dshe.gov.bd)
        - [বিনা মূল্যের পাঠ্যপুস্তক পোর্টাল (NCTB)](http://nctb.gov.bd)
        """)

    with tab4:
        st.subheader("চাকরি, বিমা ও অন্যান্য জরুরি সেবা")
        st.markdown("""
        - [বাংলাদেশ সরকারি চাকরি পোর্টাল (Teletalk Jobs)](https://alljobs.teletalk.com.bd)
        - [বাংলাদেশ ব্যাংক (Bangladesh Bank)](https://www.bb.org.bd)
        - [জরুরি সেবা - ৯৯৯ (National Emergency Service)](https://999.gov.bd)
        """)

# মোড ১১: ছবির সাইজ পরিবর্তন
elif app_mode == 11:
    st.header("📏 ছবির সাইজ পরিবর্তন ও রিসাইজার")
    if global_file is not None:
        image = Image.open(global_file)
        st.image(image, width=200)
        width_val = st.number_input("নতুন প্রস্থ (Width)", 100, 3000, 800)
        height_val = st.number_input("নতুন উচ্চতা (Height)", 100, 3000, 600)
        if st.button("রিসাইজ করুন"):
            resized_img = image.resize((width_val, height_val))
            st.image(resized_img, caption="রিসাইজ করা ছবি")

# মোড ১২: সাদাকালো কনভার্টার
elif app_mode == 12:
    st.header("⬛ সাদাকালো (Black & White) কনভার্টার")
    if global_file is not None:
        image = Image.open(global_file).convert("L")
        st.image(image, caption="সাদাকালো ছবি", use_column_width=True)
    else:
        st.info("দয়া করে একটি ছবি আপলোড করুন।")

# মোড ১৩: ছবি ঘোরানো
elif app_mode == 13:
    st.header("🔄 ছবি ঘোরানো (Rotate & Flip)")
    if global_file is not None:
        image = Image.open(global_file)
        angle = st.selectbox("ঘোরানোর কোণ", [90, 180, 270])
        if st.button("ঘোরান"):
            rotated = image.rotate(angle, expand=True)
            st.image(rotated, caption=f"{angle}° ঘোরানো ছবি")

# মোড ১৪: ওয়াটারমার্ক
elif app_mode == 14:
    st.header("💧 ওয়াটারমার্ক যুক্ত করার টুল")
    watermark_text = st.text_input("ওয়াটারমার্কের টেক্সট", "হাসানুর কম্পিউটার স্টুডিও")
    if global_file is not None:
        image = Image.open(global_file)
        st.image(image, caption="মূল ছবি")
        st.info("ওয়াটারমার্ক যুক্ত করার অপশন প্রস্তুত।")

# মোড ১৫: পিডিএফ টেক্সট এক্সট্র্যাক্ট
elif app_mode == 15:
    st.header("📄 পিডিএফ টেক্সট এক্সট্র্যাক্ট টুল")
    if global_file is not None and global_file.name.endswith('.pdf'):
        reader = PdfReader(global_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        st.text_area("পিডিএফ থেকে প্রাপ্ত টেক্সট", text, height=300)
    else:
        st.info("দয়া করে উপরে ফাইল আপলোড অপশন থেকে একটি পিডিএফ ফাইল আপলোড করুন।")
