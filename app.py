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

# ড্যাশবোর্ড থিম ও কাস্টম ডিজাইন CSS
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
    .form-preview {
        background-color: #1e293b;
        padding: 30px;
        border-radius: 8px;
        border: 2px dashed #334155;
        color: #f8fafc;
        font-family: 'Courier New', Courier, monospace;
    }
    </style>
""", unsafe_allow_html=True)

# 🛠️ সাইডবার ড্যাশবোর্ড কন্ট্রোল ও ল্যাঙ্গুয়েজ সিলেকশন
st.sidebar.markdown("## 📊 Project Structure")
lang_mode = st.sidebar.radio("🌐 Select Language / ভাষা নির্বাচন করুন:", ("🇧🇩 বাংলা UI", "🇬🇧 English UI"))
st.sidebar.markdown("---")

# ভাষা অনুযায়ী টেক্সট ভেরিয়েবল সেটআপ
if lang_mode == "🇧🇩 বাংলা UI":
    title_text = "📸 হাসানুর কম্পিউটার স্টুডিও"
    sub_text = "📍 মনিরামপুর, যশোর | অল-ইন-ওয়ান প্রফেশনাল ডিজিটাল ল্যাব ড্যাশবোর্ড"
    hotline_text = "📞 হটলাইন: 01743614359"
    menu_title = "⚙️ কাজের বিভাগসমূহ"
    footer_text = "© ২০২৬ হাসানুর কম্পিউটার স্টুডিও, মনিরামপুর, যশোর। অল রাইটস রিজার্ভড।"
    upload_msg = "এডিট করার জন্য আপনার ছবিটি এখানে আপলোড করুন..."
    apply_txt = "Apply (পরিবর্তন সেভ করুন)"
    
    menu_options = (
        "1. ✂️ Crop Tool (ফটো ক্রপ)",
        "2. 🪄 En-Real & Enhan-AI (ছবি উন্নতকরণ)",
        "3. 🎨 BG-First & BG-AI (ব্যাকগ্রাউন্ড পরিবর্তন)",
        "4. 🧽 Erase & Restore Tool (অবজেক্ট রিমুভ)",
        "5. 📜 প্রত্যয়ন পত্র ও ছাড়পত্র ফরম জেনারেটর",
        "6. 📝 প্রফেশনাল সিভি/বায়োডাটা মেকার ফরম",
        "7. 🔗 Multiple PDF Merger (পিডিএফ জোড়া)",
        "8. ❌ PDF Page Delete Tool (পেজ বাদ দেওয়া)",
        "9. 🌐 অনলাইন সেবা ও লিঙ্কসমূহ (ভিসা, পাসপোর্ট ও আবেদন)",
        "10. ⚙️ Settings & Studio Info (সেটিংস)"
    )
else:
    title_text = "📸 Hasanur Computer Studio"
    sub_text = "📍 Monirampur, Jashore | All-in-One Professional Digital Lab Dashboard"
    hotline_text = "📞 Hotline: 01743614359"
    menu_title = "⚙️ Work Modules"
    footer_text = "© 2026 Hasanur Computer Studio, Monirampur, Jashore. All Rights Reserved."
    upload_msg = "Upload your image here to edit..."
    apply_txt = "Apply Changes"
    
    menu_options = (
        "1. ✂️ Crop Tool",
        "2. 🪄 En-Real & Enhan-AI Pro",
        "3. 🎨 BG-First & BG-AI Core",
        "4. 🧽 Erase & Restore Tool",
        "5. 📜 Certificate & TC Form Generator",
        "6. 📝 Professional CV/Bio-Data Maker",
        "7. 🔗 Multiple PDF Merger",
        "8. ❌ PDF Page Delete Tool",
        "9. 🌐 Online Services & Links Portal",
        "10. ⚙️ Settings & Studio Info"
    )

# হেডার ও স্টুডিও ব্র্যান্ডিং রেন্ডারিং
st.markdown(f"<h1>{title_text}</h1>", unsafe_allow_html=True)
st.markdown(f"<div class='subtitle'>{sub_text}</div>", unsafe_allow_html=True)
st.markdown(f"<div class='contact-info'>{hotline_text}</div>", unsafe_allow_html=True)

# সাইডবারে ১ থেকে ১০ মডিউল সাজানো
st.sidebar.markdown(f"## {menu_title}")
tool_option = st.sidebar.radio("টুলবক্স মেনু:", menu_options)
st.sidebar.markdown("---")

# ইমেজ ফাইল আপলোডার গ্লোবাল হ্যান্ডলিং (ফটো মডিউলগুলোর জন্য ১-৪)
is_photo_module = any(x in tool_option for x in ["1.", "2.", "3.", "4."])
uploaded_file = st.file_uploader(upload_msg, type=["jpg", "jpeg", "png"]) if is_photo_module else None

base_image = None
if uploaded_file is not None:
    base_image = Image.open(uploaded_file)
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        st.image(base_image, caption="Original Image / মূল ছবি", use_container_width=True)

# ====================================================================
# MODULE 1: ✂️ Crop Tool
# ====================================================================
if "1." in tool_option:
    st.markdown("### ✂️ 1. Crop Tool")
    if base_image:
        crop_type = st.radio("Select Crop Ratio / ক্রপ রেশিও:", ("Passport Size (413x531 px)", "Stamp Size (236x295 px)", "Custom Auto ID Card"))
        if st.button(apply_txt, type="primary", use_container_width=True):
            if "Passport" in crop_type:
                out = base_image.resize((413, 531), Image.Resampling.LANCZOS)
            elif "Stamp" in crop_type:
                out = base_image.resize((236, 295), Image.Resampling.LANCZOS)
            else:
                out = base_image.resize((600, 400), Image.Resampling.LANCZOS)
            with col_v2:
                st.image(out, caption="Cropped Output", use_container_width=True)
                buf = io.BytesIO(); out.save(buf, format="JPEG")
                st.download_button("📥 Download Result", data=buf.getvalue(), file_name="cropped.jpg", use_container_width=True)

# ====================================================================
# MODULE 2: 🪄 En-Real & Enhan-AI
# ====================================================================
elif "2." in tool_option:
    st.markdown("### 🪄 2. En-Real & Enhan-AI Photo Enhancer")
    if base_image:
        enhance_mode = st.radio("Choose Mode / মোড সিলেক্ট করুন:", ("En-Real (Sharpness Booster)", "Enhan-AI (Auto Light & Color Adjust)"))
        if st.button(apply_txt, type="primary", use_container_width=True):
            if "En-Real" in enhance_mode:
                out = ImageEnhance.Sharpness(base_image).enhance(2.5)
            else:
                img_c = ImageEnhance.Contrast(base_image).enhance(1.3)
                out = ImageEnhance.Brightness(img_c).enhance(1.1)
            with col_v2:
                st.image(out, caption="Enhanced Output", use_container_width=True)
                buf = io.BytesIO(); out.save(buf, format="JPEG")
                st.download_button("📥 Download Result", data=buf.getvalue(), file_name="enhanced.jpg", use_container_width=True)

# ====================================================================
# MODULE 3: 🎨 BG-First & BG-AI
# ====================================================================
elif "3." in tool_option:
    st.markdown("### 🎨 3. BG-First & BG-AI Background Panel")
    if base_image:
        bg_mode = st.radio("Method / পদ্ধতি:", ("BG-First (Remove BG Transparent)", "BG-AI (Custom Solid Color BG)"))
        bg_color = st.color_picker("Choose Background Color (For BG-AI):", "#0080FF")
        if st.button(apply_txt, type="primary", use_container_width=True):
            if REMBG_AVAILABLE:
                with st.spinner("Processing AI Background..."):
                    transparent = remove(base_image)
                    if "BG-First" in bg_mode:
                        out = transparent
                        file_ext = "PNG"; mime_type = "image/png"; filename = "transparent.png"
                    else:
                        h_val = bg_color.lstrip('#')
                        bg_rgb = tuple(int(h_val[i:i+2], 16) for i in (0, 2, 4))
                        bg = Image.new("RGBA", base_image.size, bg_rgb + (255,))
                        bg.paste(transparent, (0, 0), transparent)
                        out = bg.convert("RGB")
                        file_ext = "JPEG"; mime_type = "image/jpeg"; filename = "colored.jpg"
                    with col_v2:
                        st.image(out, caption="Background Processed", use_container_width=True)
                        buf = io.BytesIO(); out.save(buf, format=file_ext)
                        st.download_button("📥 Download Background Changed Photo", data=buf.getvalue(), file_name=filename, mime=mime_type, use_container_width=True)

# ====================================================================
# MODULE 4: 🧽 Erase & Restore Tool
# ====================================================================
elif "4." in tool_option:
    st.markdown("### 🧽 4. Erase & Restore Tool")
    if base_image:
        action = st.radio("Action / কাজ:", ("Erase (Blemish Remover Filter)", "Restore (Reset Layer)"))
        if st.button(apply_txt, type="primary", use_container_width=True):
            if "Erase" in action:
                out = base_image.filter(ImageFilter.MedianFilter(size=3))
            else:
                out = base_image
            with col_v2:
                st.image(out, caption="Processed Image", use_container_width=True)
                buf = io.BytesIO(); out.save(buf, format="JPEG")
                st.download_button("📥 Download Image", data=buf.getvalue(), file_name="edited.jpg", use_container_width=True)

# ====================================================================
# MODULE 5: 📜 প্রত্যয়ন পত্র ও ছাড়পত্র ফরম জেনারেটর (NEW)
# ====================================================================
elif "5." in tool_option:
    st.markdown("### 📜 5. চারিত্রিক/নাগরিক প্রত্যয়ন পত্র ও স্কুল ছাড়পত্র (TC) জেনারেটর")
    doc_type = st.selectbox("নথিপত্রের ধরণ সিলেক্ট করুন:", ["নাগরিক/চারিত্রিক প্রত্যয়ন পত্র", "স্কুল/কলেজ ছাড়পত্র (Transfer Certificate)"])
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        c_name = st.text_input("আবেদনকারীর নাম (Name):", "মোঃ হাসানুর রহমান")
        c_father = st.text_input("পিতা/স্বামীর নাম (Father's Name):", "মোঃ আব্দুর রশিদ")
        c_mother = st.text_input("মাতার নাম (Mother's Name):", "মোসাম্মৎ রহিমা বেগম")
    with col_f2:
        c_village = st.text_input("গ্রাম/মহল্লা (Village):", "মনিরামপুর")
        c_post = st.text_input("ডাকঘর (Post Office):", "মনিরামপুর")
        c_thana = st.text_input("উপজেলা ও জেলা (Upazila & District):", "মনিরামপুর, যশোর")
        
    if doc_type == "নাগরিক/চারিত্রিক প্রত্যয়ন পত্র":
        c_character = st.selectbox("চারিত্রিক অবস্থা:", ["উত্তম", "ভালো", "সন্তোষজনক"])
        template = f"""
        ===================================================================
                                প্রত্যয়ন পত্র
        ===================================================================
        এই মর্মে প্রত্যয়ন করা যাইতেছে যে, {c_name}, পিতা: {c_father}, মাতা: {c_mother}, 
        গ্রাম: {c_village}, ডাকঘর: {c_post}, উপজেলা: {c_thana}। 
        
        তিনি আমার পরিচিত। আমার জানামতে তিনি অত্র এলাকার স্থায়ী বাসিন্দা এবং বাংলাদেশের 
        একজন সৎ ও নাগরিক। সমাজ বা রাষ্ট্র বিরোধী কোনো কাজের সাথে তিনি জড়িত নহেন। 
        তাহার নৈতিক চরিত্র অত্যন্ত {c_character}।
        
        আমি তাহার সর্বাঙ্গীন উন্নতি ও মঙ্গল কামনা করি।
        
                                                   স্বাক্ষর ও সীল 
                                             চেয়ারম্যান / পৌর মেয়র
        """
    else:
        c_class = st.text_input("শেষ পঠিত শ্রেণী (Last Class):", "নবম শ্রেণী")
        c_roll = st.text_input("রোল নম্বর (Roll No):", "০৫")
        template = f"""
        ===================================================================
                        বিদ্যালয় / কলেজ ছাড়পত্র (TC)
        ===================================================================
        এই মর্মে ছাড়পত্র প্রদান করা যাইতেছে যে, {c_name}, পিতা: {c_father}, মাতা: {c_mother}, 
        অত্র প্রতিষ্ঠানের একজন নিয়মিত শিক্ষার্থী ছিলেন। তিনি সর্বশেষ {c_class}-এ অধ্যয়ন করিয়াছেন, 
        যাহার রোল নম্বর ছিল {c_roll}। 
        
        অত্র প্রতিষ্ঠানে অধ্যয়নকালীন তাহার আচরণ সন্তোষজনক ছিল। প্রতিষ্ঠানের নিকট তাহার কোনো 
        বকেয়া পাওনা বা দেনা নাই। 
        
        তাহার ভবিষ্যতের সকল প্রকার সাফল্য ও উন্নতি কামনা করিয়া অত্র ছাড়পত্র ইস্যু করা হইলো।
        
                                                   স্বাক্ষর ও সীল 
                                                   প্রধান শিক্ষক
        """
        
    st.markdown("#### 📄 প্রিন্ট প্রিভিউ (Print Preview):")
    st.markdown(f"<div class='form-preview'><pre>{template}</pre></div>", unsafe_allow_html=True)
    st.download_button("📥 প্রিন্ট করার জন্য ডকুমেন্ট ডাউনলোড করুন (TXT/PDF)", data=template.encode('utf-8'), file_name="document_output.txt", use_container_width=True)

# ====================================================================
# MODULE 6: 📝 প্রফেশনাল সিভি/বায়োডাটা মেকার ফরম (NEW)
# ====================================================================
elif "6." in tool_option:
    st.markdown("### 📝 6. প্রফেশনাল সিভি / বায়োডাটা মেকার ফরম")
    st.info("💡 নিচের তথ্যগুলো পূরণ করুন, ডানপাশে অটোমেটিক প্রফেশনাল রেজিউমে তৈরি হয়ে যাবে।")
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        cv_name = st.text_input("পূর্ণ নাম (Full Name):", "হাসানুর রহমান")
        cv_email = st.text_input("ইমেইল (Email):", "hasanur@example.com")
        cv_phone = st.text_input("মোবাইল (Mobile):", "01743614359")
        cv_edu = st.text_area("শিক্ষাগত যোগ্যতা (Education):", "১. এসএসসি - জিপিএ ৫.০০ (২০১৮)\n২. এইচএসসি - জিপিএ ৪.৮০ (২০২০)")
    with col_c2:
        cv_skills = st.text_area("দক্ষতা (Skills):", "কম্পিউটার টাইপিং, গ্রাফিক্স ডিজাইন, ইন্টারনেট ব্রাউজিং ও অনলাইন অ্যাপ্লিকেশন")
        cv_exp = st.text_area("অভিজ্ঞতা (Experience):", "হাসানুর কম্পিউটার স্টুডিওতে ৩ বছরের ডিজিটাল সার্ভিস প্রদানের অভিজ্ঞতা।")
        
    cv_template = f"""
    =======================================================================
                                 CURRICULUM VITAE
    =======================================================================
    নাম (Name)       : {cv_name}
    মোবাইল (Mobile)  : {cv_phone}
    ইমেইল (Email)    : {cv_email}
    -----------------------------------------------------------------------
    CAREER OBJECTIVE:
    To work in a challenging environment where I can utilize my computer skills 
    and general expertise to contribute effectively to the organization.
    
    EDUCATIONAL QUALIFICATION:
    {cv_edu}
    
    PROFESSIONAL SKILLS:
    {cv_skills}
    
    WORK EXPERIENCE:
    {cv_exp}
    -----------------------------------------------------------------------
    Declaration: I hereby declare that all the information provided above is true 
    to the best of my knowledge.
    
    
    👉 Signature: __________________
    """
    st.markdown("#### 📄 সিভি রেডি প্রিভিউ:")
    st.markdown(f"<div class='form-preview'><pre>{cv_template}</pre></div>", unsafe_allow_html=True)
    st.download_button("📥 সিভি (CV) ফাইল ডাউনলোড করুন", data=cv_template.encode('utf-8'), file_name="Hasanur_Studio_CV.txt", use_container_width=True)

# ====================================================================
# MODULE 7: 🔗 Multiple PDF Merger
# ====================================================================
elif "7." in tool_option:
    st.markdown("### 🔗 7. Multiple PDF Merger")
    pdf_files = st.file_uploader("Upload 2 or more PDFs / পিডিএফ ফাইল আপলোড করুন...", type=["pdf"], accept_multiple_files=True)
    if pdf_files and len(pdf_files) >= 2:
        if st.button("Merge PDFs / ফাইলগুলো জোড়া দিন", type="primary", use_container_width=True):
            writer = PdfWriter()
            for pdf in pdf_files:
                reader = PdfReader(pdf)
                for page in reader.pages:
                    writer.add_page(page)
            out_pdf = io.BytesIO(); writer.write(out_pdf); writer.close()
            st.success("Successfully Merged! / সফলভাবে জোড়া দেওয়া হয়েছে!")
            st.download_button("📥 Download Merged PDF", data=out_pdf.getvalue(), file_name="merged.pdf", mime="application/pdf", use_container_width=True)

# ====================================================================
# MODULE 8: ❌ PDF Page Delete Tool
# ====================================================================
elif "8." in tool_option:
    st.markdown("### ❌ 8. PDF Page Delete Tool")
    single_pdf = st.file_uploader("Upload PDF / পিডিএফ ফাইলটি আপলোড করুন...", type=["pdf"])
    if single_pdf:
        reader = PdfReader(single_pdf); total = len(reader.pages)
        st.info(f"Total Pages / মোট পেজ সংখ্যা: {total}")
        del_page = st.number_input(f"Enter page number to delete (1 to {total}):", min_value=1, max_value=total, value=1)
        if st.button("Delete Page & Build PDF", type="primary", use_container_width=True):
            writer = PdfWriter()
            for i in range(total):
                if i != (del_page - 1):
                    writer.add_page(reader.pages[i])
            out_pdf = io.BytesIO(); writer.write(out_pdf); writer.close()
            st.success("Page Deleted Successfully!")
            st.download_button("📥 Download Edited PDF", data=out_pdf.getvalue(), file_name="edited.pdf", mime="application/pdf", use_container_width=True)

# ====================================================================
# MODULE 9: 🌐 অনলাইন সেবা ও লিঙ্কসমূহ (ভিসা, পাসপোর্ট ও দোকান অ্যাপ্লিকেশন স্পেশাল)
# ====================================================================
elif "9." in tool_option:
    st.markdown("### 🌐 9. অল-ইন-ওয়ান অনলাইন সেবা, অ্যাপ্লিকেশন ও লিঙ্ক ডিরেক্টরি")
    
    st.markdown("<div class='header-link'>🛂 পাসপোর্ট ও ভিসা ট্র্যাকিং পোর্টাল</div>", unsafe_allow_html=True)
    passport_links = {
        "ই-পাসপোর্ট নতুন আবেদন": "https://www.epassport.gov.bd",
        "পাসপোর্ট স্ট্যাটাস চেক": "https://www.epassport.gov.bd/landing",
        "বাংলাদেশ অনলাইন ভিসা (IVAC)": "https://www.visa.gov.bd",
        "ভারতীয় ভিসা আবেদন (IVAC)": "https://www.ivacbd.com",
        "ভিসা চেকিং পোর্টাল (বিদেশ)": "https://services.mofa.gov.bd"
    }
    html_p = "".join([f'<a class="link-box" href="{url}" target="_blank">{name}</a>' for name, url in passport_links.items()])
    st.markdown(html_p, unsafe_allow_html=True)
    
    st.markdown("<div class='header-link'>📝 চাকরি, এনআইডি ও নাগরিক আবেদন পোর্টাল</div>", unsafe_allow_html=True)
    gov_links = {
        "টেলিটক সরকারি চাকরি আবেদন": "http://teletalk.com.bd",
        "জন্ম ও মৃত্যু নিবন্ধন": "https://bdris.gov.bd",
        "জাতীয় পরিচয় পত্র (NID Correction)": "https://services.nidw.gov.bd",
        "ভূমি খতিয়ান ও পর্চা (e-Porcha)": "https://land.gov.bd",
        "ড্রাইভিং লাইসেন্স (BRTA BSP)": "https://bsp.brta.gov.bd",
        "অনলাইন আয়কর রেজিষ্ট্রেশন (e-TIN)": "https://secure.incometax.gov.bd",
        "করোনা টিকা কার্ড (সুরক্ষা)": "https://surokkha.gov.bd",
        "রেলওয়ে অনলাইন টিকেট": "https://eticket.railway.gov.bd",
        "শিক্ষা বোর্ড রেজাল্ট": "http://www.educationboardresults.gov.bd",
        "জাতীয় বিশ্ববিদ্যালয় (NU) ভর্তি/ফরম": "https://www.nu.ac.bd",
        "উন্মুক্ত বিশ্ববিদ্যালয় (BOU) পোর্টাল": "https://www.bou.ac.bd",
        "প্রবাসী কল্যাণ ও কর্মসংস্থান (BMET)": "https://www.probashi.gov.bd"
    }
    html_g = "".join([f'<a class="link-box" href="{url}" target="_blank">{name}</a>' for name, url in gov_links.items()])
    st.markdown(html_g, unsafe_allow_html=True)
    
    st.markdown("---")
    st.info("💡 এই ডিরেক্টরির যেকোনো লিংকে ক্লিক করলে কাস্টমারের ফর্ম সাবমিট করার অফিশিয়াল সরকারি বা প্রাতিষ্ঠানিক ওয়েব পোর্টাল নতুন ট্যাবে সরাসরি ওপেন হবে।")

# ====================================================================
# MODULE 10: ⚙️ Settings & Studio Info
# ====================================================================
else:
    st.markdown("### ⚙️ 10. স্টুডিও সিস্টেম সেটিংস ও ইনফো")
    st.success("💻 হাসানুর কম্পিউটার স্টুডিও অনলাইন ক্লাউড ড্যাশবোর্ড সফলভাবে সচল রয়েছে।")
    st.markdown("""
    <div style='background-color: #1e293b; padding: 20px; border-radius: 10px; border: 1px solid #334155;'>
        <h4>🛡️ অ্যাপ্লিকেশন প্রোফাইল ও কপিরাইট</h4>
        <p>এটি <b>হাসানুর কম্পিউটার স্টুডিও</b>-এর একটি সম্পূর্ণ নিজস্ব ও কাস্টমাইজড ডিজিটাল ওয়েব ল্যাব। এখানে ওয়ান-ক্লিক ফটো এডিটিং, ডিরেক্টরি অ্যাপ্লিকেশন লিঙ্ক ও প্রফেশনাল ডকুমেন্ট সলিউশন প্রদান করা হয়।</p>
        <ul>
            <li><b>ওয়েবসাইট টাইপ:</b> কাস্টম স্টুডিও ড্যাশবোর্ড ল্যাব</li>
            <li><b>কোর ইঞ্জিন:</b> প্রফেশনাল ফটোশপ এআই ফিল্টার, পিডিএফ আর্কিটেকচার ও ফর্ম মেকার</li>
            <li><b>লোকেশন:</b> মনিরামপুর, যশোর</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown(f"<div class='footer'>{footer_text}</div>", unsafe_allow_html=True)
