# NutriTrack AI 🥗

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A full-stack web application built with Flask and Python that provides AI-powered nutrition analysis, meal planning, and goal-oriented recommendations using the OpenAI API.

**[Live Demo Link Here]** `(<- Link to your deployed Render app)`

---

## ✨ Features

* **User Authentication:** Secure registration and login for both standard email/password and Google OAuth 2.0.
* **AI Nutrition Analysis:** Users can input a meal's name, ingredients, and preparation method to receive a detailed nutritional breakdown from the OpenAI API.
* **AI Meal Planner:** Generate custom meal plans tailored to user-specified requirements (e.g., "high protein, vegetarian").
* **Goal-Oriented Recommendations:** The app calculates a personalized daily calorie target based on the user's physical details and primary goal (Weight Loss, Weight Gain, Maintain Weight).
* **Dynamic Dashboard:** An interactive dashboard displays daily totals, macro-nutrient charts (Chart.js), and personalized AI-generated insights.
* **Full History:** All analyzed meals and generated meal plans are saved to the user's account for future reference.

---

## 🛠️ Tech Stack

* **Backend:** Python, Flask, SQLAlchemy, Gunicorn
* **Database:** PostgreSQL
* **AI:** OpenAI API
* **Frontend:** HTML, CSS, JavaScript, Bootstrap 5
* **Authentication:** Flask-Login (session-based), Authlib (Google OAuth)
* **Deployment:** Render

---

## ⚙️ How to Run Locally

To get a local copy up and running, follow these simple steps.

### Prerequisites

* Python 3.10+
* A virtual environment tool (like `venv`)

### Installation

1.  **Clone the repository:**
    ```sh
    git clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
    cd your-repo-name
    ```
2.  **Create and activate a virtual environment:**
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```
3.  **Install the required packages:**
    ```sh
    pip install -r requirements.txt
    ```
4.  **Set up your environment variables:**
    * Create a `.env` file in the root directory.
    * Add the following keys with your own secret values:
      ```env
      SECRET_KEY='your_flask_secret_key'
      OPENAI_API_KEY='your_openai_api_key'
      GOOGLE_CLIENT_ID='your_google_client_id'
      GOOGLE_CLIENT_SECRET='your_google_client_secret'
      MAIL_SERVER='smtp.gmail.com'
      MAIL_PORT=587
      MAIL_USE_TLS=True
      MAIL_USERNAME='your_gmail_address'
      MAIL_PASSWORD='your_gmail_app_password'
      ```
5.  **Initialize the database:**
    * Start the Flask shell:
      ```sh
      flask shell
      ```
    * Inside the shell, create the database tables:
      ```python
      >>> from app import db
      >>> db.create_all()
      >>> exit()
      ```
6.  **Run the application:**
    ```sh
    flask run
    ```
    The app will be available at `http://127.0.0.1:5000`.

---

## 📜 License

Distributed under the MIT License. See `LICENSE` file for more information.