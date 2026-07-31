import io
import cv2
import numpy as np
from PIL import Image, ImageOps
import streamlit as st
from rembg import remove, new_session
from pypdf import PdfReader

# পেজের লেআউট এবং স্টাইলিশ বক্স, হভার ইফেক্ট ও অলওয়েজ শো সাইডবার সেটআপ
st.set_page_config(page_title="Hasanur Computer Studio", layout="wide")

st.markdown("""
<style>
    /* সাইডবার সবসময় দৃশ্যমান ও ওপেন রাখার জন্য */
    [data-testid="stSidebar"] {
        min-width: 320px !important;
        max-width: 350px !important;
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
</style>
""", unsafe_allow_html=True)

st.title("🖨️ Hasanur Computer Studio - Complete 11-in-1 Master Dashboard")
st.markdown("---")

# --- গ্লোবাল ফাইল আপলোডার (একবার আপলোড করলেই সব মডিউলে কাজ করবে) ---
st.sidebar.header("📁 Master File Uploader / ফাইল আপলোড")
global_file = st.sidebar.file_uploader("Upload Image or PDF once / ছবি বা পিডিএফ আপলোড করুন", type=["jpg", "jpeg", "png", "pdf"])

# সাইডবার মেনু (১১টি ফিচার - সবসময় শো করবে)
st.sidebar.header("Navigation Menu / নেভিগেশন মেনু")
app_mode = st.sidebar.radio("Choose a Tool / টুল নির্বাচন করুন", [
    "✨ 1. remove.bg Style AI Background Remover",
    "🎨 2. Photoroom Style Custom BG Studio",
    "☀️ 3. Fotor Style Image Enhancer",
    "🆔 4. Adobe Express Style ID Cropper",
    "🛂 5. Canva Style Passport Sheet Maker",
    "📏 6. PicResize Style Image Resizer",
    "⬛ 7. Convertio Style B&W Converter",
    "🔄 8. Ezgif Style Image Rotator",
    "🖼️ 9. Pixlr Style Border & Frame",
    "💧 10. Watermarkly Style Watermark Adder",
    "📄 11. ILovePDF Style PDF Text & Image Converter"
])

# সাইডবারে অনলাইন টুলস / সরকারি সার্ভিস ওয়েবসাইট লিংক (বাংলা ও ইংরেজি) - সবসময় শো করবে
st.sidebar.markdown("---")
st.sidebar.header("🌐 Online Tools / অনলাইন টুলস")
st.sidebar.markdown("""
- [📇 NID Services / এনআইডি সেবা](https://services.nidw.gov.bd/)
- [📜 Birth Registration / জন্ম নিবন্ধন](https://bdris.gov.bd/)
- [🛂 E-Passport / ই-পাসপোর্ট](https://www.epassport.gov.bd/)
- [🎓 Education Board / শিক্ষা বোর্ড](http://www.educationboardresults.gov.bd/)
- [🏛️ Land Ministry / ভূমি মন্ত্রণালয়](https://land.gov.bd/)
- [💼 e-TIN Portal / ই-টিন পোর্টাল](https://secure.incometax.gov.bd/)
- [🚗 BRTA Services / বিআরটিএ সেবা](https://bsp.brta.gov.bd/)
- [🏫 National University / জাতীয় বিশ্ববিদ্যালয়](http://www.nu.ac.bd/)
- [🌐 National Portal / জাতীয় তথ্য বাতায়ন](https://bangladesh.gov.bd/)
- [⚡ Utility Bills / বিদ্যুৎ ও ইউটিলিটি বিল](https://ibcs.bpdb.gov.bd/)
""")

