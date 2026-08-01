import io
import cv2
import numpy as np
from PIL import Image
import streamlit as st
from pypdf import PdfReader
from datetime import date

try:
    from rembg import remove
    has_rembg = True
except ImportError:
    has_rembg = False

st.set_page_config(page_title="হাসানুর কম্পিউটার স্টুডিও", layout="wide")

# ==============================================================================
# মূল স্টাইল (প্রিন্ট এবং হেডার ডিজাইন)
# ==============================================================================
st.markdown("""
<style>
    .studio-header {
        background: linear-gradient(135deg, #0B50FA, #ff4b4b);
        padding: 25px 20px;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
    }
    .studio-header h1 {
        font-size: 26px;
        margin-bottom: 8px;
        font-weight: bold;
        color: white;
    }
    .studio-header p {
        font-size: 14px;
        margin: 4px 0;
        line-height: 1.5;
        color: white;
    }
    @media print {
        body { background: white !important; color: black !important; }
        [data-testid="stSidebar"], .studio-header, .stButton, header, footer { display: none !important; }
    }
</style>
""", unsafe_allow_html=True)

# হেডার সেকশন
st.markdown("""
<div class="studio-header">
    <div style="background: rgba(255,255,255,0.15); padding: 18px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.3);">
        <h1 style="margin: 0 0 6px 0;">🖨️ হাসানুর কম্পিউটার স্টুডিও</h1>
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
    10: ("📏 ছবির সাইজ পরিবর্তন ও রিসাইজার", "পিক্সেল অনুযায়ী সাইজ পরিবর্তন"),
    11: ("⬛ সাদাকালো (Black & White) কনভার্টার", "সাদাকালো ছবি তৈরি"),
    12: ("🔄 ছবি ঘোরানো (Rotate & Flip)", "ছবি এঙ্গেলে ঘোরানো"),
    13: ("💧 ওয়াটারমার্ক যুক্ত করার টুল", "নাম বা লোগো ওয়াটারমার্ক"),
    14: ("📄 পিডিএফ টেক্সট এক্সট্র্যাক্ট টুল", "পিডিএফ থেকে টেক্সট আলাদা করা")
}

for num, (item_name, desc) in menu_dict.items():
    if st.sidebar.button(item_name, key=f"menu_btn_{num}"):
        st.session_state.app_mode = num

app_mode = st.session_state.app_mode

# ==============================================================================
# মোড ৬: ক্যাশ মেমো / রশিদ জেনারেটর (নেটটিভ স্ট্রিমলিট ডিজাইন - কোনো কোড শো করবে না)
# ==============================================================================
if app_mode == 6:
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

    if st.button("🖨️ ক্যাশ মেমো ফাইনাল প্রিভিউ দেখুন"):
        st.success("✅ ক্যাশ মেমো সফলভাবে প্রস্তুত করা হয়েছে!")
        
        # ক্যাশ মেমোর মূল পেপার ডিজাইন (স্ট্রিমলিট কন্টেইনার দিয়ে তৈরি)
        with st.container():
            st.markdown("<div style='border: 3px solid #0B50FA; padding: 30px; border-radius: 8px; background-color: #ffffff; color: #000000;'>", unsafe_allow_html=True)
            
            # দোকানের তথ্য
            st.markdown(f"<h2 style='text-align: center; color: #0B50FA; margin-bottom: 0;'>{shop_name}</h2>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center; font-size: 13px; color: #333;'>{shop_address}</p>", unsafe_allow_html=True)
            st.markdown("<hr style='border: 1px solid #0B50FA;'>", unsafe_allow_html=True)
            st.markdown("<h3 style='text-align: center; background-color: #0B50FA; color: white; padding: 6px; border-radius: 4px;'>ক্যাশ মেমো / রসিদ</h3>", unsafe_allow_html=True)
            
            # গ্রাহক ও তারিখের তথ্য
            col_info1, col_info2 = st.columns(2)
            with col_info1:
                st.markdown(f"**গ্রাহকের নাম:** {c_name}")
                st.markdown(f"**মোবাইল নম্বর:** {c_phone}")
            with col_info2:
                st.markdown(f"<div style='text-align: right;'><b>তারিখ:</b> {date.today().strftime('%d-%m-%Y')}</div>", unsafe_allow_html=True)
            
            st.markdown("---")
            
            # টেবিল হেডার
            t_col1, t_col2, t_col3, t_col4, t_col5 = st.columns([1, 3, 2, 2, 2])
            t_col1.markdown("**ক্রমিক**")
            t_col2.markdown("**পণ্যের বিবরণ**")
            t_col3.markdown("**সিরিয়াল নম্বর**")
            t_col4.markdown("**ওয়ারেন্টি**")
            t_col5.markdown("**মূল্য (TK)**")
            st.markdown("<hr style='margin: 5px 0;'>", unsafe_allow_html=True)
            
            # টেবিল রো
            for idx, itm in enumerate(updated_items):
                r_col1, r_col2, r_col3, r_col4, r_col5 = st.columns([1, 3, 2, 2, 2])
                r_col1.write(str(idx + 1))
                r_col2.write(itm['name'])
                r_col3.write(itm['serial'])
                r_col4.write(f"{itm['has_warranty']} ({itm['warranty_period']})")
                r_col5.write(f"{itm['price']} TK")
            
            st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
            
            # মোট টাকা
            st.markdown(f"<div style='text-align: right; font-size: 16px; background-color: #f1f3f5; padding: 10px; border-radius: 5px;'><b>সর্বমোট প্রদেয় টাকা (Total): <span style='color: red; font-size: 18px;'>{total_amount} TK</span></b></div>", unsafe_allow_html=True)
            
            # স্বাক্ষর অংশ
            st.markdown("<br><br>", unsafe_allow_html=True)
            s_col1, s_col2 = st.columns(2)
            with s_col1:
                st.markdown("<p style='border-top: 1px dashed black; display: inline-block; padding-top: 4px;'>গ্রাহকের স্বাক্ষর</p>", unsafe_allow_html=True)
            with s_col2:
                st.markdown("<div style='text-align: right;'><p style='border-top: 1px solid black; display: inline-block; padding-top: 4px; font-weight: bold;'>বিক্রেতার স্বাক্ষর / সিল</p></div>", unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)

elif app_mode == 1:
    st.header("✨ ইমেজ ব্রাইটনেস ও কালার এডিটর")
    if global_file is not None:
        st.image(Image.open(global_file), use_container_width=True)
    else:
        st.info("দয়া করে ছবি আপলোড করুন।")

elif app_mode == 8:
    st.header("📜 নাগরিক সনদপত্র জেনারেটর")
    st.info("নাগরিক সনদপত্র মোড সক্রিয় আছে।")

else:
    st.header("🛠️ টুলস সেকশন")
    st.info("দয়া করে সাইডবার থেকে প্রয়োজনীয় অপশন নির্বাচন করুন।")
