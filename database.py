import sqlite3

DATABASE_NAME = "school_data.db"

def get_connection():
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # 1. جدول الأقسام
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            level TEXT NOT NULL,
            class_name TEXT NOT NULL,
            school_year TEXT NOT NULL,
            UNIQUE(level, class_name, school_year)
        )
    """)

    # 2. جدول التلاميذ
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            class_id INTEGER NOT NULL,
            FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
            UNIQUE(full_name, class_id)
        )
    """)

    # 3. نتائج التقويم التشخيصي
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS diagnostic_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL UNIQUE,
            arithmetic REAL NOT NULL DEFAULT 0,
            algebra REAL NOT NULL DEFAULT 0,
            functions REAL NOT NULL DEFAULT 0,
            geometry REAL NOT NULL DEFAULT 0,
            total REAL NOT NULL DEFAULT 0,
            classification TEXT NOT NULL,
            updated_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
        )
    """)

    # 4. جدول الدروس القادمة
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS upcoming_lessons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_id INTEGER NOT NULL,
            lesson_title TEXT NOT NULL,
            resource TEXT NOT NULL,
            lesson_date TEXT NOT NULL,
            objective TEXT NOT NULL,
            notes TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE
        )
    """)

    # 5. جدول بطاقات المعالجة الميدانية
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS remediation_activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            resource TEXT NOT NULL,
            activity_type TEXT NOT NULL,
            response_level TEXT NOT NULL,
            teacher_note TEXT,
            activity_date TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
        )
    """)

    # 6. مصفوفة شجرة كفاءات المنهاج الجزائري
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS curriculum_matrix (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            level TEXT NOT NULL,
            unit TEXT NOT NULL,
            lesson_title TEXT NOT NULL,
            prerequisite_resource TEXT NOT NULL,
            default_objective TEXT NOT NULL
        )
    """)

    # 7. بنك الأنشطة العلاجية المصغرة (10 دقائق)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS remediation_bank (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resource TEXT NOT NULL,
            title TEXT NOT NULL,
            rule_summary TEXT NOT NULL,
            exercise_content TEXT NOT NULL,
            solution_content TEXT NOT NULL
        )
    """)

    # ترقية الجداول القديمة تلقائياً دون فقدان البيانات
    cursor.execute("PRAGMA table_info(diagnostic_results)")
    diag_cols = [c[1] for c in cursor.fetchall()]
    if "updated_at" not in diag_cols and len(diag_cols) > 0:
        cursor.execute("ALTER TABLE diagnostic_results ADD COLUMN updated_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))")

    # تغذية شجرة كفاءات المنهاج الجزائري تلقائياً (1AS و 2AS) عند أول تشغيل
    cursor.execute("SELECT count(*) FROM curriculum_matrix")
    if cursor.fetchone()[0] == 0:
        curriculum_data = [
            # 1AS
            ("1AS ج م ع ت", "الأعداد والحساب", "التحليل إلى جداء عوامل أولية والـ PGCD", "الأعداد والحساب", "تعيين القاسم المشترك الأكبر وتبسيط الكسور والجذور"),
            ("1AS ج م ع ت", "الترتيب والمجالات", "المجالات وحساب المسافة بالقيمة المطلقة", "الأعداد والحساب", "ترجمة المسافة بين نقطتين إلى متباينة بالقيمة المطلقة"),
            ("1AS ج م ع ت", "الحساب الجبري", "إشارة ثنائي الحد وحل المتراجحات", "الحساب الجبري", "دراسة إشارة ax+b وتوظيفها في حل المتراجحات"),
            ("1AS ج م ع ت", "عموميات على الدوال", "قراءة السوابق والصور وجدول التغيرات", "الدوال والمنحنيات", "استخراج الصور والسوابق بيانياً وحسابياً"),
            ("1AS ج م ع ت", "الدوال المرجعية", "دراسة وتمثيل دالة تآلفية ودالة مقلوب", "الدوال والمنحنيات", "رسم منحنى الدالة واستنتاج خواص اتجاه التغير"),
            ("1AS ج م ع ت", "الهندسة المستوية", "الحساب الشعاعي ومعادلة مستقيم", "الهندسة والأشعة", "حساب مركبات شعاع وطول قطعة وشرط الارتباط الخطي"),
            # 2AS
            ("2AS علوم تجريبية", "الدوال العددية", "اتجاه تغير مركب دالتين مألوفتين", "الدوال والمنحنيات", "تركيب دالتين وتحديد اتجاه تغير الدالة المركبة"),
            ("2AS علوم تجريبية", "الاشتقاقية", "حساب الدالة المشتقة وتطبيقاتها", "الحساب الجبري", "حساب مشتقات الدوال المألوفة وتعيين معادلة المماس"),
            ("2AS علوم تجريبية", "الاشتقاقية", "دراسة اتجاه التغير وتشكيل جدول التغيرات", "الحساب الجبري", "ربط إشارة المشتقة باتجاه تغير الدالة"),
            ("2AS علوم تجريبية", "النهايات", "السلوك التقاربي والمستقيمات المقاربة", "الدوال والمنحنيات", "قراءة وتعيين المستقيمات المقاربة الأفقية والعمودية"),
            ("2AS علوم تجريبية", "المتتاليات العددية", "المتتاليات الحسابية والهندسية وتطبيقاتها", "الأعداد والحساب", "إثبات طبيعة المتتالية وحساب الحد العام والمجموع"),
            ("2AS علوم تجريبية", "الهندسة الفضائية", "الجداء السلمي وتطبيقاته في المستوي", "الهندسة والأشعة", "حساب الجداء السلمي وإثبات تعامد شعاعين")
        ]
        cursor.executemany("""
            INSERT INTO curriculum_matrix (level, unit, lesson_title, prerequisite_resource, default_objective)
            VALUES (?, ?, ?, ?, ?)
        """, curriculum_data)

    # تغذية بنك الأنشطة العلاجية المصغرة (10 دقائق)
    cursor.execute("SELECT count(*) FROM remediation_bank")
    if cursor.fetchone()[0] == 0:
        remediation_data = [
            (
                "الحساب الجبري",
                "نشاط علاجي 10 دقائق: إشارة ثنائي الحد ax + b",
                "ينعدم ax + b عند x0 = -b/a. تكون الإشارة عكس إشارة a قبل الجذر، ونفس إشارة a بعد الجذر.",
                "1) ادرس إشارة: A(x) = 2x - 6 \n2) ادرس إشارة: B(x) = -3x + 12 \n3) حل المتراجحة: 2x - 6 ≥ 0",
                "1) الجذر هو 3؛ سالبة قبل 3 وموجبة بعد 3.\n2) الجذر هو 4؛ موجبة قبل 4 وسالبة بعد 4.\n3) مجموعة الحلول: S = [3, +∞["
            ),
            (
                "الأعداد والحساب",
                "نشاط علاجي 10 دقائق: توحيد المقامات وتبسيط الجذور",
                "لجمع كسرين نوحد المقامين بضربهما في المضاعف المشترك. لتبسيط جذر: √(a² × b) = a√b.",
                "1) احسب وبسط: A = 2/3 - 5/6\n2) اكتب على الشكل a√3 العدد: B = √75 - 2√12 + √27",
                "1) A = 4/6 - 5/6 = -1/6\n2) B = 5√3 - 4√3 + 3√3 = 4√3"
            ),
            (
                "الدوال والمنحنيات",
                "نشاط علاجي 10 دقائق: التمييز بين الصورة والسابقة",
                "حساب صورة x نعوض x في عبارة الدالة f(x). إيجاد سوابق y يعني حل المعادلة f(x) = y.",
                "لتكن f(x) = x² - 1:\n1) احسب صورة العدد 2 بالدالة f.\n2) عين سوابق العدد 3 بالدالة f.",
                "1) f(2) = 2² - 1 = 3 (صورة 2 هي 3).\n2) x² - 1 = 3 ⟹ x² = 4 ⟹ x = 2 أو x = -2 (سوابق 3 هي -2 و 2)."
            ),
            (
                "الهندسة والأشعة",
                "نشاط علاجي 10 دقائق: حساب مركبات شعاع والمسافة",
                "مركبتا الشعاع AB هما (xB - xA, yB - yA). طول القطعة: AB = √[(xB - xA)² + (yB - yA)²].",
                "في معلم متعامد ومتجانس، لتكن A(1, 2) و B(4, 6):\n1) عين مركبتي الشعاع AB.\n2) احسب الطول AB.",
                "1) مركبتي AB هما: (4 - 1, 6 - 2) = (3, 4).\n2) الطول AB = √(3² + 4²) = √(9 + 16) = √25 = 5."
            )
        ]
        cursor.executemany("""
            INSERT INTO remediation_bank (resource, title, rule_summary, exercise_content, solution_content)
            VALUES (?, ?, ?, ?, ?)
        """, remediation_data)

    conn.commit()
    conn.close()