if global_file is not None:
    file_extension = global_file.name.split('.')[-1].lower()

    # =====================================================================
    # 1. remove.bg Style AI Background Remover (Default #0B50FA)
    # =====================================================================
    if app_mode == "✨ 1. remove.bg Style AI Background Remover":
        st.header("✨ AI Background Remover (Default Color: #0B50FA)")
        if file_extension in ['jpg', 'jpeg', 'png']:
            bg_color = st.color_picker("Pick Background Color (Default #0B50FA)", "#0B50FA")

            col1, col2 = st.columns(2)
            with col1:
                st.image(Image.open(global_file), use_container_width=True, caption="Original / আসল ছবি")
            with col2:
                if st.button("Remove Background & Apply Custom Color"):
                    with st.spinner("Processing with Advanced AI (HD)..."):
                        session = new_session("u2net_human_seg")
                        output_bytes = remove(global_file.getvalue(), session=session)
                        foreground = Image.open(io.BytesIO(output_bytes)).convert("RGBA")
                        
                        hex_code = bg_color.lstrip('#')
                        bg_rgb = tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))
                        
                        background = Image.new("RGBA", foreground.size, bg_rgb + (255,))
                        final_image = Image.alpha_composite(background, foreground).convert("RGB")
                        
                        st.image(final_image, use_container_width=True, caption=f"Background Color: {bg_color}")
                        
                        buf = io.BytesIO()
                        final_image.save(buf, format="JPEG", quality=95)
                        st.download_button("Download HD Background Image", buf.getvalue(), "custom_bg_hd.jpg", "image/jpeg")
        else:
            st.warning("Please upload an image file (JPG/PNG).")

    # =====================================================================
    # 2. Photoroom Style Custom BG Studio (Default #0B50FA)
    # =====================================================================
    elif app_mode == "🎨 2. Photoroom Style Custom BG Studio":
        st.header("🎨 Custom Background Color Studio (Default Color: #0B50FA)")
        if file_extension in ['jpg', 'jpeg', 'png']:
            bg_color = st.color_picker("Pick Background Color (Default #0B50FA)", "#0B50FA")

            col1, col2 = st.columns(2)
            with col1:
                st.image(Image.open(global_file), use_container_width=True, caption="Original / আসল ছবি")
            with col2:
                with st.spinner("Applying background and generating HD..."):
                    session = new_session("u2net_human_seg")
                    output_bytes = remove(global_file.getvalue(), session=session)
                    foreground = Image.open(io.BytesIO(output_bytes)).convert("RGBA")
                    
                    hex_code = bg_color.lstrip('#')
                    bg_rgb = tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))
                    
                    background = Image.new("RGBA", foreground.size, bg_rgb + (255,))
                    final_image = Image.alpha_composite(background, foreground).convert("RGB")
                    
                    st.image(final_image, use_container_width=True, caption=f"Background Color: {bg_color}")
                    
                    buf = io.BytesIO()
                    final_image.save(buf, format="JPEG", quality=95)
                    st.download_button("Download HD Studio Image", buf.getvalue(), "custom_bg_hd.jpg", "image/jpeg")
        else:
            st.warning("Please upload an image file (JPG/PNG).")

    # =====================================================================
    # 3. Fotor Style Image Enhancer
    # =====================================================================
    elif app_mode == "☀️ 3. Fotor Style Image Enhancer":
        st.header("☀️ Image Enhancer & Brightness Adjuster / ব্রাইটনেস ও কন্ট্রাস্ট ঠিক করুন")
        if file_extension in ['jpg', 'jpeg', 'png']:
            image = Image.open(global_file)
            brightness = st.slider("Brightness / আলো", 0.5, 3.0, 1.0, 0.1)
            contrast = st.slider("Contrast / বৈপরীত্য", 0.5, 3.0, 1.0, 0.1)
            
            img_np = np.array(image)
            enhanced_np = cv2.convertScaleAbs(img_np, alpha=contrast, beta=int((brightness - 1) * 50))
            enhanced_image = Image.fromarray(enhanced_np)
            
            st.image(enhanced_image, use_container_width=True, caption="Enhanced HD Image")
            buf = io.BytesIO()
            enhanced_image.save(buf, format="JPEG", quality=95)
            st.download_button("Download HD Enhanced Image", buf.getvalue(), "enhanced_hd.jpg", "image/jpeg")
        else:
            st.warning("Please upload an image file.")

    # =====================================================================
    # 4. Adobe Express Style ID Cropper
    # =====================================================================
    elif app_mode == "🆔 4. Adobe Express Style ID Cropper":
        st.header("🆔 ID Card Cropper & Straightener / আইডি কার্ড ক্রপ ও সোজা করা")
        if file_extension in ['jpg', 'jpeg', 'png']:
            img = Image.open(global_file)
            w, h = img.size
            rotation = st.slider("Rotate / ঘামান", -180, 180, 0)
            if rotation != 0:
                img = img.rotate(rotation, expand=True)
                w, h = img.size
                
            cropped = img.crop((0, 0, w, h))
            st.image(cropped, use_container_width=True, caption="ID Card HD Preview")
            buf = io.BytesIO()
            cropped.save(buf, format="JPEG", quality=95)
            st.download_button("Download HD ID Card", buf.getvalue(), "id_card_hd.jpg", "image/jpeg")
        else:
            st.warning("Please upload an image file.")

    # =====================================================================
    # 5. Canva Style Passport Sheet Maker
    # =====================================================================
    elif app_mode == "🛂 5. Canva Style Passport Sheet Maker":
        st.header("🛂 Passport Photo Sheet Generator / পাসপোর্ট ছবি শিট তৈরি")
        if file_extension in ['jpg', 'jpeg', 'png']:
            img = Image.open(global_file).resize((300, 350))
            sheet = Image.new("RGB", (650, 750), (255, 255, 255))
            sheet.paste(img, (25, 25))
            sheet.paste(img, (335, 25))
            sheet.paste(img, (25, 385))
            sheet.paste(img, (335, 385))
            
            st.image(sheet, use_container_width=True, caption="4-Copy HD Passport Sheet")
            buf = io.BytesIO()
            sheet.save(buf, format="JPEG", quality=95)
            st.download_button("Download HD Passport Sheet", buf.getvalue(), "passport_sheet_hd.jpg", "image/jpeg")
        else:
            st.warning("Please upload an image file.")

    # =====================================================================
    # 6. PicResize Style Image Resizer
    # =====================================================================
    elif app_mode == "📏 6. PicResize Style Image Resizer":
        st.header("📏 Image Resizer & Compressor / ছবির সাইজ পরিবর্তন")
        if file_extension in ['jpg', 'jpeg', 'png']:
            img = Image.open(global_file)
            width = st.slider("Width / প্রস্থ", 100, 3000, img.width)
            height = st.slider("Height / উচ্চতা", 100, 3000, img.height)
            resized = img.resize((width, height))
            st.image(resized, use_container_width=True)
            buf = io.BytesIO()
            resized.save(buf, format="JPEG", quality=95)
            st.download_button("Download HD Resized", buf.getvalue(), "resized_hd.jpg", "image/jpeg")
        else:
            st.warning("Please upload an image file.")

    # =====================================================================
    # 7. Convertio Style B&W Converter
    # =====================================================================
    elif app_mode == "⬛ 7. Convertio Style B&W Converter":
        st.header("⬛ Grayscale / Black-White Converter / সাদাকালো কনভার্টার")
        if file_extension in ['jpg', 'jpeg', 'png']:
            img = Image.open(global_file).convert("L")
            st.image(img, use_container_width=True, caption="Grayscale HD Output")
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=95)
            st.download_button("Download HD B&W", buf.getvalue(), "grayscale_hd.jpg", "image/jpeg")
        else:
            st.warning("Please upload an image file.")

    # =====================================================================
    # 8. Ezgif Style Image Rotator
    # =====================================================================
    elif app_mode == "🔄 8. Ezgif Style Image Rotator":
        st.header("🔄 Image Rotator & Flipper / ছবি ঘোরানো")
        if file_extension in ['jpg', 'jpeg', 'png']:
            img = Image.open(global_file)
            rot = st.selectbox("Rotation Angle / ঘূর্ণন কোণ", [0, 90, 180, 270])
            if rot > 0:
                img = img.rotate(rot, expand=True)
            st.image(img, use_container_width=True)
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=95)
            st.download_button("Download HD Rotated", buf.getvalue(), "rotated_hd.jpg", "image/jpeg")
        else:
            st.warning("Please upload an image file.")

    # =====================================================================
    # 9. Pixlr Style Border & Frame
    # =====================================================================
    elif app_mode == "🖼️ 9. Pixlr Style Border & Frame":
        st.header("🖼️ Border & Frame Adder / বর্ডার ও ফ্রেম যুক্ত করুন")
        if file_extension in ['jpg', 'jpeg', 'png']:
            img = Image.open(global_file)
            bordered = ImageOps.expand(img, border=20, fill='black')
            st.image(bordered, use_container_width=True)
            buf = io.BytesIO()
            bordered.save(buf, format="JPEG", quality=95)
            st.download_button("Download HD Bordered", buf.getvalue(), "bordered_hd.jpg", "image/jpeg")
        else:
            st.warning("Please upload an image file.")

    # =====================================================================
    # 10. Watermarkly Style Watermark Adder
    # =====================================================================
    elif app_mode == "💧 10. Watermarkly Style Watermark Adder":
        st.header("💧 Watermark Adder / ওয়াটারমার্ক যুক্ত করুন")
        if file_extension in ['jpg', 'jpeg', 'png']:
            img = Image.open(global_file)
            text = st.text_input("Watermark Text / ওয়াটারমার্ক টেক্সট", "Hasanur Studio")
            st.image(img, use_container_width=True, caption="Preview")
            st.success(f"Watermark '{text}' ready to apply on HD image.")
        else:
            st.warning("Please upload an image file.")

    # =====================================================================
    # 11. ILovePDF Style PDF Text & Image Converter
    # =====================================================================
    elif app_mode == "📄 11. ILovePDF Style PDF Text & Image Converter":
        st.header("📄 PDF Text Extractor & Image Converter / পিডিএফ টেক্সট ও ছবি এক্সট্র্যাক্ট")
        if file_extension == 'pdf':
            try:
                reader = PdfReader(global_file)
                
                st.subheader("📑 Extracted Text from PDF (For Editing/Copying) / পিডিএফ লেখা")
                all_text = ""
                for idx, page in enumerate(reader.pages):
                    txt = page.extract_text()
                    if txt:
                        all_text += f"--- Page {idx+1} ---\n" + txt + "\n\n"
                
                if all_text.strip():
                    st.text_area("Copy or Edit PDF Text Content", all_text, height=200)
                else:
                    st.info("No selectable text found in this PDF (scanned).")

                st.markdown("---")
                st.subheader("🖼️ Extracted Images from PDF / পিডিএফ ছবি")
                for i, page in enumerate(reader.pages):
                    for j, img_obj in enumerate(page.images):
                        img = Image.open(io.BytesIO(img_obj.data))
                        st.image(img, width=400, caption=f"Page {i+1} Image HD")
                        buf = io.BytesIO()
                        img.save(buf, format="PNG")
                        st.download_button(f"Download HD P{i+1} Img{j+1}", buf.getvalue(), f"pdf_p{i+1}_img{j+1}_hd.png", "image/png", key=f"pdf_{i}_{j}")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Please upload a PDF file for this module.")
