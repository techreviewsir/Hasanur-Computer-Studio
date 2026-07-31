import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageEnhance
import io

# rembg এরর হ্যান্ডেল করার জন্য নিরাপদ ইম্পোর্ট
try:
    from rembg import remove
    REMBG_AVAILABLE = True
except Exception:
    REMBG_AVAILABLE = False

# পেজ কনফিগারেশন
st.set_page_config(page_title="হাসানুর কম্পিউটার স্টুডিও", layout="wide", page_icon="📸")

# CSS স্টাইল
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    h1 { color: #1e3a8a; font-family: 'Segoe UI', sans-serif; text-align: center; margin-bottom: 5px; }
    .subtitle { text-align: center; color: #475569; font-size: 16px; margin-bottom: 5px; font-weight: 500; }
    .contact-info { text-align: center; color: #2563eb; font-size: 15px; margin-bottom: 25px; font-weight: bold; }
    .footer { text-align: center; margin-top: 60px; padding: 20px; color: #64748b; border-top: 1px solid #e2e8f0; font-size: 14px; }
    </style>
""", unsafe_allow_html=True)

# ব্র্যান্ডিং তথ্য
st.markdown("<h1>📸 হাসানুর কম্পিউটার স্টুডিও স্মার্ট ফটো এডিটর</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>📍 মনিরামপুর, যশোর | অল-ইন-ওয়ান ফ্রি ফটো প্রসেসিংツール</div>", unsafe_allow_html=True)
st.markdown("<div class='contact-info'>📞 যোগাযোগ: 01743614359</div>", unsafe_allow_html=True)

# সাইডবার
option = st.sidebar.selectbox(
    "ফিচার নির্বাচন করুন:",
    ("ব্যাকগ্রাউন্ড পরিবর্তন ও পাসপোর্ট সাইজ", "আইডি কার্ড সোজা করা", "বেসিক এডিটিং ও ফিল্টার")
)

uploaded_file = st.file_uploader("আপনার ছবিটি এখানে আপলোড করুন...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🖼️ মূল ছবি")
        st.image(image, use_container_width=True)

    with col2:
        st.subheader("✨ এডিটেড ফলাফল")
        
        # --- ১. ব্যাকগ্রাউন্ড মেকার ---
        if option == "ব্যাকগ্রাউন্ড পরিবর্তন ও পাসপোর্ট সাইজ":
            bg_choice = st.color_picker("ব্যাকগ্রাউন্ডের রঙ সিলেক্ট করুন", "#0080FF")
            photo_type = st.radio("ছবির সাইজ:", ("পাসপোর্ট সাইজ (413x531 px)", "স্ট্যাম্প সাইজ (236x295 px)", "মূল সাইজ"))
            
            if st.button("AI প্রসেস শুরু করুন"):
                if not REMBG_AVAILABLE:
                    st.error("⚠️ আপনার কম্পিউটারে AI ব্যাকগ্রাউন্ড রিমুভার ইঞ্জিনটি সম্পূর্ণ ইনস্টল হয়নি। তবে গিটহাবে আপলোড করলে এটি স্বয়ংক্রিয়ভাবে কাজ করবে। বাকি ফিচারগুলো নিচে চেক করুন।")
                else:
                    with st.spinner("AI ব্যাকগ্রাউন্ড পরিবর্তন করছে..."):
                        h = bg_choice.lstrip('#')
                        bg_rgb = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
                        output_transparent = remove(image)
                        target_size = (413, 531) if "পাসপোর্ট" in photo_type else ((236, 295) if "স্ট্যাম্প" in photo_type else image.size)
                        
                        background = Image.new("RGBA", target_size, bg_rgb + (255,))
                        output_transparent.thumbnail(target_size, Image.Resampling.LANCZOS)
                        x = (target_size[0] - output_transparent.width) // 2
                        y = (target_size[1] - output_transparent.height) // 2
                        background.paste(output_transparent, (x, y), output_transparent)
                        
                        final_output = background.convert("RGB")
                        st.image(final_output, use_container_width=True)
                        
                        buf = io.BytesIO()
                        final_output.save(buf, format="JPEG")
                        st.download_button("📥 ডাউনলোড করুন", data=buf.getvalue(), file_name="hasanur_studio.jpg", mime="image/jpeg")

        # --- ২. আইডি কার্ড সোজা করা ---
        elif option == "আইডি কার্ড সোজা করা":
            if st.button("আইডি কার্ড সোজা করুন"):
                open_cv_image = np.array(image.convert('RGB'))[:, :, ::-1].copy()
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
                    rect[0] = pts[np.argmin(s)]
                    rect[2] = pts[np.argmax(s)]
                    diff = np.diff(pts, axis=1)
                    rect[1] = pts[np.argmin(diff)]
                    rect[3] = pts[np.argmax(diff)]
                    
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
                    
                    result_img = Image.fromarray(cv2.cvtColor(warped, cv2.COLOR_BGR2RGB))
                    st.image(result_img, use_container_width=True)
                else:
                    st.warning("⚠️ আইডি কার্ড সনাক্ত করা যায়নি। ছবি সোজা করে তুলুন।")

        # --- ৩. বেসিক এডিটিং ---
        elif option == "বেসিক এডিটিং ও ফিল্টার":
            brightness = st.slider("☀️ ব্রাইটনেস", 0.5, 2.0, 1.0)
            contrast = st.slider("🌗 কনট্রাস্ট", 0.5, 2.0, 1.0)
            
            enhancer = ImageEnhance.Brightness(image)
            edited_img = enhancer.enhance(brightness)
            enhancer = ImageEnhance.Contrast(edited_img)
            edited_img = enhancer.enhance(contrast)
            
            st.image(edited_img, use_container_width=True)

st.markdown("<div class='footer'>© ২০২৬ হাসানুর কম্পিউটার স্টুডিও, মনিরামপুর, যশোর। যোগাযোগ: ০১৭৪৩৬১৪৩৫৯</div>", unsafe_allow_html=True)
