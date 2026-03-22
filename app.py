from flask import Flask, render_template, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Get API key safely
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json

    question = data["question"]
    subject = data["subject"]

    # Subject-based system prompt
    system_prompt = f"""
    You are a professional {subject} teacher.
    1. Explain clearly
    2. Give simple examples
    3. Then create 3 quiz questions
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ]
    )

    answer = response.choices[0].message.content

    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(debug=True)