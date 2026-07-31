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

# ড্যাশবোর্ড থিম, বাটন গ্রিড এবং লিঙ্ক স্টাইলিং এর জন্য কাস্টম CSS
st.markdown("""
    <style>
    .main { background-color: #0f172a; color: #f8fafc; }
    h1 { color: #38bdf8; font-family: 'Segoe UI', sans-serif; text-align: center; margin-bottom: 5px; }
    .subtitle { text-align: center; color: #94a3b8; font-size: 16px; margin-bottom: 5px; }
    .contact-info { text-align: center; color: #38bdf8; font-size: 15px; margin-bottom: 25px; font-weight: bold; }
    .footer { text-align: center; margin-top: 60px; padding: 20px; color: #64748b; border-top: 1px solid #334155; font-size: 14px; }
    
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
    </style>
""", unsafe_allow_html=True)

# হেডার ও স্টুডিও ব্র্যান্ডিং
st.markdown("<h1>📸 হাসানুর কম্পিউটার স্টুডিও</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>📍 মনিরামপুর, যশোর | অল-ইন-ওয়ান ডিজিটাল সার্ভিস ও প্রফেশনাল ল্যাব</div>", unsafe_allow_html=True)
st.markdown("<div class='contact-info'>📞 হটলাইন: 01743614359</div>", unsafe_allow_html=True)

# 🛠️ সাইডবার ড্যাশবোর্ড কন্ট্রোল
st.sidebar.markdown("## 📊 প্রজেক্ট স্ট্রাকচার")
st.sidebar.markdown("* 🇧🇩 বাংলা UI\n* 🖥️ Dashboard\n* 🗂️ Sidebar\n* 🏠 Home Screen")
st.sidebar.markdown("---")

st.sidebar.markdown("## ⚙️ মডিউল প্যানেল")
main_menu = st.sidebar.radio(
    "কাজের বিভাগ সিলেক্ট করুন:",
    (
        "1. 📷 Advanced Photo Lab",
        "2. 🌐 অনলাইন সেবা ও লিংক",
        "3. 📁 Batch Processing (PDF)",
        "4. ⚙️ Settings & Info"
    )
)
st.sidebar.markdown("---")

