# 📘 EasyDigest_Back

**EasyDigest** is an integrated learning platform that guides users from article selection to vocabulary learning, summarization, and quizzes — all in one seamless flow.  
This repository contains the **backend implementation** built with **Django** and **SQLite**.

---

## 🛠 Tech Stack

- ⚙️ **Backend Framework**: Django
- 🗄 **Database**: SQLite
- 🕷 **Web Crawling**: BeautifulSoup
- 🧠 **AI Integration**: OpenAI API

---

## 🚀 Getting Started

1. **Clone the repository**
   ```bash
   git clone https://github.com/syeongkim/EasyDigest_back.git
   ```

2. **Navigate to the project folder**
   ```bash
   cd easydigest
   ```

3. **Run the development server**
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

4. **Visit the local server**
   - [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 🔐 Authentication

- JWT-based authentication is implemented.
- Upon login, users receive a **JWT token**, which must be included in the `Authorization` header of all subsequent API requests.

---

## 🗂 Project Structure

```
easydigest/
├── apps/                 
│   ├── articles/         # APIs for retrieving and summarizing articles
│   ├── users/            # APIs for user authentication and profile management
│   └── words/            # APIs for vocabulary learning and quiz generation
├── easydigest/           # Project-wide Django configuration (settings, URLs, etc.)
├── .env                  # Environment variables (e.g., secret keys, DB config)
├── db.sqlite3            # Local SQLite database file
└── manage.py             # Django’s command-line utility for administrative tasks
```

---

## 📡 Core Features & API Overview

### 👤 User Authentication

| Method | Endpoint                              | Description                          |
|--------|----------------------------------------|--------------------------------------|
| POST   | `/api/users/signup/`                   | Register a new user                  |
| POST   | `/api/users/login/`                    | Login and receive JWT                |
| POST   | `/api/users/logout/`                   | Logout user                          |
| GET    | `/api/users/me/`                       | Get current user profile             |
| PATCH  | `/api/users/me/update/`                | Update user information              |
| GET    | `/api/users/check-username/`           | Check if username is available       |
| GET    | `/api/users/check-email/`              | Check if email is already in use     |
| PATCH  | `/api/users/change-password/`          | Change user password                 |

---

### 📰 Article Management

| Method | Endpoint                                              | Description                         |
|--------|--------------------------------------------------------|-------------------------------------|
| GET    | `/api/articles/<article_id>/`                          | Retrieve a specific article         |
| POST   | `/api/articles/`                                       | Upload a new article                |
| GET    | `/api/articles/my/`                                    | Retrieve articles uploaded by user  |
| GET    | `/api/articles/<article_id>/generate-summary/`         | Generate summary using AI           |

---

### 📚 Word Learning

| Method | Endpoint                                                     | Description                                      |
|--------|---------------------------------------------------------------|--------------------------------------------------|
| POST   | `/api/words/learn/`                                           | Provide AI-generated explanation for a word      |
| GET    | `/api/words/my/`                                              | Get list of words learned by the user            |
| GET    | `/api/words/article/<article_id>/`                            | Get learned words from a specific article        |
| POST   | `/api/words/generate-quiz/`                                   | Generate quiz based on learning history          |
| POST   | `/api/words/quiz/submit/`                                     | Submit quiz results and update learning history  |

---


> 🧠 **EasyDigest** helps users improve their reading comprehension and vocabulary through context-aware learning powered by AI.
