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

# পেজের লেআউট এবং কাস্টম স্টাইল সেটআপ
st.set_page_config(page_title="হাসানুর কম্পিউটার স্টুডিও / Hasanur Computer Studio", layout="wide")

st.markdown("""
<style>
    /* সাইডবার সবসময় দৃশ্যমান ও বড় রাখার জন্য */
    [data-testid="stSidebar"] {
        min-width: 380px !important;
        max-width: 410px !important;
        background-color: #fcfcfc;
    }
    
    .link-box {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #ff4b4b;
        margin-bottom: 10px;
    }
    .studio-header {
        background: linear-gradient(135deg, #0B50FA, #ff4b4b);
        padding: 22px;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* সাইডবার বাটনগুলোর স্টাইল এবং হোভার (Hover) কালারিং ইফেক্ট */
    .stButton > button {
        width: 100%;
        text-align: left;
        background-color: #ffffff;
        color: #333333;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 10px 15px;
        font-weight: 600;
        font-size: 13px;
        margin-bottom: 5px;
        transition: all 0.3s ease;
        box-shadow: 0 2px 5px rgba(0,0,0,0.02);
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #0B50FA, #ff4b4b) !important;
        color: white !important;
        border-color: #0B50FA !important;
        padding-left: 20px;
        box-shadow: 0 4px 15px rgba(11, 80, 250, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# =====================================================================
# ভাষা ডিকশনারি (বাংলা এবং ইংরেজি অনুবাদ)
# =====================================================================
st.sidebar.header("🌐 ভাষা পরিবর্তন / Language Switcher")
lang = st.sidebar.selectbox("ভাষা নির্বাচন করুন / Select Language", ["বাংলা (Bengali)", "English"])

is_eng = (lang == "English")

# মাল্টি-ল্যাঙ্গুয়েজ টেক্সট ডাটাবেস
t = {
    "title": "Hasanur Computer Studio" if is_eng else "🖨️ হাসানুর কম্পিউটার স্টুডিও",
    "address": "<b>Address:</b> Dighirpar, Monirampur, Jashore | <b>Mobile:</b> 01743-614359" if is_eng else "<b>ঠিকানা:</b> দিঘীরপাড়, মনিরামপুর, যশোর | <b>মোবাইল:</b> ০১৭৪৩-৬১৪৩৫৯",
    "subtitle": "All-in-one Master Dashboard for Computer, Design & Online Services" if is_eng else "সকল ধরনের কম্পিউটার, ডিজাইন ও অনলাইন সার্ভিসের অল-ইন-ওয়ান মাস্টার ড্যাশবোর্ড",
    "upload_header": "📁 Master File Uploader" if is_eng else "📁 ফাইল আপলোড (Master File Uploader)",
    "upload_label": "Upload Image or PDF file" if is_eng else "ছবি বা পিডিএফ ফাইল আপলোড করুন",
    "menu_header": "🧭 Navigation Menu & Features" if is_eng else "🧭 নেভিগেশন মেনু ও ফিচারের কাজ",
    "services_header": "🌐 Online Government & Essential Services" if is_eng else "🌐 অনলাইন সরকারি ও জরুরি সেবা",
}

# স্টুডিওর হেডার সেকশন
st.markdown(f"""
<div class="studio-header">
    <h1>{t['title']}</h1>
    <p style="font-size: 16px; margin: 5px 0;">{t['address']}</p>
    <p style="font-size: 13px; margin: 0;">{t['subtitle']}</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# --- সেশন স্টেট ইনিশিয়ালাইজেশন ---
if 'app_mode' not in st.session_state:
    st.session_state.app_mode = 1

# --- গ্লোবাল ফাইল আপলোডার ---
st.sidebar.header(t['upload_header'])
global_file = st.sidebar.file_uploader(t['upload_label'], type=["jpg", "jpeg", "png", "pdf"])

# সাইডবার নেভিগেশন মেনু (বাংলা ও ইংরেজি ডাইনামিক নামসহ ১ থেকে ১৭ সিরিয়াল)
st.sidebar.markdown("---")
st.sidebar.header(t['menu_header'])

if is_eng:
    menu_dict = {
        1: ("✨ AI Background Remover & HD Downloader", "Remove background, change color and download HD image."),
        2: ("🎨 Custom Background Color Studio", "Set studio quality custom background color."),
        3: ("📱 Samsung S26 Ultra AI Object Editor", "Edit object and lighting using AI prompts."),
        4: ("☀️ Image Brightness & Enhancer", "Perfect image lighting and contrast."),
        5: ("🆔 ID Card Crop & Rotate Tool", "Crop ID card and rotate at specific angles."),
        6: ("🛂 Passport Size Photo Sheet (4 Copies)", "Generate 4-copy passport photo sheet in one click."),
        7: ("🎂 Age Calculator", "Accurate age and day-month calculation."),
        8: ("🧾 Shop Cash Memo / Receipt Generator", "Create customer sales receipt and cash memo."),
        9: ("🛡️ Digital Warranty Card Generator", "Create digital warranty card for products."),
        10: ("📜 Citizenship Certificate Generator", "Create union parishad citizenship certificate."),
        11: ("⚽ Tournament Invitation & Rules (Football/Cricket/Badminton)", "Create tournament notice and guidelines."),
        12: ("📏 Image Size Changer & Resizer", "Resize images according to pixel measurements."),
        13: ("⬛ Black & White Converter", "Convert color image to black and white."),
        14: ("🔄 Image Rotate & Flip", "Rotate and flip images in various angles."),
        15: ("🖼️ Add Image Border & Frame", "Add beautiful borders and frames around images."),
        16: ("💧 Watermark Adding Tool", "Add custom name or logo watermark to images."),
        17: ("📄 PDF Text & Image Extract Tool", "Extract text content from PDF files.")
    }
else:
    menu_dict = {
        1: ("✨ এআই ব্যাকগ্রাউন্ড রিমুভার ও এইচডি ডাউনলোডার", "ছবির ব্যাকগ্রাউন্ড রিমুভ ও কালার পরিবর্তন এবং ডাউনলোড।"),
        2: ("🎨 কাস্টম ব্যাকগ্রাউন্ড কালার স্টুডিও", "স্টুডিও কোয়ালিটি ব্যাকগ্রাউন্ড কালার সেট করা।"),
        3: ("📱 স্যামসাং S26 আলট্রা এআই অবজেক্ট এডিটর", "এআই প্রম্পট দিয়ে ছবির অবজেক্ট ও লাইটিং এডিট।"),
        4: ("☀️ ইমেজ ব্রাইটনেস ও এনহ্যান্সার", "ছবির আলো ও কন্ট্রাস্ট পারফেক্ট করা।"),
        5: ("🆔 আইডি কার্ড ক্রপ ও সোজা করার টুল", "আইডি কার্ড ক্রপ ও নির্দিষ্ট কোণে ঘোরানো।"),
        6: ("🛂 পাসপোর্ট সাইজ ছবি শিট তৈরি (৪ কপি)", "এক ক্লিকে ৪ কপি পাসপোর্ট ছবি শিট তৈরি।"),
        7: ("🎂 বয়স ক্যালকুলেটর (Age Calculator)", "নির্ভুল বয়স ও দিন-মাস হিসাব।"),
        8: ("🧾 দোকানের ক্যাশ মেমো / রশিদ জেনারেটর", "গ্রাহকের বিক্রয় রশিদ ও ক্যাশ মেমো তৈরি।"),
        9: ("🛡️ ডিজিটাল ওয়ারেন্টি কার্ড জেনারেটর", "পণ্যের ডিজিটাল ওয়ারেন্টি কার্ড তৈরি।"),
        10: ("📜 নাগরিক সনদ (Citizenship Certificate) জেনারেটর", "ইউনিয়ন পরিষদের নাগরিক সনদপত্র তৈরি।"),
        11: ("⚽ টুর্নামেন্ট আমন্ত্রণপত্র ও নিয়মাবলী (Badminton/Football)", "ফুটবল বা ব্যাডমিন্টন টুর্নামেন্ট নোটিশ তৈরি।"),
        12: ("📏 ছবির সাইজ পরিবর্তন ও রিসাইজার", "পিক্সেল অনুযায়ী ছবির সাইজ ছোট-বড় করা।"),
        13: ("⬛ সাদাকালো (Black & White) কনভার্টার", "কালার ছবিকে সাদাকালো করা।"),
        14: ("🔄 ছবি ঘোরানো (Rotate & Flip)", "ছবি বিভিন্ন এঙ্গেলে ঘোরানো।"),
        15: ("🖼️ ছবি বর্ডার ও ফ্রেম যুক্ত করা", "ছবির চারপাশে সুন্দর বর্ডার ও ফ্রেম দেওয়া।"),
        16: ("💧 ওয়াটারমার্ক যুক্ত করার টুল", "ছবিতে নিজের নাম বা লোগো ওয়াটারমার্ক দেওয়া।"),
        17: ("📄 পিডিএফ টেক্সট ও ছবি এক্সট্র্যাক্ট টুল", "পিডিএফ ফাইল থেকে টেক্সট আলাদা করা।")
    }

for num, (item_name, desc) in menu_dict.items():
    if st.sidebar.button(item_name):
        st.session_state.app_mode = num
    st.sidebar.markdown(f"<p style='font-size:11px; color:gray; margin-top:-5px; margin-bottom:8px;'>ℹ️ {desc}</p>", unsafe_allow_html=True)

app_mode = st.session_state.app_mode

# সাইডবারে অনলাইন টুলস / সরকারি সার্ভিস ওয়েবসাইট লিংক
st.sidebar.markdown("---")
st.sidebar.header(t['services_header'])
st.sidebar.markdown("""
- [🏛️ ইউনিয়ন ও পৌরসভা ই-সেবা পোর্টাল / Union e-Service](https://www.upservice.gov.bd/)
- [👵 বয়স্ক ও বিধবা ভাতা আবেদন / Allowance Application](https://www.mis.bhata.gov.bd/)
- [🛂 ই-পাসপোর্ট আবেদন পোর্টাল / e-Passport Portal](https://www.epassport.gov.bd/)
- [💼 বিএমইটি (BMET) অনলাইন আবেদন / BMET Portal](https://www.bmet.gov.bd/)
- [💳 বিএমইটি স্মার্ট কার্ড ডাউনলোড / Smart Card](https://www.bmet.gov.bd/)
- [🚗 ড্রাইভিং লাইসেন্স ডাউনলোড (BRTA) / Driving License](https://bsp.brta.gov.bd/)
- [📇 এনআইডি সেবা পোর্টাল / NID Services](https://services.nidw.gov.bd/)
- [📜 জন্ম ও মৃত্যু নিবন্ধন / Birth & Death Registration](https://bdris.gov.bd/)
- [🎓 শিক্ষা বোর্ড ফলাফল / Education Board Results](http://www.educationboardresults.gov.bd/)
- [💼 ই-টিন ও আয়কর পোর্টাল / e-TIN & Income Tax](https://secure.incometax.gov.bd/)
""")

# =====================================================================
# মূল ফিচারসমূহ হ্যান্ডলিং (১ থেকে ১৭)
# =====================================================================

if app_mode == 1:
    st.header("✨ " + ("AI Background Remover & HD Downloader" if is_eng else "এআই ব্যাকগ্রাউন্ড রিমুভার ও এইচডি ডাউনলোডার"))
    st.markdown("Desktop Home Page: Easily remove background and download images." if is_eng else "ডেস্কটপ হোম পেজ: এখান থেকে যেকোনো ছবির ব্যাকগ্রাউন্ড খুব সহজে রিমুভ ও ডাউনলোড করতে পারবেন।")
    
    if global_file is not None:
        file_extension = global_file.name.split('.')[-1].lower()
        if file_extension in ['jpg', 'jpeg', 'png']:
            bg_color = st.color_picker("Choose Background Color" if is_eng else "ব্যাকগ্রাউন্ডের কালার পছন্দ করুন", "#0B50FA")
            col1, col2 = st.columns(2)
            with col1:
                st.image(Image.open(global_file), use_container_width=True, caption="Original Image" if is_eng else "আসল ছবি (Original)")
            with col2:
                if st.button("Remove Background & Change Color" if is_eng else "ব্যাকগ্রাউন্ড রিমুভ ও কালার পরিবর্তন করুন"):
                    with st.spinner("Processing advanced AI edge refinement..." if is_eng else "উন্নত এআই এজ রিফাইনিং প্রসেসিং চলছে..."):
                        session = new_session("birefnet-general")
                        output_bytes = remove(global_file.getvalue(), session=session)
                        foreground_pil = Image.open(io.BytesIO(output_bytes)).convert("RGBA")
                        orig_pil = Image.open(global_file).convert("RGB").resize(foreground_pil.size)
                        
                        img_np = np.array(orig_pil).astype(np.float32) / 255.0
                        alpha_np = np.array(foreground_pil.split()[-1]).astype(np.float32) / 255.0
                        
                        refined_fg_np = FB_blur_fusion_foreground_estimator_2(img_np, alpha_np)
                        refined_fg_np = np.clip(refined_fg_np * 255, 0, 255).astype(np.uint8)
                        
                        alpha_uint8 = (alpha_np * 255).astype(np.uint8)
                        foreground = Image.fromarray(np.dstack((refined_fg_np, alpha_uint8)), "RGBA")
                        
                        hex_code = bg_color.lstrip('#')
                        bg_rgb = tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))
                        background = Image.new("RGBA", foreground.size, bg_rgb + (255,))
                        final_image = Image.alpha_composite(background, foreground).convert("RGB")
                        
                        st.image(final_image, use_container_width=True, caption=f"Background Color: {bg_color}" if is_eng else f"ব্যাকগ্রাউন্ড কালার: {bg_color}")
                        buf = io.BytesIO()
                        final_image.save(buf, format="JPEG", quality=95)
                        st.download_button("📥 Download HD Image" if is_eng else "📥 HD ছবি ডাউনলোড করুন", buf.getvalue(), "bg_removed_hd.jpg", "image/jpeg")
        else:
            st.warning("Please upload a valid image file (jpg, jpeg, png)." if is_eng else "দয়া করে একটি ছবি (jpg, jpeg, png) ফাইল আপলোড করুন।")
    else:
        st.info("👋 **Welcome!** Please select a file from the sidebar's **'Master File Uploader'** option." if is_eng else "👋 **স্বাগতম!** ছবি আপলোড করার জন্য দয়া করে বাম পাশের সাইডবারের **'ফাইল আপলোড (Master File Uploader)'** অপশন থেকে ছবি সিলেক্ট করুন।")

