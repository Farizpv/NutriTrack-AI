import os
import json
import openai
from datetime import date

def analyze_nutrition(photo, food_name, ingredients, preparation, user_goal=None):
    print("--- Entering analyze_nutrition function ---")
    goal_context = f"Keep in mind that my primary goal is {user_goal}." if user_goal else ""

    prompt = (
        "You are a certified nutritionist AI. Provide a detailed nutrition breakdown as JSON. "
        "The 'insight' should be a short health recommendation about this specific food. "
        f"{goal_context} Your response must follow this exact JSON structure:\n"
        "{ \"calories\": {\"value\": number, \"unit\": \"kcal\"}, \"protein\": {\"value\": number, \"unit\": \"g\"}, "
        "\"carbohydrates\": {\"value\": number, \"unit\": \"g\"}, \"fats\": {\"value\": number, \"unit\": \"g\"}, "
        "\"sugars\": {\"value\": number, \"unit\": \"g\"}, \"fibre\": {\"value\": number, \"unit\": \"g\"}, "
        "\"vitamins\": {\"Vitamin A\": {\"value\": number, \"unit\": \"mcg\"}, \"Vitamin C\": {\"value\": number, \"unit\": \"mg\"}}, "
        "\"minerals\": {\"Calcium\": {\"value\": number, \"unit\": \"mg\"}, \"Iron\": {\"value\": number, \"unit\": \"mg\"}}, "
        "\"insight\": \"Short health recommendation\", \"notes\": \"Any assumptions\"}\n"
        "Respond with valid JSON only.\n\n"
        f"Food Name: {food_name}\nIngredients: {ingredients}\nPreparation: {preparation}"
    )
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI Nutrition Error: {e}")
        return None


def generate_meal_plan(requirements, user_goal=None):
    print("--- Entering plan_meal function ---")
    goal_context = f"The entire meal plan should be tailored to help me achieve my goal of {user_goal}." if user_goal else ""

    prompt = (
        "You are a dietitian AI. Provide a meal plan JSON. The 'insights' should be a health recommendation. "
        f"{goal_context} Your response must follow this exact JSON structure:\n"
        "{ \"meal_name\": \"string\", \"ingredients\": [\"list\"], \"preparation\": \"string\", "
        "\"nutrition\": {\"calories\": number, \"protein\": number, \"carbs\": number, \"fats\": number, \"sugars\": number, \"fibre\": number}, "
        "\"vitamins\": {\"Vitamin A\": number, \"Vitamin C\": number}, \"minerals\": {\"Calcium\": number, \"Iron\": number}, "
        "\"insights\": \"Health recommendation\"}\n"
        "Respond only with JSON.\n\n"
        f"User Requirements: {requirements}"
    )
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI Meal Plan Error: {e}")
        return None


def get_daily_insight(totals, food_count, calorie_target=None, user_goal=None):
    print("--- Entering get_daily_insight function ---")
    prompt_details = (
        f"Your totals today: Calories: {totals['calories']} kcal, Protein: {totals['protein']} g, "
        f"Fats: {totals['fats']} g.\nTotal foods logged: {food_count}."
    )
    if calorie_target:
        prompt_details += f"\nYour recommended calorie target is {calorie_target} kcal."
    if user_goal:
        prompt_details += f"\nYour current goal is: {user_goal}."

    prompt = (
        "You are a helpful and friendly nutrition coach speaking directly to me, the user. "
        "Use a supportive tone and the words 'You' and 'Your'. "
        "Based on my data and my primary goal below, provide a short JSON insight with three keys: "
        "'food_insight', 'calorie_insight', and 'tip'. The tip should be relevant to my goal.\n\n"
        f"My Data for Today:\n{prompt_details}\n\nRespond with valid JSON only."
    )
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI Insight Error: {e}")
        return None


def get_calorie_recommendation_from_openai(user):
    if not all([user.weight_kg, user.height_cm, user.dob, user.activity_level, user.gender, user.goal]):
        return None

    age = calculate_age(user.dob)
    bmi = calculate_bmi(user)

    prompt = (
        "You are an expert nutritionist. Based on the following user data, calculate the recommended daily calorie intake. "
        "First, calculate the user's Total Daily Energy Expenditure (TDEE). Then, adjust this value based on their goal: "
        "for 'Weight Loss', create a sensible deficit (around 300-500 kcal); "
        "for 'Weight Gain', create a sensible surplus (around 300-500 kcal); "
        "for 'Maintain Weight', stick to the TDEE. "
        "Also consider their BMI in your final recommendation. "
        "Respond ONLY with a valid JSON object in the format {\"recommended_calories\": number}.\n\n"
        f"User Data:\n- Age: {age}\n- Gender: {user.gender}\n- Height: {user.height_cm} cm\n"
        f"- Weight: {user.weight_kg} kg\n- BMI: {bmi}\n- Activity Level: {user.activity_level}\n"
        f"- Primary Goal: {user.goal}"
    )
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50
        )
        data = json.loads(response.choices[0].message.content.strip())
        return int(data.get("recommended_calories"))
    except Exception as e:
        print(f"OpenAI Calorie Recommendation Error: {e}")
        return None

def calculate_age(dob):
    if not dob:
        return 0
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))


def calculate_bmi(user):
    if not user.height_cm or not user.weight_kg:
        return None
    height_m = user.height_cm / 100
    return round(user.weight_kg / (height_m ** 2), 1)