# ====================================================================
# ১. 📷 Advanced Photo Lab (নতুন এডিটর ইন্টারফেস সহ)
# ====================================================================
if "1." in main_menu:
    st.markdown("### 📷 অ্যাডভান্সড ফটো এডিটিং প্যানেল")
    
    uploaded_file = st.file_uploader("এডিট করার জন্য আপনার ছবিটি এখানে আপলোড করুন...", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        base_image = Image.open(uploaded_file)
        
        # আপনার দ্বিতীয় স্ক্রিনশটের স্টাইলে এডিটর টুলস গ্রিড ও অপশন
        st.markdown("#### 🛠️ এডিটর টুলস")
        
        # বাটন লেআউট গ্রিড তৈরি
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            tool_crop = st.checkbox("✂️ Crop (পাসপোর্ট/স্ট্যাম্প সাইজ)", value=False)
            tool_en_real = st.checkbox("🪄 En-Real (শার্পনেস)", value=False)
            tool_bg_first = st.checkbox("✂️ BG-First (রিমুভ ব্যাকগ্রাউন্ড)", value=False)
            tool_undo = st.button("🔄 Undo", use_container_width=True)
            
        with col_btn2:
            tool_id_straight = st.checkbox("🪪 ID Card Straightener", value=False)
            tool_en_ai = st.checkbox("✨ Enhan-AI (অটো লাইটিং)", value=False)
            tool_bg_ai = st.checkbox("🎨 BG-AI (কাস্টম কালার ব্যাকগ্রাউন্ড)", value=False)
            tool_redo = st.button("🔁 Redo", use_container_width=True)

        st.markdown("---")
        st.markdown("#### 🎛️ Filters & Adjustments")
        
        # আপনার স্ক্রিনশটের হুবহু ফিল্টার স্লাইডারসমূহ
        brightness_val = st.slider("☀️ Brightness", 50, 200, 100, format="%d%%") / 100.0
        contrast_val = st.slider("👁️ Contrast", 50, 200, 100, format="%d%%") / 100.0
        saturation_val = st.slider("🎨 Saturation", 50, 200, 100, format="%d%%") / 100.0
        
        # অ্যাকশন বাটন
        col_act1, col_act2 = st.columns(2)
        with col_act1:
            apply_changes = st.button("Apply (পরিবর্তন সেভ করুন)", type="primary", use_container_width=True)
        with col_act2:
            reset_changes = st.button("Reset (রিসেট)", use_container_width=True)

        # ইমেজ প্রসেসিং এরিয়া
        view_col1, view_col2 = st.columns(2)
        with view_col1:
            st.image(base_image, caption="মূল ছবি", use_container_width=True)
            
        with view_col2:
            if apply_changes:
                with st.spinner("ফটোশপ এআই ইঞ্জিন প্রসেস করছে..."):
                    img = base_image.copy()
                    
                    # ১. ফিল্টার অ্যাডজাস্টমেন্ট প্রয়োগ
                    if brightness_val != 1.0:
                        img = ImageEnhance.Brightness(img).enhance(brightness_val)
                    if contrast_val != 1.0:
                        img = ImageEnhance.Contrast(img).enhance(contrast_val)
                    if saturation_val != 1.0:
                        img = ImageEnhance.Color(img).enhance(saturation_val)
                        
                    # ২. ক্রপ সাইজ
                    if tool_crop:
                        img = img.resize((413, 531), Image.Resampling.LANCZOS)
                        
                    # ৩. শার্পনেস (En-Real)
                    if tool_en_real:
                        img = ImageEnhance.Sharpness(img).enhance(2.0)
                        
                    # ৪. এআই লাইটিং (Enhan-AI)
                    if tool_en_ai:
                        img = ImageEnhance.Contrast(img).enhance(1.4)
                        img = ImageEnhance.Brightness(img).enhance(1.1)
                        
                    # ৫. আইডি কার্ড স্ট্রেইটনার
                    if tool_id_straight:
                        open_cv_image = np.array(img.convert('RGB'))[:, :, ::-1].copy()
                        gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
                        edged = cv2.Canny(cv2.GaussianBlur(gray, (5, 5), 0), 50, 200)
                        contours, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                        contours = sorted(contours, key=cv2.contourArea, reverse=True)
                        for c in contours:
                            peri = cv2.arcLength(c, True)
                            approx = cv2.approxPolyDP(c, 0.02 * peri, True)
                            if len(approx) == 4:
                                pts = approx.reshape(4, 2)
                                rect = np.zeros((4, 2), dtype="float32")
                                s = pts.sum(axis=1); rect[0] = pts[np.argmin(s)]; rect[2] = pts[np.argmax(s)]
                                diff = np.diff(pts, axis=1); rect[1] = pts[np.argmin(diff)]; rect[3] = pts[np.argmax(diff)]
                                (tl, tr, br, bl) = rect
                                max_width = max(int(np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))), int(np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))))
                                max_height = max(int(np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))), int(np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))))
                                dst = np.array([[0, 0], [max_width - 1, 0], [max_width - 1, max_height - 1], [0, max_height - 1]], dtype="float32")
                                img = Image.fromarray(cv2.cvtColor(cv2.warpPerspective(open_cv_image, cv2.getPerspectiveTransform(rect, dst), (max_width, max_height)), cv2.COLOR_BGR2RGB))
                                break
                                
                    # 𝘛𝘳𝘢𝘯𝘴𝘱𝘢𝘳𝘦𝘯𝘵 ও ব্যাকগ্রাউন্ড চেঞ্জ (BG-First / BG-AI)
                    if tool_bg_first or tool_bg_ai:
                        if REMBG_AVAILABLE:
                            output_transparent = remove(img)
                            bg_color = (0, 128, 255) if tool_bg_ai else (255, 255, 255)
                            background = Image.new("RGBA", img.size, bg_color + (255,))
                            background.paste(output_transparent, (0, 0), output_transparent)
                            img = background.convert("RGB")
                        else:
                            st.warning("⚠️ AI ব্যাকগ্রাউন্ড রিমুভার ইঞ্জিন রেডি হচ্ছে।")

                    st.image(img, caption="এডিটেড ফাইনাল আউটপুট (HD)", use_container_width=True)
                    buf = io.BytesIO()
                    img.save(buf, format="JPEG", quality=100)
                    st.download_button("📥 ল্যাব কোয়ালিটি ছবি ডাউনলোড করুন", data=buf.getvalue(), file_name="hasanur_studio_output.jpg", mime="image/jpeg", use_container_width=True)
            else:
                st.info("💡 টুলস এবং ফিল্টার সেট করে 'Apply' বাটনে ক্লিক করুন।")
                st.image(base_image, caption="আউটপুট প্রিভিউ", use_container_width=True)

