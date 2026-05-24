# LIDER.Uz — Netlify + Railway deploy

## 1) Backendni Railwayga joylash

1. GitHubga loyihani push qiling.
2. Railway → New Project → Deploy from GitHub repo.
3. Root deploy qilsangiz hech narsa o‘zgartirmang: `railway.json` avtomatik `backend/start.sh` ni ishga tushiradi.
   - Agar Railwayda Root Directory so‘ralsa: `backend` deb qo‘yish ham mumkin.
4. Railway Variables bo‘limiga kiriting:

```env
SECRET_KEY=uzun-random-secret-key
DEBUG=False
ALLOWED_HOSTS=.railway.app,.up.railway.app
ALLOW_NETLIFY_ORIGINS=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

5. PostgreSQL qo‘shsangiz, Railway `DATABASE_URL` ni o‘zi beradi.
6. Deploy tugagandan keyin Railway backend URL ni oching:

```text
https://YOUR-RAILWAY-BACKEND.up.railway.app/api/health/
```

`backend ishlayapti` chiqsa backend tayyor.

Backend start vaqtida quyidagilar avtomatik bajariladi:

```bash
python manage.py migrate --noinput
python manage.py seed_deploy
python manage.py collectstatic --noinput
gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
```

`seed_deploy` o‘quvchilar va natijalarni o‘chirmaydi. Faqat fanlar, darajalar va testlarni xavfsiz yaratadi/yangi qiladi.

## 2) Frontendni Netlifyga joylash

1. Netlify → Add new site → Import from GitHub.
2. Build sozlamalari:

```text
Base directory: frontend
Build command: npm ci && npm run build
Publish directory: frontend/dist
```

Agar Netlify `base=frontend` ni o‘zi olsa, publish directory `dist` bo‘lishi ham mumkin.

3. Netlify Environment variables:

```env
VITE_API_BASE_URL=https://YOUR-RAILWAY-BACKEND.up.railway.app/api
```

4. Deploy qiling.

## 3) CORS muammosi chiqsa

Railway backend Variables ichida Netlify manzilingizni qo‘shing:

```env
CORS_ALLOWED_ORIGINS=https://YOUR-NETLIFY-SITE.netlify.app,http://localhost:5173,http://127.0.0.1:5173
CSRF_TRUSTED_ORIGINS=https://YOUR-NETLIFY-SITE.netlify.app,http://localhost:5173,http://127.0.0.1:5173
ALLOW_NETLIFY_ORIGINS=True
```

Keyin Railwayda backendni redeploy qiling.

## 4) Admin login

```text
Login: ulugbek
Parol: codingwithulugbek20030313
```

Admin panel:

```text
https://YOUR-NETLIFY-SITE.netlify.app/admin/login
```
