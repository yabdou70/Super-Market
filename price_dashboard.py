import os
import sqlite3

import streamlit as st

DB_FILE = "prices_database.db"

SORT_OPTIONS = {
    "السعر: من الأرخص للأغلى": "price ASC",
    "المكان (المتجر)": "store ASC, price ASC",
    "اسم المنتج": "title ASC",
}

# منتجات/كلمات مستبعدة من النتائج
EXCLUDED_WORDS = [
    "الملكة", "مكرونة الضحى", "أرز", "جهينة", "بخيره",
    "سمن", "روابي", "سلايت", "عافية", "زيت ذرة",
]

SAMPLE_DATA = [
    ("سوبرماركت سعودي", "زيت كريستال عباد شمس 1 لتر", 87.00, "زيت"),
    ("محمود الفار ماركت", "زيت كريستال عباد شمس 1 لتر", 86.50, "زيت"),
    ("أوسكار ستورز", "زيت كريستال عباد شمس 2.2 لتر", 185.00, "زيت"),
    ("سوبرماركت سعودي", "زيت كريستال عباد شمس 5 لتر", 410.00, "زيت"),
    ("أوسكار ستورز", "زيت كريستال عباد شمس 5 لتر", 425.00, "زيت"),
    ("سوبرماركت سعودي", "أرز المصري 1 كجم", 32.00, "أرز"),
    ("محمود الفار ماركت", "أرز المصري 1 كجم", 31.50, "أرز"),
    ("سوبرماركت سعودي", "يوجو زبادي طبيعي (عبوة 4 قطع)", 24.00, "يوجو"),
    ("محمود الفار ماركت", "يوجو زبادي يوناني سادة (150جم)", 32.00, "يوجو"),
    ("سوبرماركت سعودي", "مكرونة ريجينا 400جم", 23.00, "مكرونة"),
    ("محمود الفار ماركت", "مكرونة ريجينا 400جم", 22.50, "مكرونة"),
    ("أوسكار ستورز", "مكرونة ريجينا 1 كجم", 54.00, "مكرونة"),
    ("سوبرماركت سعودي", "دقيق السوهاجي فاخر 1 كجم", 24.00, "دقيق"),
    ("محمود الفار ماركت", "دقيق السوهاجي فاخر 1 كجم", 23.50, "دقيق"),
    ("أوسكار ستورز", "دقيق السوهاجي فاخر 1 كجم", 25.50, "دقيق"),
    ("سوبرماركت سعودي", "سكر الأبيض الأسيوطي 1 كجم", 27.00, "سكر"),
    ("محمود الفار ماركت", "Jack's Dutch Classic Gouda Cheese (كجم)", 520.00, "أجبان"),
    ("سوبرماركت سعودي", "Jack's Dutch Classic Gouda Cheese (كجم)", 535.00, "أجبان"),
    ("محمود الفار ماركت", "Blue Cheese / جبنة زرقاء ممتازة (كجم)", 380.00, "أجبان"),
    ("أوسكار ستورز", "Blue Cheese / جبنة زرقاء مستوردة (200جم)", 85.00, "أجبان"),
    ("سوبرماركت سعودي", "جبنة شيدر نيوزيلندي مستوردة (كيلو)", 450.00, "أجبان"),
    ("محمود الفار ماركت", "جبنة شيدر نيوزيلندي مستوردة (كيلو)", 440.00, "أجبان"),
    ("سوبرماركت سعودي", "جبنة رومي قديمة فاخرة (كيلو)", 260.00, "أجبان"),
    ("محمود الفار ماركت", "طبق بيض أحمر طازج (30 بيضة)", 165.00, "بيض"),
    ("سوبرماركت سعودي", "طبق بيض أبيض طازج (30 بيضة)", 160.00, "بيض"),
    ("سوبرماركت سعودي", "صدور دجاج فريش مخلية (كيلو)", 210.00, "دجاج"),
    ("محمود الفار ماركت", "صدور دجاج فريش مخلية (كيلو)", 205.00, "دجاج"),
    ("سوبرماركت سعودي", "روستو لحم حلواني (كيلو)", 380.00, "لحوم مصنعة"),
    ("أوسكار ستورز", "روستو لحم حلواني (عبوة 250جم)", 98.00, "لحوم مصنعة"),
    ("سوبرماركت سعودي", "بسطرمة حلواني ممتازة (كيلو)", 460.00, "لحوم مصنعة"),
    ("محمود الفار ماركت", "كافيار مستورد فاخر (عبوة 100جم)", 340.00, "أسماك ومأكولات بحرية"),
    ("محمود الفار ماركت", "Basma Frozen Minced Green Molokhia / ملوخية بسمة مفرومة (400جم)", 18.00, "مجمدات"),
    ("سوبرماركت سعودي", "Basma Frozen Minced Green Molokhia / ملوخية بسمة مفرومة (400جم)", 19.50, "مجمدات"),
    ("محمود الفار ماركت", "Basma Frozen Okra Zero / بامية بسمة زيرو (400جم)", 45.00, "مجمدات"),
    ("أوسكار ستورز", "Basma Frozen Okra Zero / بامية بسمة زيرو (400جم)", 47.00, "مجمدات"),
    ("محمود الفار ماركت", "Brunch Time Paté / باتيه برنش تايم محشو", 22.00, "مخبوزات"),
    ("سوبرماركت سعودي", "Brunch Time Paté / باتيه برنش تايم محشو", 24.00, "مخبوزات"),
    ("محمود الفار ماركت", "V-Cola / مشروب في كولا (2 لتر)", 25.00, "مشروبات"),
    ("سوبرماركت سعودي", "V-Cola / مشروب في كولا (كانز 330 مل)", 11.00, "مشروبات"),
    ("سوبرماركت سعودي", "مشروب كوكا كولا 2 لتر", 32.00, "مشروبات"),
    ("محمود الفار ماركت", "Durra Tomato Ketchup / كاتشب درة (340جم)", 38.00, "صوصات"),
    ("أوسكار ستورز", "Durra Tomato Ketchup / كاتشب درة (500جم)", 52.00, "صوصات"),
    ("محمود الفار ماركت", "Heinz Premium Barbecue Sauce / صوص باربيكيو هاينز (400جم)", 68.00, "صوصات"),
    ("سوبرماركت سعودي", "Heinz Premium Barbecue Sauce / صوص باربيكيو هاينز (400جم)", 72.00, "صوصات"),
    ("أوسكار ستورز", "شاي أحمد تي أكياس 100 فتلة", 165.00, "شاي"),
    ("سوبرماركت سعودي", "كلوركس مبيض ومطهر الأصلي 1 لتر", 38.00, "منظفات"),
    ("محمود الفار ماركت", "كلوركس مبيض ومطهر الأصلي 1 لتر", 37.00, "منظفات"),
    ("سوبرماركت سعودي", "منظف بريكس للتواليت 500 مل", 42.00, "منظفات"),
    ("سوبرماركت سعودي", "مناديل ورق وايت عبوة اقتصادية (5 رولات)", 65.00, "مناديل"),
    ("أمازون مصر", "كبسولات غسيل أطباق فينيش كوانتوم 40 كبسولة", 320.00, "غسيل أطباق"),
    ("سوبرماركت سعودي", "مسحوق غسيل باهي أتوماتيك 2.5 كجم", 110.00, "مسحوق غسيل"),
    ("سوبرماركت سعودي", "سائل غسيل ملابس أوكسي جل 2.5 لتر", 135.00, "سائل غسيل"),
]


