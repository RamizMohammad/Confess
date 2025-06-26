<h1 align="center">🚀 Confess Backend Server</h1>

<p align="center">
  A secure and anonymous social platform backend built with <strong>FastAPI</strong>, <strong>Firebase Firestore</strong>, <strong>SMTP Email</strong>, and <strong>Telegram Bot logging</strong>.
</p>

<p align="center">
  <a href="https://confess-ysj8.onrender.com"><strong>🌐 Live Demo</strong></a> |
  <a href="#features">✨ Features</a> |
  <a href="#environment-variables">🔧 Environment</a>
</p>

---

## ✨ Features

- 🔐 Secure User Registration with optional password protection  
- 🧑‍💼 User Management: Create, Check, Delete users  
- 🔁 Password Reset Workflow with one-time token (10-min expiry)  
- 📬 Email Notifications using Jinja2 (Welcome, Forgot, Delete)  
- 🧠 Pydantic-based Request Validation  
- 📡 API Key Validation using `x-api-key` header  
- ☁️ Firebase Firestore + Storage Integration  
- 📊 Format helpers for dates (`Today`, `1w`) and counts (`1.2K`)  
- 📢 Real-time Telegram Logging for errors and events  
- 🔁 Background keep-alive thread for Render hosting  

---

---

## 🔧 Environment Variables

Set these in your `.env` file or deploy provider (e.g. Render):

```env
# Telegram Bot
BOT_TOKEN=your_telegram_bot_token
CHAT_ID=your_telegram_chat_id

# Firebase Admin SDK
FIREBASE_CREDENTIALS={"type": "..."}  # Full JSON as string

# Firebase Storage
BUCKET_NAME=your_bucket_name.appspot.com

# Gmail SMTP
SMTP_EMAIL=your_email@gmail.com
APP_PASSWORD=your_gmail_app_password

# API Key (use SHA-256 hash of your actual key)
API_KEY=sha256_hashed_api_key
```

<details> <summary><strong>📁 Project Structure</strong> (click to expand)</summary>
confess-server/
├── main.py               # FastAPI app and route definitions
├── Databaseconfig.py     # Firebase backend logic & Telegram logging
├── emailUtils.py         # Email sending using SMTP & Jinja2
├── formatMaker.py        # Human-readable date & count formatter
├── Model.py              # Pydantic data models for validation
├── Validator.py          # API key validation using SHA-256
├── Awake.py              # Keep-alive thread (Render workaround)
├── templates/            # Email HTML templates
└── static/               # Static files (optional)
</details>

<details> <summary><strong>🧪 Getting Started</strong> (click to expand)</summary>
pip install fastapi uvicorn firebase-admin jinja2 pydantic requests python-multipart
uvicorn main:app --reload

  Keep-alive thread will auto-start
  Access server at: http://127.0.0.1:8000
</details>

<details> <summary><strong>🔐 Security Notes</strong> (click to expand)</summary>
⚠️ Passwords are stored in plaintext – not recommended for production

✅ Firebase Firestore is used for all user/post/token data

🔐 All sensitive operations require hashed x-api-key

📧 Uses Gmail SMTP for email – secure with App Password

🧪 For production use, add proper password hashing and secure token storage

</details>

<details> <summary><strong>👤 Author</strong> (click to expand)</summary>
Made with ❤️ by Mohammad Ramiz
If you found this project helpful, consider starring the repo ⭐

</details>

This project is licensed under the MIT License
