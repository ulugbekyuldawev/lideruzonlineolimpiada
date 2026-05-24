# LIDER.Uz Onlayn Olimpiada

Frontend: Vue/Vite  
Backend: Django REST Framework

## Local ishga tushirish

Backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_deploy
python manage.py runserver
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## Deploy

Netlify + Railway uchun `DEPLOY_NETLIFY_RAILWAY.md` faylini o‘qing.

## Admin

```text
Login: ulugbek
Parol: codingwithulugbek20030313
```
