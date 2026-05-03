# 📊 Market Data API (FastAPI)

A FastAPI-based backend service to fetch, store, and analyze monthly market data from an external API.

- Fetch monthly market data from external API
- Store data in SQLite database
- Prevent duplicate inserts (year + month)
- Auto-fetch missing months
- Aggregate yearly data (min, max, total)


## 🏗️ Project Structure

```
market-data-api/
│
├── app/
│   ├── main.py
│   ├── api_routes.py
│   ├── market_service.py
│   ├── market_repository.py
│   ├── external_api.py
│   ├── exceptions.py
│   ├── model.py
│   ├── db.py
│   └── logger.py
│       
│
├── database/
│   └── Market_data.db
│
├── logs/
│   └── app.log
│
├── .env
├── requirements.txt
└── README.md
```

## ⚙️ Setup

### 1. Create virtual environment

```bash
python -m venv .venv

.venv\Scripts\activate

### 2. Install Dependencies
```bash
pip install -r requirements.txt

---
### 3. Configure Environment

Update `.env` file:

```ini
BASE_URL=
API_KEY=
TIMEOUT=10
DB_PATH=database/
```

---

## ▶️ Run Application

```bash
uvicorn app.main:app --reload --port 9000
```

Open:
```
http://127.0.0.1:9000/docs
```
## 📡 API Endpoints

### Save Data
```http
POST /save_all/{symbol}
```
Only used to bulk upload

### Get Annual Data
```http
GET /get_annual_market_values/symbols/{symbol}/annual/{year}
```

---

## 📝 Logs

```
logs/app.log
```

---

## 🗄️ Database

SQLite file:
```
database/Market_data.db
```

---
