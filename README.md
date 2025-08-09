# District Court Case Scraper – Faridabad

A Django-based web app that fetches and displays real-time case data from the Faridabad District Court website.  
It uses Selenium for automation, dynamically handles CAPTCHA fetching, and logs user searches for future reference.

---

## Features

- **Case Search Form:** Enter case type, registration number, and year to search.  
- **Live CAPTCHA Fetching:** CAPTCHA image is fetched live from the official court site using Selenium.  
- **Automated Data Fetching:** Retrieves case details directly from the court’s public data.  
- **Search History Logging:** Every search is logged into the database.  
- **Clean UI:** Modern, user-friendly interface for searching and viewing results.  
- **Optional PDF Export:** Download case details as a PDF for easy sharing or saving.  
- **Dummy Data Fallback:** If scraping fails, dummy data is displayed to keep the experience smooth.

---

## Tech Stack

- Backend: Django (Python)  
- Frontend: HTML, CSS  
- Web Automation: Selenium WebDriver  
- Database: SQLite (default)  
- Parsing: BeautifulSoup  

---

## CAPTCHA Strategy

The CAPTCHA image is fetched dynamically from the Faridabad court portal using Selenium and passed from backend to frontend without saving locally.

---

## Demo Video

Watch the full demo here:  
[![Demo Video](https://img.youtube.com/vi/VIDEO_ID/0.jpg)]([https://drive.google.com/file/d/1v5qX_e81DIxhBvqQasecZJDo5Y2eoYmD/view?usp=sharing](https://drive.google.com/file/d/1v5qX_e81DIxhBvqQasecZJDo5Y2eoYmD/view?usp=sharing))  

(Click the image to open the demo video in Google Drive.)

---

## Setup Instructions

1. Clone this repo.  
2. Create and activate a Python virtual environment.  
3. Install dependencies with `pip install -r requirements.txt`.  
4. Run migrations: `python manage.py migrate`.  
5. Start the development server: `python manage.py runserver`.  
6. Open `http://127.0.0.1:8000/` in your browser.  

---

## Contact

Author: **Sneha KS**  
Email: ksudheersneha2@gmail.com  
GitHub: [ksudheersneha-max](https://github.com/ksudheersneha-max)  

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
