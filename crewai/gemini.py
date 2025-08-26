import os
# ❗ Set this before importing anything from `crewai`
os.environ["CREWAI_TELEMETRY_DISABLED"] = "1"

from dotenv import load_dotenv
import google.generativeai as genai
from crewai import Agent, Task, Crew, BaseLLM

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

class GeminiLLM(BaseLLM):
    def __init__(self, api_key: str, model_name="models/gemini-2.0-flash"):
        self.model_name = model_name
        genai.configure(api_key=api_key)
        self.generator = genai.GenerativeModel(model_name)

    def call(self, messages, **kwargs):
        prompt = self._format_prompt(messages)
        response = self.generator.generate_content(prompt)
        return response.text.strip()

    def _format_prompt(self, messages):
        prompt = ""
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            if role == "user":
                prompt += f"User: {content}\n"
            elif role == "assistant":
                prompt += f"Assistant: {content}\n"
        prompt += "Assistant: "
        return prompt

    @property
    def model(self):
        return self.model_name

# === Instantiate Gemini LLM ===
gemini_llm = GeminiLLM(api_key=api_key)

# === User Inputs ===
main_ingredient = "tomato"
dietary_restrictions = "shrimps"

# === Agent ===
culinary_assistant = Agent(
    llm=gemini_llm,
    role="Culinary Assistant",
    backstory="An experienced culinary assistant skilled in finding and tailoring recipes.",
    goal="Find recipes and guide user through steps based on dietary restrictions.",
    verbose=True,
)

# === Tasks ===
find_and_filter_recipes = Task(
    description=f"Find recipes with {main_ingredient} avoiding {dietary_restrictions}.",
    expected_output="One recipe meeting the criteria.",
    agent=culinary_assistant,
)

guide_recipe_steps = Task(
    description="Provide step-by-step instructions for the chosen recipe.",
    expected_output="Cooking instructions.",
    agent=culinary_assistant,
)

# === Crew ===
crew = Crew(
    agents=[culinary_assistant],
    tasks=[find_and_filter_recipes, guide_recipe_steps],
    planning=False,
)

# === Run ===
result = crew.kickoff()
print("\nFinal Result:\n", result)
