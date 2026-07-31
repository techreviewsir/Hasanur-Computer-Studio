import streamlit as st
import os
import io
from PIL import Image

# rembg ইম্পোর্ট করার চেষ্টা
try:
    from rembg import remove, new_session
    ai_session = new_session("u2net")
    REMBG_AVAILABLE = True
except Exception as e:
    REMBG_AVAILABLE = False

st.set_page_config(page_title="Hasanur Computer Studio", page_icon="💻", layout="wide")

# সেশন স্টেট ইনিশিয়ালাইজেশন
if "active_module" not in st.session_state:
    st.session_state.active_module = "1"

st.title("💻 Hasanur Computer Studio")
st.markdown("---")

# সাইডবার বা মেনু তৈরি
st.sidebar.title("মেনুবার (Menu)")
module_choice = st.sidebar.selectbox(
    "ফিচার সিলেক্ট করুন:",
    ["1. ছবির ব্যাকগ্রাউন্ড পরিবর্তন", "অন্যান্য সেবা"],
    index=0
)

if "1" in module_choice:
    st.session_state.active_module = "1"
else:
    st.session_state.active_module = "other"

# মূল ইন্টারফেসের লেআউট
col_v1, col_v2 = st.columns(2)

with col_v1:
    st.markdown("### 📷 ইনপুট ছবি")
    uploaded_file = st.file_uploader("আপনার ছবি এখানে আপলোড করুন...", type=["jpg", "jpeg", "png"])
    base_image = None
    if uploaded_file is not None:
        base_image = Image.open(uploaded_file).convert("RGBA")
        st.image(base_image, caption="Original Image", use_container_width=True)

with col_v2:
    st.markdown("### ✨ আউটপুট")

# ================= MODULE 1 =================
if st.session_state.active_module == "1":
    st.markdown("### 🪄 1. ছবির ব্যাকগ্রাউন্ড পরিবর্তন (PhotoRoom AI)")
    if base_image:
        if REMBG_AVAILABLE:
            bg_selection = st.selectbox(
                "ব্যাকগ্রাউন্ড স্টাইল সিলেক্ট করুন:", 
                ["স্বচ্ছ (Transparent/PNG)", "আকাশী (Sky Blue)", "পাসপোর্ট নীল (Studio Blue)", "অফিসিয়াল সাদা (Pure White)", "সলিড কালার (Color Picker)", "🏞️ গ্যালারি থেকে নিজস্ব কাস্টম ছবি/সিনারি"]
            )
            custom_bg_file = None
            custom_color = "#ffffff"
            if bg_selection == "সলিড কালার (Color Picker)":
                custom_color = st.color_picker("আপনার পছন্দের রঙ সিলেক্ট করুন:", "#ff4b4b")
            elif bg_selection == "🏞️ গ্যালারি থেকে নিজস্ব কাস্টম ছবি/সিনারি":
                custom_bg_file = st.file_uploader("আপনার কাঙ্খিত ব্যাকগ্রাউন্ড সিনারিটি আপলোড করুন:", type=["jpg", "jpeg", "png"], key="m1_bg")
            
            # বডি কেটে যাওয়া রোধ করার জন্য সংবেদনশীলতা কন্ট্রোল
            ai_sensitivity = st.slider("বডি সুরক্ষা ও মাস্ক সেন্সিটিভিটি (Sensitivity):", min_value=1, max_value=20, value=5, step=1)
            
            if st.button("ব্যাকগ্রাউন্ড পরিবর্তন করুন", type="primary", use_container_width=True):
                with st.spinner("সঠিকভাবে বডি ডিটেক্ট করে ব্যাকগ্রাউন্ড রিমুভ করা হচ্ছে... প্রস্তুত থাকুন..."):
                    transparent_img = remove(
                        base_image, 
                        session=ai_session, 
                        alpha_matting=True, 
                        alpha_matting_foreground_threshold=240,
                        alpha_matting_background_threshold=10,
                        alpha_matting_erode_size=ai_sensitivity
                    )
                
                if bg_selection == "স্বচ্ছ (Transparent/PNG)":
                    out = transparent_img; file_ext = "PNG"; mime_type = "image/png"; filename = "bg_removed.png"
                elif bg_selection == "🏞️ গ্যালারি থেকে নিজস্ব কাস্টম ছবি/সিনারি" and custom_bg_file is not None:
                    bg_custom = Image.open(custom_bg_file).resize(base_image.size, Image.Resampling.LANCZOS).convert("RGBA")
                    bg_custom.paste(transparent_img, (0, 0), transparent_img)
                    out = bg_custom.convert("RGB"); file_ext = "JPEG"; mime_type = "image/jpeg"; filename = "custom_bg.jpg"
                else:
                    if bg_selection == "আকাশী (Sky Blue)": hex_val = "87CEEB"
                    elif bg_selection == "পাসপোর্ট নীল (Studio Blue)": hex_val = "0033aa"
                    elif bg_selection == "অফিসিয়াল সাদা (Pure White)": hex_val = "ffffff"
                    else: hex_val = custom_color.lstrip('#')
                    bg_rgb = tuple(int(hex_val[i:i+2], 16) for i in (0, 2, 4))
                    bg = Image.new("RGBA", base_image.size, bg_rgb + (255,))
                    bg.paste(transparent_img, (0, 0), transparent_img)
                    out = bg.convert("RGB"); file_ext = "JPEG"; mime_type = "image/jpeg"; filename = "new_bg.jpg"
                
                with col_v2:
                    st.image(out, caption="Output (Fixed Body)", use_container_width=True)
                    buf = io.BytesIO()
                    if file_ext == "PNG": out.save(buf, format=file_ext)
                    else: out.save(buf, format=file_ext, quality=100, subsampling=0)
                    st.download_button("📥 ডাউনলোড করুন", data=buf.getvalue(), file_name=filename, mime=mime_type, use_container_width=True)
        else:
            st.error("rembg মডিউল ইনস্টল করা নেই।")
    else:
        with col_v2:
            st.info("দয়া করে বাম দিক থেকে একটি ছবি আপলোড করুন।")

else:
    with col_v2:
        st.info("এই সেকশনটি পরবর্তীতে আপডেট করা হবে।")
