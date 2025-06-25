# 🚀 Confess Backend Server

This is the backend server for **Confess**, a secure and anonymous social platform where users can register, post confessions, and manage their accounts. The backend is built using **FastAPI**, **Firebase Firestore**, and **Jinja2 templated emails**. It also includes background keep-alive logic and Telegram bot logging for robust error tracking.

---

## 🌐 Live Demo

🟢 Deployed at: [https://confess-ysj8.onrender.com](https://confess-ysj8.onrender.com)

---

## 📁 Project Structure
confess-server/
├── main.py # FastAPI application and routes
├── Databaseconfig.py # Firebase backend logic & Telegram logging
├── emailUtils.py # Email sending with SMTP and Jinja2 templates
├── formatMaker.py # Utility for formatting date and count
├── Model.py # Pydantic models for request validation
├── Validator.py # API key validation using SHA-256
├── Awake.py # Keep-alive thread for Render hosting
├── templates/ # HTML templates for email (welcome, reset, etc.)
└── static/ # Static files directory (optional)


---

## 🛠 Features

- 🔐 Secure User Registration with optional password
- 🧑‍💼 User Management: Create, Check, and Delete users
- 🔁 Password Reset Workflow with one-time token
- 📬 Email Notifications using Jinja2 templates (SMTP support)
- 🧠 Pydantic-based Request Validation
- 📡 API Key Validation via `x-api-key` Header
- 📦 Firebase Firestore + Storage Integration
- 📊 Utility formatters for likes (1.2K) and post dates (Today, 1w)
- 📢 Real-time Telegram Error & Status Logging
- 🔁 Render keep-alive thread (`/jagte-raho`)

---

## 🔧 Environment Variables

You must set the following variables either in a `.env` file or via your hosting provider (e.g., Render):

```env
BOT_TOKEN=your_telegram_bot_token
CHAT_ID=your_telegram_chat_id
FIREBASE_CREDENTIALS={"type": "..."}  # Full Firebase JSON credentials
BUCKET_NAME=your_firebase_storage_bucket
SMTP_EMAIL=your_email@gmail.com
APP_PASSWORD=your_gmail_app_password
API_KEY=sha256_hashed_api_key  # Hash of your actual key

Made with ❤️ by Mohammad Ramiz
