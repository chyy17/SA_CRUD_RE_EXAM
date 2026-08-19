# SA CRUD Exam

A small Flask + MySQL CRUD application for managing branches, categories, and products.

## Requirements

- Python 3.10+
- MySQL 8.x (or a compatible MySQL server)

## Run locally

### 1. Clone the repository

```bash
git clone https://github.com/chyy17/SA_CRUD_RE_EXAM.git
cd SA_CRUD_RE_EXAM
```

### 2. Create a virtual environment

Windows:

```powershell
py -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure MySQL

The app reads these environment variables:

| Variable | Default |
|---|---|
| `DB_HOST` | `localhost` |
| `DB_PORT` | `3306` |
| `DB_USER` | `root` |
| `DB_PASSWORD` | empty |
| `DB_NAME` | `crud_db` |
| `PORT` | `5000` |

PowerShell example:

```powershell
$env:DB_HOST="localhost"
$env:DB_PORT="3306"
$env:DB_USER="root"
$env:DB_PASSWORD="your_mysql_password"
$env:DB_NAME="crud_db"
```

The application automatically creates the `crud_db` database and the `Branch`, `Category`, and `Product` tables when it starts. The MySQL account must have permission to create databases and tables.

### 5. Start the website

```bash
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

## Features

- Branch CRUD with image upload
- Category CRUD
- Product CRUD
- Product-to-category and product-to-branch relationships
- Automatic database/table initialization
- Environment-based database configuration
- 5 MB image upload limit
- Bootstrap responsive UI

## Important

Do not commit database passwords or other secrets. Use environment variables instead.
