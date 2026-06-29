# 🚀 Deployment Guide (Render)

This guide explains how to deploy the Smart Cafe project to [Render.com](https://render.com).

## 1. Prepare for Production
Before deploying, ensure your `settings.py` is ready:
- Set `DEBUG = False`.
- Update `ALLOWED_HOSTS` to include your Render URL.
- Use `python-dotenv` for environment variables.

## 2. Render Web Service Configuration
When creating a new **Web Service** on Render, use the following settings:

- **Runtime**: `Python`
- **Build Command**: `pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput`
- **Start Command**: `gunicorn cafe_project.wsgi:application`

## 3. Environment Variables
Add these in the Render Dashboard under **Environment**:

| Key | Value |
| :--- | :--- |
| `PYTHON_VERSION` | `3.10.0` (or your version) |
| `DJANGO_SETTINGS_MODULE` | `cafe_project.settings` |
| `SECRET_KEY` | `your-very-secret-key-here` |
| `DEBUG` | `False` |
| `DATABASE_URL` | *(If using external DB like Postgres)* |

## 4. Static Files
Render handles static files differently. Ensure you have `whitenoise` installed and configured in `MIDDLEWARE` for production:
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Add this
    # ...
]
```

## 5. Deployment Steps
1. Push your code to GitHub.
2. Connect your GitHub repo to Render.
3. Configure the settings above.
4. Deploy!

---

### ⚠️ Note on SQLite
Render's filesystem is ephemeral. If you use SQLite, your data will be reset on every deploy. For production, it is highly recommended to use **Render PostgreSQL**.