else:
    st.info("👈 দয়া করে বাম পাশের সাইডবার থেকে প্রথমে একটি ছবি বা পিডিএফ (Master File Uploader) আপলোড করুন। এরপর যেকোনো মডিউলে ক্লিক করলেই সেই ফাইল দিয়ে কাজ করতে পারবেন!")

# =========================================================================
# কম্পিউটারের দোকানের প্রয়োজনীয় সরকারি ও অনলাইন সার্ভিস ওয়েবসাইটসমূহের তালিকা (বাংলা ও ইংরেজি)
# =========================================================================
st.markdown("---")
st.header("🌐 প্রয়োজনীয় সরকারি ও অনলাইন সার্ভিস ওয়েবসাইট ডিরেক্টরি / Official & Online Services Directory")
st.markdown("কম্পিউটার ও স্টুডিওর দৈনন্দিন কাজের সুবিধার জন্য গুরুত্বপূর্ণ সরকারি ও অনলাইন ফর্ম ফিলাপের লিংক এবং বিবরণ নিচে দেওয়া হলো:")

col_a, col_b = st.columns(2)

with col_a:
    st.markdown("""
    <div class="link-box">
        <h4>📇 ১. জাতীয় পরিচয়পত্র (NID Services / এনআইডি সেবা)</h4>
        <p><b>কার্যকারিতা:</b> নতুন ভোটার নিবন্ধন, NID কার্ড ডাউনলোড, তথ্য সংশোধন ও স্লিপ স্ট্যাটাস চেক করা।</p>
        <a href="https://services.nidw.gov.bd/" target="_blank">🔗 NID Portal (Services)</a>
    </div>
    
    <div class="link-box">
        <h4>📜 ২. জন্ম ও মৃত্যু নিবন্ধন (Birth & Death Registration)</h4>
        <p><b>কার্যকারিতা:</b> নতুন জন্ম নিবন্ধন আবেদন, জন্ম সনদ প্রিন্ট, সংশোধন এবং মৃত্যু নিবন্ধন সংক্রান্ত কাজ।</p>
        <a href="https://bdris.gov.bd/" target="_blank">🔗 BDRIS Portal</a>
    </div>

    <div class="link-box">
        <h4>🛂 ৩. পাসপোর্ট আবেদন (E-Passport / ই-পাসপোর্ট)</h4>
        <p><b>কার্যকারিতা:</b> অনলাইন ই-পাসপোর্ট আবেদন, ফি জমা দেওয়া এবং অ্যাপয়েন্টমেন্ট শিডিউল চেক করা।</p>
        <a href="https://www.epassport.gov.bd/" target="_blank">🔗 E-Passport Portal</a>
    </div>

    <div class="link-box">
        <h4>🎓 ৪. শিক্ষা বোর্ড ফলাফল ও রেজিস্ট্রেশন (Education Board)</h4>
        <p><b>কার্যকারিতা:</b> এসএসসি, এইচএসসি ও সমমানের পরীক্ষার ফলাফল, রেজিস্ট্রেশন কার্ড ও মার্কশিট ডাউনলোড।</p>
        <a href="http://www.educationboardresults.gov.bd/" target="_blank">🔗 Education Board Results</a>
    </div>

    <div class="link-box">
        <h4>🏛️ ৫. ভূমি মন্ত্রণালয় ও ই-নামজারি (Land Services / ভূমি সেবা)</h4>
        <p><b>কার্যকারিতা:</b> জমির খাজনা পরিশোধ (হোল্ডিং ট্যাক্স), ই-নামজারি আবেদন এবং খতিয়ান বা পর্চা তোলা।</p>
        <a href="https://land.gov.bd/" target="_blank">🔗 Land Ministry Portal</a>
    </div>
    """, unsafe_allow_html=True)