elif app_mode == 2:
    st.header("🎨 " + ("Custom Background Color Studio" if is_eng else "কাস্টম ব্যাকগ্রাউন্ড কালার স্টুডিও"))
    if global_file is not None:
        file_extension = global_file.name.split('.')[-1].lower()
        if file_extension in ['jpg', 'jpeg', 'png']:
            bg_color = st.color_picker("Select Studio Background Color" if is_eng else "স্টুডিও ব্যাকগ্রাউন্ড কালার নির্বাচন করুন", "#0B50FA")
            col1, col2 = st.columns(2)
            with col1:
                st.image(Image.open(global_file), use_container_width=True, caption="Original Image" if is_eng else "আসল ছবি")
            with col2:
                with st.spinner("Generating studio quality HD image..." if is_eng else "স্টুডিও কোয়ালিটি HD ছবি তৈরি হচ্ছে..."):
                    session = new_session("birefnet-general")
                    output_bytes = remove(global_file.getvalue(), session=session)
                    foreground_pil = Image.open(io.BytesIO(output_bytes)).convert("RGBA")
                    orig_pil = Image.open(global_file).convert("RGB").resize(foreground_pil.size)
                    
                    img_np = np.array(orig_pil).astype(np.float32) / 255.0
                    alpha_np = np.array(foreground_pil.split()[-1]).astype(np.float32) / 255.0
                    
                    refined_fg_np = FB_blur_fusion_foreground_estimator_2(img_np, alpha_np)
                    refined_fg_np = np.clip(refined_fg_np * 255, 0, 255).astype(np.uint8)
                    
                    alpha_uint8 = (alpha_np * 255).astype(np.uint8)
                    foreground = Image.fromarray(np.dstack((refined_fg_np, alpha_uint8)), "RGBA")
                    
                    hex_code = bg_color.lstrip('#')
                    bg_rgb = tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))
                    background = Image.new("RGBA", foreground.size, bg_rgb + (255,))
                    final_image = Image.alpha_composite(background, foreground).convert("RGB")
                    
                    st.image(final_image, use_container_width=True, caption=f"Studio Background Color: {bg_color}" if is_eng else f"স্টুডিও ব্যাকগ্রাউন্ড কালার: {bg_color}")
                    buf = io.BytesIO()
                    final_image.save(buf, format="JPEG", quality=95)
                    st.download_button("Download Studio HD Image" if is_eng else "স্টুডিও HD ছবি ডাউনলোড করুন", buf.getvalue(), "studio_hd.jpg", "image/jpeg")
    else:
        st.warning("Please upload an image from the sidebar." if is_eng else "দয়া করে বাম পাশের সাইডবার থেকে একটি ছবি আপলোড করুন।")

