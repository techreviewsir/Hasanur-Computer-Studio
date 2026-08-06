import io
import cv2
import numpy as np
from PIL import Image
import streamlit as st
from pypdf import PdfReader
from datetime import date
import streamlit.components.v1 as components

try:
    from rembg import remove
    has_rembg = True
except ImportError:
    has_rembg = False

st.set_page_config(page_title="হাসানুর কম্পিউটার স্টুডিও", layout="wide")

# ==============================================================================
# মূল স্টাইল ও সার্কেল ইমেজ ডিজাইন
# ==============================================================================
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #071952, #0b2f64, #1b032d, #381123);
        background-attachment: fixed;
        color: #ffffff;
    }
    section[data-testid="stSidebar"] {
        background-color: #0b132b;
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
        color: white;
    }
    .studio-header p {
        font-size: 14px;
        margin: 4px 0;
        line-height: 1.5;
        color: white;
    }
    .circle-img-container {
        display: flex;
        justify-content: center;
        margin-bottom: 15px;
    }
    .circle-img {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        object-fit: cover;
        border: 4px solid white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .service-card {
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.15);
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 15px;
        transition: 0.3s;
    }
    .service-card:hover {
        background: rgba(255, 255, 255, 0.15);
        transform: translateY(-3px);
    }
    .service-card a {
        color: #ffffff;
        text-decoration: none;
        font-weight: bold;
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# গিটহাব থেকে সরাসরি গোল বৃত্তের মধ্যে ছবি প্রদর্শন
# ==============================================================================
github_image_url = "https://raw.githubusercontent.com/techreviewsir/Hasanur-Computer-Studio/45b0a5162b89ae7aea9eebf03c27684ffa636bec/hasanur.jpg"

st.markdown(f"""
<div class="circle-img-container">
    <img src="{github_image_url}" class="circle-img" alt="হাসানুর">
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# ইউটিউব ও ফেসবুক বাটন (হেডার কার্ডের উপরে)
# ==============================================================================
st.markdown("""
<div style="display: flex; justify-content: center; gap: 15px; flex-wrap: wrap; margin-bottom: 20px;">
    <a href="https://www.youtube.com/@hasanurcomputerstudio" target="_blank" style="background-color: #FF0000; color: white; padding: 10px 20px; border-radius: 25px; text-decoration: none; font-weight: bold; font-size: 14px; box-shadow: 0 4px 10px rgba(0,0,0,0.3);">
        🔴 ইউটিউব চ্যানেল ভিজিট করুন
    </a>
    <a href="https://www.facebook.com/hasanurcomputerstudio" target="_blank" style="background-color: #1877F2; color: white; padding: 10px 20px; border-radius: 25px; text-decoration: none; font-weight: bold; font-size: 14px; box-shadow: 0 4px 10px rgba(0,0,0,0.3);">
        🔵 ফেসবুক পেজ ভিজিট করুন
    </a>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# হোমপেজ হেডার কার্ড
# ==============================================================================
st.markdown("""
<div class="studio-header">
    <div style="background: rgba(255,255,255,0.15); padding: 18px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.3);">
        <h1 style="margin: 0 0 6px 0;">হাসানুর কম্পিউটার স্টুডিও</h1>
        <p style="margin: 3px 0;"><b>ঠিকানা:</b> গালদা, তালতলা বাজার, মণিরামপুর, যশোর</p>
        <p style="margin: 3px 0;"><b>মোবাইল:</b> ০১৭৪৩-৬১৪৩৫৯</p>
        <hr style="border: 0.5px solid rgba(255,255,255,0.3); width: 80%; margin: 12px auto;">
        <p style="margin: 0; font-size: 13px; font-weight: 500;">সকল ধরনের কম্পিউটার, ডিজাইন ও অনলাইন সার্ভিসের অল-ইন-ওয়ান মাস্টার ড্যাশবোর্ড</p>
    </div>
</div>
""", unsafe_allow_html=True)

# অন্যান্য কাজের জন্য ফাইল আপলোডার
global_file = st.file_uploader("এডিটিং বা কাজের জন্য ছবি বা পিডিএফ ফাইল আপলোড করুন", type=["jpg", "jpeg", "png", "pdf"])

st.markdown("---")

if 'app_mode' not in st.session_state:
    st.session_state.app_mode = 6

st.sidebar.header("⚙️ টুলস ও মেনুবার")

menu_dict = {
    1: ("✨ ইমেজ ব্রাইটনেস ও কালার এডিটর", "ছবির আলো ও ব্রাইটনেস ঠিক করুন"),
    2: ("🎨 স্টুডিও ব্যাকগ্রাউন্ড রিমুভ ও কালার", "পাসপোর্ট ছবির ব্যাকগ্রাউন্ড পরিবর্তন"),
    3: ("🆔 আইডি কার্ড ক্রপ ও সোজা করার টুল", "আইডি কার্ড ক্রপ করুন"),
    4: ("🛂 পাসপোর্ট সাইজ ছবি শিট তৈরি (৪ কপি)", "এক ক্লিকে ৪ কপি ছবি তৈরি"),
    5: ("🌐 অনলাইন ও সরকারি সেবা কর্নার", "জরুরি অনলাইন সার্ভিসসমূহ")
}

selected_menu = st.sidebar.selectbox(
    "ফিচার সিলেক্ট করুন:", 
    options=list(menu_dict.keys()), 
    format_func=lambda x: menu_dict[x][0]
)

st.session_state.app_mode = selected_menu

# ==============================================================================
# মেনু ৫: অনলাইন ও সরকারি সেবা কর্নার (স্ক্রিনশট ভিত্তিক লিংক ও ফিচারসমূহ)
# ==============================================================================
if st.session_state.app_mode == 5:
    st.header("🌐 গুরুত্বপূর্ণ অনলাইন ও সরকারি সেবা কর্নার")
    st.write("নিচের সার্ভিসগুলো থেকে আপনার প্রয়োজনীয় লিঙ্কে প্রবেশ করুন:")

    services = [
        # স্ক্রিনশট ১ ও ২ (ইকমার্স ও ফুড ডেলিভারি)
        ("📚 রকমারি বই কেনা", "https://www.rokomari.com"),
        ("🛒 চালডাল অনলাইন বাজার", "https://chaldal.com"),
        ("📦 পিকাবু ইলেকট্রনিক্স স্টোর", "https://www.pickaboo.com"),
        ("🍔 ফুডপান্ডা ফুড ডেলিভারি", "https://www.foodpanda.com.bd"),
        ("🏍️ পাঠাও রাইড ও ডেলিভারি", "https://pathao.com"),
        ("🎟️ সহজ টিকিট বুকিং", "https://www.shohoz.com"),
        
        # স্ক্রিনশট ৩ (মেডিকেল ও টেক স্পেকস)
        ("📱 মোবাইলডকান মোবাইল দাম", "https://www.mobiledokan.co"),
        ("📊 জিএসএমএরেনা মোবাইল স্পেকস", "https://www.gsmarena.com"),
        ("💊 মেডেক্স মেডিসিন ইনফো", "https://medex.com.bd"),

        # স্ক্রিনশট ৪ (সরকারি ও ট্র্যাকিং সেবা)
        ("📮 ডাক বিভাগ পার্সেল ট্র্যাকিং", "http://114.130.43.163/tracktrace/"),
        ("📞 বিটিআরসি IMEI চেক", "https://www.btrc.gov.bd"),
        ("🤝 প্রবাসী কল্যাণ সেবা", "https://www.probashi.gov.bd"),
        ("🏦 বাংলাদেশ ব্যাংক", "https://www.bb.org.bd"),
        ("🌾 ডিজিটাল ভূমি সেবা", "https://land.gov.bd"),
        ("🛍️ দারাজ অনলাইন শপিং", "https://www.daraz.com.bd"),

        # স্ক্রিনশট ৫ (শিক্ষা ও ফাইন্যান্স)
        ("🎓 জগন্নাথ বিশ্ববিদ্যালয় প্রবেশপত্র", "https://jnu.ac.bd"),
        ("🛂 ই-পাসপোর্ট আবেদন", "https://www.epassport.gov.bd"),
        ("💵 ই-চালান সরকারি ফি প্রদান", "https://echalan.gov.bd"),
        ("🏠 ভূমি উন্নয়ন কর হিসাব", "https://ldtax.gov.bd"),
        ("🏛️ সরকারি চাকরি পোর্টাল", "http://www.dpp.gov.bd"),
        ("🇧🇩 বাংলাদেশ জাতীয় তথ্য বাতায়ন", "https://bangladesh.gov.bd"),

        # স্ক্রিনশট ৬ (নোটিশ ও মেডিকেল অ্যাপয়েন্টমেন্ট)
        ("🏥 কাতার মেডিকেল অ্যাপয়েন্টমেন্ট", "https://www.qatarvisacenter.com"),
        ("📜 এইচএসসি রেজাল্ট কুমিল্লা নম্বরসহ", "http://www.comillaboard.gov.bd"),
        ("📢 মুক্তিযুদ্ধ মন্ত্রণালয় নোটিশ", "https://molwa.gov.bd"),
        ("📢 মুক্তিযোদ্ধা জামুকা নোটিশ", "http://jamuka.gov.bd"),
        ("🏫 মাধ্যমিক উচ্চমাধ্যমিক সকল নোটিশ", "https://dshe.gov.bd"),
        ("⚡ বিদ্যুৎ মিটারের জন্য আবেদন (নতুন)", "https://bpdb.gov.bd"),

        # স্ক্রিনশট ৭ (কর, টিসিবি ও ভূমি নকশা)
        ("💰 কর পরিশোধ", "https://nbr.gov.bd"),
        ("🌐 টিসিবি ওয়েবসাইট", "https://www.tcb.gov.bd"),
        ("🗺️ স্মার্ট ভূমি নকশা", "https://dlrms.land.gov.bd"),
        ("📝 মৃত্যু নিবন্ধনের আবেদন", "https://bdris.gov.bd"),

        # স্ক্রিনশট ৮ (ডিপ্লোমা, অনার্স ও বিদেশ সেবা)
        ("📜 কারিগরি শিক্ষা বোর্ড ডিপ্লোমা রেজাল্ট", "http://www.bteb.gov.bd"),
        ("🏥 স্কয়ার হাসপাতাল ডাক্তার সিরিয়াল", "https://www.squarehospital.com"),
        ("🎓 অনার্স ডিগ্রি বোর্ড চ্যালেঞ্জ", "https://www.nu.ac.bd"),
        ("📜 এসএসসি রেজাল্ট কুমিল্লা বোর্ড নম্বরসহ", "http://www.comillaboard.gov.bd"),
        ("✈️ সিঙ্গাপুর Arrival Card", "https://eservices.ica.gov.sg/sgarrivalcard"),
        ("🤝 মুক্তিযোদ্ধা কল্যাণ ট্রাস্ট", "https://mwkt.gov.bd"),

        # স্ক্রিনশট ৯ (ফাযিল, কাতার ভিসা ও কাতার ছুটি)
        ("📜 ফাযিল রেজাল্ট (ইসলামি আরবি বিশ্ববিদ্যালয়)", "https://iau.edu.bd"),
        ("✈️ কাতার ভিসা চেক", "https://portal.moi.gov.qa"),
        ("⏳ কাতার ছুটির মেয়াদ চেক", "https://portal.moi.gov.qa"),

        # স্ক্রিনশট ১০ (সৌদি ও জাতীয় বিশ্ববিদ্যালয়)
        ("🇸🇦 সৌদি ওকালা চেক", "https://visa.mofa.gov.sa"),
        ("🎓 রাজশাহী কলেজ ভর্তি ও ফরম ফিলআপ", "https://rc.edu.bd"),
        ("🇸🇦 সৌদি আরব মোফা চেক", "https://visa.mofa.gov.sa"),
        ("📚 জাতীয় বিশ্ববিদ্যালয় আপডেট নোটিশ", "https://www.nu.ac.bd"),
        ("📂 ৭ কলেজ রেজাল্ট আর্কাইভ", "https://colleges.nu.ac.bd"),
        ("🎓 ডিগ্রি অনার্স মাস্টার্স ফরম ফিলআপ", "https://www.nu.ac.bd"),

        # স্ক্রিনশট ১১ (ভ্যাকসিন ও উন্মুক্ত বিশ্ববিদ্যালয়)
        ("💉 টাইফয়েড-HPV টিকা নিবন্ধন", "https://vaxbd.gov.bd"),
        ("🎓 উন্মুক্ত বিশ্ববিদ্যালয় রেজাল্ট", "https://bou.ac.bd"),
        ("🩺 সৌদি-গামকা মেডিকেল রিপোর্ট", "https://www.gamca.org"),
        ("🧾 ভ্যাট রেজিস্ট্রেশন", "https://nbr.gov.bd"),
        ("🎖️ মুক্তিযোদ্ধা ই এম আই এস ডাউনলোড", "https://emis.gov.bd"),
        ("📚 প্রাথমিক ইবতেদায়ী শিক্ষা সমাপনী", "https://dpe.gov.bd")
    ]

    # গ্রিড আকারে সার্ভিস কার্ডগুলো প্রদর্শন
    cols = st.columns(3)
    for index, (title, link) in enumerate(services):
        col = cols[index % 3]
        with col:
            st.markdown(f"""
            <div class="service-card">
                <a href="{link}" target="_blank">{title}</a>
            </div>
            """, unsafe_allow_html=True)

# অন্যান্য মেনুগুলোর বেসিক লজিক (যদি ব্যবহারকারী অন্য অপশন সিলেক্ট করেন)
elif st.session_state.app_mode == 1:
    st.header("✨ ইমেজ ব্রাইটনেস ও কালার এডিটর")
    st.info("দয়া করে উপরের ফাইল আপলোডার থেকে ছবি আপলোড করুন এবং এডিট করুন।")

elif st.session_state.app_mode == 2:
    st.header("🎨 স্টুডিও ব্যাকগ্রাউন্ড রিমুভ ও কালার")
    st.info("ছবির ব্যাকগ্রাউন্ড রিমুভ করার জন্য ছবি আপলোড করুন।")

elif st.session_state.app_mode == 3:
    st.header("🆔 আইডি কার্ড ক্রপ ও সোজা করার টুল")
    st.info("আইডি কার্ডের ছবি আপলোড করে ক্রপ করুন।")

elif st.session_state.app_mode == 4:
    st.header("🛂 পাসপোর্ট সাইজ ছবি শিট তৈরি (৪ কপি)")
    st.info("পাসপোর্ট ছবি আপলোড করে ৪ কপি শিট তৈরি করুন।")