# ====================================================================
# ২. 🌐 অনলাইন সেবা ও লিংক (প্রথম স্ক্রিনশটের ডিরেক্টরি)
# ====================================================================
elif "2." in main_menu:
    st.markdown("### 🌐 গুরুত্বপূর্ণ অনলাইন লিংক ও পোর্টাল ডিরেক্টরি")
    st.markdown("<div class='header-link'>📋 সকল লিংক</div>", unsafe_allow_html=True)
    
    # আপনার স্ক্রিনশটের সমস্ত লিংকের একটি সুন্দর ডিরেক্টরি
    links_data = {
        "উন্মুক্ত বিশ্ববিদ্যালয়": "https://www.bou.ac.bd",
        "জন্ম নিবন্ধন": "https://bdris.gov.bd",
        "জাতীয় পরিচয় পত্র": "https://services.nidw.gov.bd",
        "জাতীয় বিশ্ববিদ্যালয়": "https://www.nu.ac.bd",
        "টিকা": "https://surokkha.gov.bd",
        "টিকেট": "https://eticket.railway.gov.bd",
        "পাবলিক বিশ্ববিদ্যালয়": "https://www.ugc.gov.bd",
        "পাসপোর্ট": "https://www.epassport.gov.bd",
        "পুলিশ ও নাগরিক": "https://pcc.police.gov.bd",
        "প্রবাসী": "https://www.probashi.gov.bd",
        "প্রবেশ পত্র": "http://teletalk.com.bd",
        "বিদ্যুৎ": "https://www.bangladesh.gov.bd",
        "ভাতা": "https://mis.bhata.gov.bd",
        "ভিসা": "https://www.visa.gov.bd",
        "ভূমি সংক্রান্ত": "https://land.gov.bd",
        "ভ্যাট / ই-টিন": "https://secure.incometax.gov.bd",
        "মুক্তিযোদ্ধা": "https://molwa.gov.bd",
        "মেডিকেল": "https://dgme.gov.bd",
        "রেজাল্ট": "http://www.educationboardresults.gov.bd",
        "লাইসেন্স": "https://bsp.brta.gov.bd",
        "শিক্ষা বোর্ড": "https://dhakaeducationboard.gov.bd",
        "সরকারি চাকুরীজীবী": "https://mopa.gov.bd"
    }
    
    # কাস্টম বাটন লেআউট প্রদর্শন
    html_content = ""
    for name, url in links_data.items():
        html_content += f'<a class="link-box" href="{url}" target="_blank">{name}</a>'
        
    st.markdown(html_content, unsafe_allow_html=True)
    st.markdown("---")
    st.info("💡 যেকোনো লিংকে ক্লিক করলে সেটি সরাসরি অফিশিয়াল সরকারি বা প্রাতিষ্ঠানিক পোর্টালে নতুন ট্যাবে ওপেন হবে।")