elif app_mode == 3:
    st.header("📱 " + ("Samsung S26 Ultra AI Object Editor" if is_eng else "স্যামসাং S26 আলট্রা এআই অবজেক্ট ও প্রম্পট এডিটর"))
    if global_file is not None:
        file_extension = global_file.name.split('.')[-1].lower()
        if file_extension in ['jpg', 'jpeg', 'png']:
            col1, col2 = st.columns(2)
            with col1:
                st.image(Image.open(global_file), use_container_width=True, caption="Original Image" if is_eng else "মূল ছবি")
            with col2:
                prompt = st.text_input("Enter AI Command" if is_eng else "এআই কমান্ড লিখুন", "Enhance and refine object lighting")
                if st.button("Start AI Processing" if is_eng else "এআই প্রসেসিং শুরু করুন"):
                    with st.spinner(f"S26 Ultra AI engine processing '{prompt}'..." if is_eng else f"S26 আলট্রা এআই ইঞ্জিন '{prompt}' নিয়ে কাজ করছে..."):
                        img = Image.open(global_file).convert("RGB")
                        img_np = np.array(img)
                        processed_np = cv2.detailEnhance(img_np, sigma_s=10, sigma_r=0.15)
                        final_ai_img = Image.fromarray(processed_np)
                        
                        st.image(final_ai_img, use_container_width=True, caption=f"AI Edit Output: {prompt}" if is_eng else f"এআই এডিট আউটপুট: {prompt}")
                        buf = io.BytesIO()
                        final_ai_img.save(buf, format="JPEG", quality=95)
                        st.download_button("Download AI Edited Image" if is_eng else "এআই এডিটেড ছবি ডাউনলোড করুন", buf.getvalue(), "s26_ai_edited.jpg", "image/jpeg")
    else:
        st.warning("Please upload an image from the sidebar." if is_eng else "দয়া করে বাম পাশের সাইডবার থেকে একটি ছবি আপলোড করুন।")

