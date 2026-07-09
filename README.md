# Anik Tech School Website

A Flask-based school website with admin panel, student portal, and email notifications.

---

## Project Structure

```
anik_tech_school/
├── app.py                        ← Main Flask app
├── requirements.txt              ← Python dependencies
├── anik_tech.db                  ← SQLite database (auto-created on first run)
├── templates/
│   ├── base.html                 ← Public layout
│   ├── index.html                ← Home page
│   ├── programs.html             ← Programs page
│   ├── admissions.html           ← Admissions page
│   ├── about.html                ← About page
│   ├── contact.html              ← Contact page (with form)
│   ├── admin/
│   │   ├── base.html             ← Admin layout (sidebar)
│   │   ├── login.html            ← Admin login
│   │   ├── dashboard.html        ← Admin dashboard
│   │   ├── students.html         ← Student list
│   │   ├── add_student.html      ← Add student form
│   │   ├── messages.html         ← Contact messages
│   │   └── announcements.html    ← Announcements
│   └── student/
│       ├── base.html             ← Student portal layout
│       ├── login.html            ← Student login
│       ├── dashboard.html        ← Student dashboard
│       ├── grades.html           ← View grades
│       ├── courses.html          ← View courses
│       └── profile.html          ← Profile & change password
└── static/
    └── css/
        ├── style.css             ← Public styles
        ├── admin.css             ← Admin panel styles
        └── portal.css            ← Student portal styles
```

---

## How to Run

### Step 1 — Open the project
Open the `anik_tech_school` folder in PyCharm (or VS Code).

### Step 2 — Install Flask
Open Terminal and run:
```
pip install flask
```

### Step 3 — Configure Email (optional but recommended)
Open `app.py` and update lines 12–13:
```python
MAIL_USERNAME = 'your_gmail@gmail.com'
MAIL_PASSWORD = 'your_app_password'
```

> **How to get a Gmail App Password:**
> 1. Go to your Google Account → Security
> 2. Enable **2-Step Verification** (required)
> 3. Go to Security → **App Passwords**
> 4. Select app: "Mail", device: "Other (Custom name)" → type "Anik Tech"
> 5. Click Generate — copy the 16-character password
> 6. Paste it into `MAIL_PASSWORD` in app.py
>
> ⚠ Do NOT use your regular Gmail password — it won't work. You need an App Password.

Alternatively, set environment variables (more secure):
```
set MAIL_USERNAME=your_email@gmail.com   (Windows)
set MAIL_PASSWORD=your_app_password

export MAIL_USERNAME=your_email@gmail.com  (Mac/Linux)
export MAIL_PASSWORD=your_app_password
```

### Step 4 — Run the app
```
python app.py
```

### Step 5 — Open in browser
```
http://127.0.0.1:5000
```

---

## Pages & Login Credentials

| Page             | URL                      |
|------------------|--------------------------|
| Home             | /                        |
| Programs         | /programs                |
| About            | /about                   |
| Admissions       | /admissions              |
| Contact (form)   | /contact                 |
| Student Portal   | /student/login           |
| Admin Panel      | /admin/login             |

**Admin login:**
- Username: `admin`
- Password: `admin123`

**Demo student login:**
- Email: `amara@aniktech.edu.ng`
- Password: `student123`

---

## Features

### Public Website
- Home page with campus photo strip
- Programs, About, Admissions pages with images
- Contact form — saves to database, sends confirmation email

### Admin Panel (`/admin`)
- Dashboard with stats (students, messages, unread count)
- Add/remove students (auto-sends welcome email with login details)
- View all contact messages
- Post/delete announcements (shown on student portal)

### Student Portal (`/student`)
- Dashboard with GPA, level, announcements
- View registered courses for current level
- View grades with letter grades (A/B+/B etc.)
- Profile page with password change

---

## Customisation Tips

- To change admin password: update the seeded value in `init_db()` or log in and update the DB directly.
- To add more courses/programs: add rows to the `courses` table via the SQLite DB.
- To deploy online: use [Render.com](https://render.com) (free tier) — just push to GitHub and connect.
