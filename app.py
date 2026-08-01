elif app_mode == 6:
    st.header("🧾 দোকানের ক্যাশ মেমো / রশিদ জেনারেটর (Items, Serial & Warranty)")
    st.info("💡 টিপস: দোকানের নাম, ঠিকানা, ক্রেতার তথ্য এবং প্রয়োজনীয় আইটেম যোগ করুন। প্রতিটি পণ্যের সিরিয়াল নম্বর (S/N) এবং ওয়ারেন্টির তথ্য দিন।")

    st.markdown("### 🏪 দোকানের তথ্য (Shop Info)")
    shop_name = st.text_input("দোকানের নাম (Shop Name)", "হাসানুর কম্পিউটার স্টুডিও")
    shop_address = st.text_input("দোকানের ঠিকানা ও ফোন (Address & Phone)", "দিঘীরপাড়, মনিরামপুর, যশোর | মোবাইল: ০১৭৪৩-৬১৪৩৫৯")

    st.markdown("---")
    st.markdown("### 🛒 ক্রেতা ও পণ্যের তালিকা (Customer & Items with Serial & Warranty)")
    c_name = st.text_input("গ্রাহকের নাম (Customer Name)", "মোঃ রহিম")
    c_phone = st.text_input("মোবাইল নম্বর (Phone Number)", "01700000000")

    if 'memo_items' not in st.session_state:
        st.session_state.memo_items = [
            {'name': 'ল্যামিনেশন ও প্রিন্ট', 'serial': 'N/A', 'price': 150, 'has_warranty': 'না', 'warranty_period': '-'},
            {'name': 'এইচপি প্রিন্টার', 'serial': 'HP-SN987654', 'price': 8500, 'has_warranty': 'হ্যাঁ', 'warranty_period': '১ বছর'}
        ]

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("➕ নতুন আইটেম যোগ করুন (Add Item)"):
            st.session_state.memo_items.append({'name': '', 'serial': '', 'price': 0, 'has_warranty': 'না', 'warranty_period': '-'})
    with col_btn2:
        if len(st.session_state.memo_items) > 1 and st.button("➖ শেষের আইটেমটি বাদ দিন"):
            st.session_state.memo_items.pop()

    updated_items = []
    total_amount = 0

    for i, item in enumerate(st.session_state.memo_items):
        st.markdown(f"**আইটেম #{i+1}**")
        c1, c2, c3, c4, c5 = st.columns([3, 2, 2, 2, 2])
        with c1:
            item_name = st.text_input(f"পণ্যের নাম", item['name'], key=f"item_name_{i}")
        with c2:
            item_serial = st.text_input(f"সিরিয়াল নম্বর (S/N)", item.get('serial', ''), key=f"item_serial_{i}")
        with c3:
            item_price = st.number_input(f"মূল্য (TK)", 0, 1000000, int(item['price']), key=f"item_price_{i}")
        with c4:
            default_w_idx = 0 if item['has_warranty'] == 'হ্যাঁ' else 1
            has_war = st.selectbox(f"ওয়ারেন্টি?", ["হ্যাঁ", "না"], index=default_w_idx, key=f"has_war_{i}")
        with c5:
            default_period = item['warranty_period'] if item['warranty_period'] else "১ বছর"
            war_period = st.text_input(f"ওয়ারেন্টি মেয়াদ", default_period, key=f"war_period_{i}")
        
        updated_items.append({
            'name': item_name, 
            'serial': item_serial if item_serial else "N/A",
            'price': item_price, 
            'has_warranty': has_war, 
            'warranty_period': war_period if has_war == "হ্যাঁ" else "প্রযোজ্য নয়"
        })
        total_amount += item_price
        st.markdown("---")

    if st.button("🖨️ ক্যাশ মেমো জেনারেট করুন (A4 Print Ready)"):
        # টেবিল রো তৈরির জন্য আলাদা লুপ
        rows_html = ""
        for idx, itm in enumerate(updated_items):
            rows_html += (
                "<tr>"
                f"<td style='padding: 10px; border-bottom: 1px solid #ddd; text-align: center;'>{idx + 1}</td>"
                f"<td style='padding: 10px; border-bottom: 1px solid #ddd;'>{itm['name']}</td>"
                f"<td style='padding: 10px; border-bottom: 1px solid #ddd; text-align: center; font-family: monospace; font-weight: bold;'>{itm['serial']}</td>"
                f"<td style='padding: 10px; border-bottom: 1px solid #ddd; text-align: center;'>{itm['has_warranty']} ({itm['warranty_period']})</td>"
                f"<td style='padding: 10px; border-bottom: 1px solid #ddd; text-align: right;'>{itm['price']} TK</td>"
                "</tr>"
            )

        # নিরাপদভাবে সিঙ্গেল ও ডাবল কোটেশন হ্যান্ডেল করে এইচটিএমএল টেমপ্লেট তৈরি
        final_memo_html = f"""
        <div class="a4-paper-box" style="border: 3px solid #0B50FA;">
            <div style="text-align:center;">
                <h2 style="color:#0B50FA; margin:0; font-size:28px;">{shop_name}</h2>
                <p style="font-size:14px; margin:5px 0; color:#333;">{shop_address}</p>
                <hr style="border: 1px solid #0B50FA; width:70%; margin:15px auto;">
                <h3 style="background:#0B50FA; color:white; display:inline-block; padding:6px 25px; border-radius:4px; margin:5px 0;">ক্যাশ মেমো / রসিদ</h3>
            </div>
            
            <div style="margin-top:25px; display:flex; justify-content:space-between; font-size:14px; background:#f8f9fa; padding:12px; border-radius:5px;">
                <div>
                    <p style="margin:3px 0;"><b>গ্রাহকের নাম:</b> {c_name}</p>
                    <p style="margin:3px 0;"><b>মোবাইল নম্বর:</b> {c_phone}</p>
                </div>
                <div style="text-align:right;">
                    <p style="margin:3px 0;"><b>তারিখ:</b> {date.today().strftime('%d-%m-%Y')}</p>
                </div>
            </div>

            <table style="width:100%; border-collapse: collapse; margin-top:20px; font-size:14px;">
                <thead>
                    <tr style="background:#0B50FA; color:white;">
                        <th style="padding: 12px; text-align: center; width: 8%;">ক্রমিক</th>
                        <th style="padding: 12px; text-align: left; width: 32%;">পণ্যের বিবরণ / সেবার নাম</th>
                        <th style="padding: 12px; text-align: center; width: 20%;">সিরিয়াল নম্বর (S/N)</th>
                        <th style="padding: 12px; text-align: center; width: 22%;">ওয়ারেন্টি স্ট্যাটাস ও মেয়াদ</th>
                        <th style="padding: 12px; text-align: right; width: 18%;">মূল্য</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>

            <div style="margin-top: 25px; text-align: right; font-size: 16px; background:#f1f3f5; padding: 12px; border-radius: 5px;">
                <b>সর্বমোট প্রদেয় টাকা (Total): <span style="color:red; font-size:19px;">{total_amount} TK</span></b>
            </div>

            <div style="margin-top: 120px; display: flex; justify-content: space-between; font-size: 14px;">
                <div>
                    <p style="border-top: 1px dashed black; padding-top: 5px; display: inline-block;">গ্রাহকের স্বাক্ষর</p>
                </div>
                <div style="text-align: right;">
                    <p style="border-top: 1px solid black; padding-top: 5px; display: inline-block; font-weight: bold;">বিক্রেতার স্বাক্ষর / সিল</p>
                </div>
            </div>
        </div>
        """
        
        st.markdown(final_memo_html, unsafe_allow_html=True)
        st.success("✅ ফুল-উইথ A4 ক্যাশ মেমো সফলভাবে জেনারেট হয়েছে!")