elif app_mode == 4:
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
            st.image(enhanced_image, use_container_width=True, caption="Enhanced Image" if is_eng else "এনহ্যান্স করা ছবি")
            buf = io.BytesIO()
            enhanced_image.save(buf, format="JPEG", quality=95)
            st.download_button("Download" if is_eng else "ডাউনলোড করুন", buf.getvalue(), "enhanced.jpg", "image/jpeg")
    else:
        st.warning("Please upload an image from the sidebar." if is_eng else "দয়া করে বাম পাশের সাইডবার থেকে একটি ছবি আপলোড করুন।")

elif app_mode == 5:
    st.header("🆔 " + ("ID Card Crop & Rotate Tool" if is_eng else "আইডি কার্ড ক্রপ ও রোটেশন টুল"))
    if global_file is not None:
        file_extension = global_file.name.split('.')[-1].lower()
        if file_extension in ['jpg', 'jpeg', 'png']:
            img = Image.open(global_file)
            rotation = st.slider("Rotate Image" if is_eng else "ছবি ঘোরান", -180, 180, 0)
            if rotation != 0:
                img = img.rotate(rotation, expand=True)
            st.image(img, use_container_width=True, caption="Preview" if is_eng else "প্রিভিউ")
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=95)
            st.download_button("Download ID Card" if is_eng else "আইডি কার্ড ডাউনলোড", buf.getvalue(), "id_card.jpg", "image/jpeg")
    else:
        st.warning("Please upload an image from the sidebar." if is_eng else "দয়া করে বাম পাশের সাইডবার থেকে একটি ছবি আপলোড করুন।")

elif app_mode == 6:
    st.header("🛂 " + ("Passport Size Photo Sheet (4 Copies)" if is_eng else "পাসপোর্ট সাইজ ফটো শিট (৪ কপি)"))
    if global_file is not None:
        file_extension = global_file.name.split('.')[-1].lower()
        if file_extension in ['jpg', 'jpeg', 'png']:
            img = Image.open(global_file).resize((300, 350))
            sheet = Image.new("RGB", (650, 750), (255, 255, 255))
            sheet.paste(img, (25, 25))
            sheet.paste(img, (335, 25))
            sheet.paste(img, (25, 385))
            sheet.paste(img, (335, 385))
            st.image(sheet, use_container_width=True, caption="4-Copy Sheet" if is_eng else "৪ কপি শিট")
            buf = io.BytesIO()
            sheet.save(buf, format="JPEG", quality=95)
            st.download_button("Download Passport Sheet" if is_eng else "পাসপোর্ট শিট ডাউনলোড", buf.getvalue(), "passport_sheet.jpg", "image/jpeg")
    else:
        st.warning("Please upload an image from the sidebar." if is_eng else "দয়া করে বাম পাশের সাইডবার থেকে একটি ছবি আপলোড করুন।")

