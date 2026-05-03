# 📊 Market Data API (FastAPI)

A FastAPI-based backend service to fetch, store, and analyze monthly market data from an external API.

- Fetch monthly market data from external API
- Store data in SQLite database
- Prevent duplicate inserts (year + month)
- Auto-fetch missing months
- Aggregate yearly data (min, max, total)


## 🏗️ Project Structure
project/
│
├── app/
│ ├── main.py
│ ├── api_routes.py
│ ├── market_service.py
│ ├── market_repository.py
│ ├── external_api.py
│ ├── exceptions.py
│ ├── model.py
│ ├── db.py
│ └── logger.py
│
├── database/
│ └── prices.db
│
├── logs/
│ └── app.log
│
├── .env
├── requirements.txt
└── README.md

## ⚙️ Setup

### 1. Create virtual environment

```bash
python -m venv .venv

.venv\Scripts\activate

pip install -r requirements.txt

BASE_URL=
API_KEY=
TIMEOUT=10
DB_PATH=database/