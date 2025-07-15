# Genarate the image from promt 

from together import Together
import os
from dotenv import load_dotenv
import together

load_dotenv()

api_key = os.getenv("TOGETHER_API_KEY")

# Initialize the InferenceClient with together as the provider

client = together.Together(api_key=api_key)

#  Generating an image

response = client.images.generate(
    prompt="a flying tume se tum tak", model="black-forest-labs/FLUX.1-schnell", steps=4
)

print(response.data[0].url)