elif app_mode == 7:
    st.header("🎂 " + ("Age Calculator" if is_eng else "নিখুঁত বয়স ক্যালকুলেটর টুল"))
    col1, col2 = st.columns(2)
    with col1:
        birth_date = st.date_input("Select Birth Date" if is_eng else "জন্ম তারিখ নির্বাচন করুন", date(1995, 1, 1))
    with col2:
        target_date = st.date_input("Calculate Age Up To" if is_eng else "যে তারিখ পর্যন্ত বয়স বের করতে চান", date.today())
        
    if st.button("Calculate Age" if is_eng else "বয়স হিসাব করুন"):
        if birth_date > target_date:
            st.error("Birth date cannot be in the future!" if is_eng else "জন্ম তারিখ বর্তমান বা ভবিষ্যতের তারিখ হতে পারে না!")
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
                
            st.success(f"🎉 Your Age: **{years} Years, {months} Months, and {days} Days**" if is_eng else f"🎉 আপনার বয়স: **{years} বছর, {months} মাস, এবং {days} দিন**")

elif app_mode == 8:
    st.header("🧾 " + ("Shop Cash Memo / Receipt Generator" if is_eng else "দোকানের বিক্রয় রশিদ (Cash Memo) জেনারেটর"))
    cust_name = st.text_input("Customer Name" if is_eng else "গ্রাহকের নাম", "Md. Rahim Uddin")
    cust_phone = st.text_input("Customer Phone Number" if is_eng else "গ্রাহকের মোবাইল নম্বর", "01700000000")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        item1 = st.text_input("Item 1 Name" if is_eng else "পণ্যের নাম ১", "Lamination & Print")
        price1 = st.number_input("Item 1 Price (TK)" if is_eng else "দাম ১ (টাকা)", 0, 10000, 150)
    with col2:
        item2 = st.text_input("Item 2 Name" if is_eng else "পণ্যের নাম ২", "Passport Size Photo")
        price2 = st.number_input("Item 2 Price (TK)" if is_eng else "দাম ২ (টাকা)", 0, 10000, 100)
    with col3:
        item3 = st.text_input("Item 3 Name" if is_eng else "পণ্যের নাম ৩", "Online Application Fee")
        price3 = st.number_input("Item 3 Price (TK)" if is_eng else "দাম ৩ (টাকা)", 0, 10000, 200)
        
    total_amount = price1 + price2 + price3
    
    if st.button("Generate Cash Memo & Print Preview" if is_eng else "ক্যাশ মেমো তৈরি ও প্রিন্ট প্রিভিউ"):
        st.markdown("---")
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
            <p style="text-align: center; margin-top: 20px; font-size: 12px;">Thank you for using our service!</p>
        </div>
        """
        st.markdown(memo_html, unsafe_allow_html=True)
        st.success("Cash memo generated successfully!" if is_eng else "ক্যাশ মেমো সফলভাবে তৈরি হয়েছে!")

elif app_mode == 9:
    st.header("🛡️ " + ("Digital Warranty Card Generator" if is_eng else "পণ্যের ডিজিটাল ওয়ারেন্টি কার্ড জেনারেটর"))
    p_name = st.text_input("Product Name & Model" if is_eng else "পণ্যের নাম ও মডেল", "HP LaserJet Pro Printer")
    buyer_name = st.text_input("Buyer Name" if is_eng else "ক্রেতার নাম", "Md. Hasan Ali")
    w_period = st.selectbox("Warranty Period" if is_eng else "ওয়ারেন্টি মেয়াদ", ["1 Year" if is_eng else "১ বছর", "2 Years" if is_eng else "২ বছর", "3 Years" if is_eng else "৩ বছর", "6 Months" if is_eng else "৬ মাস", "Lifetime" if is_eng else "লাইফটাইম"])
    
    if st.button("Generate Warranty Card" if is_eng else "ওয়ারেন্টি কার্ড জেনারেট করুন"):
        card_html = f"""
        <div style="background: linear-gradient(135deg, #1e3c72, #2a5298); padding: 30px; border-radius: 15px; color: white; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
            <h2 style="text-align: center; margin:0; letter-spacing: 2px;">WARRANTY CARD</h2>
            <p style="text-align: center; font-size: 13px; margin-top: 2px;">Hasanur Computer Studio</p>
            <hr style="border-color: rgba(255,255,255,0.3);">
            <p><b>Product:</b> {p_name}</p>
            <p><b>Buyer Name:</b> {buyer_name}</p>
            <p><b>Warranty Period:</b> {w_period}</p>
            <p><b>Purchase Date:</b> {date.today().strftime('%d-%m-%Y')}</p>
            <div style="margin-top: 25px; display: flex; justify-content: space-between; font-size: 12px;">
                <span>Stamp & Seal</span>
                <span>Authorized Signature</span>
            </div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)
        st.success("Warranty card generated successfully!" if is_eng else "ওয়ারেন্টি কার্ড সফলভাবে তৈরি করা হয়েছে!")

