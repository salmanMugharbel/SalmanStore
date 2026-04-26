# Salman Store (Django Online Store)

A simple Django-based online store project with authentication, product/category management, ordering, and security demonstrations (CSRF, XSS rendering, and deploy security audit).

## Features

- User registration, login, and logout
- Product and category listing
- Create categories/products (authenticated users)
- Place orders for products
- Contact form protected by CSRF token
- Safe template rendering for user-controlled text (XSS-safe by default)

## Tech Stack

- Python
- Django
- SQLite
- HTML/CSS templates

## Project Structure

```text
lab 13/
|- lab13/                # Django project config (settings, urls, wsgi, asgi)
|- shop/                 # Main app (models, views, forms, urls, migrations)
|- templates/            # HTML templates
|- static/               # Static files (CSS)
|- manage.py
```

## Setup and Run

1. Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

2. Install Django:

```bash
pip install django
```

3. Apply migrations:

```bash
python manage.py migrate
```

4. Run the development server:

```bash
python manage.py runserver
```

5. Open:

`http://127.0.0.1:8000/`

## Security Notes

### 1) CSRF Protection

- Form templates use `{% csrf_token %}` for POST requests.
- If the token is missing/invalid, Django rejects the request with **HTTP 403 Forbidden**.

### 2) XSS Protection

- Django templates auto-escape variables by default (`{{ value }}`).
- Example input like `<script>alert("XSS")</script>` is rendered as plain text, not executed.
- Do not use `|safe` with untrusted user input.

### 3) Deployment Security Audit

Run:

```bash
python manage.py check --deploy
```

Typical warnings in development include:

- `DEBUG=True`
- missing `SECURE_SSL_REDIRECT`
- missing `SECURE_HSTS_SECONDS`
- insecure cookie flags (`SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`)
- weak/default `SECRET_KEY`

For production, set secure values using environment variables and a production settings profile.

## Useful Commands

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py check
python manage.py check --deploy
```

## License

Educational project / lab work.
