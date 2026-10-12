
import requests

API_KEY = "6d660a3e7fea49ee107ad508def1b411"
url = "http://api.openweathermap.org/data/2.5/weather"

try:
    response = requests.get(
        url,
        params={
            "q": "Ranchi,IN",
            "appid": API_KEY,
            "units": "metric"
        },
        timeout=15
    )

    print("HTTP Status:", response.status_code)
    print("Response:", response.text)

    response.raise_for_status()
    data = response.json()

    print("\nCity:", data["name"])
    print("Temperature:", data["main"]["temp"], "°C")
    print("Weather:", data["weather"][0]["description"])

except requests.RequestException as error:
    print("Request failed:", error)