elif app_mode == 10:
    st.header("📜 " + ("Citizenship Certificate Generator" if is_eng else "নাগরিক সনদপত্র (Citizenship Certificate) প্রস্তুতকারক"))
    col1, col2 = st.columns(2)
    with col1:
        c_name = st.text_input("Applicant Name" if is_eng else "আবেদনকারীর নাম", "Md. Al-Amin Hossain")
        c_father = st.text_input("Father's Name" if is_eng else "পিতার নাম", "Md. Abdul Jabbar")
        c_mother = st.text_input("Mother's Name" if is_eng else "মাতার নাম", "Mst. Ayesha Begum")
    with col2:
        c_village = st.text_input("Village / Area" if is_eng else "গ্রাম / পাড়া", "Dighirpar")
        c_union = st.text_input("Union / Municipality" if is_eng else "ইউনিয়ন / পৌরসভা", "No. 2 Jhapa Union Parishad")
        c_upazila = st.text_input("Upazila & District" if is_eng else "উপজেলা ও জেলা", "Monirampur, Jashore")
        
    if st.button("Preview Citizenship Certificate" if is_eng else "নাগরিক সনদ প্রিভিউ করুন"):
        cert_html = f"""
        <div style="background: #ffffff; padding: 40px; border: 5px double #1e3c72; border-radius: 10px; color: #000;">
            <div style="text-align: center;">
                <h3 style="margin: 0; color: #1e3c72;">Government of the People's Republic of Bangladesh</h3>
                <h2 style="margin: 5px 0; color: #d9534f;">{c_union}</h2>
                <p style="margin: 0; font-size: 14px;">Upazila: {c_upazila}</p>
                <hr style="width: 50%; border: 1px solid #1e3c72; margin: 15px auto;">
                <h1 style="background: #1e3c72; color: white; display: inline-block; padding: 5px 30px; border-radius: 5px; font-size: 20px;">Citizenship Certificate</h1>
            </div>
            <p style="font-size: 16px; line-height: 1.8; margin-top: 30px; text-align: justify;">
                This is to certify that <b>{c_name}</b>, Father: <b>{c_father}</b>, Mother: <b>{c_mother}</b>, Village: <b>{c_village}</b>, Upazila: <b>{c_upazila}</b> is a permanent resident and citizen of Bangladesh. His character and reputation are satisfactory.
            </p>
            <div style="margin-top: 80px; display: flex; justify-content: space-between; font-size: 14px;">
                <div style="text-align: center; border-top: 1px solid #000; padding-top: 5px; width: 200px;">UP Secretary</div>
                <div style="text-align: center; border-top: 1px solid #000; padding-top: 5px; width: 200px;">Chairman<br>{c_union}</div>
            </div>
        </div>
        """
        st.markdown(cert_html, unsafe_allow_html=True)
        st.success("Citizenship certificate generated!" if is_eng else "নাগরিক সনদ তৈরি সম্পন্ন!")

elif app_mode == 11:
    st.header("⚽ " + ("Tournament Invitation & Rules Generator (Football/Badminton)" if is_eng else "ব্যাডমিন্টন ও ফুটবল টুর্নামেন্ট আমন্ত্রণপত্র ও নিয়মাবলী জেনারেটর"))
    t_type = st.selectbox("Select Tournament Type" if is_eng else "টুর্নামেন্টের ধরণ নির্বাচন করুন", ["Football Tournament" if is_eng else "ফুটবল টুর্নামেন্ট", "Badminton Tournament" if is_eng else "ব্যাডমিন্টন টুর্নামেন্ট"])
    
    col1, col2 = st.columns(2)
    with col1:
        t_name = st.text_input("Tournament Name" if is_eng else "টুর্নামেন্টের নাম", "Victory Day Premier League-2026" if "Football" in t_type or "ফুটবল" in t_type else "Winter Badminton Tournament-2026")
        t_organizer = st.text_input("Organizer Club / Committee" if is_eng else "আয়োজক কমিটি / ক্লাব", "Dighirpar Youth Society")
        t_venue = st.text_input("Venue" if is_eng else "খেলার স্থান", "Dighirpar Govt Primary School Playground")
    with col2:
        t_date = st.text_input("Date & Time" if is_eng else "খেলার তারিখ ও সময়", "15 February, 2026 | 3:00 PM")
        t_fee = st.text_input("Entry Fee (TK)" if is_eng else "এন্ট্রি ফি (টাকা)", "1000 TK per team")
        t_prize = st.text_input("Prizes" if is_eng else "পুরস্কার", "Champion: 5000 TK + Trophy / Runner-up: 3000 TK + Trophy")

    if st.button("Generate Invitation & Rules" if is_eng else "আমন্ত্রণপত্র ও নিয়মাবলী তৈরি করুন"):
        st.markdown("---")
        if "Football" in t_type or "ফুটবল" in t_type:
            rules_list = """
            <ol>
                <li>Each team will have 7 players (3 substitutes, total 10 players).</li>
                <li>Match duration: 20 minutes each half, total 40 minutes (5 min half-time).</li>
                <li>Referee and organizing committee decision will be final.</li>
                <li>Discipline must be maintained on the field.</li>
            </ol>
            """ if is_eng else """
            <ol>
                <li>প্রতি দলে খেলোয়াড়ের সংখ্যা হবে ৭ জন (৩ জন অতিরিক্তসহ সর্বমোট ১০ জন)।</li>
                <li>ম্যাচের সময়কাল: ২০ মিনিট করে মোট ৪০ মিনিট (হাফটাইম ৫ মিনিট)।</li>
                <li>রেফারি ও আয়োজক কমিটির সিদ্ধান্তই চূড়ান্ত বলে গণ্য হবে।</li>
                <li>খেলার মাঠে শৃঙ্খলা বজায় রাখতে হবে, কোনো অনিয়ম করলে দল বাতিল করা হবে।</li>
            </ol>
            """
            theme_color = "#28a745"
            icon = "⚽"
        else:
            rules_list = """
            <ol>
                <li>Matches will be played in Doubles or Singles format.</li>
                <li>Knockout format (Best of 3 sets, 21 points).</li>
                <li>Players must bring their own rackets; shuttlecocks provided by committee.</li>
                <li>Players must report 10 minutes prior to match time.</li>
            </ol>
            """ if is_eng else """
            <ol>
                <li>খেলা ডাবলস (Double) অথবা সিঙ্গেলস (Single) ফরম্যাটে অনুষ্ঠিত হবে।</li>
                <li>নকআউট পদ্ধতিতে ম্যাচগুলো পরিচালিত হবে (২১ পয়েন্টের বেস্ট অব থ্রি সেট)।</li>
                <li>খেলোয়াড়দের নিজস্ব র‍্যাকেট সাথে আনতে হবে, শাটলকক কমিটি থেকে সরবরাহ করা হবে।</li>
                <li>নির্ধারিত সময়ের ১০ মিনিট পূর্বে মাঠে উপস্থিত থাকতে হবে।</li>
            </ol>
            """
            theme_color = "#007bff"
            icon = "🏸"

        tourn_html = f"""
        <div style="background: #ffffff; padding: 35px; border-radius: 12px; border: 4px solid {theme_color}; color: #000; font-family: Arial, sans-serif;">
            <div style="text-align: center;">
                <span style="font-size: 40px;">{icon}</span>
                <h2 style="margin: 5px 0; color: {theme_color};">{t_name}</h2>
                <p style="margin: 0; font-size: 15px; font-weight: bold;">Organized by: {t_organizer}</p>
                <hr style="width: 60%; border: 1px solid {theme_color}; margin: 15px auto;">
                <h3 style="background: {theme_color}; color: white; display: inline-block; padding: 5px 20px; border-radius: 5px; font-size: 16px;">Tournament Invitation & Rules</h3>
            </div>
            
            <div style="margin-top: 20px; font-size: 15px; line-height: 1.6;">
                <p><b>Date & Time:</b> {t_date}</p>
                <p><b>Venue:</b> {t_venue}</p>
                <p><b>Entry Fee:</b> {t_fee}</p>
                <p><b>Prizes:</b> {t_prize}</p>
            </div>
            
            <div style="margin-top: 20px; background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid {theme_color};">
                <h4 style="margin-top: 0; color: {theme_color};">⚠️ Special Tournament Rules:</h4>
                {rules_list}
            </div>
            
            <p style="text-align: center; margin-top: 25px; font-weight: bold; color: #333;">Welcome all sports enthusiasts and teams!</p>
            
            <div style="margin-top: 50px; display: flex; justify-content: space-between; font-size: 14px;">
                <div style="text-align: center; border-top: 1px solid #000; padding-top: 5px; width: 180px;">Tournament Director</div>
                <div style="text-align: center; border-top: 1px solid #000; padding-top: 5px; width: 180px;">Chief Coordinator</div>
            </div>
        </div>
        """
        st.markdown(tourn_html, unsafe_allow_html=True)
        st.success("Tournament invitation generated successfully!" if is_eng else "টুর্নামেন্টের আমন্ত্রণপত্র ও নিয়মাবলী সফলভাবে তৈরি হয়েছে!")

