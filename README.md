# 🔥 fastapi-react-habit-tracker — habits & streaks (React + FastAPI + MongoDB)

> Track habits with daily check-ins; current and longest **streaks** are computed server-side. **React** + **FastAPI** + **MongoDB**, pytest/vitest harness.

![React](https://img.shields.io/badge/React-18-61dafb)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)
![MongoDB](https://img.shields.io/badge/MongoDB-7-47A248)
![Tests](https://img.shields.io/badge/tests-pytest%20%2B%20vitest-brightgreen)

## ✨ Features
- Habits with idempotent daily check-ins (`$addToSet`).
- **Streak engine**: current run (ending at the latest check-in) and longest run,
  computed from the check-in set — unit-tested directly.
- Backend tested with in-memory Mongo (`mongomock`).

## 🚀 Run
```bash
docker compose up --build
cd client && npm install && npm run dev
```

## ✅ Test
```bash
./run_harness.sh                 # pytest + vitest
```

## 🔌 API
`GET /api/habits` · `POST /api/habits` · `GET /api/habits/{id}` ·
`POST|DELETE /api/habits/{id}/checkin` · `DELETE /api/habits/{id}`

## 📝 License
MIT — see [LICENSE](LICENSE).
