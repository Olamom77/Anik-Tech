from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_from_directory, make_response
from functools import wraps
import sqlite3, hashlib, smtplib, os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "anik-tech-secret-2026")

DB_PATH = "anik_tech.db"
ADMIN_USERNAME = "abdulmalik"
ADMIN_PASSWORD = "Adeyinka77"
ADMIN_NAME     = "Abdulmalik Abdulgafar"

MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "your_email@gmail.com")
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "your_app_password")
MAIL_FROM     = f"Anik Tech School <{MAIL_USERNAME}>"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.executescript('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            program TEXT NOT NULL,
            level TEXT NOT NULL,
            gpa TEXT DEFAULT "0.00",
            status TEXT DEFAULT "Active",
            joined TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            subject TEXT,
            message TEXT NOT NULL,
            sent_at TEXT NOT NULL,
            read INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS announcements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            body TEXT NOT NULL,
            created_at TEXT NOT NULL,
            author TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL,
            title TEXT NOT NULL,
            units INTEGER NOT NULL,
            program TEXT NOT NULL,
            level TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS grades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            course_id INTEGER NOT NULL,
            score REAL NOT NULL,
            grade TEXT NOT NULL,
            semester TEXT NOT NULL
        );
    ''')

    # Always reset admin credentials
    c.execute("DELETE FROM admins")
    c.execute("INSERT INTO admins (username,password,name) VALUES (?,?,?)",
              (ADMIN_USERNAME, hash_pw(ADMIN_PASSWORD), ADMIN_NAME))

    # Seed demo student
    c.execute("INSERT OR IGNORE INTO students (student_id,name,email,password,program,level,gpa,joined) VALUES (?,?,?,?,?,?,?,?)",
              ("ANK/2024/001","Amara Okafor","amara@aniktech.edu.ng",hash_pw("student123"),
               "Computer Science","300L","3.85","2024-09-01"))

    # Seed courses
    for co in [("CSC301","Data Structures & Algorithms",3,"Computer Science","300L"),
               ("CSC302","Operating Systems",3,"Computer Science","300L"),
               ("CSC303","Database Management",3,"Computer Science","300L"),
               ("CSC304","Web Development",2,"Computer Science","300L"),
               ("CSC305","Computer Networks",3,"Computer Science","300L")]:
        c.execute("INSERT OR IGNORE INTO courses (code,title,units,program,level) VALUES (?,?,?,?,?)", co)

    # Seed grades
    for g in [("ANK/2024/001",1,85,"A","2024/2025 Semester 1"),
              ("ANK/2024/001",2,78,"B+","2024/2025 Semester 1"),
              ("ANK/2024/001",3,91,"A","2024/2025 Semester 1"),
              ("ANK/2024/001",4,88,"A","2024/2025 Semester 1"),
              ("ANK/2024/001",5,74,"B","2024/2025 Semester 1")]:
        c.execute("INSERT OR IGNORE INTO grades (student_id,course_id,score,grade,semester) VALUES (?,?,?,?,?)", g)

    # Seed announcements
    for a in [("Welcome to 2026/2027 Session",
               "We are delighted to welcome all returning and new students. Orientation begins September 5th.",
               "2026-08-20", ADMIN_NAME),
              ("Semester 1 Exam Timetable Released",
               "The examination timetable for Semester 1 has been published. Please check and prepare accordingly.",
               "2026-09-01", ADMIN_NAME)]:
        c.execute("INSERT OR IGNORE INTO announcements (title,body,created_at,author) VALUES (?,?,?,?)", a)

    conn.commit()
    conn.close()

# ── Run init_db at startup ────────────────────────────────────
init_db()

def send_email(to, subject, html):
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = MAIL_FROM
        msg["To"]      = to
        msg.attach(MIMEText(html, "html"))
        with smtplib.SMTP("smtp.gmail.com", 587) as s:
            s.starttls()
            s.login(MAIL_USERNAME, MAIL_PASSWORD)
            s.sendmail(MAIL_USERNAME, to, msg.as_string())
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

def admin_required(f):
    @wraps(f)
    def dec(*a, **kw):
        if "admin_id" not in session:
            flash("Please log in as admin.", "error")
            return redirect(url_for("admin_login"))
        return f(*a, **kw)
    return dec

def student_required(f):
    @wraps(f)
    def dec(*a, **kw):
        if "student_id" not in session:
            flash("Please log in to your student portal.", "error")
            return redirect(url_for("student_login"))
        return f(*a, **kw)
    return dec

# ══ PWA ROUTES ═══════════════════════════════════════════════
@app.route("/manifest.json")
def pwa_manifest():
    return jsonify({
        "name": "Anik Tech School",
        "short_name": "Anik Tech",
        "description": "Official app for Anik Tech School",
        "start_url": "/", "display": "standalone",
        "background_color": "#185FA5", "theme_color": "#185FA5",
        "orientation": "portrait-primary", "scope": "/",
        "icons": [{"src": f"/static/icons/icon-{s}x{s}.png","sizes": f"{s}x{s}","type":"image/png","purpose":"any maskable"} for s in [72,96,128,144,152,192,384,512]],
        "shortcuts": [
            {"name":"Student Portal","url":"/student/login","icons":[{"src":"/static/icons/icon-96x96.png","sizes":"96x96"}]},
            {"name":"Contact Us","url":"/contact","icons":[{"src":"/static/icons/icon-96x96.png","sizes":"96x96"}]},
        ]
    })

@app.route("/sw.js")
def pwa_sw():
    resp = make_response(send_from_directory("static/js", "sw.js"))
    resp.headers["Content-Type"] = "application/javascript"
    resp.headers["Service-Worker-Allowed"] = "/"
    return resp

# ══ DEBUG & SETUP ROUTES ══════════════════════════════════════
@app.route("/setup")
def setup():
    try:
        init_db()
        return "<h2>✅ Database initialized!</h2><p>Admin: <strong>abdulmalik</strong> / <strong>Adeyinka77</strong></p><a href='/admin/login'>Go to Admin Login</a>"
    except Exception as e:
        return f"<h2>❌ Error</h2><p>{e}</p>"

@app.route("/debug-admin")
def debug_admin():
    try:
        db = get_db()
        admins = db.execute("SELECT id, username, name FROM admins").fetchall()
        db.close()
        result = "<h2>Admins in DB:</h2><ul>"
        for a in admins:
            result += f"<li>Username: <strong>{a['username']}</strong> | Name: {a['name']}</li>"
        if not admins:
            result += "<li>❌ NO ADMINS - DB is empty!</li>"
        result += "</ul><a href='/setup'>Run Setup</a> | <a href='/admin/login'>Admin Login</a>"
        return result
    except Exception as e:
        return f"Error: {e} <a href='/setup'>Run Setup</a>"

# ══ PUBLIC ROUTES ═════════════════════════════════════════════
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/programs")
def programs():
    return render_template("programs.html")

@app.route("/admissions")
def admissions():
    return render_template("admissions.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/gallery")
def gallery():
    return render_template("gallery.html")

@app.route("/contact", methods=["GET","POST"])
def contact():
    if request.method == "POST":
        name    = request.form.get("name","").strip()
        email   = request.form.get("email","").strip()
        phone   = request.form.get("phone","").strip()
        subject = request.form.get("subject","").strip()
        message = request.form.get("message","").strip()
        if name and email and message:
            db = get_db()
            db.execute("INSERT INTO messages (name,email,phone,subject,message,sent_at) VALUES (?,?,?,?,?,?)",
                       (name,email,phone,subject,message,datetime.now().strftime("%Y-%m-%d %H:%M")))
            db.commit(); db.close()
            flash("Message sent! We'll reply within 24 hours. ✓","success")
            return redirect(url_for("contact"))
        flash("Please fill in all required fields.","error")
    return render_template("contact.html")

# ══ ADMIN ROUTES ══════════════════════════════════════════════
@app.route("/admin/login", methods=["GET","POST"])
def admin_login():
    if "admin_id" in session:
        return redirect(url_for("admin_dashboard"))
    if request.method == "POST":
        username = request.form.get("username","").strip()
        password = request.form.get("password","").strip()
        db = get_db()
        row = db.execute("SELECT * FROM admins WHERE username=? AND password=?",
                         (username, hash_pw(password))).fetchone()
        db.close()
        if row:
            session["admin_id"]   = row["id"]
            session["admin_name"] = row["name"]
            return redirect(url_for("admin_dashboard"))
        flash("Invalid username or password.","error")
    return render_template("admin/login.html")

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_id",None); session.pop("admin_name",None)
    return redirect(url_for("admin_login"))

@app.route("/admin")
@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    db = get_db()
    stats = {
        "students":      db.execute("SELECT COUNT(*) FROM students").fetchone()[0],
        "messages":      db.execute("SELECT COUNT(*) FROM messages").fetchone()[0],
        "unread":        db.execute("SELECT COUNT(*) FROM messages WHERE read=0").fetchone()[0],
        "announcements": db.execute("SELECT COUNT(*) FROM announcements").fetchone()[0],
    }
    recent = db.execute("SELECT * FROM messages ORDER BY sent_at DESC LIMIT 5").fetchall()
    db.close()
    return render_template("admin/dashboard.html", stats=stats, recent_msgs=recent)

@app.route("/admin/students")
@admin_required
def admin_students():
    db = get_db()
    students = db.execute("SELECT * FROM students ORDER BY joined DESC").fetchall()
    db.close()
    return render_template("admin/students.html", students=students)

@app.route("/admin/students/add", methods=["GET","POST"])
@admin_required
def admin_add_student():
    if request.method == "POST":
        name  = request.form["name"].strip()
        email = request.form["email"].strip()
        prog  = request.form["program"].strip()
        level = request.form["level"].strip()
        pw    = request.form["password"].strip()
        db    = get_db()
        count = db.execute("SELECT COUNT(*) FROM students").fetchone()[0] + 1
        sid   = f"ANK/{datetime.now().year}/{count:03d}"
        try:
            db.execute("INSERT INTO students (student_id,name,email,password,program,level,joined) VALUES (?,?,?,?,?,?,?)",
                       (sid,name,email,hash_pw(pw),prog,level,datetime.now().strftime("%Y-%m-%d")))
            db.commit()
            flash(f"Student {name} ({sid}) added successfully! ✓","success")
        except Exception as e:
            flash(f"Error: {e}","error")
        finally:
            db.close()
        return redirect(url_for("admin_students"))
    return render_template("admin/add_student.html")

@app.route("/admin/students/delete/<int:sid>", methods=["POST"])
@admin_required
def admin_delete_student(sid):
    db = get_db()
    db.execute("DELETE FROM students WHERE id=?", (sid,))
    db.commit(); db.close()
    flash("Student removed.","success")
    return redirect(url_for("admin_students"))

@app.route("/admin/messages")
@admin_required
def admin_messages():
    db = get_db()
    msgs = db.execute("SELECT * FROM messages ORDER BY sent_at DESC").fetchall()
    db.execute("UPDATE messages SET read=1"); db.commit(); db.close()
    return render_template("admin/messages.html", messages=msgs)

@app.route("/admin/announcements", methods=["GET","POST"])
@admin_required
def admin_announcements():
    db = get_db()
    if request.method == "POST":
        db.execute("INSERT INTO announcements (title,body,created_at,author) VALUES (?,?,?,?)",
                   (request.form["title"].strip(), request.form["body"].strip(),
                    datetime.now().strftime("%Y-%m-%d"), session["admin_name"]))
        db.commit()
        flash("Announcement published. ✓","success")
    anns = db.execute("SELECT * FROM announcements ORDER BY created_at DESC").fetchall()
    db.close()
    return render_template("admin/announcements.html", announcements=anns)

@app.route("/admin/announcements/delete/<int:aid>", methods=["POST"])
@admin_required
def admin_delete_announcement(aid):
    db = get_db(); db.execute("DELETE FROM announcements WHERE id=?", (aid,))
    db.commit(); db.close()
    flash("Deleted.","success")
    return redirect(url_for("admin_announcements"))

# ══ STUDENT PORTAL ROUTES ═════════════════════════════════════
@app.route("/student/login", methods=["GET","POST"])
def student_login():
    if "student_id" in session:
        return redirect(url_for("student_dashboard"))
    if request.method == "POST":
        db  = get_db()
        row = db.execute("SELECT * FROM students WHERE email=? AND password=?",
                         (request.form["email"], hash_pw(request.form["password"]))).fetchone()
        db.close()
        if row:
            session["student_id"]   = row["student_id"]
            session["student_name"] = row["name"]
            return redirect(url_for("student_dashboard"))
        flash("Invalid email or password.","error")
    return render_template("student/login.html")

@app.route("/student/logout")
def student_logout():
    session.pop("student_id",None); session.pop("student_name",None)
    return redirect(url_for("student_login"))

@app.route("/student")
@app.route("/student/dashboard")
@student_required
def student_dashboard():
    db  = get_db()
    stu = db.execute("SELECT * FROM students WHERE student_id=?", (session["student_id"],)).fetchone()
    ann = db.execute("SELECT * FROM announcements ORDER BY created_at DESC LIMIT 4").fetchall()
    db.close()
    return render_template("student/dashboard.html", student=stu, announcements=ann)

@app.route("/student/grades")
@student_required
def student_grades():
    db  = get_db()
    stu = db.execute("SELECT * FROM students WHERE student_id=?", (session["student_id"],)).fetchone()
    grd = db.execute("""SELECT g.score,g.grade,g.semester,c.code,c.title,c.units
        FROM grades g JOIN courses c ON g.course_id=c.id
        WHERE g.student_id=? ORDER BY g.semester,c.code""", (session["student_id"],)).fetchall()
    db.close()
    return render_template("student/grades.html", grades=grd, student=stu)

@app.route("/student/courses")
@student_required
def student_courses():
    db  = get_db()
    stu = db.execute("SELECT * FROM students WHERE student_id=?", (session["student_id"],)).fetchone()
    crs = db.execute("SELECT * FROM courses WHERE program=? AND level=?",
                     (stu["program"], stu["level"])).fetchall()
    db.close()
    return render_template("student/courses.html", courses=crs, student=stu)

@app.route("/student/profile", methods=["GET","POST"])
@student_required
def student_profile():
    db  = get_db()
    stu = db.execute("SELECT * FROM students WHERE student_id=?", (session["student_id"],)).fetchone()
    if request.method == "POST":
        np = request.form.get("new_password","").strip()
        cp = request.form.get("confirm_password","").strip()
        if np and np == cp:
            db.execute("UPDATE students SET password=? WHERE student_id=?",
                       (hash_pw(np), session["student_id"]))
            db.commit()
            flash("Password updated. ✓","success")
        else:
            flash("Passwords do not match.","error")
    db.close()
    return render_template("student/profile.html", student=stu)

if __name__ == "__main__":
    app.run(debug=True)