elif app_mode == 12:
    st.header("📏 " + ("Image Size Changer & Resizer" if is_eng else "ছবির সাইজ পরিবর্তন"))
    if global_file is not None:
        file_extension = global_file.name.split('.')[-1].lower()
        if file_extension in ['jpg', 'jpeg', 'png']:
            img = Image.open(global_file)
            width = st.slider("Width" if is_eng else "প্রস্থ", 100, 3000, img.width)
            height = st.slider("Height" if is_eng else "উচ্চতা", 100, 3000, img.height)
            resized = img.resize((width, height))
            st.image(resized, use_container_width=True)
            buf = io.BytesIO()
            resized.save(buf, format="JPEG", quality=95)
            st.download_button("Download Resized Image" if is_eng else "রিসাইজ ছবি ডাউনলোড", buf.getvalue(), "resized.jpg", "image/jpeg")
    else:
        st.warning("Please upload an image from the sidebar." if is_eng else "দয়া করে বাম পাশের সাইডবার থেকে একটি ছবি আপলোড করুন।")

elif app_mode == 13:
    st.header("⬛ " + ("Black & White Converter" if is_eng else "সাদাকালো ছবি কনভার্টার"))
    if global_file is not None:
        file_extension = global_file.name.split('.')[-1].lower()
        if file_extension in ['jpg', 'jpeg', 'png']:
            img = Image.open(global_file).convert("L")
            st.image(img, use_container_width=True)
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=95)
            st.download_button("Download B&W Image" if is_eng else "সাদাকালো ছবি ডাউনলোড", buf.getvalue(), "bw.jpg", "image/jpeg")
    else:
        st.warning("Please upload an image from the sidebar." if is_eng else "দয়া করে বাম পাশের সাইডবার থেকে একটি ছবি আপলোড করুন।")

elif app_mode == 14:
    st.header("🔄 " + ("Image Rotate & Flip" if is_eng else "ছবি ঘোরানোর টুল"))
    if global_file is not None:
        file_extension = global_file.name.split('.')[-1].lower()
        if file_extension in ['jpg', 'jpeg', 'png']:
            img = Image.open(global_file)
            rot = st.selectbox("Rotation Angle" if is_eng else "ঘূর্ণন কোণ", [0, 90, 180, 270])
            if rot > 0:
                img = img.rotate(rot, expand=True)
            st.image(img, use_container_width=True)
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=95)
            st.download_button("Download Rotated Image" if is_eng else "ঘোরানো ছবি ডাউনলোড", buf.getvalue(), "rotated.jpg", "image/jpeg")
    else:
        st.warning("Please upload an image from the sidebar." if is_eng else "দয়া করে বাম পাশের সাইডবার থেকে একটি ছবি আপলোড করুন।")