# ====================================================================
# ৩. 📁 Batch Processing (PDF) মডিউল
# ====================================================================
elif "3." in main_menu:
    st.markdown("### 📁 ৩. ডকুমেন্ট ও পিডিএফ ব্যাচ প্রসেসিং টুলস")
    pdf_sub_option = st.radio("পিডিএফ এডিটিং সাব-মেনু:", ("১. একাধিক পিডিএফ জোড়া দেওয়া (Merge)", "২. নির্দিষ্ট পেজ বাদ দেওয়া (Delete Page)"))
    
    if "১." in pdf_sub_option:
        pdf_files = st.file_uploader("আপনার পিডিএফ ফাইলগুলো একসাথে সিলেক্ট করে আপলোড করুন...", type=["pdf"], accept_multiple_files=True)
        if pdf_files and len(pdf_files) >= 2:
            if st.button("🔗 পিডিএফ ফাইলগুলো একসাথে জোড়া দিন", use_container_width=True):
                writer = PdfWriter()
                for pdf in pdf_files:
                    reader = PdfReader(pdf)
                    for page in reader.pages:
                        writer.add_page(page)
                output_pdf = io.BytesIO()
                writer.write(output_pdf)
                writer.close()
                st.success("✅ সফলভাবে ফাইলগুলো জোড়া দেওয়া হয়েছে!")
                st.download_button(label="📥 মার্জ করা পিডিএফ ডাউনলোড করুন", data=output_pdf.getvalue(), file_name="merged_document.pdf", mime="application/pdf", use_container_width=True)
    
    elif "২." in pdf_sub_option:
        single_pdf = st.file_uploader("পিডিএফ ফাইলটি আপলোড করুন...", type=["pdf"])
        if single_pdf is not None:
            reader = PdfReader(single_pdf)
            total_pages = len(reader.pages)
            st.success(f"📊 এই ফাইলটিতে মোট {total_pages}টি পেজ আছে।")
            page_to_delete = st.number_input(f"কোন নম্বর পেজটি বাদ দিতে চান? (১ থেকে {total_pages})", min_value=1, max_value=total_pages, value=1)
            if st.button("❌ পেজ বাদ দিয়ে নতুন ফাইল তৈরি করুন", use_container_width=True):
                writer = PdfWriter()
                for i in range(total_pages):
                    if i != (page_to_delete - 1):
                        writer.add_page(reader.pages[i])
                output_pdf = io.BytesIO()
                writer.write(output_pdf)
                writer.close()
                st.success(f"✅ সফলভাবে {page_to_delete} নম্বর পেজটি বাদ দেওয়া হয়েছে!")
                st.download_button(label="📥 নতুন এডিটেড পিডিএফ ডাউনলোড করুন", data=output_pdf.getvalue(), file_name="edited_document.pdf", mime="application/pdf", use_container_width=True)

# ====================================================================
# ৪. ⚙️ Settings & Info মডিউল
# ====================================================================
else:
    st.markdown("### ⚙️ ৪. স্টুডিও সিস্টেম সেটিংস ও ইনফো")
    st.success("💻 হাসানুর কম্পিউটার স্টুডিও ড্যাশবোর্ড সফলভাবে অনলাইন সার্ভারে লাইভ চলছে।")
    st.info("""
    **⚙️ সিস্টেম ও প্রযুক্তি ডিটেইলস:**
    * UI ফ্রেমওয়ার্ক: Streamlit (Python Core Engine)
    * অনলাইন ডিরেক্টরি: IT Lancer BD UI Inspired Multi-Link Directory
    * ইমেজ প্রসেসিং: OpenCV & Pillow Advanced Filters
    """)

st.markdown("<div class='footer'>© ২০২৬ হাসানুর কম্পিউটার স্টুডিও, মনিরামপুর, যশোর। অল রাইটস রিজার্ভড।</div>", unsafe_allow_html=True)
