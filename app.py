from flask import Flask, render_template, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
import os
import sqlite3

load_dotenv()

app = Flask(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect("wallet.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS wallet (
        id INTEGER PRIMARY KEY,
        balance REAL
    )
    """)

    c.execute("INSERT OR IGNORE INTO wallet (id, balance) VALUES (1, 0)")

    conn.commit()
    conn.close()

init_db()

# ---------------- AI TUTOR ----------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json

    question = data["question"]
    subject = data["subject"]

    system_prompt = f"You are a professional {subject} teacher. Explain clearly and give 3 quiz questions."

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ]
    )

    answer = response.choices[0].message.content

    return jsonify({"answer": answer})

# ---------------- WALLET ----------------
@app.route("/wallet")
def wallet():
    return render_template("wallet.html")

@app.route("/balance")
def balance():
    conn = sqlite3.connect("wallet.db")
    c = conn.cursor()

    c.execute("SELECT balance FROM wallet WHERE id=1")
    balance = c.fetchone()[0]

    conn.close()

    return jsonify({"balance": balance})

@app.route("/deposit", methods=["POST"])
def deposit():
    amount = float(request.json["amount"])

    conn = sqlite3.connect("wallet.db")
    c = conn.cursor()

    c.execute("UPDATE wallet SET balance = balance + ?", (amount,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Deposited successfully"})

@app.route("/withdraw", methods=["POST"])
def withdraw():
    amount = float(request.json["amount"])

    conn = sqlite3.connect("wallet.db")
    c = conn.cursor()

    c.execute("SELECT balance FROM wallet WHERE id=1")
    balance = c.fetchone()[0]

    if balance >= amount:
        c.execute("UPDATE wallet SET balance = balance - ?", (amount,))
        conn.commit()
        message = "Withdraw successful"
    else:
        message = "Insufficient funds"

    conn.close()

    return jsonify({"message": message})

if __name__ == "__main__":
    app.run(debug=True)