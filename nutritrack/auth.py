from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
from . import mail, db
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, History, MealPlan
from . import db
from .utils import analyze_nutrition, get_daily_insight, get_calorie_recommendation_from_openai, calculate_bmi
import json
from datetime import datetime, time, date, timedelta
import os

auth = Blueprint('auth', __name__)
auth.google=None


@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        password2 = request.form.get('password2')

        if not password:
            flash("Password cannot be empty.", "danger")
            return redirect(url_for('auth.register'))

        if password != password2:
            flash("Passwords do not match.", "danger")
            return redirect(url_for('auth.register'))

        if User.query.filter_by(email=email).first():
            flash("Email already registered", "danger")
            return redirect(url_for('auth.register'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('auth.login'))

    return render_template("register.html")


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            flash("Invalid credentials", "danger")
            return redirect(url_for('auth.login'))

        login_user(user)
        return redirect(url_for('auth.dashboard'))

    return render_template("login.html")


@auth.route("/dashboard")
@login_required
def dashboard():
    today = datetime.now().date()
    start_of_day = datetime.combine(today, time.min)
    end_of_day = datetime.combine(today, time.max)

    history = History.query.filter(
        History.user_id == current_user.id,
        History.timestamp.between(start_of_day, end_of_day)
    ).all()

    total_calories = total_protein = total_carbs = total_fats = total_sugars = total_fibre = 0
    parsed_history = []
    for record in history:
        try:
            data = json.loads(record.nutrition_result)

            total_calories += data.get("calories", {}).get("value", 0)
            total_protein += data.get("protein", {}).get("value", 0)
            total_carbs += data.get("carbohydrates", {}).get("value", 0)
            total_fats += data.get("fats", {}).get("value", 0)
            total_sugars += data.get("sugars", {}).get("value", 0)
            total_fibre += data.get("fibre", {}).get("value", 0)

            if "calories" in data:
                parsed_history.append({
                    "food_name": record.food_name,
                    "timestamp": record.timestamp.strftime("%Y-%m-%d %H:%M"),
                    "calories": data.get("calories", {}).get("value", 0)
                })
        except Exception as e:
            print(f"⚠️ Dashboard data processing failed for record ID {record.id}: {e}")

    totals = {
        "calories": round(total_calories), "protein": round(total_protein),
        "carbohydrates": round(total_carbs), "fats": round(total_fats),
        "sugars": round(total_sugars), "fibre": round(total_fibre)
    }

    insight = {}
    if len(parsed_history) > 0:
        insight_raw = get_daily_insight(totals, len(parsed_history), current_user.recommended_calories, user_goal=current_user.goal)
        try:
            insight = json.loads(insight_raw) if insight_raw else {}
        except Exception as e:
            print(f"⚠️ Insight JSON parsing failed: {e}")
            insight = {}

    insight.setdefault("food_insight", "Log your first food to get a daily insight!")
    insight.setdefault("calorie_insight", "Your calorie summary will appear here.")
    insight.setdefault("tip", "Ready for a new day! Analyze a meal to get started.")

    recent_meal = MealPlan.query.filter_by(user_id=current_user.id).order_by(MealPlan.timestamp.desc()).first()


    return render_template(
        "dashboard.html",
        totals=totals,
        total_count=len(parsed_history),
        recent_entries=parsed_history[:3],
        recent_meal=recent_meal,
        insight=insight,
        username=current_user.username,
        recommended_calories=current_user.recommended_calories,
        show_setup_prompt=(not current_user.weight_kg),
        show_update_prompt=(
                    current_user.last_health_update and (datetime.now() - current_user.last_health_update).days >= 7)
    )

@auth.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "info")
    return redirect(url_for('auth.login'))

@auth.route('/nutrition', methods=['GET', 'POST'])
@login_required
def nutrition():
    result = None
    if request.method == 'POST':
        photo = request.files.get('photo')
        food_name = request.form.get('food_name')
        ingredients = request.form.get('ingredients')
        preparation = request.form.get('preparation')

        try:
            raw_result = analyze_nutrition(photo, food_name, ingredients, preparation, user_goal=current_user.goal)
            if not raw_result:
                flash("Failed to analyze nutrition. Please try again.", "danger")
                return redirect(url_for("auth.nutrition"))

            parsed_result = json.loads(raw_result)

            new_record = History(
                food_name=food_name,
                ingredients=ingredients,
                nutrition_result=raw_result,
                user_id=current_user.id
            )
            db.session.add(new_record)
            db.session.commit()

            flash("Nutrition analysis saved to your history.", "success")
            result = parsed_result

        except Exception as e:
            flash(f'Error: {e}', 'danger')

    return render_template('nutrition.html', result=result)