with col_b:
    st.markdown("""
    <div class="link-box">
        <h4>💼 ৬. টিন সার্টিফিকেট ও ভ্যাট (NTRCA / Income Tax / e-TIN)</h4>
        <p><b>কার্যকারিতা:</b> নতুন ই-টিন (TIN) সার্টিফিকেট তৈরি, আয়কর রিটার্ন দাখিল এবং ভ্যাট সংক্রান্ত কার্যক্রম।</p>
        <a href="https://secure.incometax.gov.bd/" target="_blank">🔗 e-TIN Portal</a>
    </div>

    <div class="link-box">
        <h4>🚗 ৭. ড্রাইভিং লাইসেন্স ও বিআরটিএ (BRTA Services)</h4>
        <p><b>কার্যকারিতা:</b> লার্নার ড্রাইভিং লাইসেন্স আবেদন, পরীক্ষার ডেট ও স্মার্ট কার্ড স্ট্যাটাস চেক।</p>
        <a href="https://bsp.brta.gov.bd/" target="_blank">🔗 BRTA Services Portal (BSP)</a>
    </div>

    <div class="link-box">
        <h4>🏫 ৮. জাতীয় বিশ্ববিদ্যালয় সার্ভিস (National University)</h4>
        <p><b>কার্যকারিতা:</b> অনার্স, মাস্টার্স ও ডিগ্রি ভর্তি আবেদন, ফরম পূরণ, রেজাল্ট এবং ট্রান্সক্রিপ্ট উত্তোলনের আবেদন।</p>
        <a href="http://www.nu.ac.bd/" target="_blank">🔗 National University Portal</a>
    </div>

    <div class="link-box">
        <h4>🌐 ৯. বাংলাদেশ সরকারের কেন্দ্রীয় পোর্টাল (National Web Portal)</h4>
        <p><b>কার্যকারিতা:</b> সরকারের সকল ই-সেবা, মন্ত্রণালয় এবং বিভিন্ন দাপ্তরিক ফরম এক ঠিকানায় পাওয়ার জন্য।</p>
        <a href="https://bangladesh.gov.bd/" target="_blank">🔗 Bangladesh National Portal</a>
    </div>

    <div class="link-box">
        <h4>⚡ বিদ্যুৎ ও ইউটিলিটি বিল (Electricity & Utilities)</h4>
        <p><b>কার্যকারিতা:</b> প্রিপেইড মিটার রিচার্জ, পল্লি বিদ্যুৎ, ডেস্কো, ডিপিডিসি ও ওয়াসার বিল চেক ও প্রদান।</p>
        <a href="https://ibcs.bpdb.gov.bd/" target="_blank">🔗 BPDB / Utility Portal</a>
    </div>
    """, unsafe_allow_html=True)
