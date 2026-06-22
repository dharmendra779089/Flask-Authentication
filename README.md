# 🔐 Flask Authentication

A complete user authentication system built with **Flask**, **Flask-Login**, and **SQLAlchemy**. This application demonstrates secure user registration, login, logout, session management, and protected routes with file downloads.

---

## ✨ Features

| Feature | Description |
|---|---|
| **User Registration** | Create a new account with name, email, and password |
| **Secure Password Storage** | Passwords are hashed using PBKDF2-SHA256 with salting (never stored as plaintext) |
| **User Login** | Authenticate with email and password credentials |
| **Session Management** | Flask-Login manages user sessions via secure cookies |
| **Protected Routes** | Pages restricted to authenticated users only via `@login_required` |
| **Flash Messages** | Real-time feedback for duplicate emails, wrong passwords, etc. |
| **File Download** | Authenticated users can download a protected PDF file |
| **Responsive UI** | Bootstrap 4 navbar with conditional navigation based on auth state |

---

## 📁 Project Structure

```
Flask-Authentication/
│
├── main.py                    # Main application — routes, models, config
├── requirements.txt           # Python dependencies with pinned versions
├── .gitignore                 # Files excluded from version control
├── README.md                  # This documentation file
│
├── templates/                 # Jinja2 HTML templates
│   ├── base.html              # Base layout (navbar, head, CSS imports)
│   ├── index.html             # Home page (login/register buttons)
│   ├── login.html             # Login form with flash messages
│   ├── register.html          # Registration form (name, email, password)
│   └── secrets.html           # Protected page with file download link
│
├── static/                    # Static assets served by Flask
│   ├── css/
│   │   └── styles.css         # Custom styles (gradients, buttons, inputs)
│   └── files/
│       └── cheat_sheet.pdf    # Downloadable file for authenticated users
│
└── instance/                  # Auto-generated at runtime (not committed)
    └── users.db               # SQLite database storing user records
```

---

## 🛠️ Tech Stack

| Technology | Version | Purpose |
|---|---|---|
| [Python](https://www.python.org/) | 3.11+ | Programming language |
| [Flask](https://flask.palletsprojects.com/) | 3.0.0 | Web framework |
| [Flask-Login](https://flask-login.readthedocs.io/) | 0.6.3 | User session management |
| [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/) | 3.1.1 | Database ORM integration |
| [SQLAlchemy](https://www.sqlalchemy.org/) | 2.0.25 | SQL toolkit & ORM |
| [Werkzeug](https://werkzeug.palletsprojects.com/) | 3.0.0 | Password hashing & WSGI utilities |
| [Bootstrap](https://getbootstrap.com/) | 4.5.2 | Frontend CSS framework (via CDN) |
| [SQLite](https://www.sqlite.org/) | — | Lightweight file-based database |

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.11** or higher installed on your system
- **pip** (Python package manager, included with Python)

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/your-username/Flask-Authentication.git
   cd Flask-Authentication
   ```

2. **Create a virtual environment**

   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\activate

   # macOS / Linux
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**

   ```bash
   python main.py
   ```

5. **Open in your browser**

   Navigate to [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 📖 How It Works

### Application Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────────┐
│  Home Page   │────▶│  Register    │────▶│  Secrets Page    │
│  (index.html)│     │  (register)  │     │  (Protected)     │
└──────┬───────┘     └──────────────┘     └────────┬─────────┘
       │                                           │
       ▼                                           ▼
┌──────────────┐                          ┌──────────────────┐
│  Login Page  │─────────────────────────▶│  Download File   │
│  (login)     │                          │  (Protected)     │
└──────────────┘                          └──────────────────┘
```

### Authentication Flow

1. **Registration** (`/register`):
   - User submits name, email, and password.
   - The app checks if the email already exists in the database.
   - If new, the password is hashed with PBKDF2-SHA256 (8-byte salt).
   - A new `User` record is created and saved to SQLite.
   - The user is automatically logged in and redirected to `/secrets`.

2. **Login** (`/login`):
   - User submits email and password.
   - The app queries the database for the email.
   - If found, it verifies the password against the stored hash.
   - On success, the user session is created via `login_user()`.

3. **Session Management**:
   - Flask-Login stores the user ID in a signed session cookie.
   - On every request, `@login_manager.user_loader` reloads the user from the database.
   - `current_user` proxy provides access to the logged-in user's data.

4. **Logout** (`/logout`):
   - `logout_user()` clears the session cookie data.
   - The user is redirected to the home page.

### Password Security

Passwords are **never stored as plaintext**. The app uses Werkzeug's `generate_password_hash()` with:
- **Algorithm**: PBKDF2 with SHA-256
- **Salt**: 8 random bytes (unique per password)
- **Output**: A hash string like `pbkdf2:sha256:260000$salt$hash`

---

## 🗄️ Database Schema

The application uses a single `User` table in SQLite:

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `INTEGER` | `PRIMARY KEY`, auto-increment | Unique user identifier |
| `email` | `VARCHAR(100)` | `UNIQUE`, `NOT NULL` | User's email address |
| `password` | `VARCHAR(100)` | `NOT NULL` | Hashed password (PBKDF2) |
| `name` | `VARCHAR(1000)` | `NOT NULL` | User's display name |

The database file is automatically created at `instance/users.db` on first run.

---

## 🔗 API Routes

| Route | Methods | Auth Required | Description |
|---|---|---|---|
| `/` | `GET` | ❌ | Home page with login/register buttons |
| `/register` | `GET`, `POST` | ❌ | User registration form and handler |
| `/login` | `GET`, `POST` | ❌ | User login form and handler |
| `/secrets` | `GET` | ✅ | Protected page with welcome message |
| `/logout` | `GET` | ✅ | Logs out the user and redirects home |
| `/download` | `GET` | ✅ | Downloads `cheat_sheet.pdf` |

---

## ⚠️ Important Security Notes

> **This project is for educational/demonstration purposes.**

For production deployment, you should:

1. **Change the secret key** — Replace `'secret-key-goes-here'` with a long, random string:
   ```python
   import os
   app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
   ```

2. **Use environment variables** — Store sensitive config (secret key, database URI) in `.env` files, not in source code.

3. **Disable debug mode** — Never run `debug=True` in production:
   ```python
   app.run(debug=False)
   ```

4. **Use HTTPS** — Deploy behind a reverse proxy (Nginx/Apache) with SSL/TLS certificates.

5. **Add CSRF protection** — Use [Flask-WTF](https://flask-wtf.readthedocs.io/) for form validation and CSRF tokens.

6. **Use a production database** — Replace SQLite with PostgreSQL or MySQL for concurrent access.

---

## 📜 License

This project is open source and available under the [MIT License](LICENSE).

---

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

## 📬 Contact

If you have questions or suggestions, feel free to open an [Issue](https://github.com/your-username/Flask-Authentication/issues) on GitHub.