@auth.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    from werkzeug.utils import secure_filename
    import os

    uploads_dir = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
    os.makedirs(uploads_dir, exist_ok=True)

    user = current_user
    history_count = History.query.filter_by(user_id=user.id).count()
    meals_count = MealPlan.query.filter_by(user_id=user.id).count()

    total_calories = 0
    history = History.query.filter_by(user_id=user.id).all()
    for record in history:
        try:
            data = json.loads(record.nutrition_result)
            total_calories += data.get("calories", {}).get("value", 0)
        except:
            continue

    if request.method == "POST":
        if "profile_pic" in request.files:
            file = request.files["profile_pic"]
            if file.filename and file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                filename = secure_filename(f"{user.id}_profile.png")
                filepath = os.path.join(uploads_dir, filename)
                file.save(filepath)
                flash("Profile picture updated!", "success")
            else:
                flash("Invalid file type. Only PNG/JPG allowed.", "danger")
            return redirect(url_for("auth.profile"))

    profile_pic = current_user.profile_pic_url or url_for('static', filename='profile_pics/default.png')
    # Check for a user-uploaded file, which takes precedence
    user_uploaded_pic = os.path.join(os.path.dirname(__file__), 'static', 'uploads', f"{current_user.id}_profile.png")
    if os.path.exists(user_uploaded_pic):
        profile_pic = url_for('static', filename=f'uploads/{current_user.id}_profile.png')

    return render_template(
        "profile.html",
        user=user,
        history_count=history_count,
        meals_count=meals_count,
        total_calories=total_calories,
        profile_pic=profile_pic
    )


@auth.route("/history")
@login_required
def history():
    records = History.query.filter_by(user_id=current_user.id).order_by(History.timestamp.desc()).all()

    for r in records:
        try:
            parsed = json.loads(r.nutrition_result)

            if isinstance(parsed.get("vitamins"), list):
                parsed["vitamins"] = {item["name"]: {"value": item["value"], "unit": item["unit"]} for item in parsed["vitamins"]}
            if isinstance(parsed.get("minerals"), list):
                parsed["minerals"] = {item["name"]: {"value": item["value"], "unit": item["unit"]} for item in parsed["minerals"]}

            required_keys = ["calories", "protein", "carbohydrates", "fats", "sugars", "fibre"]
            if all(k in parsed for k in required_keys):
                r.parsed_data = parsed
            else:
                r.parsed_data = None
        except:
            r.parsed_data = None

    return render_template("history.html", records=records)

@auth.route('/')
def home():
    return render_template('landing.html')

@auth.route("/plan-meal", methods=["GET", "POST"])
@login_required
def plan_meal():
    meal_plan = None
    if request.method == "POST":
        requirements = request.form.get('requirements')

        try:
            from .utils import generate_meal_plan
            raw_result = generate_meal_plan(requirements,user_goal=current_user.goal)
            if not raw_result:
                flash("Failed to generate meal plan. Please try again.", "danger")
                return redirect(url_for("auth.plan-meal"))

            parsed_result = json.loads(raw_result)

            new_plan = MealPlan(
                requirements=requirements,
                meal_plan_result=raw_result,
                user_id=current_user.id
            )
            db.session.add(new_plan)
            db.session.commit()

            meal_plan = parsed_result

        except Exception as e:
            flash(f"Error generating meal plan: {e}", "danger")

    return render_template("plan_meal.html", meal_plan=meal_plan)

@auth.route("/your-meals")
@login_required
def your_meals():

    meals = MealPlan.query.filter_by(user_id=current_user.id).order_by(MealPlan.timestamp.desc()).all()

    for meal in meals:
        try:
            meal.parsed_data = json.loads(meal.meal_plan_result)
        except:
            meal.parsed_data = {}

    return render_template("your_meals.html", meals=meals)

@auth.route('/delete-history/<int:id>', methods=["POST"])
@login_required
def delete_history(id):
    print(f"DELETE attempt for record {id} by user {current_user.id}")
    record = History.query.get_or_404(id)
    if record.user_id != current_user.id:
        return "Unauthorized", 403

    db.session.delete(record)
    db.session.commit()
    return '', 200

@auth.route('/delete-meal/<int:id>', methods=["POST"])
@login_required
def delete_meal(id):
    meal = MealPlan.query.get_or_404(id)
    if meal.user_id != current_user.id:
        return "Unauthorized", 403

    db.session.delete(meal)
    db.session.commit()
    return '', 200


@auth.route('/edit-username', methods=['POST'])
@login_required
def edit_username():
    new_username = request.form.get('username').strip()
    if new_username:
        current_user.username = new_username
        db.session.commit()
        flash("Username updated.", "success")
    else:
        flash("Username cannot be empty.", "danger")
    return redirect(url_for('auth.profile'))


@auth.route('/change-password', methods=['POST'])
@login_required
def change_password():
    if not current_user.password:
        flash("Password cannot be changed for accounts signed in with Google.", "warning")
        return redirect(url_for('auth.profile'))
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')

    if not check_password_hash(current_user.password, current_password):
        flash("Incorrect current password.", "danger")
    else:
        current_user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
        db.session.commit()
        flash("Password changed successfully.", "success")

    return redirect(url_for('auth.profile'))

