# NutriTrack AI 🥗

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-black.svg)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-blue.svg)](https://www.postgresql.org/)

A full-stack web application built with Python and Flask that provides AI-powered nutrition analysis, goal-oriented meal planning, and personalized health insights using the OpenAI API.

### 🚀 **[View the Live Demo](https://nutritrack-ai-6s55.onrender.com)** 🚀

*(Note: Free-tier deployment may take a moment to spin up on the first visit.)*

---

## ✨ Key Features

* **Secure User Authentication:**
    * Standard email/password registration with server-side validation.
    * Seamless "Sign in with Google" (OAuth 2.0) integration.
    * Full password recovery flow ("Forgot Password") via email.

* **AI-Powered Nutrition Engine (OpenAI):**
    * **Nutrition Analysis:** Get a detailed nutritional breakdown (calories, macros, vitamins, minerals) for any meal by describing it.
    * **Meal Planner:** Generate custom meal plans tailored to user-specified requirements (e.g., "high protein, vegetarian").
    * **Personalized Recommendations:** The app calculates a unique daily calorie target based on the user's physical details (age, height, weight, gender, activity level) and their primary fitness goal (Weight Loss, Weight Gain, or Maintain Weight).
    * **Dynamic Daily Insights:** The dashboard provides real-time, personalized tips and feedback based on the user's daily intake versus their goals.

* **Dynamic & Interactive Frontend:**
    * A responsive, mobile-friendly interface built with Bootstrap 5.
    * Interactive data visualization for macronutrient breakdown using Chart.js.
    * Consistent and modern dark/themed UI for all pop-up modals and public-facing pages.
    * Full user profile management, including profile picture uploads.
    * Complete history of all analyzed foods and saved meal plans.

---

## 🛠️ Tech Stack & Architecture

* **Backend:** Python, Flask, Gunicorn
* **Database:** PostgreSQL (Production), SQLite (Development)
* **ORM:** SQLAlchemy
* **AI:** OpenAI API (`gpt-3.5-turbo`)
* **Frontend:** HTML5, CSS3, JavaScript, Jinja2, Bootstrap 5, Chart.js
* **Authentication:**
    * Session-based management with Flask-Login.
    * Google OAuth 2.0 handled by Authlib.
    * Secure password hashing with Werkzeug.
    * Timed, secure tokens for password reset with ItsDangerous.
* **Email:** Flask-Mail with a Google App Password.
* **Deployment:** Render (Web Service + PostgreSQL)

---

## ⚙️ How to Run Locally

To get a local copy up and running, follow these simple steps.

### Prerequisites

* Python 3.10+
* A virtual environment tool (like `venv`)

### Installation & Setup

1.  **Clone the repository:**
    ```sh
    git clone [https://github.com/](https://github.com/)[your-github-username]/[your-repo-name].git
    cd [your-repo-name]
    ```
2.  **Create and activate a virtual environment:**
    ```sh
    python -m venv venv
    # On Windows:
    venv\Scripts\activate
    # On Mac/Linux:
    source venv/bin/activate
    ```
3.  **Install the required packages:**
    ```sh
    pip install -r requirements.txt
    ```
4.  **Set up your environment variables:**
    * Create a `.env` file in the root directory.
    * Add the following keys with your own secret values:
        ```env
        # Flask & Security
        SECRET_KEY='your_strong_flask_secret_key'

        # OpenAI
        OPENAI_API_KEY='your_openai_api_key'

        # Google OAuth
        GOOGLE_CLIENT_ID='your_google_client_id'
        GOOGLE_CLIENT_SECRET='your_google_client_secret'

        # Gmail for Password Reset
        MAIL_SERVER='smtp.gmail.com'
        MAIL_PORT=587
        MAIL_USE_TLS=True
        MAIL_USERNAME='your_gmail_address'
        MAIL_PASSWORD='your_16_digit_gmail_app_password'
        ```
5.  **Initialize the local database:**
    * Start the Flask shell:
        ```sh
        flask shell
        ```
    * Inside the shell, create the database tables:
        ```python
        >>> from nutritrack import db, create_app
        >>> app = create_app()
        >>> with app.app_context():
        ...     db.create_all()
        ...
        >>> exit()
        ```
6.  **Run the application:**
    ```sh
    flask run
    ```
    The app will be available at `http://127.0.0.1:5000`.

---

## 📜 License

Distributed under the MIT License.