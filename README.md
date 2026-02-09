# Sakura Gacha API

A gacha (loot box) pull simulator backend built with **FastAPI** and **SQLite**. Features weighted random drops, a pity system, inventory tracking, pull history, and player statistics.

## Features

- **JWT Authentication** — register and login to track your collection
- **Themed Banners** — multiple item pools with unique drop tables
- **Weighted Random Drops** — Common (70%), Rare (20%), Epic (8%), Legendary (2%)
- **Pity System** — guaranteed Epic after 50 pulls, guaranteed Legendary after 90 pulls
- **10-Pull Guarantee** — at least one Rare or above in every multi-pull
- **Inventory Tracking** — see all collected items and duplicates
- **Pull History** — timestamped log of every pull
- **Statistics** — pull counts, rarity breakdown, luck rating, and pity counters

## Tech Stack

- Python, FastAPI, SQLAlchemy, Pydantic, SQLite, JWT (python-jose), bcrypt

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Seed the database with banners and items
python -m app.seed

# Start the server
uvicorn app.main:app --reload
```

Then open **http://localhost:8000/docs** for the interactive Swagger UI.

## API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/auth/register` | Create an account | No |
| POST | `/auth/login` | Get JWT token | No |
| GET | `/banners` | List active banners | No |
| GET | `/banners/{id}` | Banner details + drop rates | No |
| POST | `/banners/{id}/pull` | Pull 1 item | Yes |
| POST | `/banners/{id}/pull/ten` | Pull 10 items | Yes |
| GET | `/inventory` | Your collected items | Yes |
| GET | `/history` | Your pull history | Yes |
| GET | `/stats` | Your pull statistics | Yes |

## How the Gacha System Works

Items are selected using weighted random sampling based on configured drop rates. A pity system tracks consecutive pulls without high-rarity items:

- **Soft pity (Epic)**: After 50 pulls without an Epic or Legendary, the next pull is a guaranteed Epic
- **Hard pity (Legendary)**: After 90 pulls without a Legendary, the next pull is a guaranteed Legendary
- **10-pull safety net**: Every multi-pull guarantees at least one Rare or above
