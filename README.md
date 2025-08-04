# 💼 Full-Stack Job Listing Web App – Project Documentation

This is a full-stack job listing web application that allows users to add, edit, delete, filter, and view job postings. It also includes a web scraper that automatically collects job data from the internet and populates the app.

---

## 🚀 Tech Stack

### Frontend:
- React.js (Functional Components, Hooks)
- HTML + CSS

### Backend:
- Flask (Python)
- SQLAlchemy + SQLite
- Flask-CORS

### Scraper:
- Python + Selenium
- Requests (for API communication)

---

## 📂 Project Structure

```
job-listing-app/
├── backend/
│   ├── __init__.py
│   ├── app.py
│   ├── models.py
│   ├── routes.py
│   ├── init_db.py
│   └── .env.example
├── frontend/
│   └── src/
│       ├── App.js
│       ├── JobCard.js
│       ├── JobForm.js
│       ├── Filters.js
│       ├── index.js
│       └── index.css
└── scraper/
    └── scrape_jobs.py
```

---

## 🛠️ Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/job-listing-app.git
cd job-listing-app
```

---

### 2. Backend Setup (Flask + SQLite)
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
python -m backend.init_db
python -m backend.app
```
Flask API will run at: `http://localhost:5000`

---

### 3. Frontend Setup (React)
```bash
cd frontend
npm install
npm start
```
React App will run at: `http://localhost:3000`

---

### 4. Scraper Setup (Optional)
```bash
cd scraper
pip install selenium requests
python scrape_jobs.py
```
> Make sure Flask backend is running **before** running the scraper.

---

## ✨ Features

- Add, edit, and delete jobs
- Filter jobs by type, location, and tags
- Sort by newest or oldest
- Responsive UI built with React
- Selenium-based scraper for auto-importing jobs


🎥 **Watch Introductory Video:** [Google Drive Link]([https://drive.google.com/your-demo-video-link](https://drive.google.com/drive/folders/1G9gAUy502usKGYwZJj3H5o2_xDvHgav_?usp=drive_link))

---

## 👨‍💻 Author

**[DecIder23]**  
GitHub: [github.com/DecIder23](https://github.com/DecIder23/Full-Stack-Job-Listing-Web-App)

---
