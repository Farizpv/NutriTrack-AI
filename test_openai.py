import os
import openai
from dotenv import load_dotenv

# Load variables from your .env file
load_dotenv()

print("Attempting to call the OpenAI API...")

try:
    # Configure the API key
    openai.api_key = os.getenv("OPENAI_API_KEY")

    # Check if the key was loaded
    if not openai.api_key:
        raise ValueError("OPENAI_API_KEY not found in .env file.")

    # Make a simple API call
    response = openai.chat.completions.create(
      model="gpt-4.1-nano",  # Using the exact model name from your utils.py
      messages=[
        {"role": "user", "content": "Say 'Hello, World!' in JSON format: {\"greeting\": \"...\"}"}
      ]
    )

    print("\n✅ API Call Successful!")
    print("Response:")
    print(response.choices[0].message.content)

except openai.AuthenticationError as e:
    print("\n❌ AUTHENTICATION ERROR:")
    print("This means your API key is invalid, expired, or incorrect.")
    print("Please double-check the OPENAI_API_KEY in your .env file.")

except openai.NotFoundError as e:
    print("\n❌ NOT FOUND ERROR:")
    print(f"This likely means the model name 'gpt-4.1-nano' is incorrect or you don't have access to it.")
    print("Try changing the model name in this script to 'gpt-3.5-turbo' and run it again.")

except openai.RateLimitError as e:
    print("\n❌ RATE LIMIT or BILLING ERROR:")
    print("This means you have either run out of credits, have no payment method on file with OpenAI, or are sending requests too quickly.")
    print("Please check your usage and billing details on the OpenAI website.")

except Exception as e:
    print(f"\n❌ AN UNEXPECTED ERROR OCCURRED:")
    print(e)