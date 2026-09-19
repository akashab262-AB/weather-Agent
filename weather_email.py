"""
Pune Weather Update - Automatic Email Sender
=============================================

What this program does:
1. Fetches the current weather for Pune, Maharashtra from the free
   Open-Meteo API (no API key needed).
2. Builds a nicely formatted email with the weather details.
3. Sends that email to you using Gmail's SMTP server.

How to use:
1. Install the only external library needed:
       pip install requests
2. Fill in your Gmail address and Gmail "App Password" in the
   CONFIGURATION section below.
3. Run the program:
       python pune_weather_email.py

No .env files, no environment variables, no JSON config files,
no Zapier, no external automation tools. Everything lives right here
in this one file.
"""

import smtplib
from email.mime.text import MIMEText
from datetime import datetime

import requests


# =========================================================
# CONFIGURATION (edit these values yourself)
# =========================================================

# --- Weather API settings (Open-Meteo, free, no API key required) ---
WEATHER_API_URL = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude=18.5204&longitude=73.8567"
    "&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m"
    "&timezone=Asia%2FKolkata"
)

# --- Gmail SMTP settings ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Replace these with your own details.
SENDER_EMAIL = "mylyrical226@gmail.com"
SENDER_APP_PASSWORD = "ykhn ezhq nrqd hknm"   # Gmail "App Password", not your normal password
RECEIVER_EMAIL = "akashab262@gmail.com"


# =========================================================
# STEP 1: Get the weather data
# =========================================================
def get_weather():
    """
    Contacts the Open-Meteo API and returns the current weather
    for Pune as a dictionary with:
        temperature, humidity, weather_code, wind_speed, timestamp
    """
    try:
        response = requests.get(WEATHER_API_URL, timeout=10)
    except requests.exceptions.ConnectionError:
        raise RuntimeError(
            "Could not connect to the internet. Please check your connection."
        )
    except requests.exceptions.Timeout:
        raise RuntimeError("The weather request timed out. Please try again.")
    except requests.exceptions.RequestException as error:
        raise RuntimeError(f"Something went wrong contacting the weather service: {error}")

    if response.status_code != 200:
        raise RuntimeError(
            f"Weather service returned an error (status code {response.status_code})."
        )

    try:
        data = response.json()
        current = data["current"]

        temperature = current["temperature_2m"]
        humidity = current["relative_humidity_2m"]
        weather_code = current["weather_code"]
        wind_speed = current["wind_speed_10m"]
        timestamp = current["time"]
    except (KeyError, ValueError, TypeError):
        raise RuntimeError("The weather service sent back an unexpected response format.")

    return {
        "temperature": temperature,
        "humidity": humidity,
        "weather_code": weather_code,
        "wind_speed": wind_speed,
        "timestamp": timestamp,
    }


# =========================================================
# STEP 2: Create the email
# =========================================================
def create_email(weather_data):
    """
    Builds the email subject and body using the weather data,
    and returns a ready-to-send MIMEText message.
    """
    subject = "🌤️ Pune Weather Update"

    # Make the timestamp a bit more readable, e.g. "2026-09-19 14:00"
    try:
        parsed_time = datetime.fromisoformat(weather_data["timestamp"])
        readable_time = parsed_time.strftime("%Y-%m-%d %H:%M")
    except (ValueError, TypeError):
        readable_time = weather_data["timestamp"]

    body = f"""Hello Bala,

Here is the current weather update for Pune, Maharashtra:

📍 Location: Pune, Maharashtra, India
🌡️ Temperature: {weather_data['temperature']} °C
💧 Humidity: {weather_data['humidity']} %
🌤️ Weather Code: {weather_data['weather_code']}
💨 Wind Speed: {weather_data['wind_speed']} km/h
🕒 Updated: {readable_time}

This weather report was generated automatically by Python.
"""

    message = MIMEText(body, "plain", "utf-8")
    message["Subject"] = subject
    message["From"] = SENDER_EMAIL
    message["To"] = RECEIVER_EMAIL

    return message


# =========================================================
# STEP 3: Send the email
# =========================================================
def send_email(message):
    """
    Connects to Gmail's SMTP server, logs in, sends the email,
    and closes the connection. Never prints the app password.
    """
    server = None
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, message.as_string())

    except smtplib.SMTPAuthenticationError:
        raise RuntimeError(
            "Gmail login failed. Please check that SENDER_EMAIL and "
            "SENDER_APP_PASSWORD are correct. (Remember: use a Gmail "
            "App Password, not your normal password.)"
        )
    except smtplib.SMTPConnectError:
        raise RuntimeError("Could not connect to the Gmail SMTP server. Check your internet connection.")
    except smtplib.SMTPException as error:
        raise RuntimeError(f"Something went wrong while sending the email: {error}")
    except OSError:
        raise RuntimeError("Network error while trying to send the email. Please check your connection.")
    finally:
        if server is not None:
            try:
                server.quit()
            except Exception:
                pass


# =========================================================
# STEP 4: Main program
# =========================================================
def main():
    try:
        # 1. Get the weather
        weather_data = get_weather()
        print("Weather data fetched successfully.")
        print("📍 Pune, Maharashtra")
        print(f"🌡️ Temperature: {weather_data['temperature']} °C")
        print(f"💧 Humidity: {weather_data['humidity']} %")
        print(f"🌤️ Weather Code: {weather_data['weather_code']}")
        print(f"💨 Wind Speed: {weather_data['wind_speed']} km/h")

        # 2. Create the email
        message = create_email(weather_data)

        # 3. Send the email
        send_email(message)
        print("📧 Email sent successfully!")

    except RuntimeError as error:
        # Friendly, beginner-readable error messages
        print(f"❌ Error: {error}")
    except Exception as error:
        # Catch-all for anything unexpected, without ever showing the password
        print(f"❌ An unexpected error occurred: {error}")


if __name__ == "__main__":
    main()
