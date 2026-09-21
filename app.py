import io
import sqlite3
from datetime import date
import pandas as pd
import streamlit as st

# استدعاء plotly بأمان مع دعم الوضع المظلم
try:
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

from database import create_tables, get_connection

# تهيئة قاعدة البيانات
create_tables()

st.set_page_config(
    page_title="منظومة التقويم التشخيصي والمعالجة البيداغوجية",
    page_icon="📐",
    layout="wide"
)

# ==============================================================================
# 🎨 التصميم الفني العصري (متكيف 100% مع الوضع الليلي والنهاري)
# ==============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800;900&display=swap');
    
    html, body, [class*="css"], .stMarkdown, p, div, span, label, h1, h2, h3, h4, input, select, textarea {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
    }

    /* بطاقات متكيفة مع الثيم المظلم والفاتح */
    .art-card {
        background-color: var(--secondary-background-color);
        color: var(--text-color);
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-right: 6px solid #1E88E5;
        border-radius: 12px;
        padding: 18px 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }

    .art-alert-danger {
        background-color: rgba(239, 68, 68, 0.12);
        border: 1px solid rgba(239, 68, 68, 0.35);
        border-right: 6px solid #EF4444;
        color: var(--text-color);
        padding: 16px;
        border-radius: 10px;
        margin-bottom: 12px;
        font-weight: 600;
    }
    
    .art-alert-success {
        background-color: rgba(34, 197, 94, 0.12);
        border: 1px solid rgba(34, 197, 94, 0.35);
        border-right: 6px solid #22C55E;
        color: var(--text-color);
        padding: 16px;
        border-radius: 10px;
        margin-bottom: 12px;
        font-weight: 600;
    }

    .art-alert-warning {
        background-color: rgba(245, 158, 11, 0.12);
        border: 1px solid rgba(245, 158, 11, 0.35);
        border-right: 6px solid #F59E0B;
        color: var(--text-color);
        padding: 16px;
        border-radius: 10px;
        margin-bottom: 12px;
        font-weight: 600;
    }

    .art-alert-info {
        background-color: rgba(59, 130, 246, 0.12);
        border: 1px solid rgba(59, 130, 246, 0.35);
        border-right: 6px solid #3B82F6;
        color: var(--text-color);
        padding: 16px;
        border-radius: 10px;
        margin-bottom: 12px;
    }

    /* شارات التقدير النوعي الأنيقة */
    .badge-pill {
        display: inline-block;
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 0.85em;
        font-weight: 700;
        white-space: nowrap;
        text-align: center;
    }
    .badge-red { background-color: rgba(239, 68, 68, 0.2); color: #FF6B6B; border: 1px solid #EF4444; }
    .badge-orange { background-color: rgba(245, 158, 11, 0.2); color: #FFA94D; border: 1px solid #F59E0B; }
    .badge-green { background-color: rgba(34, 197, 94, 0.2); color: #51CF66; border: 1px solid #22C55E; }
    .badge-star { background-color: rgba(168, 85, 247, 0.2); color: #CC5DE8; border: 1px solid #A855F7; }

    /* جداول منضبطة الاتجاه والأعمدة */
    .art-table-wrapper {
        width: 100%;
        overflow-x: auto;
        border-radius: 12px;
        border: 1px solid rgba(128, 128, 128, 0.2);
        margin: 15px 0;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.04);
    }
    table.art-table {
        width: 100%;
        border-collapse: collapse;
        direction: rtl;
        font-family: 'Cairo', sans-serif;
        background-color: var(--secondary-background-color);
        color: var(--text-color);
    }
    table.art-table th {
        background-color: rgba(30, 136, 229, 0.15);
        color: var(--text-color);
        padding: 13px 15px;
        font-weight: 800;
        font-size: 0.95em;
        border-bottom: 2px solid rgba(30, 136, 229, 0.35);
        text-align: right;
        white-space: nowrap;
    }
    table.art-table td {
        padding: 12px 15px;
        border-bottom: 1px solid rgba(128, 128, 128, 0.15);
        font-size: 0.92em;
        text-align: right;
        vertical-align: middle;
    }
    table.art-table tr:hover {
        background-color: rgba(128, 128, 128, 0.07);
    }
</style>
""", unsafe_allow_html=True)

# ----------------- الثوابت الرسمية -----------------
RESOURCES = [
    "الأعداد والحساب",
    "الحساب الجبري",
    "الدوال والمنحنيات",
    "الهندسة والأشعة"
]

# ----------------- الدوال المساعدة -----------------
def get_classes():
    conn = get_connection()
    try:
        return conn.execute("SELECT * FROM classes ORDER BY level, class_name").fetchall()
    finally:
        conn.close()

def get_students(class_id=None):
    conn = get_connection()
    try:
        if class_id is not None:
            return conn.execute("SELECT * FROM students WHERE class_id = ? ORDER BY full_name", (class_id,)).fetchall()
        return conn.execute("""
            SELECT students.*, classes.level, classes.class_name 
            FROM students 
            INNER JOIN classes ON students.class_id = classes.id 
            ORDER BY classes.level, classes.class_name, students.full_name
        """).fetchall()
    finally:
        conn.close()

def classification(total):
    if total >= 15:
        return "متحكم جدًا"
    elif total >= 10:
        return "متحكم"
    elif total >= 7:
        return "متحكم جزئيًا"
    return "غير متحكم"

def format_badge_html(status):
    if "غير متحكم" in status:
        return "<span class='badge-pill badge-red'>🔴 غير متحكم</span>"
    elif "جزئي" in status:
        return "<span class='badge-pill badge-orange'>🟠 متحكم جزئيًا</span>"
    elif "متحكم جد" in status:
        return "<span class='badge-pill badge-star'>⭐ متحكم جدًا</span>"
    return "<span class='badge-pill badge-green'>🟢 متحكم</span>"

def render_artistic_table(data_list):
    if not data_list:
        st.info("لا توجد بيانات متاحة لعرضها.")
        return
    headers = list(data_list[0].keys())
    html = "<div class='art-table-wrapper'><table class='art-table'><thead><tr>"
    for h in headers:
        html += f"<th>{h}</th>"
    html += "</tr></thead><tbody>"
    for row in data_list:
        html += "<tr>"
        for h in headers:
            html += f"<td>{row.get(h, '')}</td>"
        html += "</tr>"
    html += "</tbody></table></div>"
    st.markdown(html, unsafe_allow_html=True)

def class_options_dict():
    return {f"{item['level']} — {item['class_name']}": item["id"] for item in get_classes()}

def student_options_dict(class_id=None):
    return {item["full_name"]: item["id"] for item in get_students(class_id)}

def safe_float(val, default=0.0):
    try:
        if pd.isna(val):
            return default
        s = str(val).strip().replace(',', '.')
        res = float(s)
        return max(0.0, min(5.0, res))
    except Exception:
        return default

# ----------------- القائمة الجانبية -----------------
st.sidebar.title("📐 الرقمنة البيداغوجية")
st.sidebar.caption("المتابعة الذكية للتقويم التشخيصي والمعالجة © 2026")

menu = st.sidebar.radio(
    "المحطات البيداغوجية:",
    [
        "الرئيسية",
        "الأقسام والتلاميذ (استيراد إكسل والنقاط)",
        "التقويم التشخيصي (تعديل يدوي)",
        "خارطة الفوارق والتصدير الرسمي",
        "تقرير استثمار النتائج واستراتيجية المعالجة",
        "بطاقة المتابعة الفردية (الفئة الهشة)",
        "التنبيهات الاستباقية للدروس",
        "بنك الأنشطة العلاجية (10 دقائق)",
        "دليل وتوجيهات السيد المفتش"
    ]
)

# ==============================================================================
# 1. لوحة القيادة
# ==============================================================================
if menu == "الرئيسية":
    st.header("📊 لوحة القيادة البيداغوجية لمادة الرياضيات")
    classes = get_classes()
    students = get_students()
    
    conn = get_connection()
    try:
        diag_count = conn.execute("SELECT COUNT(*) AS total FROM diagnostic_results").fetchone()["total"]
        weak_count = conn.execute("SELECT COUNT(*) AS total FROM diagnostic_results WHERE classification = 'غير متحكم'").fetchone()["total"]
        fragile_count = conn.execute("""
            SELECT COUNT(*) AS total FROM diagnostic_results 
            WHERE total < 7 OR (
                (arithmetic < 2.5) + (algebra < 2.5) + (functions < 2.5) + (geometry < 2.5) >= 3
            )
        """).fetchone()["total"]
    finally:
        conn.close()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("عدد الأقسام", len(classes))
    col2.metric("إجمالي التلاميذ", len(students))
    col3.metric("النتائج المسجلة", f"{diag_count} / {len(students)}")
    col4.metric("الفئة الهشة (المعنية بالمتابعة)", fragile_count, delta=f"{fragile_count} تلميذ" if fragile_count > 0 else None, delta_color="inverse")

    st.divider()
    st.markdown("""
    <div class="art-card">
        <h4 style="margin: 0 0 10px 0; color:#1E88E5;">🎯 الشعار البيداغوجي المعتمد للمقاطعة التفتيشية:</h4>
        <i>«من التشخيص إلى العلاج.. لا تشخيص بدون دواء»</i><br>
        <i>«الخطأ هو بداية التعلم.. والصدق في الإجابة هو مفتاح مساعدتك.»</i>
    </div>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. استيراد الأسماء والنقاط من الإكسل
# ==============================================================================
# ==============================================================================
# 2. الأقسام والتلاميذ (استيراد إكسل + إدارة الأقسام: إضافة، تعديل، حذف)
# ==============================================================================
elif menu == "الأقسام والتلاميذ (استيراد إكسل والنقاط)":
    st.header("📚 إدارة الأقسام والتلاميذ")
    st.caption("إدارة شاملة: استيراد القوائم، إضافة وتعديل وحذف الأقسام، وتسجيل التلاميذ.")

    tab1, tab2, tab3, tab4 = st.tabs([
        "📥 استيراد فوج شامل من إكسل", 
        "🏫 إدارة الأقسام (إضافة / تعديل / حذف)", 
        "👤 إضافة تلميذ فردي",
        "📋 نسخ ولصق الأسماء"
    ])

    # -------------------------------------------------------------
    # 1. استيراد ملف إكسل شامل
    # -------------------------------------------------------------
    with tab1:
        cls_opts = class_options_dict()
        if not cls_opts:
            st.warning("⚠️ لا يوجد أي قسم مسجل بعد. أنشئي قسماً أولاً من تبويب «إدارة الأقسام».")
        else:
            target_cls = st.selectbox("1. اختاري القسم الموجه إليه الملف:", list(cls_opts.keys()), key="import_cls")
            class_id = cls_opts[target_cls]

            uploaded_file = st.file_uploader("2. اختاري ملف الإكسل (.xlsx أو .xls أو .csv):", type=["xlsx", "xls", "csv"], key="excel_uploader")

            if uploaded_file is not None:
                try:
                    df_raw = None
                    try:
                        df_raw = pd.read_excel(uploaded_file, header=None)
                    except Exception:
                        try:
                            uploaded_file.seek(0)
                            tables = pd.read_html(uploaded_file)
                            df_raw = tables[0]
                        except Exception:
                            uploaded_file.seek(0)
                            df_raw = pd.read_csv(uploaded_file, header=None)

                    if df_raw is not None:
                        header_idx = None
                        full_name_idx = None
                        sur_idx, nam_idx = None, None
                        arith_idx, alg_idx, func_idx, geom_idx = None, None, None, None

                        for r_idx, row in df_raw.iterrows():
                            row_text = " ".join([str(v) for v in row.values if pd.notna(v)])
                            if "اللقب" in row_text or "الاسم" in row_text or "nom" in row_text.lower():
                                header_idx = r_idx
                                for c_idx, val in enumerate(row.values):
                                    v_str = str(val).strip()
                                    if v_str in ["اللقب والاسم", "الاسم واللقب", "الاسم الكامل", "التلميذ", "Nom et Prénom", "nom_prenom"]:
                                        full_name_idx = c_idx
                                    elif v_str in ["اللقب", "Nom", "nom"]:
                                        sur_idx = c_idx
                                    elif v_str in ["الاسم", "Prénom", "prenom"]:
                                        name_col_idx = c_idx
                                    elif "أعداد" in v_str or "حساب" in v_str or "arithmetic" in v_str.lower():
                                        if arith_idx is None: arith_idx = c_idx
                                    elif "جبر" in v_str or "algebra" in v_str.lower():
                                        alg_idx = c_idx
                                    elif "دوال" in v_str or "منحنيات" in v_str or "functions" in v_str.lower():
                                        func_idx = c_idx
                                    elif "هندسة" in v_str or "أشعة" in v_str or "geometry" in v_str.lower():
                                        geom_idx = c_idx
                                break

                        parsed_records = []
                        if header_idx is not None:
                            data_rows = df_raw.iloc[header_idx + 1:]
                            for _, r in data_rows.iterrows():
                                name = ""
                                if full_name_idx is not None and pd.notna(r[full_name_idx]):
                                    name = str(r[full_name_idx]).strip()
                                elif sur_idx is not None and nam_idx is not None:
                                    s = str(r[sur_idx]).strip() if pd.notna(r[sur_idx]) else ""
                                    n = str(r[nam_idx]).strip() if pd.notna(r[nam_idx]) else ""
                                    name = f"{s} {n}".strip()

                                if name and len(name) > 3 and not name.isdigit() and name.lower() != "nan":
                                    arith = safe_float(r[arith_idx]) if arith_idx is not None else 0.0
                                    alg = safe_float(r[alg_idx]) if alg_idx is not None else 0.0
                                    func = safe_float(r[func_idx]) if func_idx is not None else 0.0
                                    geom = safe_float(r[geom_idx]) if geom_idx is not None else 0.0
                                    tot = arith + alg + func + geom
                                    parsed_records.append({
                                        "name": name,
                                        "arith": arith,
                                        "alg": alg,
                                        "func": func,
                                        "geom": geom,
                                        "total": tot,
                                        "status": classification(tot)
                                    })

                        if parsed_records:
                            st.markdown(f"<div class='art-alert-success'>✅ تم التعرف على <b>{len(parsed_records)} تلميذ</b> بنقاطهم الكاملة!</div>", unsafe_allow_html=True)
                            
                            preview_table = [
                                {
                                    "اسم ولقب التلميذ": p["name"],
                                    "الأعداد والحساب": f"{p['arith']:.1f} / 5",
                                    "الحساب الجبري": f"{p['alg']:.1f} / 5",
                                    "الدوال والمنحنيات": f"{p['func']:.1f} / 5",
                                    "الهندسة والأشعة": f"{p['geom']:.1f} / 5",
                                    "المجموع العام": f"<b>{p['total']:.2f} / 20</b>",
                                    "التقدير": format_badge_html(p["status"])
                                } for p in parsed_records
                            ]
                            render_artistic_table(preview_table)

                            if st.button("🚀 تأكيد حفظ الأسماء والنقاط في قاعدة البيانات", type="primary"):
                                conn = get_connection()
                                saved_s, saved_d = 0, 0
                                try:
                                    for p in parsed_records:
                                        cursor = conn.cursor()
                                        cursor.execute("SELECT id FROM students WHERE full_name = ? AND class_id = ?", (p["name"], class_id))
                                        row = cursor.fetchone()
                                        if row:
                                            stu_id = row[0]
                                        else:
                                            cursor.execute("INSERT INTO students (full_name, class_id) VALUES (?, ?)", (p["name"], class_id))
                                            stu_id = cursor.lastrowid
                                            saved_s += 1

                                        conn.execute("""
                                            INSERT INTO diagnostic_results (student_id, arithmetic, algebra, functions, geometry, total, classification, updated_at)
                                            VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now', 'localtime'))
                                            ON CONFLICT(student_id) DO UPDATE SET
                                                arithmetic=excluded.arithmetic,
                                                algebra=excluded.algebra,
                                                functions=excluded.functions,
                                                geometry=excluded.geometry,
                                                total=excluded.total,
                                                classification=excluded.classification,
                                                updated_at=excluded.updated_at
                                        """, (stu_id, p["arith"], p["alg"], p["func"], p["geom"], p["total"], p["status"]))
                                        saved_d += 1

                                    conn.commit()
                                    st.success(f"🎉 تم تسجيل {saved_s} تلميذ جديد وتحديث نتائج {saved_d} تلميذ في قسم {target_cls}!")
                                    st.rerun()
                                finally:
                                    conn.close()
                        else:
                            st.error("تعذر قراءة بيانات الأسماء أو النقاط. تأكدي من تسمية الأعمدة بوضوح.")
                except Exception as e:
                    st.error(f"خطأ أثناء معالجة الملف: {e}")

    # -------------------------------------------------------------
    # 2. إدارة الأقسام (إضافة / تعديل / حذف) ⭐ جديد
    # -------------------------------------------------------------
    with tab2:
        st.subheader("🏫 تسيير وإدارة الأقسام")
        
        # اختيار العملية عبر أزرار أفقية مريحة
        class_action = st.radio(
            "اختاري العملية المطلوبة:", 
            ["➕ إضافة قسم جديد", "✏️ تعديل بيانات قسم مسجل", "🗑️ حذف قسم نهائياً"], 
            horizontal=True
        )

        st.write("---")

        # --- أ) إضافة قسم جديد ---
        if class_action == "➕ إضافة قسم جديد":
            st.markdown("##### ➕ بيانات القسم الجديد:")
            col_a1, col_a2, col_a3 = st.columns(3)
            with col_a1:
                new_level = st.text_input("المستوى التعليمي:", placeholder="مثال: 1AS ج م ع ت أو 2AS علوم", key="new_cls_lvl")
            with col_a2:
                new_cname = st.text_input("اسم الفوج / القسم:", placeholder="مثال: 1 ع 1 أو 2 ع ت 2", key="new_cls_name")
            with col_a3:
                new_syear = st.text_input("السنة الدراسية:", value="2026/2027", key="new_cls_year")

            if st.button("💾 حفظ القسم الجديد", type="primary"):
                if not new_level.strip() or not new_cname.strip():
                    st.warning("يرجى كتابة المستوى واسم القسم.")
                else:
                    conn = get_connection()
                    try:
                        conn.execute("INSERT INTO classes (level, class_name, school_year) VALUES (?, ?, ?)",
                                     (new_level.strip(), new_cname.strip(), new_syear.strip()))
                        conn.commit()
                        st.success(f"✅ تم إنشاء القسم ({new_level} — {new_cname}) بنجاح.")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("⚠️ هذا القسم مسجل مسبقاً بنفس الاسم والمستوى.")
                    finally:
                        conn.close()

        # --- ب) تعديل قسم مسجل ---
        elif class_action == "✏️ تعديل بيانات قسم مسجل":
            cls_opts = class_options_dict()
            if not cls_opts:
                st.info("لا توجد أقسام مسجلة لتعديلها.")
            else:
                sel_edit_class = st.selectbox("اختاري القسم المراد تعديله:", list(cls_opts.keys()), key="edit_cls_selector")
                edit_id = cls_opts[sel_edit_class]

                conn = get_connection()
                curr_cls = conn.execute("SELECT * FROM classes WHERE id = ?", (edit_id,)).fetchone()
                conn.close()

                st.markdown(f"##### ✏️ تعديل بيانات القسم: `{curr_cls['level']} — {curr_cls['class_name']}`")
                col_e1, col_e2, col_e3 = st.columns(3)
                with col_e1:
                    edit_level = st.text_input("المستوى الدراسي المحدث:", value=curr_cls['level'], key="edit_lvl_input")
                with col_e2:
                    edit_cname = st.text_input("اسم الفوج المحدث:", value=curr_cls['class_name'], key="edit_name_input")
                with col_e3:
                    edit_syear = st.text_input("السنة الدراسية:", value=curr_cls['school_year'], key="edit_year_input")

                if st.button("🔄 حفظ التعديلات وتحديث البيانات", type="primary"):
                    if not edit_level.strip() or not edit_cname.strip():
                        st.warning("يرجى ملء جميع الحقول.")
                    else:
                        conn = get_connection()
                        try:
                            conn.execute("""
                                UPDATE classes 
                                SET level = ?, class_name = ?, school_year = ? 
                                WHERE id = ?
                            """, (edit_level.strip(), edit_cname.strip(), edit_syear.strip(), edit_id))
                            conn.commit()
                            st.success("✅ تم تحديث بيانات القسم بنجاح في كافة واجهات التطبيق.")
                            st.rerun()
                        except sqlite3.IntegrityError:
                            st.error("⚠️ توجد بيانات لقسم آخر مسجل بنفس هذه التسمية.")
                        finally:
                            conn.close()

        # --- ج) حذف قسم نهائياً ---
        elif class_action == "🗑️ حذف قسم نهائياً":
            cls_opts = class_options_dict()
            if not cls_opts:
                st.info("لا توجد أقسام مسجلة لحذفها.")
            else:
                sel_del_class = st.selectbox("اختاري القسم المراد حذفه نهائياً:", list(cls_opts.keys()), key="del_cls_selector")
                del_id = cls_opts[sel_del_class]

                conn = get_connection()
                stu_count = conn.execute("SELECT COUNT(*) AS total FROM students WHERE class_id = ?", (del_id,)).fetchone()["total"]
                conn.close()

                st.markdown(f"""
                <div class="art-alert-danger">
                    ⚠️ <b>تنبيه أمني هام:</b> هذا القسم يحتوي حالياً على <b>{stu_count} تلميذ</b>.<br>
                    حذف القسم سيؤدي إلى <u>حذف جميع تلاميذه ونقاطهم وسجلات معالجتهم نهائياً</u> من قاعدة البيانات!
                </div>
                """, unsafe_allow_html=True)

                confirm_delete = st.checkbox("نعم، أنا متأكدة وأرغب في حذف هذا القسم بجميع تلاميذه نهائياً", key="confirm_del_box")

                if st.button("🚨 حذف القسم نهائياً من النظام", type="primary", disabled=not confirm_delete):
                    conn = get_connection()
                    try:
                        conn.execute("DELETE FROM classes WHERE id = ?", (del_id,))
                        conn.commit()
                        st.success(f"تم حذف القسم وجميع بياناته بنجاح.")
                        st.rerun()
                    finally:
                        conn.close()

        st.divider()
        # عرض جدول الأقسام وتعداد التلاميذ
        st.markdown("##### 📋 قائمة الأقسام وتعداد التلاميذ المسجلين في كل قسم:")
        conn = get_connection()
        try:
            classes_stats = conn.execute("""
                SELECT c.id, c.level, c.class_name, c.school_year, COUNT(s.id) as student_count
                FROM classes c
                LEFT JOIN students s ON c.id = s.class_id
                GROUP BY c.id
                ORDER BY c.level, c.class_name
            """).fetchall()
        finally:
            conn.close()

        if classes_stats:
            cls_table = [
                {
                    "المستوى التعليمي": c["level"],
                    "اسم القسم": c["class_name"],
                    "السنة الدراسية": c["school_year"],
                    "عدد التلاميذ المسجلين": f"<b>{c['student_count']} تلميذ</b>"
                } for c in classes_stats
            ]
            render_artistic_table(cls_table)
        else:
            st.info("لا توجد أقسام مسجلة حتى الآن.")

    # -------------------------------------------------------------
    # 3. إضافة تلميذ فردي
    # -------------------------------------------------------------
    with tab3:
        st.subheader("👤 إضافة تلميذ فردي")
        cls_opts = class_options_dict()
        if cls_opts:
            sel_cc = st.selectbox("القسم الموجه إليه التلميذ:", list(cls_opts.keys()), key="manual_single_cls")
            st_name = st.text_input("اسم ولقب التلميذ:", placeholder="مثال: مراد يوسف")
            if st.button("حفظ التلميذ"):
                if st_name.strip():
                    conn = get_connection()
                    try:
                        conn.execute("INSERT INTO students (full_name, class_id) VALUES (?, ?)", (st_name.strip(), cls_opts[sel_cc]))
                        conn.commit()
                        st.success(f"تم تسجيل التلميذ ({st_name}) بنجاح.")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("التلميذ مسجل مسبقاً في هذا القسم.")
                    finally:
                        conn.close()
                else:
                    st.warning("يرجى كتابة الاسم.")

    # -------------------------------------------------------------
    # 4. نسخ ولصق الأسماء
    # -------------------------------------------------------------
    with tab4:
        st.subheader("📋 نسخ ولصق الأسماء مباشرة")
        cls_opts = class_options_dict()
        if cls_opts:
            sel_c = st.selectbox("القسم:", list(cls_opts.keys()), key="paste_cls_tab")
            p_text = st.text_area("الصقي الأسماء (اسم في كل سطر):", height=150)
            if st.button("حفظ الأسماء المنسوخة"):
                lines = [l.strip() for l in p_text.split("\n") if l.strip()]
                conn = get_connection()
                try:
                    for s in lines:
                        try:
                            conn.execute("INSERT INTO students (full_name, class_id) VALUES (?, ?)", (s, cls_opts[sel_c]))
                        except sqlite3.IntegrityError:
                            pass
                    conn.commit()
                    st.success("تم الحفظ بنجاح.")
                    st.rerun()
                finally:
                    conn.close()

    st.divider()
    # استعراض تلاميذ أي قسم
    st.subheader("📋 استعراض التلاميذ المسجلين في كل قسم")
    classes = get_classes()
    if classes:
        cls_filter = {"جميع الأقسام": None}
        cls_filter.update(class_options_dict())
        chosen_filter = st.selectbox("تصفية عرض التلاميذ حسب القسم:", list(cls_filter.keys()), key="view_cls_filter")
        
        students_list = get_students(cls_filter[chosen_filter])
        if students_list:
            df_disp = [
                {
                    "الرقم": idx + 1,
                    "الاسم واللقب الكامل": s["full_name"],
                    "المستوى": s["level"],
                    "القسم": s["class_name"]
                } for idx, s in enumerate(students_list)
            ]
            render_artistic_table(df_disp)
        else:
            st.info("لا يوجد تلاميذ مسجلون في هذا القسم.")

# ==============================================================================
# 3. التقويم التشخيصي (جدول الكفاءات الأربع الملون + التعديل اليدوي + تحميل الإكسل)
# ==============================================================================
elif menu == "التقويم التشخيصي (تعديل يدوي)":
    st.header("📝 شبكة كفاءات التقويم التشخيصي والتعديل اليدوي")
    st.caption("تحليل الكفاءات الأربع لكل تلميذ، تصدير ملف إكسل ملون رسمي، وتعديل النقاط يدوياً.")

    cls_opts = class_options_dict()
    if not cls_opts:
        st.warning("⚠️ يرجى تسجيل قسم أولاً من واجهة «الأقسام والتلاميذ».")
    else:
        # شريط اختيار القسم
        selected_class = st.selectbox("🎯 اختاري القسم للمعاينة والتقييم:", list(cls_opts.keys()), key="diag_class_select")
        class_id = cls_opts[selected_class]

        tab_table, tab_edit = st.tabs([
            "📊 جدول الكفاءات الأربع الملون للقسم (مع التحميل)", 
            "✍️ تعديل نقاط تلميذ يدوياً"
        ])

        # -------------------------------------------------------------
        # دالة مساعدة لتحديد شارة كل كفاءة من 5 نقاط
        # -------------------------------------------------------------
        def eval_competency(score):
            if score >= 3.5:
                return "<span class='badge-pill badge-green'>🟢 متحكم</span>", "متحكم", "D1E7DD", "0F5132"
            elif score >= 2.5:
                return "<span class='badge-pill badge-orange'>🟠 جزئي</span>", "متحكم جزئياً", "FFF3CD", "664D03"
            else:
                return "<span class='badge-pill badge-red'>🔴 غير متحكم</span>", "غير متحكم", "F8D7DA", "842029"

        # -------------------------------------------------------------
        # 1. جدول الكفاءات الأربع للقسم + زر تصدير الإكسل الملون
        # -------------------------------------------------------------
        with tab_table:
            conn = get_connection()
            try:
                c_info = conn.execute("SELECT * FROM classes WHERE id = ?", (class_id,)).fetchone()
                students_diag = conn.execute("""
                    SELECT s.id, s.full_name, 
                           r.arithmetic, r.algebra, r.functions, r.geometry, 
                           r.total, r.classification, r.updated_at
                    FROM students s
                    LEFT JOIN diagnostic_results r ON s.id = r.student_id
                    WHERE s.class_id = ?
                    ORDER BY s.full_name ASC
                """, (class_id,)).fetchall()
            finally:
                conn.close()

            if not students_diag:
                st.info("لا يوجد تلاميذ مسجلون في هذا القسم بعد.")
            else:
                st.markdown(f"##### 📋 جدول رصد الكفاءات الأربع لفوج: `{selected_class}`")
                
                table_html_rows = []
                excel_rows = []

                for idx, row in enumerate(students_diag):
                    name = row["full_name"]
                    has_diag = row["total"] is not None

                    if has_diag:
                        arith = row["arithmetic"]
                        alg = row["algebra"]
                        func = row["functions"]
                        geom = row["geometry"]
                        tot = row["total"]
                        status = row["classification"]

                        b_arith, t_arith, c_arith, f_arith = eval_competency(arith)
                        b_alg, t_alg, c_alg, f_alg = eval_competency(alg)
                        b_func, t_func, c_func, f_func = eval_competency(func)
                        b_geom, t_geom, c_geom, f_geom = eval_competency(geom)

                        table_html_rows.append({
                            "الرقم": idx + 1,
                            "اسم ولقب التلميذ": f"<b>{name}</b>",
                            "1. الأعداد والحساب": f"<b>{arith:.1f}/5</b> &nbsp; {b_arith}",
                            "2. الحساب الجبري": f"<b>{alg:.1f}/5</b> &nbsp; {b_alg}",
                            "3. الدوال والمنحنيات": f"<b>{func:.1f}/5</b> &nbsp; {b_func}",
                            "4. الهندسة والأشعة": f"<b>{geom:.1f}/5</b> &nbsp; {b_geom}",
                            "المجموع العام": f"<b>{tot:.2f} / 20</b>",
                            "التقدير العام": format_badge_html(status)
                        })

                        excel_rows.append({
                            "num": idx + 1,
                            "name": name,
                            "arith_score": arith, "arith_text": t_arith, "arith_color": c_arith, "arith_font": f_arith,
                            "alg_score": alg, "alg_text": t_alg, "alg_color": c_alg, "alg_font": f_alg,
                            "func_score": func, "func_text": t_func, "func_color": c_func, "func_font": f_func,
                            "geom_score": geom, "geom_text": t_geom, "geom_color": c_geom, "geom_font": f_geom,
                            "total": tot,
                            "status": status
                        })
                    else:
                        table_html_rows.append({
                            "الرقم": idx + 1,
                            "اسم ولقب التلميذ": name,
                            "1. الأعداد والحساب": "<span style='color:gray;'>غير مقيم</span>",
                            "2. الحساب الجبري": "<span style='color:gray;'>غير مقيم</span>",
                            "3. الدوال والمنحنيات": "<span style='color:gray;'>غير مقيم</span>",
                            "4. الهندسة والأشعة": "<span style='color:gray;'>غير مقيم</span>",
                            "المجموع العام": "—",
                            "التقدير العام": "<span style='color:gray;'>—</span>"
                        })
                        excel_rows.append({
                            "num": idx + 1, "name": name,
                            "arith_score": 0, "arith_text": "غير مقيم", "arith_color": "FFFFFF", "arith_font": "000000",
                            "alg_score": 0, "alg_text": "غير مقيم", "alg_color": "FFFFFF", "alg_font": "000000",
                            "func_score": 0, "func_text": "غير مقيم", "func_color": "FFFFFF", "func_font": "000000",
                            "geom_score": 0, "geom_text": "غير مقيم", "geom_color": "FFFFFF", "geom_font": "000000",
                            "total": 0, "status": "غير مقيم"
                        })

                # عرض الجدول الفخم عالي الوضوح
                render_artistic_table(table_html_rows)

                # -------------------------------------------------------------
                # توليد ملف إكسل رسمي ملون بالكامل عبر openpyxl
                # -------------------------------------------------------------
                import openpyxl
                from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
                from openpyxl.utils import get_column_letter

                def create_colored_diagnostic_excel(class_name, level, school_year, data):
                    output = io.BytesIO()
                    wb = openpyxl.Workbook()
                    ws = wb.active
                    ws.title = "شبكة الكفاءات التشخيصية"
                    ws.views.sheetView[0].rightToLeft = True

                    # خطوط وتنسيقات
                    f_cairo = "Cairo"
                    border_thin = Border(left=Side(style='thin', color='A0AEC0'),
                                         right=Side(style='thin', color='A0AEC0'),
                                         top=Side(style='thin', color='A0AEC0'),
                                         bottom=Side(style='thin', color='A0AEC0'))
                    align_center = Alignment(horizontal='center', vertical='center', wrap_text=True)

                    # ترويسة الصفحة الرسمية
                    ws.merge_cells('A1:I1')
                    ws['A1'] = "الجمهورية الجزائرية الديمقراطية الشعبية — وزارة التربية الوطنية"
                    ws['A1'].font = Font(name=f_cairo, size=11, bold=True, color="2C3E50")
                    ws['A1'].alignment = align_center

                    ws.merge_cells('A2:I2')
                    ws['A2'] = f"شبكة تحليل الكفاءات ومخرجات التقويم التشخيصي — {level} ({class_name}) — السنة: {school_year}"
                    ws['A2'].font = Font(name=f_cairo, size=13, bold=True, color="1E88E5")
                    ws['A2'].alignment = align_center
                    ws.row_dimensions[2].height = 30

                    # عناوين الأعمدة
                    headers = [
                        "الرقم",
                        "اسم ولقب التلميذ",
                        "الأعداد والحساب (/5)",
                        "الحساب الجبري (/5)",
                        "الدوال والمنحنيات (/5)",
                        "الهندسة والأشعة (/5)",
                        "المجموع العام (/20)",
                        "التقدير الإجمالي",
                        "التوجيه البيداغوجي"
                    ]
                    ws.row_dimensions[4].height = 28
                    for col_idx, h in enumerate(headers, 1):
                        cell = ws.cell(row=4, column=col_idx, value=h)
                        cell.font = Font(name=f_cairo, size=10, bold=True, color="FFFFFF")
                        cell.fill = PatternFill(start_color="1E88E5", end_color="1E88E5", fill_type="solid")
                        cell.alignment = align_center
                        cell.border = border_thin

                    # إدراج أسطر التلاميذ مع التلوين الشرطي الدقيق
                    for r_idx, r_data in enumerate(data, start=5):
                        ws.row_dimensions[r_idx].height = 24
                        
                        # التوجيه البيداغوجي التلقائي
                        tot_val = r_data["total"]
                        if tot_val >= 15:
                            recom = "فئة الرواد: تكليف بمهام إشرافية وتحديات إدماجية"
                            status_bg = "E2D9F3" # بنفسجي فاخر
                            status_fg = "432874"
                        elif tot_val >= 10:
                            recom = "فئة متمكنة: تعزيز المكتسبات والمتابعة العادية"
                            status_bg = "D1E7DD" # أخضر
                            status_fg = "0F5132"
                        elif tot_val >= 7:
                            recom = "تحكم جزئي: معالجة مصغرة في الانطلاق (10د)"
                            status_bg = "FFF3CD" # برتقالي/أصفر
                            status_fg = "664D03"
                        else:
                            recom = "فئة هشة (منطقة حمراء): معالجة قاعدية وبطاقة فردية"
                            status_bg = "F8D7DA" # أحمر
                            status_fg = "842029"

                        # 1. الرقم
                        c_num = ws.cell(row=r_idx, column=1, value=r_data["num"])
                        c_num.alignment = align_center
                        c_num.border = border_thin

                        # 2. الاسم
                        c_name = ws.cell(row=r_idx, column=2, value=r_data["name"])
                        c_name.alignment = Alignment(horizontal='right', vertical='center')
                        c_name.font = Font(name=f_cairo, size=10, bold=True)
                        c_name.border = border_thin

                        # 3. الأعداد والحساب
                        c_ar = ws.cell(row=r_idx, column=3, value=f"{r_data['arith_score']:.1f} ({r_data['arith_text']})")
                        c_ar.fill = PatternFill(start_color=r_data["arith_color"], end_color=r_data["arith_color"], fill_type="solid")
                        c_ar.font = Font(name=f_cairo, size=9, bold=True, color=r_data["arith_font"])
                        c_ar.alignment = align_center
                        c_ar.border = border_thin

                        # 4. الحساب الجبري
                        c_al = ws.cell(row=r_idx, column=4, value=f"{r_data['alg_score']:.1f} ({r_data['alg_text']})")
                        c_al.fill = PatternFill(start_color=r_data["alg_color"], end_color=r_data["alg_color"], fill_type="solid")
                        c_al.font = Font(name=f_cairo, size=9, bold=True, color=r_data["alg_font"])
                        c_al.alignment = align_center
                        c_al.border = border_thin

                        # 5. الدوال والمنحنيات
                        c_fn = ws.cell(row=r_idx, column=5, value=f"{r_data['func_score']:.1f} ({r_data['func_text']})")
                        c_fn.fill = PatternFill(start_color=r_data["func_color"], end_color=r_data["func_color"], fill_type="solid")
                        c_fn.font = Font(name=f_cairo, size=9, bold=True, color=r_data["func_font"])
                        c_fn.alignment = align_center
                        c_fn.border = border_thin

                        # 6. الهندسة والأشعة
                        c_ge = ws.cell(row=r_idx, column=6, value=f"{r_data['geom_score']:.1f} ({r_data['geom_text']})")
                        c_ge.fill = PatternFill(start_color=r_data["geom_color"], end_color=r_data["geom_color"], fill_type="solid")
                        c_ge.font = Font(name=f_cairo, size=9, bold=True, color=r_data["geom_font"])
                        c_ge.alignment = align_center
                        c_ge.border = border_thin

                        # 7. المجموع
                        c_tot = ws.cell(row=r_idx, column=7, value=f"{r_data['total']:.2f}")
                        c_tot.font = Font(name=f_cairo, size=10, bold=True)
                        c_tot.alignment = align_center
                        c_tot.border = border_thin

                        # 8. التقدير الإجمالي الملون
                        c_st = ws.cell(row=r_idx, column=8, value=r_data["status"])
                        c_st.fill = PatternFill(start_color=status_bg, end_color=status_bg, fill_type="solid")
                        c_st.font = Font(name=f_cairo, size=10, bold=True, color=status_fg)
                        c_st.alignment = align_center
                        c_st.border = border_thin

                        # 9. التوجيه
                        c_rec = ws.cell(row=r_idx, column=9, value=recom)
                        c_rec.alignment = Alignment(horizontal='right', vertical='center')
                        c_rec.font = Font(name=f_cairo, size=8)
                        c_rec.border = border_thin

                    # ضبط أوتوماتيكي لعروض الأعمدة
                    for col in ws.columns:
                        max_len = max(len(str(cell.value or '')) for cell in col)
                        col_letter = get_column_letter(col[0].column)
                        ws.column_dimensions[col_letter].width = max(max_len + 3, 13)

                    ws.column_dimensions['A'].width = 8
                    ws.column_dimensions['B'].width = 24
                    ws.column_dimensions['I'].width = 38

                    wb.save(output)
                    return output.getvalue()

                # زر التحميل الملون الرسمي
                st.write("")
                excel_binary = create_colored_diagnostic_excel(c_info["class_name"], c_info["level"], c_info["school_year"], excel_rows)
                st.download_button(
                    label="📥 تحميل شبكة الكفاءات الأربع كملف Excel ملون وواضح (جاهز للتفتيش)",
                    data=excel_binary,
                    file_name=f"شبكة_الكفاءات_الأربع_الملونة_{c_info['class_name']}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary"
                )

        # -------------------------------------------------------------
        # 2. واجهة التعديل اليدوي السلس مع المؤشرات الفورية
        # -------------------------------------------------------------
        with tab_edit:
            st.markdown("##### ✍️ تعديل نقاط الكفاءات لتلميذ معين:")
            
            conn = get_connection()
            try:
                class_students = conn.execute("SELECT id, full_name FROM students WHERE class_id = ? ORDER BY full_name", (class_id,)).fetchall()
            finally:
                conn.close()

            if not class_students:
                st.info("لا يوجد تلاميذ في هذا القسم لتعديلهم.")
            else:
                stu_dict = {s["full_name"]: s["id"] for s in class_students}
                target_student_name = st.selectbox("اختاري التلميذ المراد مراجعة أو تعديل علاماته:", list(stu_dict.keys()), key="edit_manual_student_sel")
                student_id = stu_dict[target_student_name]

                # جلب النقاط الحالية
                conn = get_connection()
                try:
                    curr_diag = conn.execute("SELECT * FROM diagnostic_results WHERE student_id = ?", (student_id,)).fetchone()
                finally:
                    conn.close()

                c_arith = curr_diag["arithmetic"] if curr_diag else 0.0
                c_alg = curr_diag["algebra"] if curr_diag else 0.0
                c_func = curr_diag["functions"] if curr_diag else 0.0
                c_geom = curr_diag["geometry"] if curr_diag else 0.0

                st.markdown("<div class='art-card'>قومي بتعديل علامة كل محور من 0 إلى 5 (سيتغير المؤشر اللوني تلقائياً فورياً):</div>", unsafe_allow_html=True)

                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    new_arith = st.number_input("1. الأعداد والحساب (0 إلى 5):", 0.0, 5.0, float(c_arith), 0.5, key="inp_arith")
                    b_ar, _, _, _ = eval_competency(new_arith)
                    st.markdown(f"حالة الكفاءة: {b_ar}", unsafe_allow_html=True)
                    st.write("")

                    new_alg = st.number_input("2. الحساب الجبري (0 إلى 5):", 0.0, 5.0, float(c_alg), 0.5, key="inp_alg")
                    b_al, _, _, _ = eval_competency(new_alg)
                    st.markdown(f"حالة الكفاءة: {b_al}", unsafe_allow_html=True)

                with col_e2:
                    new_func = st.number_input("3. الدوال والمنحنيات (0 إلى 5):", 0.0, 5.0, float(c_func), 0.5, key="inp_func")
                    b_fn, _, _, _ = eval_competency(new_func)
                    st.markdown(f"حالة الكفاءة: {b_fn}", unsafe_allow_html=True)
                    st.write("")

                    new_geom = st.number_input("4. الهندسة والتحليل الشعاعي (0 إلى 5):", 0.0, 5.0, float(c_geom), 0.5, key="inp_geom")
                    b_ge, _, _, _ = eval_competency(new_geom)
                    st.markdown(f"حالة الكفاءة: {b_ge}", unsafe_allow_html=True)

                new_total = new_arith + new_alg + new_func + new_geom
                new_class = classification(new_total)

                st.divider()
                m_c1, m_c2 = st.columns(2)
                m_c1.metric("المجموع الإجمالي المحدث", f"{new_total:.2f} / 20")
                m_c2.markdown(f"**التقدير الإجمالي:** {format_badge_html(new_class)}", unsafe_allow_html=True)

                if st.button("💾 حفظ التعديل وتحديث بطاقة التلميذ فوراً", type="primary", key="save_manual_diag_btn"):
                    conn = get_connection()
                    try:
                        conn.execute("""
                            INSERT INTO diagnostic_results (student_id, arithmetic, algebra, functions, geometry, total, classification, updated_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now', 'localtime'))
                            ON CONFLICT(student_id) DO UPDATE SET
                                arithmetic = excluded.arithmetic,
                                algebra = excluded.algebra,
                                functions = excluded.functions,
                                geometry = excluded.geometry,
                                total = excluded.total,
                                classification = excluded.classification,
                                updated_at = excluded.updated_at
                        """, (student_id, new_arith, new_alg, new_func, new_geom, new_total, new_class))
                        conn.commit()
                        st.success(f"✅ تم بنجاح تحديث علامات التلميذ ({target_student_name}) ومجاميعه في كافة الجداول والرسوم البيانية.")
                        st.rerun()
                    finally:
                        conn.close()

# ==============================================================================
# 4. خارطة الفوارق والتصدير الرسمي
# ==============================================================================
elif menu == "خارطة الفوارق والتصدير الرسمي":
    st.header("🗺️ خارطة الفوارق الإحصائية وشبكة التفريغ")
    st.caption("التصنيف الرسمي وفق ملتقى وهران وتصدير تقرير التفريغ البيداغوجي الملون المعتمد في التفتيش.")

    cls_opts = class_options_dict()
    if cls_opts:
        sel_c = st.selectbox("القسم:", list(cls_opts.keys()), key="diff_map_cls")
        cid = cls_opts[sel_c]

        conn = get_connection()
        try:
            rows = conn.execute("""
                SELECT s.full_name, r.arithmetic, r.algebra, r.functions, r.geometry, r.total, r.classification
                FROM students s INNER JOIN diagnostic_results r ON s.id = r.student_id
                WHERE s.class_id = ? ORDER BY r.total DESC
            """, (cid,)).fetchall()
            
            c_info = conn.execute("SELECT * FROM classes WHERE id = ?", (cid,)).fetchone()
        finally:
            conn.close()

        if not rows:
            st.info("لا توجد نتائج مسجلة لهذا القسم. قومي باستيراد النقاط أولاً.")
        else:
            # مؤشرات المفتشية العامة
            total_students = len(rows)
            mastered_count = sum(1 for r in rows if r["total"] >= 10)
            mastery_rate = (mastered_count / total_students) * 100 if total_students > 0 else 0

            # حساب نسب التحكم لكل محور (عتبة 2.5/5)
            r_arith_pct = (sum(1 for r in rows if r["arithmetic"] >= 2.5) / total_students) * 100
            r_alg_pct = (sum(1 for r in rows if r["algebra"] >= 2.5) / total_students) * 100
            r_func_pct = (sum(1 for r in rows if r["functions"] >= 2.5) / total_students) * 100
            r_geom_pct = (sum(1 for r in rows if r["geometry"] >= 2.5) / total_students) * 100

            rates = {
                "الأعداد والحساب": r_arith_pct,
                "الحساب الجبري": r_alg_pct,
                "الدوال والمنحنيات": r_func_pct,
                "الهندسة والأشعة": r_geom_pct
            }
            strongest_res = max(rates, key=rates.get)
            weakest_res = min(rates, key=rates.get)

            # عرض المؤشرات الإحصائية الأربعة للمفتشية
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("نسبة التحكم الكلية (علامة ≥ 10)", f"{mastery_rate:.1f}%")
            m2.metric("المورد الأكثر تحكماً (قوة)", strongest_res, f"{rates[strongest_res]:.1f}%")
            m3.metric("المورد الأقل تحكماً (ضعف)", weakest_res, f"{rates[weakest_res]:.1f}%", delta_color="inverse")
            m4.metric("تعداد التلاميذ المفحوصين", f"{total_students} تلميذ")

            # تصنيف خارطة الفوارق
            pioneers, algebra_w, geom_w, fragile = [], [], [], []
            for r in rows:
                name, tot = r["full_name"], r["total"]
                if tot >= 10 and r["arithmetic"] >= 2.5 and r["algebra"] >= 2.5 and r["functions"] >= 2.5 and r["geometry"] >= 2.5:
                    pioneers.append((name, tot))
                elif tot < 7 or (sum([r["arithmetic"] < 2.5, r["algebra"] < 2.5, r["functions"] < 2.5, r["geometry"] < 2.5]) >= 3):
                    fragile.append((name, tot))
                elif r["algebra"] < 2.5 or r["arithmetic"] < 2.5:
                    algebra_w.append((name, f"جبر: {r['algebra']} | حساب: {r['arithmetic']}"))
                else:
                    geom_w.append((name, f"هندسة: {r['geometry']} | دوال: {r['functions']}"))

            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"<div class='art-card' style='border-right-color:#22C55E;'><b>⭐ فئة المتحكمين (الرواد): {len(pioneers)} تلميذ</b><br><small><b>الإجراء المقترح:</b> تكليفهم بمهام إشرافية (الأستاذ الصغير) وتدريبهم على وضعيات إدماج مركبة.</small><hr style='margin:6px 0;'>" + "<br>".join([f"• {p[0]} ({p[1]:.1f}/20)" for p in pioneers]) + "</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='art-card' style='border-right-color:#F59E0B;'><b>🔢 المتعثرون جبرياً: {len(algebra_w)} تلميذ</b><br><small><b>الإجراء المقترح:</b> حصص دعم في قواعد الحساب وتوزيع بطاقات تقنية للمتطابقات الشهيرة.</small><hr style='margin:6px 0;'>" + "<br>".join([f"• {a[0]} ({a[1]})" for a in algebra_w]) + "</div>", unsafe_allow_html=True)
            with c2:
                st.markdown(f"<div class='art-card' style='border-right-color:#3B82F6;'><b>📐 المتعثرون هندسياً: {len(geom_w)} تلميذ</b><br><small><b>الإجراء المقترح:</b> استخدام برمجية GeoGebra للتجسيد والتركيز على الإنشاءات الهندسية البسيطة.</small><hr style='margin:6px 0;'>" + "<br>".join([f"• {g[0]} ({g[1]})" for g in geom_w]) + "</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='art-card' style='border-right-color:#EF4444;'><b>🔴 الفئة الهشة: {len(fragile)} تلميذ</b><br><small><b>الإجراء المقترح:</b> معالجة قاعدية تبدأ من مفاهيم التعليم المتوسط وبطاقات متابعة فردية مستمرة.</small><hr style='margin:6px 0;'>" + "<br>".join([f"• {f[0]} ({f[1]:.1f}/20)" for f in fragile]) + "</div>", unsafe_allow_html=True)

            # جدول التفريغ الأنيق
            st.subheader("📋 شبكة تفريغ نتائج التقويم التشخيصي للقسم:")
            table_data = [
                {
                    "اسم ولقب التلميذ": r["full_name"],
                    "الأعداد والحساب": f"{r['arithmetic']:.1f} / 5",
                    "الحساب الجبري": f"{r['algebra']:.1f} / 5",
                    "الدوال والمنحنيات": f"{r['functions']:.1f} / 5",
                    "الهندسة والأشعة": f"{r['geometry']:.1f} / 5",
                    "المجموع الإجمالي": f"<b>{r['total']:.2f} / 20</b>",
                    "الوضعية": format_badge_html(r["classification"])
                } for r in rows
            ]
            render_artistic_table(table_data)

            # تصدير ملف Excel مع التنسيق الشرطي التلقائي
            df_export = pd.DataFrame([
                {
                    "اسم ولقب التلميذ": r["full_name"],
                    "الأعداد والحساب (/5)": r["arithmetic"],
                    "الحساب الجبري (/5)": r["algebra"],
                    "الدوال والمنحنيات (/5)": r["functions"],
                    "الهندسة والأشعة (/5)": r["geometry"],
                    "المجموع الإجمالي (/20)": r["total"],
                    "التقدير النوعي": r["classification"]
                } for r in rows
            ])
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_export.to_excel(writer, index=False, sheet_name="تفريغ التقويم التشخيصي")
                ws = writer.sheets["تفريغ التقويم التشخيصي"]
                ws.views.sheetView[0].rightToLeft = True

            st.download_button(
                "📥 تحميل شبكة التفريغ الرسمية (ملف Excel جاهز لملف التفتيش)",
                data=output.getvalue(),
                file_name=f"شبكة_التقويم_التشخيصي_{sel_c.replace(' ', '_')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary"
            )

# ==============================================================================
# 5. تقرير استثمار النتائج واستراتيجية المعالجة (وثيقة 4)
# ==============================================================================
elif menu == "تقرير استثمار النتائج واستراتيجية المعالجة":
    st.header("📑 تقرير استثمار النتائج واستراتيجية المعالجة البيداغوجية")
    st.caption("وثيقة رسمية مؤتمتة مطابقة لنموذج مديرية التربية لولاية وهران - مقاطعة تفتيشية رقم 03.")

    cls_opts = class_options_dict()
    if cls_opts:
        sel_c = st.selectbox("اختاري القسم لاستخراج تقريره:", list(cls_opts.keys()))
        cid = cls_opts[sel_c]

        conn = get_connection()
        try:
            c_info = conn.execute("SELECT * FROM classes WHERE id = ?", (cid,)).fetchone()
            rows = conn.execute("""
                SELECT r.* FROM diagnostic_results r
                INNER JOIN students s ON r.student_id = s.id
                WHERE s.class_id = ?
            """, (cid,)).fetchall()
        finally:
            conn.close()

        if not rows:
            st.warning("لا توجد نتائج مسجلة لهذا القسم لاستخراج التقرير.")
        else:
            total_s = len(rows)
            mastered = sum(1 for r in rows if r["total"] >= 10)
            rate = (mastered / total_s) * 100 if total_s > 0 else 0

            rates = {
                "الأعداد والحساب": (sum(1 for r in rows if r["arithmetic"] >= 2.5) / total_s) * 100,
                "الحساب الجبري": (sum(1 for r in rows if r["algebra"] >= 2.5) / total_s) * 100,
                "الدوال والمنحنيات": (sum(1 for r in rows if r["functions"] >= 2.5) / total_s) * 100,
                "الهندسة والتحليل الشعاعي": (sum(1 for r in rows if r["geometry"] >= 2.5) / total_s) * 100
            }
            strongest = max(rates, key=rates.get)
            weakest = min(rates, key=rates.get)

            # نص التقرير الرسمي المؤتمت
            report_text = f"""
بناءً على المعطيات الإحصائية المستخلصة من شبكة التقويم التشخيصي أعلاه، تبيّن أن النسبة العامة للتحكم في المكتسبات القبلية بلغت [{rate:.1f}%]. 

ومن خلال القراءة التقنية للنتائج، نلاحظ تبايناً واضحاً في الكفاءات؛ حيث سجلت فئة [{strongest}] أعلى معدلات التحكم بنسبة [{rates[strongest]:.1f}%]، مما يشير إلى قاعدة معرفية صلبة يمكن الاستناد إليها في بناء الوحدات التعليمية القادمة.

وفي المقابل، كشف التشخيص عن تعثرات حرجة في مورد [{weakest}]، حيث لم تتجاوز نسبة التحكم فيه [{rates[weakest]:.1f}%]. ويعزى هذا الضعف غالباً إلى تراكم الصعوبات المفاهيمية أو نقص الممارسة والتطبيق في المراحل السابقة.

وعليه، تقرر اعتماد خطة معالجة بيداغوجية ترتكز على:
1. تدخلات جماعية: تخصيص حصص استدراكية لتبسيط القواعد المتعثرة وتكثيف التطبيقات المباشرة.
2. تدخلات فارقية: تقسيم القسم إلى مجموعات عمل (أقران) لتمكين الفئة الهشة من الاستفادة من دعم التلاميذ المتحكمين (الرواد) تحت إشراف الأستاذ.
3. دعم مستمر: إدراج وضعيات تقويمية قصيرة (5 إلى 10 دقائق) في بداية كل حصة لترسيخ هذه الموارد قبل الانطلاق في البرنامج الرسمي.
            """

            st.markdown(f"""
            <div class="art-card">
                <h4 style="color:#1E88E5; margin-top:0;">الجمهورية الجزائرية الديمقراطية الشعبية — وزارة التربية الوطنية</h4>
                <p><b>مديرية التربية لولاية وهران — المقاطعة التفتيشية رقم 03</b></p>
                <p><b>المستوى:</b> {c_info['level']} &nbsp;&nbsp;|&nbsp;&nbsp; <b>القسم:</b> {c_info['class_name']} &nbsp;&nbsp;|&nbsp;&nbsp; <b>السنة الدراسية:</b> {c_info['school_year']}</p>
                <hr>
                <h3 style="text-align:center; color:#2C3E50;">تقرير عن نتائج التشخيص واستراتيجية المعالجة</h3>
                <div style="line-height: 1.8; font-size: 1.05em; text-align: justify;">
                    {report_text.replace(chr(10), '<br>')}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # وثيقة HTML الرسمية الجاهزة للطباعة فوراً
            official_report_html = f"""
            <!DOCTYPE html>
            <html dir="rtl" lang="ar">
            <head>
                <meta charset="UTF-8">
                <title>تقرير نتائج التشخيص واستراتيجية المعالجة</title>
                <style>
                    body {{ font-family: 'Cairo', Arial, sans-serif; margin: 30px; line-height: 1.8; }}
                    .header {{ text-align: center; border-bottom: 2px solid #000; padding-bottom: 12px; margin-bottom: 20px; }}
                    .info-table {{ width: 100%; margin-bottom: 25px; }}
                    .title {{ text-align: center; margin: 25px 0; font-size: 1.3em; font-weight: bold; text-decoration: underline; }}
                    .content {{ text-align: justify; font-size: 1.1em; }}
                    .signatures {{ display: flex; justify-content: space-between; margin-top: 50px; font-weight: bold; }}
                    @media print {{ body {{ margin: 15mm; }} button {{ display: none; }} }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h3 style="margin: 0;">الجمهورية الجزائرية الديمقراطية الشعبية</h3>
                    <h4 style="margin: 5px 0;">وزارة التربية الوطنية</h4>
                    <p style="margin: 0;">مديرية التربية لولاية وهران — مقاطعة تفتيشية رقم 03</p>
                </div>
                <table class="info-table">
                    <tr>
                        <td><b>المستوى:</b> {c_info['level']}</td>
                        <td><b>القسم:</b> {c_info['class_name']}</td>
                        <td><b>السنة الدراسية:</b> {c_info['school_year']}</td>
                        <td><b>التاريخ:</b> {date.today().strftime('%d/%m/%Y')}</td>
                    </tr>
                </table>
                <div class="title">تقرير عن نتائج التشخيص واستراتيجية المعالجة البيداغوجية</div>
                <div class="content">
                    {report_text.replace(chr(10), '<br>')}
                </div>
                <div class="signatures">
                    <span>توقيع الأستاذ(ة): .........................</span>
                    <span>تأشيرة السيد المفتش: .........................</span>
                </div>
            </body>
            </html>
            """

            st.download_button(
                label="📄 تحميل التقرير الرسمي بصيغة HTML (جاهز للطباعة المباشرة بختم المفتشية)",
                data=official_report_html.encode("utf-8"),
                file_name=f"تقرير_استثمار_النتائج_{c_info['class_name']}.html",
                mime="text/html",
                type="primary"
            )

# ==============================================================================
# 6. بطاقة المتابعة الفردية الرسمية (خاصة بالفئة الهشة)
# ==============================================================================
elif menu == "بطاقة المتابعة الفردية (الفئة الهشة)":
    st.header("🪪 بطاقة المتابعة البيداغوجية الفردية (مادة الرياضيات)")
    
    st.markdown("""
    <div class="art-alert-info">
        <b>💡 توجيهات السيد المفتش لجعل هذه البطاقة عملية (بدون عبء ورقي):</b><br>
        1. <b>الاختزال:</b> لا تفتح بطاقة لكل تلاميذ القسم، بل فقط لـ <u>الفئة الهشة (أصحاب المنطقة الحمراء في الخارطة)</u>.<br>
        2. <b>الإشراك:</b> اجعل التلميذ يوقع على البطاقة بعد كل "نشاط علاجي" ليشعر بمسؤوليته تجاه التغيير.<br>
        3. <b>الاحترافية:</b> تقديم هذه البطاقات عند زيارة المفتش يُعد أقوى دليل ملموس على أنكِ تمارسين البيداغوجيا الفارقية فعلياً.
    </div>
    """, unsafe_allow_html=True)

    cls_opts = class_options_dict()
    if cls_opts:
        sel_c = st.selectbox("اختاري القسم:", list(cls_opts.keys()), key="stu_card_cls")
        cid = cls_opts[sel_c]

        # جلب تلاميذ الفئة الهشة فقط
        conn = get_connection()
        try:
            fragile_students = conn.execute("""
                SELECT s.id, s.full_name, r.total, r.classification
                FROM students s
                INNER JOIN diagnostic_results r ON s.id = r.student_id
                WHERE s.class_id = ? AND (
                    r.total < 7 OR ((r.arithmetic < 2.5) + (r.algebra < 2.5) + (r.functions < 2.5) + (r.geometry < 2.5) >= 3)
                )
                ORDER BY r.total ASC
            """, (cid,)).fetchall()
            
            # خيار عرض جميع التلاميذ لمن يريد
            all_students = conn.execute("SELECT id, full_name FROM students WHERE class_id = ? ORDER BY full_name", (cid,)).fetchall()
        finally:
            conn.close()

        show_all = st.checkbox("عرض جميع تلاميذ القسم (افتراضياً يعرض الفئة الهشة فقط وفق توجيه المفتش)")
        target_list = all_students if show_all else fragile_students

        if not target_list:
            st.success("🎉 ممتاز! لا يوجد تلاميذ في الفئة الهشة بهذا القسم وفق معايير التقويم التشخيصي.")
        else:
            s_map = {s["full_name"]: s["id"] for s in target_list}
            sel_s_name = st.selectbox("اختاري التلميذ المعني بالمتابعة:", list(s_map.keys()))
            s_id = s_map[sel_s_name]

            conn = get_connection()
            try:
                s_info = conn.execute("SELECT s.full_name, c.level, c.class_name, c.school_year FROM students s INNER JOIN classes c ON s.class_id = c.id WHERE s.id = ?", (s_id,)).fetchone()
                diag = conn.execute("SELECT * FROM diagnostic_results WHERE student_id = ?", (s_id,)).fetchone()
                history = conn.execute("SELECT * FROM remediation_activities WHERE student_id = ? ORDER BY activity_date DESC", (s_id,)).fetchall()
            finally:
                conn.close()

            last_date = diag['updated_at'] if (diag and 'updated_at' in diag.keys()) else "غير مسجل"
            st.markdown(f"""
            <div class="art-card">
                <h3 style="margin:0; color:#1E88E5;">{s_info['full_name']}</h3>
                <p style="margin: 5px 0;"><b>القسم:</b> {s_info['level']} ({s_info['class_name']}) &nbsp;&nbsp;|&nbsp;&nbsp; <b>السنة:</b> {s_info['school_year']}</p>
                <p style="margin: 0;"><b>الوضعية التشخيصية:</b> {format_badge_html(diag['classification'])} &nbsp;&nbsp;|&nbsp;&nbsp; <b>العلامة:</b> {diag['total']:.2f}/20</p>
            </div>
            """, unsafe_allow_html=True)

            c_info, c_radar = st.columns([1.1, 0.9])
            with c_info:
                c1, c2 = st.columns(2)
                c1.metric("الأعداد والحساب", f"{diag['arithmetic']:.1f}/5", delta="تعثر" if diag['arithmetic'] < 2.5 else "متحكم", delta_color="inverse")
                c2.metric("الحساب الجبري", f"{diag['algebra']:.1f}/5", delta="تعثر" if diag['algebra'] < 2.5 else "متحكم", delta_color="inverse")
                c3, c4 = st.columns(2)
                c3.metric("الدوال والمنحنيات", f"{diag['functions']:.1f}/5", delta="تعثر" if diag['functions'] < 2.5 else "متحكم", delta_color="inverse")
                c4.metric("الهندسة والأشعة", f"{diag['geometry']:.1f}/5", delta="تعثر" if diag['geometry'] < 2.5 else "متحكم", delta_color="inverse")

            with c_radar:
                if HAS_PLOTLY:
                    cats = ['الأعداد والحساب', 'الحساب الجبري', 'الدوال والمنحنيات', 'الهندسة والأشعة']
                    vals = [diag['arithmetic'], diag['algebra'], diag['functions'], diag['geometry']]
                    fig = go.Figure()
                    fig.add_trace(go.Scatterpolar(
                        r=vals + [vals[0]], theta=cats + [cats[0]], 
                        fill='toself', name='تحصيل التلميذ', line_color='#1E88E5',
                        fillcolor='rgba(30, 136, 229, 0.25)'
                    ))
                    fig.add_trace(go.Scatterpolar(
                        r=[2.5]*5, theta=cats + [cats[0]], 
                        name='عتبة التحكم (2.5)', line=dict(color='#EF4444', dash='dash')
                    ))
                    fig.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(family='Cairo', color='gray'),
                        polar=dict(
                            bgcolor='rgba(0,0,0,0)',
                            radialaxis=dict(visible=True, range=[0, 5], tickfont=dict(size=10, color='gray'), gridcolor='rgba(128,128,128,0.2)'),
                            angularaxis=dict(gridcolor='rgba(128,128,128,0.2)')
                        ),
                        showlegend=True,
                        height=290,
                        margin=dict(l=30, r=30, t=25, b=25)
                    )
                    st.plotly_chart(fig, use_container_width=True)

            # تسجيل نشاط علاجي وفق النموذج الرسمي للمفتش (وثيقة 7)
            st.subheader("✍️ 1. تسجيل نشاط علاجي مقترح (جدول المتابعة الميدانية):")
            with st.form("add_official_rem"):
                rc1, rc2, rc3 = st.columns(3)
                with rc1:
                    r_date = st.date_input("التاريخ:", value=date.today())
                    r_res = st.selectbox("نوع التعثر المرصود:", RESOURCES)
                with rc2:
                    r_act = st.selectbox("النشاط العلاجي المقترح:", [
                        "تمرين منزلي حول المتطابقات الشهيرة / الحساب",
                        "ورشة ثنائية (مع تلميذ مساعد من الرواد)",
                        "اختبار سريع في الحساب الذهني / الإشارات (10د)",
                        "معالجة قاعدية من مفاهيم المتوسط"
                    ])
                    r_resp = st.selectbox("درجة الاستجابة:", ["جيد (أبدى تحسناً)", "متوسط (يحتاج لدعم)", "ضعيف (لم يتجاوز التعثر)"])
                with rc3:
                    r_note = st.text_area("ملاحظات الأستاذ:", placeholder="أبدى تحسناً في النشر، يحتاج لدعم في التحليل...")

                if st.form_submit_button("💾 إضافة النشاط إلى بطاقة المتابعة الرسمية", type="primary"):
                    conn = get_connection()
                    try:
                        conn.execute("""
                            INSERT INTO remediation_activities (student_id, resource, activity_type, response_level, teacher_note, activity_date)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (s_id, r_res, r_act, r_resp, r_note, r_date.isoformat()))
                        conn.commit()
                        st.success("تم تدوين الحصة في البطاقة.")
                        st.rerun()
                    finally:
                        conn.close()

            # أرشيف التدخلات وجدول المتابعة
            history_rows_html = ""
            if history:
                st.write("📋 **سجل الأنشطة العلاجية المنجزة مع هذا التلميذ:**")
                hist_table = [
                    {
                        "التاريخ": h["activity_date"],
                        "نوع التعثر المرصود": h["resource"],
                        "النشاط العلاجي المقترح": h["activity_type"],
                        "درجة الاستجابة": h["response_level"],
                        "ملاحظات الأستاذ": h["teacher_note"] if h["teacher_note"] else "—"
                    } for h in history
                ]
                render_artistic_table(hist_table)

                for h in history:
                    history_rows_html += f"""
                    <tr>
                        <td style="padding:8px; border:1px solid #000;">{h['activity_date']}</td>
                        <td style="padding:8px; border:1px solid #000;">{h['activity_type']}<br><small>({h['resource']})</small></td>
                        <td style="padding:8px; border:1px solid #000;">{h['response_level']}</td>
                        <td style="padding:8px; border:1px solid #000;">{h['teacher_note']}</td>
                        <td style="padding:8px; border:1px solid #000; text-align:center;">✓</td>
                    </tr>
                    """
            else:
                history_rows_html = "<tr><td colspan='5' style='text-align:center; padding:15px; border:1px solid #000;'>لم تسجل أنشطة بعد</td></tr>"

            # إنشاء وتحميل بطاقة المتابعة الرسمية الفردية (وثيقة 7 حرفياً)
            st.divider()
            card_official_html = f"""
            <!DOCTYPE html>
            <html dir="rtl" lang="ar">
            <head>
                <meta charset="UTF-8">
                <title>بطاقة المتابعة البيداغوجية الفردية</title>
                <style>
                    body {{ font-family: 'Cairo', Arial, sans-serif; margin: 25px; line-height: 1.6; color: #000; }}
                    .header {{ text-align: center; border-bottom: 2px solid #000; padding-bottom: 8px; margin-bottom: 15px; }}
                    .title {{ text-align: center; font-size: 1.3em; font-weight: bold; margin: 15px 0; border: 1px solid #000; padding: 6px; background: #f9f9f9; }}
                    table {{ width: 100%; border-collapse: collapse; margin-bottom: 15px; font-size: 0.95em; }}
                    th, td {{ border: 1px solid #000; padding: 7px; text-align: center; }}
                    th {{ background-color: #eee; }}
                    .section-title {{ font-weight: bold; margin: 12px 0 6px 0; font-size: 1.05em; }}
                    .box-info {{ border: 1px dashed #444; padding: 10px; margin-top: 15px; font-size: 0.85em; background: #fafafa; }}
                    .footer-sig {{ display: flex; justify-content: space-between; margin-top: 30px; font-weight: bold; }}
                    @media print {{ body {{ margin: 10mm; }} button {{ display: none; }} }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h3 style="margin:0;">الجمهورية الجزائرية الديمقراطية الشعبية</h3>
                    <h4 style="margin:4px 0;">وزارة التربية الوطنية</h4>
                    <p style="margin:0;">مديرية التربية لولاية وهران — ثانوية: .........................</p>
                </div>

                <div class="title">بطاقة المتابعة البيداغوجية الفردية (مادة الرياضيات)</div>

                <table style="border:none; margin-bottom: 10px;">
                    <tr style="border:none;">
                        <td style="border:none; text-align:right;"><b>اسم ولقب التلميذ:</b> {s_info['full_name']}</td>
                        <td style="border:none; text-align:center;"><b>المستوى والقسم:</b> {s_info['level']} ({s_info['class_name']})</td>
                        <td style="border:none; text-align:left;"><b>السنة الدراسية:</b> {s_info['school_year']}</td>
                    </tr>
                </table>

                <div class="section-title">1. نوع التعثر المرصود وجدول المتابعة الميدانية:</div>
                <table>
                    <thead>
                        <tr>
                            <th style="width: 15%;">التاريخ</th>
                            <th style="width: 30%;">النشاط العلاجي المقترح</th>
                            <th style="width: 20%;">درجة الاستجابة<br>(ضعيف / متوسط / جيد)</th>
                            <th style="width: 25%;">ملاحظات الأستاذ</th>
                            <th style="width: 10%;">توقيع التلميذ</th>
                        </tr>
                    </thead>
                    <tbody>
                        {history_rows_html}
                    </tbody>
                </table>

                <div class="section-title">2. مؤشر التطور النهائي (بعد المعالجة):</div>
                <p style="margin: 5px 0;">
                    (1) [ &nbsp; ] <b>تحسن ملحوظ:</b> انتقل من "غير متحكم" إلى "متحكم جزئي / كلي".<br>
                    (2) [ &nbsp; ] <b>تحسن طفيف:</b> لا يزال بحاجة لمتابعة في الموارد المعقدة.<br>
                    (3) [ &nbsp; ] <b>لم يتحسن:</b> يتطلب تدخلاً أعمق (استدعاء ولي الأمر أو دعم خارجي).
                </p>

                <div class="box-info">
                    <b>تنبيه بيداغوجي (توجيهات المفتش لجعل البطاقة عملية بدون عبء):</b><br>
                    • <b>الاختزال:</b> لا تفتح بطاقة لكل تلاميذ القسم، بل فقط للفئة الهشة (أصحاب المنطقة الحمراء).<br>
                    • <b>الإشراك:</b> اجعل التلميذ يوقع على البطاقة بعد كل "نشاط علاجي" ليشعر بمسؤوليته تجاه التغيير.<br>
                    • <b>الاحترافية:</b> عند زيارة المفتش، تقديم هذه البطاقات يُعد أقوى دليل على ممارسة البيداغوجيا الفارقية فعلياً.
                </div>

                <div class="footer-sig">
                    <span>توقيع الأستاذ(ة): .........................</span>
                    <span>تأشيرة السيد المفتش: .........................</span>
                </div>
            </body>
            </html>
            """

            st.download_button(
                label="🖨️ تحميل / طباعة بطاقة المتابعة الرسمية لهذا التلميذ (PDF/HTML جاهز للتفتيش)",
                data=card_official_html.encode("utf-8"),
                file_name=f"بطاقة_متابعة_{s_info['full_name'].replace(' ', '_')}.html",
                mime="text/html",
                type="primary"
            )

# ==============================================================================
# 7. التنبيهات الاستباقية للدروس
# ==============================================================================
elif menu == "التنبيهات الاستباقية للدروس":
    st.header("🔔 التنبيه البيداغوجي الاستباقي للدروس")
    conn = get_connection()
    try:
        lessons = conn.execute("""
            SELECT l.*, c.level, c.class_name FROM upcoming_lessons l
            INNER JOIN classes c ON l.class_id = c.id ORDER BY l.lesson_date ASC
        """).fetchall()
    finally:
        conn.close()

    if not lessons:
        st.info("لا توجد دروس مبرمجة حالياً.")
    else:
        l_opts = {f"{l['lesson_date']} | {l['lesson_title']} ({l['level']} - {l['class_name']})": l["id"] for l in lessons}
        sel_l = st.selectbox("اختاري الدرس:", list(l_opts.keys()))
        lid = l_opts[sel_l]

        conn = get_connection()
        try:
            ldata = conn.execute("SELECT * FROM upcoming_lessons WHERE id = ?", (lid,)).fetchone()
            target_res = ldata["resource"]
            cid = ldata["class_id"]
            col_map = {"الأعداد والحساب": "arithmetic", "الحساب الجبري": "algebra", "الدوال والمنحنيات": "functions", "الهندسة والأشعة": "geometry"}
            scol = col_map.get(target_res, "algebra")

            weaks = conn.execute(f"""
                SELECT s.full_name, r.{scol} as score, r.total, r.classification
                FROM diagnostic_results r INNER JOIN students s ON r.student_id = s.id
                WHERE s.class_id = ? AND r.{scol} < 2.5 ORDER BY r.{scol} ASC
            """, (cid,)).fetchall()
        finally:
            conn.close()

        if weaks:
            st.markdown(f"""
            <div class="art-alert-danger">
                ⚠️ <b>تنبيه بيداغوجي استباقي:</b> يوجد <b>{len(weaks)} تلاميذ</b> في هذا القسم يعانون من ضعف في ركيزة (<b>{target_res}</b>) المشروطة لهذا الدرس!
            </div>
            """, unsafe_allow_html=True)

            weak_table = [
                {
                    "الرقم": idx + 1,
                    "اسم ولقب التلميذ": w["full_name"],
                    f"علامة تحكم {target_res}": f"<b>{w['score']:.1f} / 5</b>",
                    "المجموع التشخيصي العام": f"{w['total']:.2f} / 20",
                    "الوضعية": format_badge_html(w["classification"])
                } for idx, w in enumerate(weaks)
            ]
            render_artistic_table(weak_table)

            st.markdown("""
            <div class="art-alert-info">
                💡 <b>التوجيه البيداغوجي (استراتيجية التعليم المصغر):</b> خصصي نشاطاً علاجياً مدته <b>10 دقائق</b> في بداية الحصة لسد هذه الثغرة من «بنك الأنشطة العلاجية» قبل بناء المفاهيم الجديدة.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("<div class='art-alert-success'>✅ جميع تلاميذ هذا الفوج متمكنون من المكتسبات القبلية لهذا الدرس (العلامة ≥ 2.5 / 5).</div>", unsafe_allow_html=True)

# ==============================================================================
# 8. بنك الأنشطة العلاجية المصغرة (10 دقائق)
# ==============================================================================
elif menu == "بنك الأنشطة العلاجية (10 دقائق)":
    st.header("⏱️ بنك الأنشطة العلاجية المصغرة (10 دقائق)")
    st.caption("مستوحى من الاستراتيجية الرابعة المعتمدة رسمياً: سد الفجوات التقنية دون تعطيل البرنامج الدراسي.")

    conn = get_connection()
    try:
        cards = conn.execute("SELECT * FROM remediation_bank").fetchall()
    finally:
        conn.close()

    res_f = st.selectbox("تصفية حسب المحور:", ["جميع المحاور"] + RESOURCES)
    filtered = [c for c in cards if res_f == "جميع المحاور" or c["resource"] == res_f]
    for c in filtered:
        with st.expander(f"📌 {c['title']} — ({c['resource']})", expanded=True):
            st.markdown(f"""
            <div class="art-card">
                <h4 style="margin-top:0; color:#1E88E5;">📖 خلاصة القاعدة الأساسية:</h4>
                <p style="font-size: 1.05em;">{c['rule_summary']}</p>
                <hr style="border-color: rgba(128,128,128,0.2);">
                <h4 style="color:#EF4444;">✍️ التطبيق المباشر (7 دقائق):</h4>
                <pre style="background: rgba(128,128,128,0.1); color: var(--text-color); padding: 12px; border-radius: 6px; font-family: Cairo;">{c['exercise_content']}</pre>
                <hr style="border-color: rgba(128,128,128,0.2);">
                <h4 style="color:#22C55E;">✅ الحل النموذجي والمناقشة (3 دقائق):</h4>
                <pre style="background: rgba(128,128,128,0.1); color: var(--text-color); padding: 12px; border-radius: 6px; font-family: Cairo;">{c['solution_content']}</pre>
            </div>
            """, unsafe_allow_html=True)

# ==============================================================================
# 9. دليل وتوجيهات السيد المفتش
# ==============================================================================
elif menu == "دليل وتوجيهات السيد المفتش":
    st.header("📘 الدليل البيداغوجي المعتمد من مفتشية مادة الرياضيات")
    st.caption("خلاصة مخرجات الملتقى التكويني حول هندسة وأدوات التقويم التشخيصي - ولاية وهران.")

    t1, t2, t3 = st.tabs(["🎯 استراتيجيات المعالجة الأربع", "📁 مكونات ملف التقويم (معيار الجودة)", "⚖️ الأطر المرجعية والقانونية"])

    with t1:
        st.markdown("""
        <div class="art-card">
            <h4 style="color:#1E88E5;">1. استراتيجية "تحليل المسارات الإدراكية" (التعلم بالخطأ):</h4>
            <b>الوصف:</b> بدلاً من إعطاء الحل الصحيح مباشرة، نركز على <i>"لماذا أخطأ التلميذ؟"</i>.<br>
            <b>التطبيق:</b> اختيار "خطأ شائع" من أوراق التقويم وعرضه على السبورة (بدون اسم التلميذ)، وفتح نقاش جماعي لتحليل المنطق الذي أدى للخطأ وتصحيحه.<br>
            <b>الهدف:</b> تطوير النقد الذاتي لدى تلاميذ الثانوي.
        </div>
        <div class="art-card">
            <h4 style="color:#1E88E5;">2. استراتيجية "التدرج في التجريد" (النمذجة):</h4>
            <b>الوصف:</b> تلميذ الثانوي يعاني غالباً من الانتقال من المحسوس إلى الرمزي (مثلاً من قيم عددية إلى دوال عامة).<br>
            <b>التطبيق:</b> البدء بأمثلة عددية بسيطة، ثم الانتقال تدريجياً لتعميم القاعدة باستخدام المتغيرات x و y.<br>
            <b>الهدف:</b> بناء المفهوم الرياضي المجرد بشكل متين.
        </div>
        <div class="art-card">
            <h4 style="color:#1E88E5;">3. استراتيجية "الخرائط الذهنية للمفاهيم":</h4>
            <b>الوصف:</b> ربط الدروس ببعضها، لأن الرياضيات في الثانوي تراكمية حلزونية.<br>
            <b>التطبيق:</b> عند معالجة نقص في "المتتاليات" مثلاً، يتم رسم خريطة تربطها بـ "الدوال" و"الحساب الجبري".<br>
            <b>الهدف:</b> معالجة تشتت المعلومات لدى التلميذ وربط المكتسبات القبلية بالجديدة.
        </div>
        <div class="art-card">
            <h4 style="color:#1E88E5;">4. استراتيجية "التعليم المصغر":</h4>
            <b>الوصف:</b> استهداف ثغرة تقنية محددة جداً.<br>
            <b>التطبيق:</b> تخصيص 10 دقائق بداية كل حصة لمعالجة "ثغرة تقنية" ظهرت في التشخيص (مثلاً: توحيد المقامات، خواص القوى، جدول الإشارة).<br>
            <b>الهدف:</b> سد الفجوات التقنية دون تعطيل البرنامج الدراسي.
        </div>
        """, unsafe_allow_html=True)

    with t2:
        st.markdown("""
        <div class="art-card">
            <h4 style="color:#22C55E;">📋 مكونات ملف التقويم التشخيصي الجاهز للتفتيش (معيار الجودة):</h4>
            <p>لضمان الجاهزية التربوية أمام التفتيش والإدارة، يجب أن يتضمن ملف الأستاذ(ة):</p>
            <ul>
                <li><b>1. الجانب الوثائقي:</b> مقدمة التقويم، نسخة الاختبار، الإجابة النموذجية بسلم التنقيط، وتقرير تحليل النتائج المعتمد.</li>
                <li><b>2. الجانب الرقمي:</b> شبكة التفريغ (Excel) متضمنة التنسيق الشرطي والرسوم البيانية وخارطة الفوارق.</li>
                <li><b>3. الجانب العلاجي:</b> رزنامة المعالجة الزمنية، بنك تمارين المعالجة المركزة، وبطاقات المتابعة الفردية (خاصة بالفئة الهشة).</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with t3:
        st.markdown("""
        <div class="art-card">
            <h4 style="color:#9C27B0;">⚖️ المرجعيات البيداغوجية والقانونية:</h4>
            <ul>
                <li><b>المرجعية المعرفية (مصفوفة المدى والتتابع):</b> تعتمد مبدأ الحلزونية، حيث تشترط فهم موارد سابقة لاستيعاب دروس جديدة (مثال: الحساب الشعاعي في السنة الأولى كشرط للاشتقاقية في السنة الثانية).</li>
                <li><b>المرجعية البيداغوجية (المقاربة بالكفاءات):</b> قياس القدرة على تعبئة الموارد وحل المشكلات وفق تصنيف "بلوم" (معرفة، فهم، تطبيق، تحليل).</li>
                <li><b>المرجعية القانونية:</b> الالتزام بالمناشير الوزارية التي تنص على إجراء التقويم واستثمار نتائجه كجزء من التقويم التكويني الذي لا يدخل في المعدل الفصلي.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# ----------------- التذييل -----------------
st.sidebar.divider()
st.sidebar.markdown("""
<div style="text-align: center; color: gray; font-size: 0.85em;">
<b>المنظومة البيداغوجية الذكية لمادة الرياضيات</b><br>
مصممة وفق مخرجات مقاطعة تفتيش وهران 🇩🇿
</div>
""", unsafe_allow_html=True)