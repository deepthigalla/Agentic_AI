import os
from flask import Flask, render_template, request
from dotenv import load_dotenv
import openai

load_dotenv()

app = Flask(__name__)

openai.api_type = "azure"
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_version = "2023-07-01-preview"
openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")
deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT")

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    prompt = request.form.get("prompt", "")
    try:
        response = openai.ChatCompletion.create(
            engine=deployment_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=100
        )
        answer = response["choices"][0]["message"]["content"]
    except Exception as e:
        answer = f"Error: {str(e)}"

    return render_template("index.html", response=answer)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
