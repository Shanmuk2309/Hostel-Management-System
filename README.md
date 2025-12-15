# Hostel Management (Flask)

Quick steps to run the project locally.

Prerequisites
- Python 3.8+ installed
- MySQL server running and accessible

Install Python dependencies
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
```

Database setup
1. Start your MySQL server and create a database named `hostel_management`:
```sql
CREATE DATABASE hostel_management;
```
2. Run the SQL schema and seed scripts (from project root):
```bash
# Import schema
mysql -u root -p hostel_management < "DBMS files/setup.sql"
# Import seed data
mysql -u root -p hostel_management < "DBMS files/seed.sql"
```

Notes
- The DB connection configuration is in `app.py` (variable `DB_CONFIG`). Update user/password/host if needed.
- To run the app:
```bash
python app.py
```
Open http://127.0.0.1:5000/

Security
- Passwords are stored in plain text in the database and in `app.py` for convenience. For production use, please store secrets in environment variables and hash passwords.

If you want, I can also add a small script that automates DB creation and import. Would you like that?