# genarte the promt using huggingface from agno 

from huggingface_hub import InferenceClient

import os
from dotenv import load_dotenv
import together

load_dotenv()

api_key = os.getenv("TOGETHER_API_KEY")

# Initialize the InferenceClient with together as the provider

client = together.Together(api_key=api_key)

# Define the chat messages

messages = [  
    {  
        "role": "user",  
        "content": "What is the capital of France?"  
    }  
]

# Generate a chat completion

completion = client.chat.completions.create(  
    model="deepseek-ai/DeepSeek-R1",  
    messages=messages,  
    max_tokens=500  
)

# Print the response

print(completion.choices[0].message)