import streamlit as st
import sqlite3

DB_FILE = "prices_database.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            store TEXT NOT NULL,
            title TEXT NOT NULL,
            price REAL NOT NULL,
            query TEXT NOT NULL
        )
    """)
    conn.commit()
    
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        sample_data = [
            # زيوت عباد الشمس فقط
            ("سوبرماركت سعودي", "زيت كريستال عباد شمس 1 لتر", 87.00, "زيت"),
            ("أوسكار ستورز", "زيت كريستال عباد شمس 2.2 لتر", 185.00, "زيت"),

            # أرز ومكرونة (ريجينا وأرز المصري والضحى للأرز)
            ("سوبرماركت سعودي", "أرز المصري 1 كجم", 32.00, "أرز"),
            ("أوسكار ستورز", "أرز الضحى 1 كجم", 35.00, "أرز"),
            ("سوبرماركت سعودي", "مكرونة ريجينا 400جم", 23.00, "مكرونة"),
            ("أوسكار ستورز", "مكرونة ريجينا 1 كجم", 54.00, "مكرونة"),

            # دقيق وسكر
            ("سوبرماركت سعودي", "دقيق السوهاجي فاخر 1 كجم", 24.00, "دقيق"),
            ("أوسكار ستورز", "دقيق السوهاجي فاخر 1 كجم", 25.50, "دقيق"),
            ("سوبرماركت سعودي", "سكر الأبيض الأسيوطي 1 كجم", 27.00, "سكر"),
            ("أوسكار ستورز", "سكر الضحى 1 كجم", 30.00, "سكر"),

            # أجبان ولحوم مصنعة
            ("سوبرماركت سعودي", "جبنة شيدر نيوزيلندي مستوردة (كيلو)", 450.00, "أجبان"),
            ("أوسكار ستورز", "جبنة شيدر نيوزيلندي بريزيدنت (200جم)", 110.00, "أجبان"),
            ("سوبرماركت سعودي", "روستو لحم حلواني (كيلو)", 380.00, "لحوم مصنعة"),
            ("أوسكار ستورز", "روستو لحم حلواني (عبوة 250جم)", 98.00, "لحوم مصنعة"),
            ("سوبرماركت سعودي", "بسطرمة حلواني ممتازة (كيلو)", 460.00, "لحوم مصنعة"),
            ("أوسكار ستورز", "بسطرمة حلواني فاخرة (250جم)", 125.00, "لحوم مصنعة"),

            # شاي
            ("أوسكار ستورز", "شاي أحمد تي أكياس 100 فتلة", 165.00, "شاي"),
            ("سوبرماركت سعودي", "شاي أحمد تي نكهة إيرل جراي 100 فتلة", 175.00, "شاي"),

            # منتجات العناية والنظافة
            ("سوبرماركت سعودي", "مناديل ورق وايت عبوة اقتصادية (5 رولات)", 65.00, "مناديل"),
            ("أوسكار ستورز", "مناديل ورق وايت مفرودة (550 منديل)", 48.00, "مناديل"),
            ("أمازون مصر", "كبسولات غسيل أطباق فينيش كوانتوم 40 كبسولة", 320.00, "غسيل أطباق"),
            ("سوبرماركت سعودي", "كبسولات غسيل أطباق فينيش 20 كبسولة", 175.00, "غسيل أطباق"),
            ("سوبرماركت سعودي", "مسحوق غسيل باهي أتوماتيك 2.5 كجم", 110.00, "مسحوق غسيل"),
            ("أوسكار ستورز", "مسحوق غسيل باهي أتوماتيك 5 كجم", 210.00, "مسحوق غسيل"),
            ("سوبرماركت سعودي", "مسحوق غسيل باهي اليدوي 1 كجم", 45.00, "مسحوق غسيل"),
            ("سوبرماركت سعودي", "سائل غسيل ملابس أوكسي جل 2.5 لتر", 135.00, "سائل غسيل"),
            ("أوسكار ستورز", "سائل غسيل ملابس أوكسي جل 3 لتر", 155.00, "سائل غسيل")
        ]
        cursor.executemany("INSERT INTO products (store, title, price, query) VALUES (?, ?, ?, ?)", sample_data)
        conn.commit()
    conn.close()

def get_cheapest_items(search_term="", sort_option="السعر: من الأرخص للأغلى"):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    if sort_option == "المكان (المتجر)":
        order_sql = "store ASC, price ASC"
    elif sort_option == "اسم المنتج":
        order_sql = "title ASC"
    else:
        order_sql = "price ASC"
        
    if search_term:
        query = f"""
            WITH ranked AS (
                SELECT store, title, price, query,
                       ROW_NUMBER() OVER(PARTITION BY title ORDER BY price ASC) as rn
                FROM products
                WHERE (query LIKE ? OR title LIKE ?) 
                  AND title NOT LIKE '%الملكة%' 
                  AND title NOT LIKE '%مكرونة الضحى%'
                  AND title NOT LIKE '%جهينة%'
                  AND title NOT LIKE '%بخيره%'
                  AND title NOT LIKE '%سمن%'
                  AND title NOT LIKE '%روابي%'
                  AND title NOT LIKE '%سلايت%'
                  AND title NOT LIKE '%عافية%'
                  AND title NOT LIKE '%زيت ذرة%'
            )
            SELECT store, title, price, query FROM ranked 
            WHERE rn = 1 
            ORDER BY {order_sql}
        """
        cursor.execute(query, (f"%{search_term}%", f"%{search_term}%"))
    else:
        query = f"""
            WITH ranked AS (
                SELECT store, title, price, query,
                       ROW_NUMBER() OVER(PARTITION BY title ORDER BY price ASC) as rn
                FROM products
                WHERE title NOT LIKE '%الملكة%' 
                  AND title NOT LIKE '%مكرونة الضحى%'
                  AND title NOT LIKE '%جهينة%'
                  AND title NOT LIKE '%بخيره%'
                  AND title NOT LIKE '%سمن%'
                  AND title NOT LIKE '%روابي%'
                  AND title NOT LIKE '%سلايت%'
                  AND title NOT LIKE '%عافية%'
                  AND title NOT LIKE '%زيت ذرة%'
            )
            SELECT store, title, price, query FROM ranked 
            WHERE rn = 1 
            ORDER BY {order_sql}
        """
        cursor.execute(query)
        
    rows = cursor.fetchall()
    conn.close()
    return rows

def add_new_product(store, title, price, query):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (store, title, price, query) VALUES (?, ?, ?, ?)", (store, title, price, query))
    conn.commit()
    conn.close()

# إعدادات واجهة الويب
st.set_page_config(page_title="داشبورد مقارنة الأسعار", page_icon="🛒", layout="wide")
init_db()

st.title("🛒 الداشبورد التفاعلية لمقارنة الأسعار (المتاجر المصرية)")
st.markdown("---")

# القائمة الجانبية للبحث والترتيب
st.sidebar.header("🔍 خيارات البحث والترتيب")
search_query = st.sidebar.text_input("ابحث عن منتج (مثل: باهي، أوكسي، كريستال، شيدر):", "")
sort_choice = st.sidebar.selectbox("ترتيب النتائج حسب:", ["السعر: من الأرخص للأغلى", "المكان (المتجر)", "اسم المنتج"])

# زر لإعادة تهيئة وتنظيف القاعدة
if st.sidebar.button("🔄 إعادة تهيئة وتنظيف القاعدة"):
    import os
    if os.path.exists(DB_FILE):
        conn = sqlite3.connect(DB_FILE)
        conn.cursor().execute("DROP TABLE IF EXISTS products")
        conn.commit()
        conn.close()
    st.sidebar.success("تم مسح القاعدة بنجاح! قم بتحديث الصفحة.")
    st.rerun()

# جلب البيانات
rows = get_cheapest_items(search_query, sort_choice)

if not rows:
    st.warning("⚠️ لا توجد نتائج مطابقة لبحثك.")
else:
    cheapest_row = min(rows, key=lambda x: x[2]) if rows else None
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="🏆 أرخص سعر متاح", value=f"{cheapest_row[2]} ج.م" if cheapest_row else "0", delta=cheapest_row[0] if cheapest_row else "")
    with col2:
        st.metric(label="🛍️ المتجر الأرخص", value=cheapest_row[0] if cheapest_row else "")
    with col3:
        st.metric(label="📦 عدد المنتجات المعروضة", value=len(rows))

    st.markdown("---")
    
    st.subheader(f"📋 قائمة المنتجات وأرخص سعر (الترتيب حسب: {sort_choice})")
    
    for idx, r in enumerate(rows, 1):
        st.markdown(f"🔹 **المنتج:** {r[1]} | 📍 **المتجر الأرخص:** `{r[0]}` | 💰 السعر: `{r[2]} ج.م` (التصنيف: {r[3]})")

    st.markdown("---")
    st.subheader("📊 مؤشر الأسعار")
    max_p = max([r[2] for r in rows]) if rows else 1
    
    for r in rows:
        store_name, title_name, price, _ = r
        percentage = int((price / max_p) * 100)
        st.write(f"**{title_name}** عند ({store_name}) : **{price} ج.م**")
        st.progress(percentage if percentage <= 100 else 100)

# قسم إضافة منتج جديد
st.markdown("---")
with st.expander("➕ إضافة منتج جديد أو تحديث سعر متجر"):
    with st.form("add_form"):
        col_a, col_b = st.columns(2)
        with col_a:
            new_store = st.text_input("اسم المتجر (مثل: سعودي، أوسكار، أمازون)")
            new_title = st.text_input("اسم المنتج ووصفه التفصيلي")
        with col_b:
            new_price = st.number_input("السعر (بالجنيه المصري)", min_value=0.0, format="%.2f")
            new_category = st.text_input("التصنيف الرئيسي (مثل: مسحوق غسيل، زيت، أجبان)")
            
        submitted = st.form_submit_button("حفظ وإضافة للقاعدة")
        if submitted:
            if new_store and new_title and new_price > 0 and new_category:
                add_new_product(new_store, new_title, new_price, new_category)
                st.success(f"تم بنجاح إضافة المنتج ({new_title}) من متجر ({new_store}) بسعر ({new_price} ج.م)!")
                st.rerun()
            else:
                st.error("الرجاء إدخال جميع البيانات بشكل صحيح.")