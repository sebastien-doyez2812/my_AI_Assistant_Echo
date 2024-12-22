from langchain.agents import initialize_agent
from langchain.tools import BaseTool
from math import pi
from typing import Union
from langchain_ollama import OllamaLLM
from langchain.memory import ConversationBufferMemory
import requests
from datetime import datetime
from langchain.globals import set_debug, set_verbose
import json #TODO Todelete


def read_text_from_json(path):
    """
    Extract the data from a JSON file and return it.

    ARGS:
        path = Path where the JSON file is stored.
    """
    with open(path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

PATH_JSON = "JSON_files/prompt.json"

llm = OllamaLLM(model="gemma", prompt=read_text_from_json(PATH_JSON)["starting prompt"])
# Step 4: Set up Conversation Memory
memory = ConversationBufferMemory(memory_key="chat_history")

def read_text_from_json(path):
    """
    Extract the data from a JSON file and return it.

    ARGS:
        path = Path where the JSON file is stored.
    """
    with open(path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

class MultiTool(BaseTool):
    name: str
    description: str

    def _run(self, query: str) -> Union[str, float]:
        if self.name == "Get Current Location":
            return self.get_current_location()
        elif self.name == "time":
            return self.what_time_is_it()
        elif self.name == "weather":
            return self.what_the_weather()
        elif self.name == "wikipedia":
            return self.wikipedia_research()
        else:
            return "Tool not supported."

    def _arun(self, query: str):
        raise NotImplementedError("This tool does not support async")

    def get_current_location(self) -> str:
        try:
            response = requests.get("https://ipinfo.io")
            data = response.json()
            city = data.get("city", "unknown")
            return f"Nous sommes à {city}"
        except Exception as e:
            return f"Error getting location: {e}"


    def what_time_is_it(self):
        now = datetime.now()
        hour = now.strftime("%H")
        minute = now.strftime("%M")
        return f"il est {hour} h {minute} "
    
    def what_the_weather(self, city) -> str:
        try:
            api_key_meteo = "e5859cf005fb60a5e50a53233a95b79a"
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key_meteo}&units=metric"
            response = requests.get(url)
            data = response.json()
            if data["cod"] == 200:
                weather = data["main"]
                temp = weather["temp"]
                real_temp = weather["feels_like"]
                desc = data["weather"][0]["description"]
                return f"Le temps est {desc}, la température est de {temp}°C (mais la température ressenti est de {real_temp}°C)!"
            else:
                return "Erreur lors de la récupération des données météorologiques."
        except Exception as e:
            return f"get_weather error: {e}"

# Define tools using the MultiTool class
location_tool = MultiTool(
    name="Get Current Location",
    description="Useful for  Cet outils va te donner la position à laquelle nous nous trouvons, si l'utilisateur demande ou sommes nous, tu dois t'aider de cette outils.",
)

weather_tool = MultiTool(
    name="Weather",
    description="Cet outils nous donne le temps de dehors, la température exterieur, ainsi que la température ressenti.",
)
time_tool = MultiTool(
    name="time",
    description="Cet outils donne l'heure actuel"
)


PATH_JSON = "JSON_files/prompt.json"
# Initialize LLM

# Initialize agent with tools
tools = [location_tool, time_tool]
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent="zero-shot-react-description",  # Ensures a simple agent
    verbose=True,  # Turn off verbose for cleaner output
    memory= memory,
    handle_parsing_errors=True
)

