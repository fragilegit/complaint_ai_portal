# Complaint & Fault Management System with AI Chatbot

A containerised Django/PostgreSQL application that implements the take-home requirements for a complaint and fault management workflow plus a Groq-powered customer chatbot.

## Project Overview

The application has two modules:

1. Complaint & Fault Management System
   - Customers submit and track complaints
   - Agents manage assigned complaints, add notes, and escalate when needed
   - Admins assign complaints, move complaints through the full workflow, and view dashboard metrics
2. AI Customer Chatbot
   - Logged-in customers ask natural-language account questions
   - The chatbot answers only from retrieved database context using Groq `llama-3.1-8b-instant`


## Prerequisites

- Docker
- Docker Compose

## Environment Setup

1. Copy `.env.example` to `.env`
2. Populate the values:

| Variable | Description |
|---|---|
| `DEBUG` | Django debug flag |
| `SECRET_KEY` | Django secret key |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts |
| `POSTGRES_DB` | PostgreSQL database name |
| `POSTGRES_USER` | PostgreSQL username |
| `POSTGRES_PASSWORD` | PostgreSQL password |
| `POSTGRES_HOST` | PostgreSQL host (use `db` in Docker) |
| `POSTGRES_PORT` | PostgreSQL port |
| `GROQ_API_KEY` | Groq API key used by the chatbot |
| `SLA_BREACH_DAYS` | SLA breach threshold in days |
| `DEFAULT_CURRENCY` | Currency of choice |
| `CURRENCY_SYMBOL` | Currency Symbol of choice |

## How to Run

```bash
cp .env.example .env
# edit .env and add your GROQ_API_KEY

docker compose up --build -d
```

After startup the app is available at `http://localhost:8000`.

## How Seeding Works

On container startup the entrypoint automatically:

1. Waits for PostgreSQL
2. Runs migrations
3. Runs `python manage.py seed_initial_data`

The seed command is idempotent and only inserts the sample dataset when core records are missing.

## Default Login Credentials

All seeded passwords are: `Password123!`

### Admin
- `admin1`

### Agents
- `agent1`
- `agent2`
- `agent3`

### Customers
- `customer1`
- `customer2`
- `customer3`
- `customer4`
- `customer5`

## Chatbot Setup

- Add a valid `GROQ_API_KEY` to `.env`
- Log in as any customer
- Open the Chatbot page and ask account questions

## Assumptions & Design Decisions

- A custom `User` model is used with role-based permissions (`customer`, `agent`, `admin`)
- Complaint workflow transitions are enforced in application logic; admins can override any status
- Bootstrap via CDN is used to keep the UI simple and fast to review
- Chat history is persisted in the database and also mirrored in the session for continuity
- The chatbot prompt is deliberately constrained so the LLM answers only from retrieved account context
- Active faults are tied to customer regions to support outage questions