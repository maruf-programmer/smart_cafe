# 🛠 Installation Guide

Follow these steps to set up the Smart Cafe Management System on your local machine.

## 📋 Prerequisites
- Python 3.10 or higher
- Git
- Virtualenv (recommended)

## 📥 Step 1: Clone the Repository
```bash
git clone https://github.com/SizningUsername/cafe_project.git
cd cafe_project
```

## 🌐 Step 2: Virtual Environment Setup
It's best practice to use a virtual environment to avoid dependency conflicts.

**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**Linux / MacOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

## 📦 Step 3: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 🗄️ Step 4: Database Configuration
1. **Apply Migrations**: Create the database schema.
   ```bash
   python manage.py migrate
   ```
2. **Seed Data**: Populate the database with initial categories, items, and tables.
   ```bash
   python seed_data.py
   python seed_staff.py
   ```

## 👤 Step 5: Create Administrative User
```bash
python manage.py createsuperuser
```
*Note: If you used the seed scripts, an admin user might already exist (admin / admin123).*

## 🚀 Step 6: Launch the Server
```bash
python manage.py runserver
```
- **Public Site**: `http://127.0.0.1:8000/`
- **Staff Dashboard**: `http://127.0.0.1:8000/staff/`
- **Django Admin**: `http://127.0.0.1:8000/admin/`

---

## 🧪 Running Tests
To ensure everything is working correctly:
```bash
python manage.py test
```

## 🛠️ Troubleshooting
- **Images not loading?** Ensure `DEBUG = True` in `settings.py` for local development.
- **Port already in use?** Try `python manage.py runserver 8080`.
