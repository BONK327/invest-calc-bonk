# Инвестиционный калькулятор (MVP)

Веб-приложение на FastAPI: расчёт сложных процентов с ежемесячной капитализацией и пополнениями.

## Структура

```
invest-calc/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI: API + раздача страницы
│   ├── calculator.py    # расчётное ядро (формулы)
│   └── static/
│       ├── index.html   # интерфейс
│       ├── style.css
│       └── app.js       # запрос к API и вывод результатов
├── requirements.txt
├── Dockerfile
└── .dockerignore
```

## Локальный запуск

```bash
cd invest-calc
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Откройте http://127.0.0.1:8000 — калькулятор.
Документация API (Swagger): http://127.0.0.1:8000/docs

## Запуск в Docker

```bash
docker build -t invest-calc .
docker run --rm -p 8000:8000 invest-calc
```

Откройте http://localhost:8000

## Пример запроса к API

```bash
curl -X POST http://localhost:8000/api/calculate \
  -H "Content-Type: application/json" \
  -d '{"initial": 100000, "monthly": 10000, "rate": 12, "years": 10}'
```

## Формулы

- Месячная ставка: `i = rate / 100 / 12`
- Каждый месяц: `баланс = баланс * (1 + i) + пополнение`
- Замкнутая форма: `FV = P*(1+i)^n + C*((1+i)^n - 1)/i`, где `n = years * 12`
- Внесено: `P + C*n`; чистый доход: `FV - (P + C*n)`
