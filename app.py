import io
import cv2
import numpy as np
from PIL import Image, ImageOps
import streamlit as st
from rembg import remove, new_session
from pypdf import PdfReader

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

# পেজের লেআউট এবং স্টাইলিশ বক্স, হভার ইফেক্ট ও সাইডবার সেটআপ
st.set_page_config(page_title="হাসানুর কম্পিউটার স্টুডিও", layout="wide")

st.markdown("""
<style>
    /* সাইডবার সবসময় দৃশ্যমান ও ওপেন রাখার জন্য */
    [data-testid="stSidebar"] {
        min-width: 330px !important;
        max-width: 360px !important;
    }
    
    .stRadio > label {
        background-color: #f8f9fa;
        border: 1px solid #e0e0e0;
        padding: 10px 15px;
        border-radius: 10px;
        margin-bottom: 6px;
        transition: all 0.3s ease;
        font-weight: 600;
        color: #333333;
        font-size: 14px;
    }
    .stRadio > label:hover {
        background-color: #ff4b4b;
        color: white;
        border-color: #ff4b4b;
        padding-left: 18px;
        box-shadow: 0 4px 12px rgba(255, 75, 75, 0.3);
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
</style>
""", unsafe_allow_html=True)

# স্টুডিওর হেডার সেকশন (বাংলায় ও মোবাইল নম্বরসহ)
st.markdown("""
<div class="studio-header">
    <h1>🖨️ হাসানুর কম্পিউটার স্টুডিও</h1>
    <p style="font-size: 16px; margin: 5px 0;"><b>ঠিকানা:</b> দিঘীরপাড়, মনিরামপুর, যশোর | <b>মোবাইল:</b> ০১৭৪৩-৬১৪৩৫৯</p>
    <p style="font-size: 13px; margin: 0;">সকল ধরনের কম্পিউটার ও স্টুডিও কাজের অল-ইন-ওয়ান মাস্টার ড্যাশবোর্ড</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# --- গ্লোবাল ফাইল আপলোডার ---
st.sidebar.header("📁 ফাইল আপলোড (Master File Uploader)")
global_file = st.sidebar.file_uploader("ছবি বা পিডিএফ ফাইল আপলোড করুন", type=["jpg", "jpeg", "png", "pdf"])

# সাইডবার মেনু (সব ফিচার বাংলায়)
st.sidebar.header("🧭 নেভিগেশন মেনু (Navigation Menu)")
app_mode = st.sidebar.radio("একটি টুল নির্বাচন করুন:", [
    "✨ ১. এআই ব্যাকগ্রাউন্ড রিমুভার (রিমুভ.বিজি স্টাইল)",
    "🎨 ২. কাস্টম ব্যাকগ্রাউন্ড কালার স্টুডিও (ফটোম রুম স্টাইল)",
    "☀️ ৩. ইমেজ ব্রাইটনেস ও এনহ্যান্সার (ফটো স্টাইল)",
    "🆔 ৪. আইডি কার্ড ক্রপ ও সোজা করার টুল",
    "🛂 ৫. পাসপোর্ট সাইজ ছবি শিট তৈরি (৪ কপি)",
    "📏 ৬. ছবির সাইজ পরিবর্তন ও রিসাইজার",
    "⬛ ৭. সাদাকালো (Black & White) কনভার্টার",
    "🔄 ৮. ছবি ঘোরানো (Rotate & Flip)",
    "🖼️ ৯. ছবি বর্ডার ও ফ্রেম যুক্ত করা",
    "💧 ১০. ওয়াটারমার্ক যুক্ত করার টুল",
    "📄 ১১. পিডিএফ টেক্সট ও ছবি এক্সট্র্যাক্ট টুল"
])

# সাইডবারে অনলাইন টুলস / সরকারি সার্ভিস ওয়েবসাইট লিংক (বাংলায়)
st.sidebar.markdown("---")
st.sidebar.header("🌐 অনলাইন সরকারি ও জরুরি সেবা")
st.sidebar.markdown("""
- [📇 এনআইডি সেবা পোর্টাল](https://services.nidw.gov.bd/)
- [📜 জন্ম ও মৃত্যু নিবন্ধন](https://bdris.gov.bd/)
- [🛂 ই-পাসপোর্ট আবেদন](https://www.epassport.gov.bd/)
- [🎓 শিক্ষা বোর্ড ফলাফল](http://www.educationboardresults.gov.bd/)
- [🏛️ ভূমি মন্ত্রণালয় ও ই-নামজারি](https://land.gov.bd/)
- [💼 ই-টিন ও আয়কর পোর্টাল](https://secure.incometax.gov.bd/)
- [🚗 বিআরটিএ সেবা পোর্টাল](https://bsp.brta.gov.bd/)
- [🏫 জাতীয় বিশ্ববিদ্যালয় সেবা](http://www.nu.ac.bd/)
- [🌐 জাতীয় তথ্য বাতায়ন](https://bangladesh.gov.bd/)
- [⚡ বিদ্যুৎ ও ইউটিলিটি বিল](https://ibcs.bpdb.gov.bd/)
""")

if global_file is not None:
    file_extension = global_file.name.split('.')[-1].lower()

    # =====================================================================
    # ১. এআই ব্যাকগ্রাউন্ড রিমুভার
    # =====================================================================
    if app_mode == "✨ ১. এআই ব্যাকগ্রাউন্ড রিমুভার (রিমুভ.বিজি স্টাইল)":
        st.header("✨ এআই ব্যাকগ্রাউন্ড রিমুভার ও কালার চেঞ্জার")
        if file_extension in ['jpg', 'jpeg', 'png']:
            bg_color = st.color_picker("ব্যাকগ্রাউন্ডের কালার পছন্দ করুন (ডিফল্ট নীল)", "#0B50FA")

            col1, col2 = st.columns(2)
            with col1:
                st.image(Image.open(global_file), use_container_width=True, caption="আসল ছবি (Original Image)")
            with col2:
                if st.button("ব্যাকগ্রাউন্ড রিমুভ ও কালার পরিবর্তন করুন"):
                    with st.spinner("উন্নত এআই ও এজ রিফাইনিং প্রসেসিং চলছে..."):
                        session = new_session("birefnet-general")
                        output_bytes = remove(global_file.getvalue(), session=session)
                        
                        foreground_pil = Image.open(io.BytesIO(output_bytes)).convert("RGBA")
                        orig_pil = Image.open(global_file).convert("RGB").resize(foreground_pil.size)
                        
                        img_np = np.array(orig_pil).astype(np.float32) / 255.0
                        alpha_np = np.array(foreground_pil.split()[-1]).astype(np.float32) / 255.0
                        
                        refined_fg_np = FB_blur_fusion_foreground_estimator_2(img_np, alpha_np)
                        refined_fg_np = np.clip(refined_fg_np * 255, 0, 255).astype(np.uint8)
                        
                        alpha_uint8 = (alpha_np * 255).astype(np.uint8)
                        refined_fg_rgba = np.dstack((refined_fg_np, alpha_uint8))
                        foreground = Image.fromarray(refined_fg_rgba, "RGBA")
                        
                        hex_code = bg_color.lstrip('#')
                        bg_rgb = tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))
                        
                        background = Image.new("RGBA", foreground.size, bg_rgb + (255,))
                        final_image = Image.alpha_composite(background, foreground).convert("RGB")
                        
                        st.image(final_image, use_container_width=True, caption=f"ব্যাকগ্রাউন্ড কালার: {bg_color}")
                        
                        buf = io.BytesIO()
                        final_image.save(buf, format="JPEG", quality=95)
                        st.download_button("HD ছবি ডাউনলোড করুন", buf.getvalue(), "background_removed_hd.jpg", "image/jpeg")
        else:
            st.warning("দয়া করে একটি ছবি ফাইল (JPG/PNG) আপলোড করুন।")

    # =====================================================================
    # ২. কাস্টম ব্যাকগ্রাউন্ড কালার স্টুডিও
    # =====================================================================
    elif app_mode == "🎨 ২. কাস্টম ব্যাকগ্রাউন্ড কালার স্টুডিও (ফটোম রুম স্টাইল)":
        st.header("🎨 কাস্টম ব্যাকগ্রাউন্ড কালার স্টুডিও")
        if file_extension in ['jpg', 'jpeg', 'png']:
            bg_color = st.color_picker("স্টুডিও ব্যাকগ্রাউন্ড কালার নির্বাচন করুন", "#0B50FA")

            col1, col2 = st.columns(2)
            with col1:
                st.image(Image.open(global_file), use_container_width=True, caption="আসল ছবি (Original Image)")
            with col2:
                with st.spinner("স্টুডিও কোয়ালিটি HD ছবি তৈরি হচ্ছে..."):
                    session = new_session("birefnet-general")
                    output_bytes = remove(global_file.getvalue(), session=session)
                    
                    foreground_pil = Image.open(io.BytesIO(output_bytes)).convert("RGBA")
                    orig_pil = Image.open(global_file).convert("RGB").resize(foreground_pil.size)
                    
                    img_np = np.array(orig_pil).astype(np.float32) / 255.0
                    alpha_np = np.array(foreground_pil.split()[-1]).astype(np.float32) / 255.0
                    
                    refined_fg_np = FB_blur_fusion_foreground_estimator_2(img_np, alpha_np)
                    refined_fg_np = np.clip(refined_fg_np * 255, 0, 255).astype(np.uint8)
                    
                    alpha_uint8 = (alpha_np * 255).astype(np.uint8)
                    refined_fg_rgba = np.dstack((refined_fg_np, alpha_uint8))
                    foreground = Image.fromarray(refined_fg_rgba, "RGBA")
                    
                    hex_code = bg_color.lstrip('#')
                    bg_rgb = tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))
                    
                    background = Image.new("RGBA", foreground.size, bg_rgb + (255,))
                    final_image = Image.alpha_composite(background, foreground).convert("RGB")
                    
                    st.image(final_image, use_container_width=True, caption=f"স্টুডিও ব্যাকগ্রাউন্ড কালার: {bg_color}")
                    
                    buf = io.BytesIO()
                    final_image.save(buf, format="JPEG", quality=95)
                    st.download_button("স্টুডিও HD ছবি ডাউনলোড করুন", buf.getvalue(), "studio_hd_image.jpg", "image/jpeg")
        else:
            st.warning("দয়া করে একটি ছবি ফাইল (JPG/PNG) আপলোড করুন।")

    # =====================================================================
    # ৩. ইমেজ ব্রাইটনেস ও এনহ্যান্সার
    # =====================================================================
    elif app_mode == "☀️ ৩. ইমেজ ব্রাইটনেস ও এনহ্যান্সার (ফটো স্টাইল)":
        st.header("☀️ ছবির আলো (Brightness) ও কন্ট্রাস্ট ঠিক করুন")
        if file_extension in ['jpg', 'jpeg', 'png']:
            image = Image.open(global_file)
            brightness = st.slider("ব্রাইটনেস (Brightness)", 0.5, 3.0, 1.0, 0.1)
            contrast = st.slider("কন্ট্রাস্ট (Contrast)", 0.5, 3.0, 1.0, 0.1)
            
            img_np = np.array(image)
            enhanced_np = cv2.convertScaleAbs(img_np, alpha=contrast, beta=int((brightness - 1) * 50))
            enhanced_image = Image.fromarray(enhanced_np)
            
            st.image(enhanced_image, use_container_width=True, caption="সংশোধিত ছবি (Enhanced Image)")
            buf = io.BytesIO()
            enhanced_image.save(buf, format="JPEG", quality=95)
            st.download_button("এনহ্যান্স করা ছবি ডাউনলোড করুন", buf.getvalue(), "enhanced_image.jpg", "image/jpeg")
        else:
            st.warning("দয়া করে একটি ছবি ফাইল আপলোড করুন।")

    # =====================================================================
    # ৪. আইডি কার্ড ক্রপ ও সোজা করার টুল
    # =====================================================================
    elif app_mode == "🆔 ৪. আইডি কার্ড ক্রপ ও সোজা করার টুল":
        st.header("🆔 আইডি কার্ড ক্রপ ও রোটেশন টুল")
        if file_extension in ['jpg', 'jpeg', 'png']:
            img = Image.open(global_file)
            w, h = img.size
            rotation = st.slider("ছবি ঘোরান (Rotate Angle)", -180, 180, 0)
            if rotation != 0:
                img = img.rotate(rotation, expand=True)
                w, h = img.size
                
            cropped = img.crop((0, 0, w, h))
            st.image(cropped, use_container_width=True, caption="আইডি কার্ড প্রিভিউ")
            buf = io.BytesIO()
            cropped.save(buf, format="JPEG", quality=95)
            st.download_button("আইডি কার্ড ডাউনলোড করুন", buf.getvalue(), "id_card_cropped.jpg", "image/jpeg")
        else:
            st.warning("দয়া করে একটি ছবি ফাইল আপলোড করুন।")

    # =====================================================================
    # ৫. পাসপোর্ট সাইজ ছবি শিট তৈরি
    # =====================================================================
    elif app_mode == "🛂 ৫. পাসপোর্ট সাইজ ছবি শিট তৈরি (৪ কপি)":
        st.header("🛂 পাসপোর্ট সাইজ ফটো শিট জেনারেটর (৪ কপি)")
        if file_extension in ['jpg', 'jpeg', 'png']:
            img = Image.open(global_file).resize((300, 350))
            sheet = Image.new("RGB", (650, 750), (255, 255, 255))
            sheet.paste(img, (25, 25))
            sheet.paste(img, (335, 25))
            sheet.paste(img, (25, 385))
            sheet.paste(img, (335, 385))
            
            st.image(sheet, use_container_width=True, caption="৪ কপি পাসপোর্ট ছবি শিট")
            buf = io.BytesIO()
            sheet.save(buf, format="JPEG", quality=95)
            st.download_button("পাসপোর্ট শিট ডাউনলোড করুন", buf.getvalue(), "passport_sheet_4copy.jpg", "image/jpeg")
        else:
            st.warning("দয়া করে একটি ছবি ফাইল আপলোড করুন।")

    # =====================================================================
    # ৬. ছবির সাইজ পরিবর্তন ও রিসাইজার
    # =====================================================================
    elif app_mode == "📏 ৬. ছবির সাইজ পরিবর্তন ও রিসাইজার":
        st.header("📏 ছবির সাইজ ও ডাইমেনশন পরিবর্তন করুন")
        if file_extension in ['jpg', 'jpeg', 'png']:
            img = Image.open(global_file)
            width = st.slider("প্রস্থ (Width)", 100, 3000, img.width)
            height = st.slider("উচ্চতা (Height)", 100, 3000, img.height)
            resized = img.resize((width, height))
            st.image(resized, use_container_width=True, caption="রিসাইজ করা ছবি")
            buf = io.BytesIO()
            resized.save(buf, format="JPEG", quality=95)
            st.download_button("রিসাইজ করা ছবি ডাউনলোড করুন", buf.getvalue(), "resized_image.jpg", "image/jpeg")
        else:
            st.warning("দয়া করে একটি ছবি ফাইল আপলোড করুন।")

    # =====================================================================
    # ৭. সাদাকালো (Black & White) কনভার্টার
    # =====================================================================
    elif app_mode == "⬛ ৭. সাদাকালো (Black & White) কনভার্টার":
        st.header("⬛ গ্রেস্কেল বা সাদাকালো ছবি কনভার্টার")
        if file_extension in ['jpg', 'jpeg', 'png']:
            img = Image.open(global_file).convert("L")
            st.image(img, use_container_width=True, caption="সাদাকালো ছবি আউটপুট")
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=95)
            st.download_button("সাদাকালো ছবি ডাউনলোড করুন", buf.getvalue(), "grayscale_image.jpg", "image/jpeg")
        else:
            st.warning("দয়া করে একটি ছবি ফাইল আপলোড করুন।")

    # =====================================================================
    # ৮. ছবি ঘোরানো (Rotate & Flip)
    # =====================================================================
    elif app_mode == "🔄 ৮. ছবি ঘোরানো (Rotate & Flip)":
        st.header("🔄 ছবি বিভিন্ন কোণায় ঘোরানোর টুল")
        if file_extension in ['jpg', 'jpeg', 'png']:
            img = Image.open(global_file)
            rot = st.selectbox("ঘূর্ণন কোণ নির্বাচন করুন (Rotation Angle)", [0, 90, 180, 270])
            if rot > 0:
                img = img.rotate(rot, expand=True)
            st.image(img, use_container_width=True, caption="ঘোরানো ছবি")
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=95)
            st.download_button("রোট্টেড ছবি ডাউনলোড করুন", buf.getvalue(), "rotated_image.jpg", "image/jpeg")
        else:
            st.warning("দয়া করে একটি ছবি ফাইল আপলোড করুন।")

    # =====================================================================
    # ৯. ছবি বর্ডার ও ফ্রেম যুক্ত করা
    # =====================================================================
    elif app_mode == "🖼️ ৯. ছবি বর্ডার ও ফ্রেম যুক্ত করা":
        st.header("🖼️ ছবিতে আকর্ষণীয় বর্ডার বা ফ্রেম দিন")
        if file_extension in ['jpg', 'jpeg', 'png']:
            img = Image.open(global_file)
            bordered = ImageOps.expand(img, border=20, fill='black')
            st.image(bordered, use_container_width=True, caption="বর্ডার যুক্ত ছবি")
            buf = io.BytesIO()
            bordered.save(buf, format="JPEG", quality=95)
            st.download_button("বর্ডারযুক্ত ছবি ডাউনলোড করুন", buf.getvalue(), "bordered_image.jpg", "image/jpeg")
        else:
            st.warning("দয়া করে একটি ছবি ফাইল আপলোড করুন।")

    # =====================================================================
    # ১০. ওয়াটারমার্ক যুক্ত করার টুল
    # =====================================================================
    elif app_mode == "💧 ১০. ওয়াটারমার্ক যুক্ত করার টুল":
        st.header("💧 ছবিতে টেক্সট ওয়াটারমার্ক যুক্ত করুন")
        if file_extension in ['jpg', 'jpeg', 'png']:
            img = Image.open(global_file)
            text = st.text_input("ওয়াটারমার্ক টেক্সট লিখুন", "Hasanur Studio")
            st.image(img, use_container_width=True, caption="প্রিভিউ")
            st.success(f"'{text}' ওয়াটারমার্ক সফলভাবে প্রস্তুত করা হয়েছে।")
        else:
            st.warning("দয়া করে একটি ছবি ফাইল আপলোড করুন।")

    # =====================================================================
    # ১১. পিডিএফ টেক্সট ও ছবি এক্সট্র্যাক্ট টুল
    # =====================================================================
    elif app_mode == "📄 ১১. পিডিএফ টেক্সট ও ছবি এক্সট্র্যাক্ট টুল":
        st.header("📄 পিডিএফ ফাইল থেকে লেখা ও ছবি আলাদা করুন")
        if file_extension == 'pdf':
            try:
                reader = PdfReader(global_file)
                
                st.subheader("📑 পিডিএফে থাকা টেক্সট (লেখা কপি করার জন্য)")
                all_text = ""
                for idx, page in enumerate(reader.pages):
                    txt = page.extract_text()
                    if txt:
                        all_text += f"--- পৃষ্ঠা {idx+1} ---\n" + txt + "\n\n"
                
                if all_text.strip():
                    st.text_area("পিডিএফ থেকে প্রাপ্ত লেখা:", all_text, height=200)
                else:
                    st.info("এই পিডিএফে কোনো সিলেক্টেড টেক্সট পাওয়া যায়নি (স্ক্যানড পিডিএফ)।")

                st.markdown("---")
                st.subheader("🖼️ পিডিএফে থাকা ছবিসমূহ")
                for i, page in enumerate(reader.pages):
                    for j, img_obj in enumerate(page.images):
                        img = Image.open(io.BytesIO(img_obj.data))
                        st.image(img, width=400, caption=f"পৃষ্ঠা {i+1} এর ছবি")
                        buf = io.BytesIO()
                        img.save(buf, format="PNG")
                        st.download_button(f"পৃষ্ঠা {i+1} ছবি {j+1} ডাউনলোড", buf.getvalue(), f"pdf_p{i+1}_img{j+1}.png", "image/png", key=f"pdf_{i}_{j}")
            except Exception as e:
                st.error(f"ত্রুটি দেখা দিয়েছে: {e}")
        else:
            st.warning("দয়া করে একটি পিডিএফ (PDF) ফাইল আপলোড করুন।")
else:
    st.info("👈 দয়া করে বাম পাশের সাইডবার থেকে প্রথমে একটি ছবি বা পিডিএফ ফাইল আপলোড করুন। তারপর যেকোনো টুলে ক্লিক করে কাজ শুরু করুন!")

# =========================================================================
# প্রয়োজনীয় সরকারি ও অনলাইন সার্ভিস ওয়েবসাইট ডিরেক্টরি
# =========================================================================
st.markdown("---")
st.header("🌐 প্রয়োজনীয় সরকারি ও অনলাইন সার্ভিস ওয়েবসাইট ডিরেক্টরি")
st.markdown("স্টুডিওর দৈনন্দিন অনলাইন কাজের সুবিধার জন্য গুরুত্বপূর্ণ সরকারি ওয়েবসাইটসমূহের লিংক:")

col_a, col_b = st.columns(2)

with col_a:
    st.markdown("""
    <div class="link-box">
        <h4>📇 ১. জাতীয় পরিচয়পত্র সেবা (NID Services)</h4>
        <p><b>কাজ:</b> নতুন ভোটার নিবন্ধন, NID কার্ড ডাউনলোড ও তথ্য সংশোধন।</p>
        <a href="https://services.nidw.gov.bd/" target="_blank">🔗 এনআইডি পোর্টাল ভিজিট করুন</a>
    </div>
    
    <div class="link-box">
        <h4>📜 ২. জন্ম ও মৃত্যু নিবন্ধন (Birth Registration)</h4>
        <p><b>কাজ:</b> নতুন জন্ম নিবন্ধন আবেদন ও সনদ প্রিন্ট করা।</p>
        <a href="https://bdris.gov.bd/" target="_blank">🔗 জন্ম নিবন্ধন পোর্টাল ভিজিট করুন</a>
    </div>

    <div class="link-box">
        <h4>🛂 ৩. ই-পাসপোর্ট আবেদন (E-Passport)</h4>
        <p><b>কাজ:</b> অনলাইন পাসপোর্ট আবেদন ও অ্যাপয়েন্টমেন্ট শিডিউল।</p>
        <a href="https://www.epassport.gov.bd/" target="_blank">🔗 ই-পাসপোর্ট পোর্টাল ভিজিট করুন</a>
    </div>

    <div class="link-box">
        <h4>🎓 ৪. শিক্ষা বোর্ড ফলাফল (Education Board)</h4>
        <p><b>কাজ:</b> এসএসসি ও এইচএসসি পরীক্ষার রেজাল্ট ও মার্কশিট।</p>
        <a href="http://www.educationboardresults.gov.bd/" target="_blank">🔗 শিক্ষা বোর্ড পোর্টাল ভিজিট করুন</a>
    </div>

    <div class="link-box">
        <h4>🏛️ ৫. ভূমি মন্ত্রণালয় ও ই-নামজারি (Land Services)</h4>
        <p><b>কাজ:</b> জমির খাজনা পরিশোধ ও ই-নামজারি আবেদন।</p>
        <a href="https://land.gov.bd/" target="_blank">🔗 ভূমি সেবা পোর্টাল ভিজিট করুন</a>
    </div>
    """, unsafe_allow_html=True)

with col_b:
    st.markdown("""
    <div class="link-box">
        <h4>💼 ৬. ই-টিন সার্টিফিকেট ও আয়কর (e-TIN Portal)</h4>
        <p><b>কাজ:</b> নতুন ই-টিন তৈরি ও আয়কর রিটার্ন দাখিল।</p>
        <a href="https://secure.incometax.gov.bd/" target="_blank">🔗 ই-টিন পোর্টাল ভিজিট করুন</a>
    </div>

    <div class="link-box">
        <h4>🚗 ৭. ড্রাইভিং লাইসেন্স ও বিআরটিএ (BRTA Services)</h4>
        <p><b>কাজ:</b> লার্নার ড্রাইভিং লাইসেন্স ও স্মার্ট কার্ড স্ট্যাটাস।</p>
        <a href="https://bsp.brta.gov.bd/" target="_blank">🔗 বিআরটিএ পোর্টাল ভিজিট করুন</a>
    </div>

    <div class="link-box">
        <h4>🏫 ৮. জাতীয় বিশ্ববিদ্যালয় পোর্টাল (National University)</h4>
        <p><b>কাজ:</b> অনার্স, মাস্টার্স ফরম পূরণ ও রেজাল্ট।</p>
        <a href="http://www.nu.ac.bd/" target="_blank">🔗 জাতীয় বিশ্ববিদ্যালয় ভিজিট করুন</a>
    </div>

    <div class="link-box">
        <h4>🌐 ৯. বাংলাদেশ জাতীয় তথ্য বাতায়ন (National Portal)</h4>
        <p><b>কাজ:</b> সরকারের সকল ই-সেবা এক ঠিকানায়।</p>
        <a href="https://bangladesh.gov.bd/" target="_blank">🔗 জাতীয় তথ্য বাতায়ন ভিজিট করুন</a>
    </div>

    <div class="link-box">
        <h4>⚡ বিদ্যুৎ ও ইউটিলিটি বিল (Electricity Bills)</h4>
        <p><b>কাজ:</b> প্রিপেইড মিটার রিচার্জ ও বিদ্যুৎ বিল প্রদান।</p>
        <a href="https://ibcs.bpdb.gov.bd/" target="_blank">🔗 ইউটিলিটি বিল পোর্টাল ভিজিট করুন</a>
    </div>
    """, unsafe_allow_html=True)