def init_db():
    conn = sqlite3.connect(DB_FILE)
    try:
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
        cursor.execute("SELECT COUNT(*) FROM products")
        if cursor.fetchone()[0] == 0:
            cursor.executemany(
                "INSERT INTO products (store, title, price, query) VALUES (?, ?, ?, ?)",
                SAMPLE_DATA,
            )
        conn.commit()
    finally:
        conn.close()


def reset_db():
    """مسح القاعدة وإعادة تحميل البيانات الافتراضية."""
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute("DROP TABLE IF EXISTS products")
        conn.commit()
    finally:
        conn.close()
    init_db()


def get_cheapest_items(search_term="", sort_option="السعر: من الأرخص للأغلى"):
    order_sql = SORT_OPTIONS.get(sort_option, "price ASC")

    conditions = []
    params = []

    search_term = search_term.strip()
    if search_term:
        conditions.append("(query LIKE ? OR title LIKE ?)")
        params += [f"%{search_term}%", f"%{search_term}%"]

    for word in EXCLUDED_WORDS:
        conditions.append("title NOT LIKE ?")
        params.append(f"%{word}%")

    where_sql = "WHERE " + " AND ".join(conditions) if conditions else ""

    sql = f"""
        WITH ranked AS (
            SELECT store, title, price, query,
                   ROW_NUMBER() OVER (PARTITION BY title ORDER BY price ASC) AS rn
            FROM products
            {where_sql}
        )
        SELECT store, title, price, query FROM ranked
        WHERE rn = 1
        ORDER BY {order_sql}
    """

    conn = sqlite3.connect(DB_FILE)
    try:
        return conn.execute(sql, params).fetchall()
    finally:
        conn.close()


