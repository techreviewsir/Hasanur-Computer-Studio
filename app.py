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

# সুন্দর স্টুডিও থিম ও সিএসএস
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    h1 { color: #1e3a8a; font-family: 'Segoe UI', sans-serif; text-align: center; margin-bottom: 5px; }
    .subtitle { text-align: center; color: #475569; font-size: 16px; margin-bottom: 5px; font-weight: 500; }
    .contact-info { text-align: center; color: #2563eb; font-size: 15px; margin-bottom: 25px; font-weight: bold; }
    .footer { text-align: center; margin-top: 60px; padding: 20px; color: #64748b; border-top: 1px solid #e2e8f0; font-size: 14px; }
    div[data-testid="stSidebarNav"] { display: none; }
    </style>
""", unsafe_allow_html=True)

# হেডার ও স্টুডিও ব্র্যান্ডিং
st.markdown("<h1>📸 হাসানুর কম্পিউটার স্টুডিও প্রফেশনাল ফটো ও ডকুমেন্ট ল্যাব</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>📍 মনিরামপুর, যশোর | ওয়ান-ক্লিক ফটো এডিটিং ও প্রফেশনাল পিডিএফ টুলস</div>", unsafe_allow_html=True)
st.markdown("<div class='contact-info'>📞 হটলাইন: 01743614359</div>", unsafe_allow_html=True)

# 🛠️ বাম সাইডবারে ফটোশপ ও পিডিএফ টুলবক্স (পরপর সাজানো)
st.sidebar.title("🛠️ স্টুডিও টুলবক্স")
st.sidebar.markdown("---")

# ১. মেইন ক্যাটাগরি সিলেক্টর
app_mode = st.sidebar.radio("কাজ নির্ধারণ করুন:", ("📷 ফটো প্রসেসিং ল্যাব", "📄 পিডিএফ (PDF) এডিটর টুলস"))
st.sidebar.markdown("---")

# ====================================================================
# 📷 সেকশন ১: ফটো প্রসেসিং ল্যাব
# ====================================================================
if app_mode == "📷 ফটো প্রসেসিং ল্যাব":
    tool_option = st.sidebar.radio(
        "মূল ফটো টুল সিলেক্ট করুন:",
        (
            "১. ব্যাকগ্রাউন্ড চেঞ্জ ও পাসপোর্ট সাইজ",
            "২. ডিএসএলআর ব্যাকগ্রাউন্ড ব্লার (Blur)",
            "৩. ঘোলা ছবি পরিষ্কার ও লাইটিং (Enhance)",
            "৪. আইডি কার্ড সোজা ও ক্রপ করা",
            "৫. কাস্টম রোটেশন ও ফ্লিপ (Rotate)",
            "৬. অ্যাডভান্সড কালার ও ফিল্টার"
        )
    )
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎛️ টুল কন্ট্রোল প্যানেল")

    uploaded_file = st.file_uploader("এডিট করার জন্য আপনার ছবিটি এখানে আপলোড করুন...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        base_image = Image.open(uploaded_file)
        processed_image = base_image.copy()
        
        # টুল অনুসারে সাইডবার অপশন
        if "১." in tool_option:
            bg_choice = st.sidebar.color_picker("১. ব্যাকগ্রাউন্ডের রঙ নির্বাচন:", "#0080FF")
            photo_type = st.sidebar.radio("২. আউটপুট সাইজ নির্ধারণ:", ("পাসপোর্ট সাইজ (413x531 px)", "স্ট্যাম্প সাইজ (236x295 px)", "মূল রেজোলিউশন (HD)"))
            apply_btn = st.sidebar.button("💥 এআই প্রসেস চালু করুন", use_container_width=True)
        elif "২." in tool_option:
            blur_amount = st.sidebar.slider("১. ব্লারের পরিমাণ (Blur Radius):", 1, 30, 15)
            apply_btn = st.sidebar.button("✨ ব্যাকগ্রাউন্ড ব্লার করুন", use_container_width=True)
        elif "৩." in tool_option:
            sharpness_val = st.sidebar.slider("১. শার্পনেস (ঘোলা দূরীকরণ):", 1.0, 5.0, 2.0, 0.5)
            contrast_val = st.sidebar.slider("২. লাইটিং কনট্রাস্ট:", 0.5, 3.0, 1.2, 0.1)
            apply_btn = st.sidebar.button("⚡ ছবি পরিষ্কার করুন", use_container_width=True)
        elif "৪." in tool_option:
            apply_btn = st.sidebar.button("📐 আইডি কার্ড সোজা করুন", use_container_width=True)
        elif "৫." in tool_option:
            rotate_angle = st.sidebar.slider("১. কাস্টম ডিগ্রি ঘোরান (Rotate):", -180, 180, 0, 1)
            flip_option = st.sidebar.radio("২. ছবি ফ্লিপ করুন:", ("স্বাভাবিক", "ডানে-বামে ফ্লিপ (Horizontal)", "উপরে-নিচে ফ্লিপ (Vertical)"))
            apply_btn = st.sidebar.button("🔄 রোটেশন প্রয়োগ", use_container_width=True)
        elif "৬." in tool_option:
            brightness_val = st.sidebar.slider("☀️ উজ্জ্বলতা (Brightness):", 0.5, 2.0, 1.0, 0.1)
            saturation_val = st.sidebar.slider("🎨 রঙের গভীরতা (Saturation):", 0.5, 2.0, 1.0, 0.1)
            filter_type = st.sidebar.selectbox("🎬 ফিল্টার ইফেক্ট:", ["None", "সাদাকালো (Black & White)", "ভিন্টেজ ক্লাসিক (Sepia)"])
            apply_btn = st.sidebar.button("🎨 কালার ফিল্টার সেট করুন", use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 🖼️ কাস্টমারের মূল ছবি")
            st.image(base_image, use_container_width=True)

        with col2:
            st.markdown("### ✨ ফটোশপ ফাইনাল আউটপুট (HD)")
            if apply_btn:
                with st.spinner("ফটোশপ ইঞ্জিন প্রসেস করছে..."):
                    if "১." in tool_option:
                        if not REMBG_AVAILABLE:
                            st.error("⚠️ AI ব্যাকগ্রাউন্ড রিমুভার ইঞ্জিনটি লোড হচ্ছে।")
                        else:
                            h = bg_choice.lstrip('#')
                            bg_rgb = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
                            output_transparent = remove(base_image)
                            target_size = (413, 531) if "পাসপোর্ট" in photo_type else ((236, 295) if "স্ট্যাম্প" in photo_type else base_image.size)
                            background = Image.new("RGBA", target_size, bg_rgb + (255,))
                            output_transparent.thumbnail(target_size, Image.Resampling.LANCZOS)
                            x = (target_size[0] - output_transparent.width) // 2
                            y = (target_size[1] - output_transparent.height) // 2
                            background.paste(output_transparent, (x, y), output_transparent)
                            processed_image = background.convert("RGB")
                    elif "২." in tool_option:
                        if not REMBG_AVAILABLE:
                            st.error("⚠️ AI ইঞ্জিন লোড হচ্ছে।")
                        else:
                            blurred_bg = base_image.filter(ImageFilter.GaussianBlur(radius=blur_amount))
                            transparent_subject = remove(base_image)
                            combined = blurred_bg.convert("RGBA")
                            combined.paste(transparent_subject, (0, 0), transparent_subject)
                            processed_image = combined.convert("RGB")
                    elif "৩." in tool_option:
                        enhancer_sharp = ImageEnhance.Sharpness(base_image)
                        sharp_img = enhancer_sharp.enhance(sharpness_val)
                        enhancer_contrast = ImageEnhance.Contrast(sharp_img)
                        processed_image = enhancer_contrast.enhance(contrast_val)
                    elif "৪." in tool_option:
                        open_cv_image = np.array(base_image.convert('RGB'))[:, :, ::-1].copy()
                        gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
                        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
                        edged = cv2.Canny(blurred, 50, 200)
                        contours, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                        contours = sorted(contours, key=cv2.contourArea, reverse=True)
                        card_contour = None
                        for c in contours:
                            peri = cv2.arcLength(c, True)
                            approx = cv2.approxPolyDP(c, 0.02 * peri, True)
                            if len(approx) == 4:
                                card_contour = approx
                                break
                        if card_contour is not None:
                            pts = card_contour.reshape(4, 2)
                            rect = np.zeros((4, 2), dtype="float32")
                            s = pts.sum(axis=1)
                            rect[0] = pts[np.argmin(s)]; rect[2] = pts[np.argmax(s)]
                            diff = np.diff(pts, axis=1)
                            rect[1] = pts[np.argmin(diff)]; rect[3] = pts[np.argmax(diff)]
                            (tl, tr, br, bl) = rect
                            widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
                            widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
                            max_width = max(int(widthA), int(widthB))
                            heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
                            heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
                            max_height = max(int(heightA), int(heightB))
                            dst = np.array([[0, 0], [max_width - 1, 0], [max_width - 1, max_height - 1], [0, max_height - 1]], dtype="float32")
                            M = cv2.getPerspectiveTransform(rect, dst)
                            warped = cv2.warpPerspective(open_cv_image, M, (max_width, max_height))
                            processed_image = Image.fromarray(cv2.cvtColor(warped, cv2.COLOR_BGR2RGB))
                        else:
                            st.warning("⚠️ আইডি CARD সনাক্ত করা যায়নি।")
                            processed_image = base_image
                    elif "৫." in tool_option:
                        if rotate_angle != 0:
                            processed_image = base_image.rotate(rotate_angle, expand=True, resample=Image.Resampling.BICUBIC)
                        if flip_option == "ডানে-বামে ফ্লিপ (Horizontal)":
                            processed_image = processed_image.transpose(Image.FLIP_LEFT_RIGHT)
                        elif flip_option == "উপরে-নিচে ফ্লিপ (Vertical)":
                            processed_image = processed_image.transpose(Image.FLIP_TOP_BOTTOM)
                    elif "৬." in tool_option:
                        enhancer_b = ImageEnhance.Brightness(base_image)
                        img_b = enhancer_b.enhance(brightness_val)
                        enhancer_s = ImageEnhance.Color(img_b)
                        processed_image = enhancer_s.enhance(saturation_val)
                        if filter_type == "সাদাকালো (Black & White)":
                            processed_image = processed_image.convert("L")
                        elif filter_type == "ভিন্টেজ ক্লাসিক (Sepia)":
                            np_img = np.array(processed_image)
                            limg = cv2.transform(np_img, np.matrix([[0.393, 0.769, 0.189], [0.349, 0.686, 0.168], [0.272, 0.534, 0.131]]))
                            limg[limg > 255] = 255
                            processed_image = Image.fromarray(limg.astype(np.uint8))

                    st.image(processed_image, use_container_width=True)
                    buf = io.BytesIO()
                    save_image = processed_image.convert("RGB") if processed_image.mode in ("RGBA", "P") else processed_image
                    save_image.save(buf, format="JPEG", quality=100, subsampling=0)
                    st.success("✅ ছবি এডিটিং সফল হয়েছে!")
                    st.download_button(label="📥 ল্যাব কোয়ালিটি HD ডাউনলোড করুন", data=buf.getvalue(), file_name="hasanur_studio_hd.jpg", mime="image/jpeg", use_container_width=True)
            else:
                st.info("👈 বাম পাশের টুলবক্স থেকে অপশন সিলেক্ট করে বাটন ক্লিক করুন।")
                st.image(base_image, use_container_width=True)

# ====================================================================
# 📄 সেকশন ২: পিডিএফ (PDF) এডিটর টুলস
# ====================================================================
else:
    pdf_option = st.sidebar.radio(
        "পিডিএফ টুলস:",
        (
            "১. একাধিক পিডিএফ জোড়া দেওয়া (Merge)",
            "২. নির্দিষ্ট পেজ বাদ দেওয়া (Delete Page)",
            "৩. পিডিএফ থেকে টেক্সট ও তথ্য দেখা"
        )
    )
    st.sidebar.markdown("---")

    st.markdown(f"### 📄 {pdf_option}")

    # --- ১. পিডিএফ জোড়া দেওয়া ---
    if "১." in pdf_option:
        st.info("💡 এখানে ২টি বা তার বেশি আলাদা পিডিএফ আপলোড করে একসাথে জোড়া (Merge) লাগিয়ে একটি ফাইলে রূপান্তর করতে পারবেন।")
        pdf_files = st.file_uploader("আপনার পিডিএফ ফাইলগুলো একসাথে সিলেক্ট করে আপলোড করুন...", type=["pdf"], accept_multiple_files=True)
        
        if pdf_files and len(pdf_files) >= 2:
            if st.button("🔗 পিডিএফ ফাইলগুলো একসাথে জোড়া দিন"):
                with st.spinner("পিডিএফ মার্জ করা হচ্ছে..."):
                    writer = PdfWriter()
                    for pdf in pdf_files:
                        reader = PdfReader(pdf)
                        for page in reader.pages:
                            writer.add_page(page)
                    
                    output_pdf = io.BytesIO()
                    writer.write(output_pdf)
                    writer.close()
                    
                    st.success("✅ সফলভাবে ফাইলগুলো জোড়া দেওয়া হয়েছে!")
                    st.download_button(
                        label="📥 মার্জ করা পিডিএফ ডাউনলোড করুন",
                        data=output_pdf.getvalue(),
                        file_name="hasanur_studio_merged.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
        elif pdf_files:
            st.warning("⚠️ জোড়া দেওয়ার জন্য কমপক্ষে ২টি পিডিএফ ফাইল আপলোড করতে হবে।")

    # --- ২. পেজ বাদ দেওয়া ---
    elif "২." in pdf_option:
        st.info("💡 কোনো বড় পিডিএফ ফাইল থেকে অপ্রয়োজনীয় পেজ বাদ দিয়ে নতুন একটি পিডিএফ তৈরি করার টুল।")
        single_pdf = st.file_uploader("যে পিডিএফ থেকে পেজ বাদ দিতে চান সেটি আপলোড করুন...", type=["pdf"])
        
        if single_pdf is not None:
            reader = PdfReader(single_pdf)
            total_pages = len(reader.pages)
            st.success(f"📊 এই ফাইলটিতে মোট {total_pages}টি পেজ আছে।")
            
            page_to_delete = st.number_input(f"কোন নম্বর পেজটি বাদ দিতে চান? (১ থেকে {total_pages} এর মধ্যে)", min_value=1, max_value=total_pages, value=1)
            
            if st.button("❌ পেজ বাদ দিয়ে নতুন ফাইল তৈরি করুন"):
                with st.spinner("পেজ বাদ দেওয়া হচ্ছে..."):
                    writer = PdfWriter()
                    delete_index = page_to_delete - 1 
                    
                    for i in range(total_pages):
                        if i != delete_index:
                            writer.add_page(reader.pages[i])
                    
                    output_pdf = io.BytesIO()
                    writer.write(output_pdf)
                    writer.close()
                    
                    st.success(f"✅ সফলভাবে {page_to_delete} নম্বর পেজটি বাদ দেওয়া হয়েছে!")
                    st.download_button(
                        label="📥 নতুন এডিটেড পিডিএফ ডাউনলোড করুন",
                        data=output_pdf.getvalue(),
                        file_name="hasanur_studio_edited.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )

    # --- ৩. পিডিএফ ইনফো ও টেক্সট ভিউ ---
    elif "৩." in pdf_option:
        st.info("💡 এই টুলের মাধ্যমে যেকোনো পিডিএফ-এর ভেতরে কী কী টেক্সট বা লেখা আছে তা সরাসরি স্ক্রিনে দেখতে পারবেন।")
        view_pdf = st.file_uploader("পিডিএফ ফাইলটি আপলোড করুন...", type=["pdf"])
        
        if view_pdf is not None:
            reader = PdfReader(view_pdf)
            st.success(f"📄 ফাইলে মোট পেজ সংখ্যা: {len(reader.pages)}")
            
            page_num = st.selectbox("কোন পেজের লেখা দেখতে চান সিলেক্ট করুন:", list(range(1, len(reader.pages) + 1)))
            
            with st.spinner("টেক্সট এক্সট্রাক্ট করা হচ্ছে..."):
                current_page = reader.pages[page_num - 1]
                text = current_page.extract_text()
                
                st.markdown(f"#### 📝 পেজ নম্বর {page_num} এর টেক্সট:")
                if text.strip():
                    st.code(text, language="text")
                else:
                    st.warning("⚠️ এই পেজে কোনো কপি করার মতো টেক্সট পাওয়া যায়নি (এটি স্ক্যান করা ছবি হতে পারে)।")

st.markdown("<div class='footer'>© ২০২৬ হাসানুর কম্পিউটার স্টুডিও, মনিরামপুর, যশোর। অল রাইটস রিজার্ভড।</div>", unsafe_allow_html=True)
