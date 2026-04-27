# Security Report - Salman Store

## Goal

Protect the Django project from basic web attacks and control user access at the author level.

## 1) CSRF Protection

### Implemented

- Protected form page: `/contact/` (`templates/contact_form.html`)
- The form includes `{% csrf_token %}`.
- Experiment page without token: `/contact/no-csrf/` (`templates/contact_no_csrf.html`)

### What happens without token

When posting from `/contact/no-csrf/`, Django rejects the request with **HTTP 403 Forbidden** because `CsrfViewMiddleware` requires a valid CSRF token on unsafe methods (POST/PUT/PATCH/DELETE).

## 2) XSS Protection in Templates

### Implemented

- User-controlled fields are rendered using normal Django template variables:
  - `{{ category.obj.description }}`
  - `{{ product.obj.description }}`
  - `{{ submitted_data.message }}`
- No `|safe` filter is used for untrusted user input.

### Experiment

If the database contains `<script>alert("XSS")</script>`, Django auto-escapes output in templates and displays it as plain text in the browser (not executable JavaScript).

## 3) Author-Level Access Control

### Implemented

- Added `owner` foreign key (`User`) to:
  - `Category`
  - `Product`
  - `Order`
- List views show only data owned by the logged-in user.
- Create views set the owner automatically to `request.user`.
- Product creation limits category choices to categories owned by the current user.
- Order endpoint requires ownership of the selected product.
- Product detail page checks ownership before showing data.

Result: users can only view and manipulate their own records.

## 4) Security Audit (`check --deploy`)

Command used:

```bash
python manage.py check --deploy
```

Warnings returned:

- `security.W004`: `SECURE_HSTS_SECONDS` not set
- `security.W008`: `SECURE_SSL_REDIRECT` not set to `True`
- `security.W009`: insecure/auto-generated `SECRET_KEY`
- `security.W012`: `SESSION_COOKIE_SECURE` not set to `True`
- `security.W016`: `CSRF_COOKIE_SECURE` not set to `True`
- `security.W018`: `DEBUG=True` in deployment

### Meaning of severities

- **Critical**: severe security risk with immediate high-impact exposure; fix urgently before deployment.
- **Warning**: significant hardening gap that increases risk; should be resolved before production release.

### Recommended fixes

- Set `DEBUG=False` in production.
- Use a strong random `DJANGO_SECRET_KEY` from environment variables.
- Enable HTTPS-only behavior:
  - `SECURE_SSL_REDIRECT=True`
  - `SECURE_HSTS_SECONDS=31536000` (or policy-appropriate value)
  - `SECURE_HSTS_INCLUDE_SUBDOMAINS=True`
  - `SECURE_HSTS_PRELOAD=True`
  - `SESSION_COOKIE_SECURE=True`
  - `CSRF_COOKIE_SECURE=True`

## Summary

The project now demonstrates CSRF protection (including a 403 no-token experiment), XSS-safe template rendering, and author-level access control for core store data.