def add_new_product(store, title, price, query):
    """يضيف المنتج، أو يحدّث سعره إذا كان موجودًا بنفس المتجر والاسم.
    تُرجع True عند التحديث و False عند الإضافة."""
    conn = sqlite3.connect(DB_FILE)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE products SET price = ?, query = ? WHERE store = ? AND title = ?",
            (price, query, store, title),
        )
        updated = cursor.rowcount > 0
        if not updated:
            cursor.execute(
                "INSERT INTO products (store, title, price, query) VALUES (?, ?, ?, ?)",
                (store, title, price, query),
            )
        conn.commit()
        return updated
    finally:
        conn.close()


st.set_page_config(page_title="داشبورد مقارنة الأسعار", page_icon="🛒", layout="wide")
init_db()

st.title("🛒 الداشبورد التفاعلية لمقارنة الأسعار (المتاجر المصرية)")

# رسالة تظهر مرة واحدة بعد إعادة التشغيل (st.rerun كانت تمسحها قبل أن تُعرض)
flash = st.session_state.pop("flash", None)
if flash:
    st.success(flash)

st.markdown("---")

st.sidebar.header("🔍 خيارات البحث والترتيب")
search_query = st.sidebar.text_input("ابحث عن منتج (مثل: يوجو، زبادي، ريجينا):", "")
sort_choice = st.sidebar.selectbox("ترتيب النتائج حسب:", list(SORT_OPTIONS))

if st.sidebar.button("🔄 إعادة تهيئة وتنظيف القاعدة"):
    reset_db()
    st.session_state["flash"] = "تمت إعادة تهيئة القاعدة بنجاح."
    st.rerun()

rows = get_cheapest_items(search_query, sort_choice)

if not rows:
    st.warning("⚠️ لا توجد نتائج مطابقة لبحثك.")
else:
    cheapest_row = min(rows, key=lambda x: x[2])

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="🏆 أرخص سعر متاح", value=f"{cheapest_row[2]:g} ج.م")
    with col2:
        st.metric(label="🛍️ المتجر الأرخص", value=cheapest_row[0])
    with col3:
        st.metric(label="📦 عدد المنتجات المعروضة", value=len(rows))

    st.markdown("---")
    st.subheader(f"📋 قائمة المنتجات وأرخص سعر (الترتيب حسب: {sort_choice})")

    for store_name, title_name, price, category in rows:
        st.markdown(
            f"🔹 **المنتج:** {title_name} | 📍 **المتجر الأرخص:** `{store_name}` "
            f"| 💰 السعر: `{price:g} ج.م` (التصنيف: {category})"
        )

    st.markdown("---")
    st.subheader("📊 مؤشر الأسعار")
    max_p = max(r[2] for r in rows) or 1

    for store_name, title_name, price, _ in rows:
        percentage = min(100, max(0, int((price / max_p) * 100)))
        st.write(f"**{title_name}** عند ({store_name}) : **{price:g} ج.م**")
        st.progress(percentage)

st.markdown("---")
with st.expander("➕ إضافة منتج جديد أو تحديث سعر متجر"):
    with st.form("add_form", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        with col_a:
            new_store = st.text_input("اسم المتجر:")
            new_title = st.text_input("اسم المنتج ووصفه التفصيلي:")
        with col_b:
            new_price = st.number_input("السعر (بالجنيه المصري):", min_value=0.0, format="%.2f")
            new_category = st.text_input("التصنيف الرئيسي (مثل: يوجو، أجبان، مجمدات):")

        submitted = st.form_submit_button("حفظ وإضافة للقاعدة")

    if submitted:
        new_store, new_title, new_category = (
            new_store.strip(), new_title.strip(), new_category.strip(),
        )
        if new_store and new_title and new_price > 0 and new_category:
            was_update = add_new_product(new_store, new_title, new_price, new_category)
            action = "تحديث سعر" if was_update else "إضافة"
            st.session_state["flash"] = (
                f"تم بنجاح {action} المنتج ({new_title}) من متجر ({new_store}) "
                f"بسعر ({new_price:g} ج.م)!"
            )
            st.rerun()
        else:
            st.error("الرجاء إدخال جميع البيانات بشكل صحيح.")