@auth.route('/delete-account', methods=['POST'])
@login_required
def delete_account():
    user_to_delete = User.query.get(current_user.id)

    if not user_to_delete:
        flash("User not found.", "danger")
        return redirect(url_for('auth.profile'))


    History.query.filter_by(user_id=user_to_delete.id).delete()
    MealPlan.query.filter_by(user_id=user_to_delete.id).delete()

    try:
        profile_pic_path = os.path.join(
            os.path.dirname(__file__),
            'static', 'uploads', f"{user_to_delete.id}_profile.png"
        )
        if os.path.exists(profile_pic_path):
            os.remove(profile_pic_path)
    except Exception as e:
        print(f"Error deleting profile picture: {e}")

    logout_user()

    db.session.delete(user_to_delete)
    db.session.commit()

    flash("Your account has been permanently deleted.", "success")
    return redirect(url_for('auth.home'))


@auth.route("/health-details", methods=["GET", "POST"])
@login_required
def health_details():
    if request.method == "POST":
        current_user.dob = datetime.strptime(request.form.get('dob'), '%Y-%m-%d').date()
        current_user.gender = request.form.get('gender')
        current_user.height_cm = float(request.form.get('height_cm'))
        current_user.weight_kg = float(request.form.get('weight_kg'))
        current_user.activity_level = request.form.get('activity_level')
        current_user.goal = request.form.get('goal')
        current_user.last_health_update = datetime.now()

        new_target = get_calorie_recommendation_from_openai(current_user)
        if new_target:
            current_user.recommended_calories = new_target

        db.session.commit()
        flash("Your health details have been updated!", "success")
        return redirect(url_for('auth.health_details'))

    bmi = calculate_bmi(current_user)
    recommended_calories = current_user.recommended_calories

    return render_template(
        "health_details.html",
        bmi=bmi,
        recommended_calories=recommended_calories,
        max_date=date.today().isoformat()
    )

@auth.route('/google-login')
def google_login():
    # Redirect to Google's authentication page
    redirect_uri = url_for('auth.google_callback', _external=True)
    return auth.google.authorize_redirect(redirect_uri)


@auth.route('/google-callback')
def google_callback():
    # Get the authorization token from Google
    token = auth.google.authorize_access_token()
    # Get the user's profile info
    user_info = token.get('userinfo')
    if not user_info:
        flash("Could not retrieve user information from Google.", "danger")
        return redirect(url_for('auth.login'))

    # Find or create the user in your database
    user = User.query.filter_by(email=user_info['email']).first()

    if not user:
        # If user doesn't exist, create a new one
        new_user = User(
            email=user_info['email'],
            username=user_info['name'],
            profile_pic_url=user_info['picture'],
            # Password is not needed for OAuth users
            password=None
        )
        db.session.add(new_user)
        db.session.commit()
        user = new_user

    # Log the user in and redirect to the dashboard
    login_user(user)
    flash("Successfully logged in with Google!", "success")
    return redirect(url_for('auth.dashboard'))

@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()

        if user:
            # Generate a secure, timed token
            s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
            token = s.dumps(user.email, salt='password-reset-salt')

            # Create the reset URL
            reset_url = url_for('auth.reset_password', token=token, _external=True)

            # Create and send the email
            msg = Message('Password Reset Request for NutriTrack AI',
                          sender=current_app.config['MAIL_USERNAME'],
                          recipients=[user.email])
            msg.body = f'Hello {user.username},\n\nPlease click the following link to reset your password: {reset_url}\n\nIf you did not request this, please ignore this email.'
            mail.send(msg)

        # Show a confirmation message whether the user exists or not, for security
        flash('If an account with that email exists, a password reset link has been sent.', 'info')
        return redirect(url_for('auth.login'))

    return render_template('forgot_password.html')


@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        # Verify the token is valid and not expired (set to 30 minutes)
        email = s.loads(token, salt='password-reset-salt', max_age=1800)
    except (SignatureExpired, BadTimeSignature):
        flash('The password reset link is invalid or has expired.', 'danger')
        return redirect(url_for('auth.forgot_password'))

    user = User.query.filter_by(email=email).first()
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        password = request.form.get('password')
        password2 = request.form.get('password2')

        if not password or password != password2:
            flash('Passwords do not match or are empty.', 'danger')
            return redirect(url_for('auth.reset_password', token=token))

        # Update the user's password
        user.password = generate_password_hash(password, method='pbkdf2:sha256')
        db.session.commit()

        flash('Your password has been successfully updated! You can now log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('reset_password.html', token=token)


@auth.route('/create-tables-for-real')
def create_tables_once():
    """
    A secret, one-time-use URL to initialize the database tables on Supabase.
    """
    # We import these here to make this function self-contained
    from . import db
    from flask import current_app

    # The app_context is needed for database operations outside of a request
    with current_app.app_context():
        db.create_all()

    return "✅ Database tables created successfully! You can now remove this route from your auth.py file for security."