import os
from dotenv import load_dotenv
from langchain_community.tools import GoogleSerperRun
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain.tools import Tool  # 🟢 THIS IS IMPORTANT
from crewai import Agent, Task, Crew, LLM

# ❗ Disable telemetry before using crewai
os.environ["CREWAI_TELEMETRY_DISABLED"] = "1"

# Load environment variables
load_dotenv()
api_key = os.getenv("SERPER_API_KEY")  # Make sure this is set

# Define custom web search tool
#serper = GoogleSerperAPIWrapper(type="search") # or "news" if you prefer

# Schema for tool input
# def web_search(query: str) -> str:
#     # Your logic with Serper API here
#     return f"Results for: {query}"

# Set up Serper tool
serper_wrapper = GoogleSerperAPIWrapper(type="search")

# Wrap it into a valid LangChain Tool for CrewAI
from crewai.tools import BaseTool
from typing import Any

class WebSearchTool(BaseTool):
    name: str = "WebSearch"
    description: str = "Performs a web search for fitness-related questions."

    def _run(self, query: str, **kwargs: Any) -> str:
        return serper_wrapper.invoke(query)



# Instantiate CrewAI-compatible tool
web_search_tool = WebSearchTool()

 
# Then use it in your agent
#web_search_tool = web_search  # Don't call it — just reference it


# Initialize LLM
llm = LLM(model="gpt-4")

# User inputs
fitness_goal = "muscle gain"
nutrition_preference = "high protein"
historical_weight_data = ["87kg", "85kg", "88kg", "87kg", "86kg"]

# Agents
fitness_tracker_agent = Agent(
    llm=llm,
    role="Fitness Tracker",
    backstory="An AI-powered fitness tracker agent that helps users set goals, track progress, and recommend personalized workout plans.",
    goal="Set fitness goals, track progress, and offer recommendations.",
    verbose=True,
)

recommendation_agent = Agent(
    role="Fitness Recommender",
    goal="Suggest fitness plans and health tips to users",
    backstory="Expert in health, pulling current data from the web.",
    tools=[web_search_tool],  # ✅ This is now valid
    llm=llm,
    verbose=True
)

# Tasks
set_and_track_goals = Task(
    description=f"Set the user's fitness goal to {fitness_goal} and track their progress using this data: {historical_weight_data}.",
    expected_output="A fitness plan for muscle gain and a tracking strategy.",
    agent=fitness_tracker_agent,
)

fetch_fitness_recommendations = Task(
    description=f"Find fitness and nutrition recommendations for goal '{fitness_goal}' with a '{nutrition_preference}' diet.",
    expected_output="Personalized fitness and dietary recommendations.",
    agent=recommendation_agent,
)

provide_workout_plan = Task(
    description="Create a step-by-step workout plan for muscle gain.",
    expected_output="A structured workout plan.",
    agent=fitness_tracker_agent,
)

# Crew setup
crew = Crew(
    agents=[fitness_tracker_agent, recommendation_agent],
    tasks=[set_and_track_goals, fetch_fitness_recommendations, provide_workout_plan],
    planning=True,
)

# Start execution
crew.kickoff()
