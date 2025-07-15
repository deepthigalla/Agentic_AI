# Sample agno from image to genarate the json text 

import json
import together
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv
import together

# Load environment variables from .env file
load_dotenv()

# Initialize the client using the environment variable
client = together.Together(api_key=os.getenv("TOGETHER_API_KEY"))


#client = together.Together()


# Define the schema for the output
class ImageDescription(BaseModel):
    project_name: str = Field(description="The name of the project shown in the image")
    col_num: int = Field(description="The number of columns in the board")


def main():
    imageUrl = "https://napkinsdev.s3.us-east-1.amazonaws.com/next-s3-uploads/d96a3145-472d-423a-8b79-bca3ad7978dd/trello-board.png"

    # Call the LLM with the JSON schema
    extract = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Extract a JSON object from the image."},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": imageUrl,
                        },
                    },
                ],
            },
        ],
        model="Qwen/Qwen2.5-VL-72B-Instruct",
        response_format={
            "type": "json_schema",
            "schema": ImageDescription.model_json_schema(),
        },
    )

    output = json.loads(extract.choices[0].message.content)
    print(json.dumps(output, indent=2))
    return output


main()