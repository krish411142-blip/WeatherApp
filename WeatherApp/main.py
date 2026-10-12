
import requests
from threading import Thread

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.widget import Widget


# Original GUI settings — unchanged
Window.size = (400, 650)
Window.clearcolor = (0.05, 0.12, 0.25, 1)

# OpenWeatherMap API settings
API_KEY = "6d660a3e7fea49ee107ad508def1b411"
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"


class WeatherApp(App):

    def build(self):
        self.title = "Weather App"

        root = BoxLayout(
            orientation="vertical",
            padding=25,
            spacing=15
         )

        root.add_widget(Label(
            text="[b]WEATHER APP[/b]",
            markup=True,
            font_size=30,
            size_hint_y=None,
            height=70,
            color=(0.4, 0.8, 1, 1)
        ))

        root.add_widget(Label(
            text="Check current weather of any city",
            font_size=15,
            size_hint_y=None,
            height=35
        ))

        self.city_input = TextInput(
            hint_text="Enter city name...",
            multiline=False,
            font_size=18,
            size_hint_y=None,
            height=55,
            padding=15
        )

        self.city_input.bind(
            on_text_validate=self.search_weather
        )
        root.add_widget(self.city_input)

        self.search_button = Button(
            text="GET WEATHER",
            font_size=18,
            bold=True,
            size_hint_y=None,
            height=55,
            background_normal="",
            background_color=(0.05, 0.55, 0.9, 1)
        )

        self.search_button.bind(
            on_press=self.search_weather
        )
        root.add_widget(self.search_button)

        self.result = Label(
            text="Enter a city to see its weather.",
            markup=True,
            font_size=17,
            halign="center",
            valign="middle"
        )

        self.result.bind(
            size=lambda obj, size:
            setattr(obj, "text_size", size)
        )
        root.add_widget(self.result)

        root.add_widget(Widget())

        root.add_widget(Label(
            text="Powered by OpenWeatherMap",
            font_size=12,
            size_hint_y=None,
            height=30,
            color=(2,5,8,5)
        ))

        return root


    def search_weather(self, instance):
     print("GET WEATHER button clicked!")

     city = self.city_input.text.strip()

     if not city:
        self.show_result("Please enter a city name.")
        return

     if not API_KEY.strip() or API_KEY == "YOUR_VALID_API_KEY":
        self.show_result("API key is missing or invalid.")
        return  # Return sirf API key missing hone par chalega

     self.search_button.disabled = True
     self.search_button.text = "LOADING..."
     self.show_result("Fetching weather data...")

     print("Searching weather for:", city)

     Thread(
        target=self.fetch_weather,
        args=(city,),
        daemon=True
     ).start()


    def fetch_weather(self, city):
        message = "Unable to fetch weather data."

        try:
            response = requests.get(
                BASE_URL,
                params={
                    "q": city,
                    "appid": API_KEY,
                    "units": "metric"
                },
                timeout=15
            )

            print("HTTP Status:", response.status_code)

            try:
                data = response.json()
            except ValueError:
                data = {}

            print("API response:", data)

            if response.status_code == 200:
                weather_info = data["weather"][0]
                main_info = data["main"]

                weather = weather_info["description"].title()
                temp = float(main_info["temp"])
                feels = float(main_info["feels_like"])
                humidity = main_info["humidity"]
                wind = data.get("wind", {}).get("speed", 0)

                city_name = data.get("name", city)
                country = data.get("sys", {}).get("country", "")

                message = (
                    f"[b]{city_name}, {country}[/b]\n\n"
                    f"Temperature: {temp:.1f} °C\n\n"
                    f"Feels Like: {feels:.1f} °C\n\n"
                    f"Condition: {weather}\n\n"
                    f"Humidity: {humidity}%\n\n"
                    f"Wind Speed: {wind} m/s"
                )

            elif response.status_code == 401:
                message = (
                    "Invalid API key.\n"
                    "Check your OpenWeatherMap API key."
                )

            elif response.status_code == 404:
                message = (
                    f"City '{city}' not found.\n"
                    "Please check the city name."
                )

            else:
                api_error = data.get("message", "Unknown API error")
                message = (
                    f"API Error: {response.status_code}\n"
                    f"{api_error}"
                )

        except requests.exceptions.Timeout:
            message = "Request timed out.\nPlease try again."

        except requests.exceptions.ConnectionError:
            message = (
                "Connection failed.\n"
                "Check your internet connection."
            )

        except requests.exceptions.RequestException as error:
            message = f"Network error:\n{error}"

        except (ValueError, KeyError, IndexError, TypeError) as error:
            message = f"Weather data error:\n{error}"

        except Exception as error:
            message = f"Unexpected error:\n{error}"
            print("Unexpected error:", repr(error))

        print("Final message:", message)

        # Update Kivy widgets on the main UI thread.
        Clock.schedule_once(
            lambda dt, result=message: self.finish_search(result),
            0
        )

    def finish_search(self, message):
        self.result.markup = True
        self.result.text = message

        self.search_button.disabled = False
        self.search_button.text = "GET WEATHER"

    
    def show_result(self, message):
        self.result.markup = False
        self.result.text = message



if __name__ == "__main__":
    WeatherApp().run()