elif app_mode == 15:
    st.header("🖼️ " + ("Add Image Border & Frame" if is_eng else "বর্ডার ও ফ্রেম যুক্ত করুন"))
    if global_file is not None:
        file_extension = global_file.name.split('.')[-1].lower()
        if file_extension in ['jpg', 'jpeg', 'png']:
            img = Image.open(global_file)
            bordered = ImageOps.expand(img, border=20, fill='black')
            st.image(bordered, use_container_width=True)
            buf = io.BytesIO()
            bordered.save(buf, format="JPEG", quality=95)
            st.download_button("Download Bordered Image" if is_eng else "বর্ডারযুক্ত ছবি ডাউনলোড", buf.getvalue(), "bordered.jpg", "image/jpeg")
    else:
        st.warning("Please upload an image from the sidebar." if is_eng else "দয়া করে বাম পাশের সাইডবার থেকে একটি ছবি আপলোড করুন।")

elif app_mode == 16:
    st.header("💧 " + ("Watermark Adding Tool" if is_eng else "টেক্সট ওয়াটারমার্ক টুল"))
    if global_file is not None:
        file_extension = global_file.name.split('.')[-1].lower()
        if file_extension in ['jpg', 'jpeg', 'png']:
            img = Image.open(global_file)
            text = st.text_input("Watermark Text" if is_eng else "ওয়াটারমার্ক টেক্সট", "Hasanur Studio")
            st.image(img, use_container_width=True)
            st.success(f"Watermark '{text}' prepared." if is_eng else f"'{text}' ওয়াটারমার্ক প্রস্তুত করা হয়েছে।")
    else:
        st.warning("Please upload an image from the sidebar." if is_eng else "দয়া করে বাম পাশের সাইডবার থেকে একটি ছবি আপলোড করুন।")

elif app_mode == 17:
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
                if all_text.strip():
                    st.text_area("PDF Text:" if is_eng else "পিডিএফ টেক্সট:", all_text, height=200)
                else:
                    st.info("Scanned PDF file." if is_eng else "স্ক্যানড পিডিএফ ফাইল।")
            except Exception as e:
                st.error(f"Error: {e}" if is_eng else f"ত্রুটি: {e}")
        else:
            st.warning("Please upload a PDF file from the sidebar." if is_eng else "দয়া করে বাম পাশের সাইডবার থেকে একটি পিডিএফ ফাইল আপলোড করুন।")
    else:
        st.warning("Please upload a PDF file from the sidebar." if is_eng else "দয়া করে বাম পাশের সাইডবার থেকে একটি পিডিএফ ফাইল আপলোড করুন।")

# =========================================================================
# ওয়েবসাইট ডিরেক্টরি সেকশন
# =========================================================================
st.markdown("---")
st.header("🌐 " + ("Required Government & Online Service Directory" if is_eng else "প্রয়োজনীয় সরকারি ও অনলাইন সার্ভিস ওয়েবসাইট ডিরেক্টরি"))

col_a, col_b = st.columns(2)

with col_a:
    if is_eng:
        st.markdown("""
        <div class="link-box">
            <h4>🏛️ 1. Union & Municipality e-Service Portal</h4>
            <p><b>Work:</b> Citizenship, Inheritance certificates and Trade license applications.</p>
            <a href="https://www.upservice.gov.bd/" target="_blank">🔗 Visit e-Service Portal</a>
        </div>
        <div class="link-box">
            <h4>👵 2. Old Age & Widow Allowance Application</h4>
            <p><b>Work:</b> Online application and verification for allowances.</p>
            <a href="https://www.mis.bhata.gov.bd/" target="_blank">🔗 Visit Allowance Portal</a>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="link-box">
            <h4>🏛️ ১. ইউনিয়ন ও পৌরসভা ই-সেবা পোর্টাল</h4>
            <p><b>কাজ:</b> নাগরিক সনদ, ওয়ারিশান সনদ ও ট্রেড লাইসেন্স আবেদন।</p>
            <a href="https://www.upservice.gov.bd/" target="_blank">🔗 ই-সেবা পোর্টাল ভিজিট করুন</a>
        </div>
        <div class="link-box">
            <h4>👵 ২. বয়স্ক ও বিধবা ভাতা আবেদন</h4>
            <p><b>কাজ:</b> বয়স্ক, বিধবা ও স্বামী পরিত্যক্তা ভাতা অনলাইন আবেদন ও যাচাই।</p>
            <a href="https://www.mis.bhata.gov.bd/" target="_blank">🔗 ভাতা পোর্টাল ভিজিট করুন</a>
        </div>
        """, unsafe_allow_html=True)

with col_b:
    if is_eng:
        st.markdown("""
        <div class="link-box">
            <h4>📇 6. National Identity Card (NID) Services</h4>
            <p><b>Work:</b> New voter registration and NID card download.</p>
            <a href="https://services.nidw.gov.bd/" target="_blank">🔗 Visit NID Portal</a>
        </div>
        <div class="link-box">
            <h4>📜 7. Birth & Death Registration</h4>
            <p><b>Work:</b> New birth registration application and certificate print.</p>
            <a href="https://bdris.gov.bd/" target="_blank">🔗 Visit Birth Registration Portal</a>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="link-box">
            <h4>📇 ৬. জাতীয় পরিচয়পত্র সেবা (NID)</h4>
            <p><b>কাজ:</b> নতুন ভোটার নিবন্ধন ও NID কার্ড ডাউনলোড।</p>
            <a href="https://services.nidw.gov.bd/" target="_blank">🔗 এনআইডি পোর্টাল ভিজিট করুন</a>
        </div>
        <div class="link-box">
            <h4>📜 ৭. জন্ম ও মৃত্যু নিবন্ধন</h4>
            <p><b>কাজ:</b> নতুন জন্ম নিবন্ধন আবেদন ও সনদ প্রিন্ট।</p>
            <a href="https://bdris.gov.bd/" target="_blank">🔗 জন্ম নিবন্ধন পোর্টাল ভিজিট করুন</a>
        </div>
        """, unsafe_allow_html=True)
